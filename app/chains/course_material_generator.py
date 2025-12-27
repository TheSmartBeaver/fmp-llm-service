from typing import List, Dict, Any
import asyncio
from sqlalchemy.orm import Session
from sentence_transformers import SentenceTransformer
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from app.models.dto.user_entry.user_entry_dto import UserEntryDto
from app.utils.template_search import fetch_similar_templates
from app.chains.llm.open_ai_gpt5_mini_llm import OpenAiGPT5MiniLlm
from app.chains.llm.open_ai_o3_mini_llm import OpenAiO3MiniLlm


class CourseMaterialGenerator:
    """
    Générateur de supports de cours utilisant la recherche vectorielle et LangChain.

    Le workflow :
    1. Agrège le contenu textuel (book_scan + diction) et les médias (img + video)
    2. Génère des paires info-format intermédiaires à partir du contenu agrégé
    3. Pour chaque paire, recherche les templates HTML les plus similaires dans PostgreSQL (pgvector)
    4. Utilise un LLM pour générer un JSON structuré pour chaque morceau de support
    5. Valide et retourne le JSON final
    """

    def __init__(
        self,
        db_session: Session,
        llm: BaseChatModel,
        embedding_model: SentenceTransformer,
    ):
        """
        Args:
            db_session: Session SQLAlchemy pour accéder à la DB
            llm: Modèle LangChain (ChatOpenAI)
            embedding_model: Modèle sentence-transformers pour les embeddings
        """
        self.db = db_session
        self.llm = llm
        self.embedding_model = embedding_model

    def generate_course_material(
        self, user_entry: UserEntryDto, top_k: int = 15
    ) -> Dict[str, Any]:
        """
        Génère des supports de cours à partir d'un UserEntryDto.

        Args:
            user_entry: Contient le contexte, le contenu textuel et les médias
            top_k: Nombre de templates similaires à récupérer par paire (défaut: 15)

        Returns:
            Dict contenant:
            - supports: Liste de Dict contenant les supports de cours avec structure:
                [
                    {
                        "support": {...},
                        "version": "1.0.0"
                    },
                    ...
                ]
            - prompt: Le prompt complet envoyé au LLM (premier et derniers prompts)
        """
        # Étape 1: Agréger le contenu
        aggregated_content = self._aggregate_content(user_entry)

        # Étape 2: Générer les paires informations-format intermédiaires
        info_format_pairs, info_format_prompt = self._generate_info_format_pairs(
            aggregated_content, user_entry.context_entry
        )

        # Étape 3 & 4: Pour chaque paire, récupérer les templates et générer le support EN PARALLÈLE
        all_supports = []
        generation_prompts = []

        # Créer une liste de coroutines pour l'exécution parallèle
        tasks = []
        for info_format_pair in info_format_pairs:
            # Calculer l'embedding pour cette paire
            pair_text = (
                f"{info_format_pair['objectif']} {info_format_pair['format']}"
            )
            embedding = self._generate_embedding(pair_text)

            # Récupérer les templates pertinents pour cette paire
            templates = fetch_similar_templates(self.db, embedding, top_k, { "layouts/": 3, "text/": 5}, True)

            # Créer une tâche asynchrone pour générer le support
            tasks.append(
                self._generate_single_support_from_info_format_async(
                    info_format_pair, templates, aggregated_content
                )
            )

        # Exécuter toutes les tâches en parallèle
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        results = loop.run_until_complete(asyncio.gather(*tasks))

        # Extraire les résultats
        for support, gen_prompt in results:
            all_supports.append(support)
            generation_prompts.append(gen_prompt)

        # Préparer le prompt complet pour le retour
        full_prompt = (
            f"=== PROMPT DE GÉNÉRATION DES PAIRES INFORMATIONS-FORMAT ===\n{info_format_prompt}\n\n=== PROMPTS DE GÉNÉRATION DES SUPPORTS ===\n"
            + "\n\n---\n\n".join(generation_prompts)
        )

        # Étape 5: Valider le JSON de tous les supports
        validated_json = self._validate_json(all_supports)

        return {"supports": validated_json, "prompt": full_prompt}

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

    def _generate_info_format_pairs(
        self, aggregated_content: Dict[str, Any], context_entry
    ) -> tuple[List[Dict[str, str]], str]:
        """
        Génère des paires information-format intermédiaires à partir du contenu agrégé.

        Args:
            aggregated_content: Contenu agrégé (texte + médias + contexte)
            context_entry: Contexte pédagogique

        Returns:
            Tuple contenant:
            - Liste de dictionnaires avec les clés 'information' et 'format'
            - Le prompt complet envoyé au LLM
        """
        # Construire la description des médias disponibles
        media_description = self._format_media_for_prompt(
            aggregated_content["images"], aggregated_content["videos"]
        )

        # Créer le prompt système
        system_prompt = """Tu es un expert en pédagogie spécialisé dans la structuration de contenu éducatif pour application mobile.

CONTEXTE PÉDAGOGIQUE:
- Cours: {course}
- Chemin du sujet: {topic_path}

MÉDIAS DISPONIBLES:
{media_description}

Ta mission est d'analyser des notes de cours et de produire une structure optimale pour l'apprentissage sur mobile.

RÈGLES DE STRUCTURATION:
1. "objectif" : l'objectif d'apprentissage spécifique et focalisé
2. "texte_associe" : le texte exact issu des notes (ne pas inventer ou reformuler, juste extraire)
3. "format" : le format de présentation le plus adapté pour atteindre cet objectif d'apprentissage


STRUCTURE ATTENDUE (TABLEAU JSON):
[
    {{
        "objectif": "Objectif d'apprentissage précis et actionnable",
        "texte_associe": "Citation exacte du texte original, sans modification",
        "format": "comment cette information devrait être structurée/présentée"
    }}
]

Réponds UNIQUEMENT avec le TABLEAU JSON valide, sans texte additionnel."""

        user_prompt = """Voici la prise de notes de mes cours. Donne-moi la structure optimale pour apprendre ce lot d'informations:

{text}
"""

        # Créer le prompt template
        prompt = ChatPromptTemplate.from_messages(
            [("system", system_prompt), ("human", user_prompt)]
        )

        # Créer la chaîne avec parser JSON
        gpt5_mini_llm = OpenAiGPT5MiniLlm().get_llm()
        chain = prompt | gpt5_mini_llm | JsonOutputParser()

        # Préparer le prompt complet pour le retour
        full_prompt = prompt.format(
            course=context_entry.course,
            topic_path=context_entry.topic_path,
            media_description=media_description,
            text=aggregated_content["text"],
        )

        # Exécuter la chaîne
        result = chain.invoke(
            {
                "course": context_entry.course,
                "topic_path": context_entry.topic_path,
                "media_description": media_description,
                "text": aggregated_content["text"],
            }
        )

        return result, full_prompt

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

    def _generate_embedding(self, text: str) -> List[float]:
        """
        Génère un embedding à 384 dimensions du texte.

        Args:
            text: Texte à encoder

        Returns:
            Liste de 384 floats représentant l'embedding
        """
        embedding = self.embedding_model.encode(text, normalize_embeddings=True)
        return embedding.tolist()


    def _build_single_support_prompt_and_chain(
        self,
        info_format_pair: Dict[str, str],
        templates: List[Dict[str, Any]],
        aggregated_content: Dict[str, Any],
    ) -> tuple[Any, str, Dict]:
        """
        Construit le prompt et la chaîne LangChain pour générer un support de cours unique.

        Args:
            info_format_pair: Dictionnaire contenant 'objectif', 'texte_associe' et 'format'
            templates: Liste des templates disponibles avec leurs métadonnées
            aggregated_content: Contenu agrégé incluant les médias

        Returns:
            Tuple contenant:
            - La chaîne LangChain configurée
            - Le prompt complet formaté
            - Les paramètres d'invocation
        """
        # Préparer la liste des templates pour le prompt
        templates_description = self._format_templates_for_prompt(templates)

        # Préparer la description des médias
        media_description = self._format_media_for_prompt(
            aggregated_content["images"], aggregated_content["videos"]
        )

        # Créer le prompt système
        system_prompt = """Tu es un expert en pédagogie et en création de supports de cours éducatifs.

Ton rôle est de transformer UN objectif d'apprentissage avec son texte et format associés en UN support de cours structuré au format JSON.

CONTEXTE PÉDAGOGIQUE:
- Cours: {course}
- Chemin du sujet: {topic_path}

TEMPLATES DISPONIBLES:
{templates}

MÉDIAS DISPONIBLES:
{media_description}

RÈGLES IMPORTANTES:
1. Tu dois créer UN objet JSON représentant UN morceau de support de cours
2. Le support utilise des templates (briques HTML) identifiés par "template_name"
3. ⚠️ CRITIQUE: Les "template_name" doivent EXACTEMENT correspondre aux "Path" des templates disponibles ci-dessus (copie-colle exact)
4. ⚠️ CRITIQUE: Les noms de champs (field_name_X) doivent STRICTEMENT correspondre à ceux décrits dans "Usage des champs" de chaque template
5. ❌ N'INVENTE JAMAIS de template_name ou de nom de champ qui n'est pas explicitement listé dans les templates disponibles
6. Tu peux imbriquer les structures (objets dans objets, tableaux, etc.) pour créer un support riche
7. ❌ Ne duplique pas le même contenu textuel dans plusieurs champs du support
8. Le FORMAT spécifié doit guider ton choix de templates et la structure du support
9. ⚠️ IMPORTANT: Si le format mentionne une image ou vidéo, tu DOIS l'intégrer en utilisant les médias disponibles ci-dessus
10. Pour intégrer un média, utilise un template approprié et référence l'URL du média disponible
11. ⚠️ IMPORTANT: Utilise le TEXTE ASSOCIÉ fourni sans l'inventer ou le reformuler (c'est le texte original des notes de cours)
12. ⚠️ IMPORTANT: Si aucune template ne convient parfaitement, écris avec une template qu'il manque une template pour tel texte et format.

STRUCTURE ATTENDUE (UN SEUL OBJET JSON):
{{
    "support": {{
        "template_name": "COPIE EXACTE du Path d'un template listé ci-dessus",
        "nom_de_champ_exact": "contenu pédagogique ou objet imbriqué",
        "autre_nom_exact": "contenu ou tableau",
        ...
    }},
    "version": "1.0.0"
}}

ATTENTION: Les noms des champs doivent provenir UNIQUEMENT de la description "Usage des champs" du template choisi.

EXEMPLE D'INTÉGRATION DE MÉDIA:
Si le format demande "explication avec image illustrative" et qu'une image pertinente est disponible:
{{
    "support": {{
        "template_name": "section_with_media_template",
        "field_name_1": "Titre de la section",
        "field_name_2": "Explication textuelle...",
        "field_name_3": {{
            "template_name": "image_template",
            "field_name_1": "Description de l'image",
            "field_name_2": "URL_DE_L_IMAGE_DISPONIBLE"
        }}
    }},
    "version": "1.0.0"
}}

Réponds UNIQUEMENT avec l'OBJET JSON valide, sans texte additionnel."""

        user_prompt = """Voici l'objectif d'apprentissage à transformer en support de cours:

OBJECTIF: {objectif}

TEXTE ASSOCIÉ (texte original à utiliser): {texte_associe}

FORMAT: {format}

Génère le JSON du support de cours en utilisant les templates disponibles. Si le format mentionne des médias (image/vidéo), utilise les médias disponibles listés ci-dessus."""

        # Créer le prompt template
        prompt = ChatPromptTemplate.from_messages(
            [("system", system_prompt), ("human", user_prompt)]
        )

        # Créer la chaîne avec parser JSON
        o1_mini_llm = OpenAiO3MiniLlm().get_llm()
        chain = prompt | o1_mini_llm | JsonOutputParser()

        # Préparer les paramètres d'invocation
        invoke_params = {
            "course": aggregated_content["context"]["course"],
            "topic_path": aggregated_content["context"]["topic_path"],
            "templates": templates_description,
            "media_description": media_description,
            "objectif": info_format_pair["objectif"],
            "texte_associe": info_format_pair["texte_associe"],
            "format": info_format_pair["format"],
        }

        # Préparer le prompt complet pour le retour
        full_prompt = prompt.format(**invoke_params)

        return chain, full_prompt, invoke_params

    async def _generate_single_support_from_info_format_async(
        self,
        info_format_pair: Dict[str, str],
        templates: List[Dict[str, Any]],
        aggregated_content: Dict[str, Any],
    ) -> tuple[Dict[str, Any], str]:
        """
        Génère un support de cours unique à partir d'une paire information-format (VERSION ASYNCHRONE).

        Args:
            info_format_pair: Dictionnaire contenant 'information' et 'format'
            templates: Liste des templates disponibles
            aggregated_content: Contenu agrégé incluant les médias

        Returns:
            Tuple contenant:
            - Dict JSON contenant un support de cours structuré
            - Le prompt complet envoyé au LLM
        """
        chain, full_prompt, invoke_params = self._build_single_support_prompt_and_chain(
            info_format_pair, templates, aggregated_content
        )

        # Exécuter la chaîne de manière ASYNCHRONE
        result = await chain.ainvoke(invoke_params)

        return result, full_prompt

    def _format_templates_for_prompt(self, templates: List[Dict[str, Any]]) -> str:
        """
        Formate les templates pour les inclure dans le prompt du LLM.

        Args:
            templates: Liste des templates avec métadonnées

        Returns:
            String formaté décrivant chaque template
        """
        formatted = []
        for i, tmpl in enumerate(templates, 1):
            # Créer un exemple de structure JSON pour ce template
            json_example = self._create_template_json_example(tmpl)

            formatted.append(
                f"""
Template {i}:
- Path (à utiliser EXACTEMENT comme template_name): "{tmpl['template_name']}"
- Usage des champs: {tmpl['fields_usage']}
- Description courte: {tmpl['short_description']}
- Exemple de structure JSON attendue:
{json_example}
"""
            )
        return "\n".join(formatted)

    def _create_template_json_example(self, template: Dict[str, Any]) -> str:
        """
        Crée un exemple de structure JSON pour un template donné.

        Args:
            template: Métadonnées du template

        Returns:
            String contenant un exemple de structure JSON
        """
        import re

        fields_usage = template.get("fields_usage", "")
        field_matches = re.findall(r"(\w+)\s*:", fields_usage)

        if field_matches:
            example_fields = []
            for field_name in field_matches[:3]:
                example_fields.append(
                    f'    "{field_name}": "valeur du contenu pédagogique"'
                )

            example = "{\n" + f'    "template_name": "{template["template_name"]}",\n'
            example += ",\n".join(example_fields)
            example += "\n  }"
        else:
            example = "{\n" + f'    "template_name": "{template["template_name"]}",\n'
            example += '    "voir_usage_des_champs_ci_dessus": "..."\n  }'

        return example

    def _validate_json(
        self, supports_json: Any, templates: List[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Valide la structure du JSON généré (tableau de supports de cours).

        Args:
            supports_json: JSON à valider (doit être un tableau)
            templates: (Optionnel) Liste des templates pour validation stricte

        Returns:
            Tableau JSON validé

        Raises:
            ValueError: Si le JSON est invalide
        """
        # Vérifier que c'est bien un tableau
        if not isinstance(supports_json, list):
            raise ValueError("Le JSON doit être un tableau de supports de cours")

        # Vérifier que le tableau n'est pas vide
        if len(supports_json) == 0:
            raise ValueError("Le tableau de supports ne peut pas être vide")

        # Créer un set de template_names valides si fourni
        valid_template_names = None
        if templates:
            valid_template_names = {tmpl["template_name"] for tmpl in templates}

        # Valider chaque support du tableau
        validated_supports = []
        for i, support_item in enumerate(supports_json):
            if not isinstance(support_item, dict):
                raise ValueError(f"L'élément {i} du tableau doit être un objet")

            # Vérifier la présence de la clé obligatoire
            if "support" not in support_item:
                raise ValueError(
                    f"Clé obligatoire manquante dans l'élément {i}: support"
                )

            # Ajouter la version si absente
            if "version" not in support_item:
                support_item["version"] = "1.0.0"

            # Vérifier que support a un template_name
            self._validate_structure(
                support_item["support"], f"support[{i}].support", valid_template_names
            )

            validated_supports.append(support_item)

        return validated_supports

    def _validate_structure(
        self, obj: Any, path: str, valid_template_names: set = None
    ):
        """
        Valide récursivement la structure d'un objet.

        Args:
            obj: Objet à valider
            path: Chemin pour les messages d'erreur
            valid_template_names: (Optionnel) Set des template_names valides

        Raises:
            ValueError: Si la structure est invalide
        """
        if isinstance(obj, dict):
            # Si c'est un dict avec template_name, vérifier sa présence
            if "template_name" in obj:
                template_name = obj["template_name"]
                if not isinstance(template_name, str) or not template_name:
                    raise ValueError(f"template_name invalide à {path}")

                # Validation stricte : vérifier que le template_name existe
                if (
                    valid_template_names is not None
                    and template_name not in valid_template_names
                ):
                    raise ValueError(
                        f"Template inexistant '{template_name}' utilisé à {path}. "
                        f"Templates valides: {', '.join(sorted(valid_template_names))}"
                    )

            # Valider récursivement les valeurs
            for key, value in obj.items():
                self._validate_structure(value, f"{path}.{key}", valid_template_names)

        elif isinstance(obj, list):
            # Valider récursivement les éléments de la liste
            for i, item in enumerate(obj):
                self._validate_structure(item, f"{path}[{i}]", valid_template_names)

        # Les valeurs primitives (str, int, float, bool, None) sont valides
