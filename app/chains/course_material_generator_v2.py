from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sentence_transformers import SentenceTransformer
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from app.models.dto.user_entry.user_entry_dto import UserEntryDto
from app.chains.llm.open_ai_gpt5_mini_llm import OpenAiGPT5MiniLlm
from app.chains.template_structure_generator import TemplateStructureGenerator


class CourseMaterialGeneratorV2:
    """
    Générateur de supports de cours V2 utilisant TemplateStructureGenerator.

    Le workflow :
    1. Génère un JSON pédagogique enrichi à partir de UserEntryDto avec un LLM
    2. Utilise TemplateStructureGenerator pour mapper ce JSON vers des templates
    3. Construit le JSON final en hydratant la structure
    4. Valide et retourne le support de cours

    Avantages vs V1:
    - Cohérence globale (structure d'un seul coup vs morceaux isolés)
    - Contenu enrichi et contextualisé (pas de phrases courtes)
    - Meilleure imbrication sémantique des templates
    - Moins de duplication de contenu
    """

    def __init__(
        self,
        db_session: Session,
        embedding_model: SentenceTransformer,
    ):
        """
        Args:
            db_session: Session SQLAlchemy pour accéder à la DB
            embedding_model: Modèle sentence-transformers pour les embeddings
        """
        self.db = db_session
        self.embedding_model = embedding_model
        self.llm = OpenAiGPT5MiniLlm().get_llm()
        self.template_structure_generator = TemplateStructureGenerator(
            db_session=db_session,
            embedding_model=embedding_model
        )

    def generate_course_material(
        self,
        user_entry: UserEntryDto,
        top_k: int = 20,
        category_quotas: Dict[str, int] = None
    ) -> Dict[str, Any]:
        """
        Génère des supports de cours à partir d'un UserEntryDto.

        Args:
            user_entry: Contient le contexte, le contenu textuel et les médias
            top_k: Nombre de templates similaires à récupérer (défaut: 20)
            category_quotas: Dictionnaire {catégorie: quota} pour limiter par catégorie
                           Ex: {"layouts/": 5, "conceptual/": 8}

        Returns:
            Dict contenant:
            - support: Le support de cours complet structuré
            - prompts: Dict avec les prompts de chaque étape
        """
        # Étape 1: Générer le JSON pédagogique enrichi
        pedagogical_json, pedagogical_prompt = self._generate_pedagogical_json(user_entry)

        # Étape 2: Générer la structure de templates
        context_description = self._create_context_description(user_entry)

        if category_quotas is None:
            # Par défaut: peu de layouts, plus de contenu conceptuel
            category_quotas = {"layouts/": 5, "conceptual/": 10, "text/": 5}

        structure_result = self.template_structure_generator.generate_template_structure(
            source_json=pedagogical_json,
            context_description=context_description,
            top_k=top_k,
            category_quotas=category_quotas
        )

        template_structure = structure_result["template_structure"]
        structure_prompt = structure_result["prompt"]

        # Étape 3: Le JSON final est déjà construit par TemplateStructureGenerator
        # Il contient la structure avec les valeurs hydratées

        # Étape 4: Validation
        validated_support = self._validate_support(template_structure)

        return {
            "support": validated_support,
            "prompts": {
                "step1_pedagogical_json": pedagogical_prompt,
                "step2_template_structure": structure_prompt
            }
        }

    def _aggregate_content(self, user_entry: UserEntryDto) -> Dict[str, Any]:
        """
        Agrège le contenu textuel et les médias depuis UserEntryDto.

        Args:
            user_entry: Données d'entrée de l'utilisateur

        Returns:
            Dict contenant le contenu agrégé:
            - text: Texte agrégé (book_scan + diction triés par order)
            - images: Liste des images disponibles
            - videos: Liste des vidéos disponibles
            - context: Informations de contexte (course, topic_path)
        """
        # Agréger le texte (book_scan + diction triés par order)
        text_entries = []

        # Ajouter book_scan_entry
        for entry in user_entry.book_scan_entry:
            text_entries.append(
                {"order": entry.order, "content": entry.raw_data, "type": "book_scan"}
            )

        # Ajouter diction_entry
        for entry in user_entry.diction_entry:
            # Combiner les blocs de texte
            combined_text = "\n".join(entry.text_blocs)
            text_entries.append(
                {"order": entry.order, "content": combined_text, "type": "diction"}
            )

        # Trier par order
        text_entries.sort(key=lambda x: x["order"])

        # Créer le texte agrégé
        aggregated_text = "\n\n".join([entry["content"] for entry in text_entries])

        # Agréger les médias
        images = [
            {"order": img.order, "description": img.img_description, "url": img.img_url}
            for img in user_entry.img_entry
        ]

        videos = [
            {
                "order": video.order,
                "url": video.video_url,
                "description": video.video_description,
                "start_time": video.video_start_time,
            }
            for video in user_entry.video_entry
        ]

        return {
            "text": aggregated_text,
            "images": images,
            "videos": videos,
            "context": {
                "course": user_entry.context_entry.course,
                "topic_path": user_entry.context_entry.topic_path,
            },
        }

    def _format_media_for_prompt(self, images: List[Dict], videos: List[Dict]) -> str:
        """
        Formate les médias disponibles pour inclusion dans le prompt.

        Args:
            images: Liste des images
            videos: Liste des vidéos

        Returns:
            String formaté décrivant les médias disponibles
        """
        formatted_parts = []

        if images:
            formatted_parts.append("IMAGES DISPONIBLES:")
            for i, img in enumerate(images, 1):
                formatted_parts.append(
                    f"  - Image {i}: {img['description']} (URL: {img['url']})"
                )

        if videos:
            formatted_parts.append("\nVIDÉOS DISPONIBLES:")
            for i, video in enumerate(videos, 1):
                formatted_parts.append(
                    f"  - Vidéo {i}: {video['description']} (URL: {video['url']}, Début: {video['start_time']})"
                )

        if not formatted_parts:
            return "Aucun média disponible."

        return "\n".join(formatted_parts)

    def _generate_pedagogical_json(
        self, user_entry: UserEntryDto
    ) -> tuple[Dict[str, Any], str]:
        """
        Génère un JSON pédagogique enrichi à partir de UserEntryDto.

        Ce JSON contient des explications complètes, contextualisées, sans phrases courtes.
        Il structure le contenu de manière optimale pour l'apprentissage.

        Args:
            user_entry: Données d'entrée de l'utilisateur

        Returns:
            Tuple contenant:
            - Dict: JSON pédagogique enrichi
            - str: Le prompt complet envoyé au LLM
        """
        # Agréger le contenu brut
        aggregated_content = self._aggregate_content(user_entry)

        # Formater les médias pour le prompt
        media_description = self._format_media_for_prompt(
            aggregated_content["images"],
            aggregated_content["videos"]
        )

        # Créer le prompt système
        system_prompt = """Tu es un expert pédagogue spécialisé dans la structuration de contenu éducatif.

CONTEXTE PÉDAGOGIQUE:
- Cours: {course}
- Chemin du sujet: {topic_path}

MÉDIAS DISPONIBLES:
{media_description}

Ta mission : transformer des notes de cours brutes en un JSON structuré OPTIMAL pour l'apprentissage.

RÈGLES CRITIQUES:
1. ✅ Crée des explications COMPLÈTES et CONTEXTUALISÉES (plusieurs phrases développées)
2. ✅ NE fais PAS de phrases trop courtes - développe les concepts avec du contexte
3. ✅ Ajoute du contexte pour faciliter la compréhension (pourquoi, comment, dans quel cas)
4. ✅ Regroupe les informations par thèmes logiques et cohérents
5. ✅ Explicite les liens entre les concepts (similitudes, différences, relations)
6. ✅ Enrichis avec des exemples concrets et pertinents
7. ✅ Intègre les références aux médias disponibles de manière sémantique
8. 🚫 INTERDICTION ABSOLUE: NE crée PAS d'exercices, questions, QCM, quiz ou évaluations
9. ✅ Utilise un langage clair et pédagogique, adapté à l'apprentissage

STRUCTURE JSON ATTENDUE:
{{
  "learning_objective": "Objectif d'apprentissage global détaillé (plusieurs phrases explicatives)",
  "course_sections": [
    {{
      "section_title": "Titre clair de la section",
      "section_description": "Description complète et contextualisée sur plusieurs phrases qui explique le sujet, son importance et son contexte",
      "key_concepts": [
        {{
          "concept_name": "Nom du concept principal",
          "explanation": "Explication détaillée et complète avec contexte, exemples et clarifications (plusieurs phrases bien développées)",
          "examples": ["Exemple concret 1 avec contexte", "Exemple concret 2 avec contexte"],
          "related_media": {{
            "image_url": "URL de l'image si pertinent pour ce concept",
            "image_description": "Description détaillée de ce que montre l'image",
            "video_url": "URL de la vidéo si pertinent pour ce concept",
            "video_description": "Description de ce que montre la vidéo",
            "video_timestamp": "timestamp de début"
          }}
        }}
      ],
      "additional_notes": "Notes complémentaires contextualisées qui apportent des précisions, des nuances ou des informations utiles (plusieurs phrases)"
    }}
  ]
}}

EXEMPLE DE BON CONTENU (développé et contextualisé):
❌ MAUVAIS: "Le verbe ser. Conjugaison: soy, eres, es."
✅ BON: "Le verbe 'ser' est l'un des deux verbes signifiant 'être' en espagnol. Il s'utilise spécifiquement pour exprimer les caractéristiques permanentes d'une personne ou d'une chose, comme l'identité, la profession, l'origine géographique ou la nationalité. Sa conjugaison au présent de l'indicatif est irrégulière et doit être mémorisée: yo soy (je suis), tú eres (tu es), él/ella es (il/elle est), nosotros somos (nous sommes), vosotros sois (vous êtes), ellos/ellas son (ils/elles sont)."

Réponds UNIQUEMENT avec le JSON valide, sans texte additionnel."""

        user_prompt = """Voici les notes de cours brutes à transformer en JSON pédagogique optimal:

CONTENU TEXTUEL:
{text}

Génère le JSON structuré en suivant STRICTEMENT les règles ci-dessus. Développe les explications, ajoute du contexte, ne fais pas de phrases courtes."""

        # Créer le prompt template
        prompt = ChatPromptTemplate.from_messages(
            [("system", system_prompt), ("human", user_prompt)]
        )

        # Créer la chaîne avec parser JSON
        chain = prompt | self.llm | JsonOutputParser()

        # Préparer le prompt complet pour le retour
        full_prompt = prompt.format(
            course=aggregated_content["context"]["course"],
            topic_path=aggregated_content["context"]["topic_path"],
            media_description=media_description,
            text=aggregated_content["text"]
        )

        # Exécuter la chaîne
        result = chain.invoke({
            "course": aggregated_content["context"]["course"],
            "topic_path": aggregated_content["context"]["topic_path"],
            "media_description": media_description,
            "text": aggregated_content["text"]
        })

        return result, full_prompt

    def _create_context_description(self, user_entry: UserEntryDto) -> str:
        """
        Crée une description de contexte pour TemplateStructureGenerator.

        Args:
            user_entry: Données d'entrée de l'utilisateur

        Returns:
            String décrivant le contexte pédagogique
        """
        return f"Cours de {user_entry.context_entry.course} - Sujet: {user_entry.context_entry.topic_path}"

    def _validate_support(self, support_json: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valide la structure du support de cours généré.

        Args:
            support_json: JSON du support à valider

        Returns:
            Support JSON validé avec version

        Raises:
            ValueError: Si le JSON est invalide
        """
        if not isinstance(support_json, dict):
            raise ValueError("Le support doit être un objet JSON")

        # Vérifier qu'il y a au moins un template_name quelque part dans la structure
        if not self._contains_template_name(support_json):
            raise ValueError("Le support doit contenir au moins un template_name")

        # Ajouter la version si absente
        if "version" not in support_json:
            support_json["version"] = "1.0.0"

        return support_json

    def _contains_template_name(self, obj: Any) -> bool:
        """
        Vérifie récursivement si un objet contient au moins un template_name.

        Args:
            obj: Objet à vérifier

        Returns:
            True si un template_name est trouvé, False sinon
        """
        if isinstance(obj, dict):
            if "template_name" in obj:
                return True
            for value in obj.values():
                if self._contains_template_name(value):
                    return True
        elif isinstance(obj, list):
            for item in obj:
                if self._contains_template_name(item):
                    return True
        return False
