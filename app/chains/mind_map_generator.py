from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.sql import literal_column
from sentence_transformers import SentenceTransformer
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from app.models.db.fmp_models import CardTemplates


class MindMapGenerator:
    """
    Générateur de cartes mentales utilisant la recherche vectorielle et LangChain.

    Le workflow :
    1. Génère un embedding des raw_data pédagogiques
    2. Recherche les templates HTML les plus similaires dans PostgreSQL (pgvector)
    3. Utilise un LLM pour générer un JSON structuré avec recto/verso
    4. Valide et retourne le JSON final
    """

    def __init__(self, db_session: Session, llm: BaseChatModel, embedding_model: SentenceTransformer):
        """
        Args:
            db_session: Session SQLAlchemy pour accéder à la DB
            llm: Modèle LangChain (ChatOpenAI)
            embedding_model: Modèle sentence-transformers pour les embeddings
        """
        self.db = db_session
        self.llm = llm
        self.embedding_model = embedding_model

    def generate_mind_map(self, raw_data: str, top_k: int = 15) -> Dict[str, Any]:
        """
        Génère une carte mentale complète à partir de données brutes.

        Args:
            raw_data: Informations pédagogiques brutes à transformer en carte
            top_k: Nombre de templates similaires à récupérer (défaut: 15)

        Returns:
            Dict contenant le JSON de la carte mentale avec structure:
            {
                "recto": {...},
                "verso": {...},
                "version": "1.0.0"
            }
        """
        # Étape 1: Générer l'embedding des raw_data
        embedding = self._generate_embedding(raw_data)

        # Étape 2: Récupérer les templates les plus similaires
        templates = self._fetch_similar_templates(embedding, top_k)

        # Étape 3: Générer le JSON avec le LLM
        mind_map_json = self._generate_json_with_llm(raw_data, templates)
       
        # generate fake json for testing
        # mind_map_json = {
        #         "recto": {
        #             "template_name": "layouts/tree_left_right/container",
        #             "min_height": "400px",
        #             "padding": "30px",
        #             "background_color": "#ffffff",
        #             "horizontal_spacing": "60px",
        #             "items": [
        #                 {
        #                     "template_name": "layouts/tree_left_right/item",
        #                     "title": "Photosynthèse",
        #                     "content": "Processus par lequel les plantes vertes utilisent la lumière du soleil.",
        #                     "item_padding": "12px",
        #                     "item_background": "#e9f5f9",
        #                     "item_border": "none",
        #                     "item_shadow": "0 2px 4px rgba(0,0,0,0.1)",
        #                     "item_min_width": "120px",
        #                     "item_max_width": "220px",
        #                     "item_margin_top": "0px",
        #                     "connector_length": "40px",
        #                     "connector_width": "2px",
        #                     "connector_color": "#999999",
        #                     "connector_display": "block",
        #                     "arrow_size": "8px",
        #                     "children_spacing": "16px",
        #                     "children_indent": "60px",
        #                     "title_color": "#333333",
        #                     "content_color": "#666666",
        #                 },
        #                 {
        #                     "template_name": "layouts/tree_left_right/item",
        #                     "title": "Utilisation de la lumière",
        #                     "content": "Les plantes vertes utilisent la lumière du soleil.",
        #                     "item_padding": "12px",
        #                     "item_background": "#ffffff",
        #                     "item_border": "1px solid #e0e0e0",
        #                     "item_shadow": "0 2px 6px rgba(0,0,0,0.1)",
        #                     "item_min_width": "120px",
        #                     "item_max_width": "220px",
        #                     "item_margin_top": "20px",
        #                     "connector_length": "40px",
        #                     "connector_width": "2px",
        #                     "connector_color": "#999999",
        #                     "connector_display": "block",
        #                     "arrow_size": "8px",
        #                     "children_spacing": "16px",
        #                     "children_indent": "60px",
        #                     "title_color": "#333333",
        #                     "content_color": "#666666",
        #                 },
        #                 {
        #                     "template_name": "layouts/tree_left_right/item",
        #                     "title": "Synthèse de nutriments",
        #                     "content": "Nutriments synthétisés à partir de dioxyde de carbone et d'eau.",
        #                     "item_padding": "12px",
        #                     "item_background": "#ffffff",
        #                     "item_border": "1px solid #e0e0e0",
        #                     "item_shadow": "0 2px 6px rgba(0,0,0,0.1)",
        #                     "item_min_width": "120px",
        #                     "item_max_width": "220px",
        #                     "item_margin_top": "20px",
        #                     "connector_length": "40px",
        #                     "connector_width": "2px",
        #                     "connector_color": "#999999",
        #                     "connector_display": "block",
        #                     "arrow_size": "8px",
        #                     "children_spacing": "16px",
        #                     "children_indent": "60px",
        #                     "title_color": "#333333",
        #                     "content_color": "#666666",
        #                 },
        #                 {
        #                     "template_name": "layouts/tree_left_right/item",
        #                     "title": "Sous-produit",
        #                     "content": "Génération d'oxygène comme sous-produit.",
        #                     "item_padding": "12px",
        #                     "item_background": "#ffffff",
        #                     "item_border": "1px solid #e0e0e0",
        #                     "item_shadow": "0 2px 6px rgba(0,0,0,0.1)",
        #                     "item_min_width": "120px",
        #                     "item_max_width": "220px",
        #                     "item_margin_top": "20px",
        #                     "connector_length": "40px",
        #                     "connector_width": "2px",
        #                     "connector_color": "#999999",
        #                     "connector_display": "block",
        #                     "arrow_size": "8px",
        #                     "children_spacing": "16px",
        #                     "children_indent": "60px",
        #                     "title_color": "#333333",
        #                     "content_color": "#666666",
        #                 },
        #             ],
        #         },
        #         "verso": {
        #             "template_name": "recipe/footer",
        #             "text": "La photosynthèse est cruciale pour la vie sur Terre.",
        #         },
        #         "version": "1.0.0",
        #     }

        # Étape 4: Valider le JSON
        validated_json = self._validate_json(mind_map_json)

        return validated_json

    def _generate_embedding(self, text: str) -> List[float]:
        """
        Génère un embedding à 384 dimensions du texte.

        Args:
            text: Texte à encoder

        Returns:
            Liste de 384 floats représentant l'embedding
        """
        embedding = self.embedding_model.encode(
            text,
            normalize_embeddings=True  # Important pour cosine similarity
        )
        return embedding.tolist()

    def _fetch_similar_templates(self, embedding: List[float], top_k: int) -> List[Dict[str, Any]]:
        """
        Recherche les templates les plus similaires via similarité vectorielle (pgvector).

        Args:
            embedding: Vecteur d'embedding de dimension 384
            top_k: Nombre de résultats à retourner

        Returns:
            Liste de dictionnaires contenant les métadonnées des templates:
            - Path: nom du template
            - TemplateFieldsUsage: description des champs
            - ShortSemanticRepresentation: description courte
            - FullSemanticRepresentation: description complète
        """
        # Convertir l'embedding en format string PostgreSQL array
        embedding_str = "[" + ",".join(str(float(x)) for x in embedding) + "]"

        # Utiliser SQLAlchemy ORM avec l'opérateur pgvector <=> (cosine distance)
        # literal_column permet de créer une expression SQL brute qui sera injectée telle quelle
        distance_expr = literal_column(f'"Embedding" <=> \'{embedding_str}\'::vector')

        # Construire la requête avec SQLAlchemy ORM
        query = (
            self.db.query(
                CardTemplates.Path,
                CardTemplates.TemplateFieldsUsage,
                CardTemplates.ShortSemanticRepresentation,
                CardTemplates.FullSemanticRepresentation,
                distance_expr.label('distance')
            )
            .filter(CardTemplates.Embedding.isnot(None))
            .order_by(distance_expr)
            .limit(top_k)
        )

        result = query.all()

        templates = []
        for row in result:
            templates.append({
                "template_name": row.Path,
                "fields_usage": row.TemplateFieldsUsage,
                "short_description": row.ShortSemanticRepresentation,
                "full_description": row.FullSemanticRepresentation,
                "similarity_distance": float(row.distance)
            })

        # raise NotImplementedError

        return templates

    def _generate_json_with_llm(self, raw_data: str, templates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Utilise le LLM pour générer le JSON structuré de la carte mentale.

        Args:
            raw_data: Données pédagogiques brutes
            templates: Liste des templates disponibles avec leurs métadonnées

        Returns:
            JSON structuré de la carte mentale
        """
        # Préparer la liste des templates pour le prompt
        templates_description = self._format_templates_for_prompt(templates)

        # Créer le prompt système
        system_prompt = """Tu es un expert en pédagogie et en création de cartes mentales éducatives.

Ton rôle est de transformer des informations pédagogiques brutes en une carte mentale structurée au format JSON.

TEMPLATES DISPONIBLES:
{templates}

RÈGLES IMPORTANTES:
1. Tu dois créer un JSON avec DEUX parties: "recto" (la question) et "verso" (la réponse)
2. Chaque partie utilise des templates (briques HTML) identifiés par "template_name"
3. Les "template_name" doivent EXACTEMENT correspondre aux "Path" des templates disponibles ci-dessus
4. Tu peux imbriquer les structures (objets dans objets, tableaux, etc.) pour créer des cartes riches
5. Utilise l'imbrication seulement si cela améliore la pédagogie de la carte
6. Les champs "field1", "field2", etc. correspondent aux placeholders {{{{field_1}}}}, {{{{field_2}}}}, etc. dans le HTML
7. Assure-toi que chaque valeur de champ est du contenu pédagogique pertinent

STRUCTURE ATTENDUE:
{{
    "recto": {{
        "template_name": "nom_du_template",
        "field1": "contenu ou objet imbriqué",
        "field2": "contenu ou tableau",
        ...
    }},
    "verso": {{
        "template_name": "nom_du_template",
        "field1": "contenu",
        ...
    }},
    "version": "1.0.0"
}}

EXEMPLE D'IMBRICATION:
{{
    "recto": {{
        "template_name": "question_template",
        "field1": "Qu'est-ce que la photosynthèse?",
        "field2": {{
            "template_name": "hint_template",
            "field1": "Pense aux plantes et à la lumière"
        }}
    }},
    "verso": {{
        "template_name": "answer_list_template",
        "field1": "La photosynthèse est:",
        "field2": [
            {{
                "template_name": "bullet_point",
                "field1": "Un processus de conversion d'énergie lumineuse"
            }},
            {{
                "template_name": "bullet_point",
                "field1": "Réalisée par les plantes vertes"
            }}
        ]
    }},
    "version": "1.0.0"
}}

Réponds UNIQUEMENT avec le JSON valide, sans texte additionnel."""

        user_prompt = f"""Voici les informations pédagogiques brutes à transformer en carte mentale:

{raw_data}

Génère le JSON de la carte mentale en utilisant les templates disponibles."""

        # Créer le prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", user_prompt)
        ])

        # Créer la chaîne avec parser JSON
        chain = prompt | self.llm | JsonOutputParser()

        # Exécuter la chaîne
        result = chain.invoke({"templates": templates_description})

        return result

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
            formatted.append(f"""
Template {i}:
- Path (à utiliser comme template_name): "{tmpl['template_name']}"
- Usage des champs: {tmpl['fields_usage']}
- Description courte: {tmpl['short_description']}
- Description complète: {tmpl['full_description']}
- Score de similarité: {1 - tmpl['similarity_distance']:.3f}
""")
        return "\n".join(formatted)

    def _validate_json(self, mind_map_json: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valide la structure du JSON généré.

        Args:
            mind_map_json: JSON à valider

        Returns:
            JSON validé

        Raises:
            ValueError: Si le JSON est invalide
        """
        # Vérifier la présence des clés obligatoires
        required_keys = ["recto", "verso"]
        for key in required_keys:
            if key not in mind_map_json:
                raise ValueError(f"Clé obligatoire manquante: {key}")

        # Ajouter la version si absente
        if "version" not in mind_map_json:
            mind_map_json["version"] = "1.0.0"

        # Vérifier que recto et verso ont des template_name
        self._validate_structure(mind_map_json["recto"], "recto")
        self._validate_structure(mind_map_json["verso"], "verso")

        return mind_map_json

    def _validate_structure(self, obj: Any, path: str):
        """
        Valide récursivement la structure d'un objet.

        Args:
            obj: Objet à valider
            path: Chemin pour les messages d'erreur

        Raises:
            ValueError: Si la structure est invalide
        """
        if isinstance(obj, dict):
            # Si c'est un dict avec template_name, vérifier sa présence
            if "template_name" in obj:
                if not isinstance(obj["template_name"], str) or not obj["template_name"]:
                    raise ValueError(f"template_name invalide à {path}")

            # Valider récursivement les valeurs
            for key, value in obj.items():
                self._validate_structure(value, f"{path}.{key}")

        elif isinstance(obj, list):
            # Valider récursivement les éléments de la liste
            for i, item in enumerate(obj):
                self._validate_structure(item, f"{path}[{i}]")

        # Les valeurs primitives (str, int, float, bool, None) sont valides
