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
        Génère un tableau de cartes mentales à partir de données brutes.

        Nouveau workflow:
        1. Génère des paires question-réponse intermédiaires à partir des raw_data
        2. Pour chaque paire, calcule l'embedding et récupère les templates pertinents
        3. Génère une carte mentale pour chaque paire avec ses templates spécifiques

        Args:
            raw_data: Informations pédagogiques brutes à transformer en cartes
            top_k: Nombre de templates similaires à récupérer par paire (défaut: 15)

        Returns:
            Dict contenant:
            - mind_map: Liste de Dict contenant les cartes mentales avec structure:
                [
                    {
                        "recto": {...},
                        "verso": {...},
                        "version": "1.0.0"
                    },
                    ...
                ]
            - prompt: Le prompt complet envoyé au LLM (premier et derniers prompts)
        """
        # Étape 1: Générer les paires question-réponse intermédiaires
        qa_pairs, qa_prompt = self._generate_qa_pairs(raw_data)

        # Étape 2 & 3: Pour chaque paire, récupérer les templates et générer la carte
        all_mind_maps = []
        generation_prompts = []

        for qa_pair in qa_pairs:
            # Calculer l'embedding pour cette paire (question + réponse)
            qa_text = f"{qa_pair['question']} {qa_pair['answer']}"
            embedding = self._generate_embedding(qa_text)

            # Récupérer les templates pertinents pour cette paire
            templates = self._fetch_similar_templates(embedding, top_k)

            # Générer la carte mentale pour cette paire
            mind_map, gen_prompt = self._generate_single_card_from_qa(qa_pair, templates)
            all_mind_maps.append(mind_map)
            generation_prompts.append(gen_prompt)

        # Préparer le prompt complet pour le retour
        full_prompt = f"=== PROMPT DE GÉNÉRATION DES PAIRES Q/R ===\n{qa_prompt}\n\n=== PROMPTS DE GÉNÉRATION DES CARTES ===\n" + "\n\n---\n\n".join(generation_prompts)

        # Étape 4: Valider le JSON de toutes les cartes
        validated_json = self._validate_json(all_mind_maps)

        return {
            "mind_map": validated_json,
            "prompt": full_prompt
        }

    def _generate_qa_pairs(self, raw_data: str) -> tuple[List[Dict[str, str]], str]:
        """
        Génère des paires question-réponse intermédiaires à partir des données brutes.

        Args:
            raw_data: Informations pédagogiques brutes

        Returns:
            Tuple contenant:
            - Liste de dictionnaires avec les clés 'question' et 'answer'
            - Le prompt complet envoyé au LLM
        """
        # Créer le prompt système
        system_prompt = """Tu es un expert en pédagogie. Ton rôle est d'analyser du contenu éducatif brut et de le transformer en paires question-réponse pertinentes.

RÈGLES IMPORTANTES:
1. Crée des questions claires et précises qui testent la compréhension du sujet
2. Les réponses doivent être complètes et pédagogiques
3. Chaque paire doit être indépendante et autonome
4. Adapte le nombre de paires à la richesse du contenu (minimum 1, pas de maximum strict)
5. Les questions peuvent être de différents types: définition, explication, application, comparaison, etc.

STRUCTURE ATTENDUE (TABLEAU JSON):
[
    {
        "question": "Question pédagogique claire et précise",
        "answer": "Réponse complète et détaillée"
    },
    {
        "question": "Autre question pertinente",
        "answer": "Autre réponse détaillée"
    }
]

Réponds UNIQUEMENT avec le TABLEAU JSON valide, sans texte additionnel."""

        user_prompt = f"""Voici le contenu pédagogique à analyser:

{raw_data}

Génère les paires question-réponse au format JSON."""

        # Créer le prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", user_prompt)
        ])

        # Créer la chaîne avec parser JSON
        chain = prompt | self.llm | JsonOutputParser()

        # Préparer le prompt complet pour le retour
        full_prompt = prompt.format()

        # Exécuter la chaîne
        result = chain.invoke({})

        return result, full_prompt

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

    def _generate_single_card_from_qa(self, qa_pair: Dict[str, str], templates: List[Dict[str, Any]]) -> tuple[Dict[str, Any], str]:
        """
        Génère une carte mentale unique à partir d'une paire question-réponse.

        Args:
            qa_pair: Dictionnaire contenant 'question' et 'answer'
            templates: Liste des templates disponibles avec leurs métadonnées

        Returns:
            Tuple contenant:
            - Dict JSON contenant une carte mentale structurée
            - Le prompt complet envoyé au LLM
        """
        # Préparer la liste des templates pour le prompt
        templates_description = self._format_templates_for_prompt(templates)

        # Créer le prompt système
        system_prompt = """Tu es un expert en pédagogie et en création de cartes mentales éducatives.

Ton rôle est de transformer UNE paire question-réponse en UNE carte mentale structurée au format JSON.

TEMPLATES DISPONIBLES:
{templates}

RÈGLES IMPORTANTES:
1. Tu dois créer UN JSON avec DEUX parties: "recto" (la question) et "verso" (la réponse)
2. "recto" doit contenir la question de manière visuelle et engageante
3. "verso" doit contenir la réponse complète et pédagogique
4. Chaque partie utilise des templates (briques HTML) identifiés par "template_name"
5. Les "template_name" doivent EXACTEMENT correspondre aux "Path" des templates disponibles ci-dessus
6. Tu peux imbriquer les structures (objets dans objets, tableaux, etc.) pour créer une carte riche
7. Utilise l'imbrication seulement si cela améliore la pédagogie de la carte
8. Les champs "field1", "field2", etc. correspondent aux placeholders {{{{field_1}}}}, {{{{field_2}}}}, etc. dans le HTML
9. Assure-toi que chaque valeur de champ est du contenu pédagogique pertinent

STRUCTURE ATTENDUE (UN SEUL OBJET JSON):
{{
    "recto": {{
        "template_name": "nom_du_template",
        "field1": "contenu de la question ou objet imbriqué",
        "field2": "contenu ou tableau",
        ...
    }},
    "verso": {{
        "template_name": "nom_du_template",
        "field1": "contenu de la réponse",
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

Réponds UNIQUEMENT avec l'OBJET JSON valide, sans texte additionnel."""

        user_prompt = f"""Voici la paire question-réponse à transformer en carte mentale:

QUESTION: {qa_pair['question']}

RÉPONSE: {qa_pair['answer']}

Génère le JSON de la carte mentale en utilisant les templates disponibles."""

        # Créer le prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", user_prompt)
        ])

        # Créer la chaîne avec parser JSON
        chain = prompt | self.llm | JsonOutputParser()

        # Préparer le prompt complet pour le retour
        full_prompt = prompt.format(templates=templates_description)

        # Exécuter la chaîne
        result = chain.invoke({"templates": templates_description})

        return result, full_prompt

    def _generate_json_with_llm(self, raw_data: str, templates: List[Dict[str, Any]]) -> tuple[List[Dict[str, Any]], str]:
        """
        Utilise le LLM pour générer le JSON structuré d'un tableau de cartes mentales.

        Args:
            raw_data: Données pédagogiques brutes
            templates: Liste des templates disponibles avec leurs métadonnées

        Returns:
            Tuple contenant:
            - Tableau JSON contenant les cartes mentales structurées
            - Le prompt complet envoyé au LLM
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
2. "recto" doit OBLIGATOIREMENT contenir une question et "verso" EXACTEMENT une réponse
3. Chaque partie utilise des templates (briques HTML) identifiés par "template_name"
4. Les "template_name" doivent EXACTEMENT correspondre aux "Path" des templates disponibles ci-dessus
5. Tu dois OBLIGATOIREMENT générer un TABLEAU (array) de cartes mentales au format JSON
6. Tu peux imbriquer les structures (objets dans objets, tableaux, etc.) pour créer des cartes riches
7. Utilise l'imbrication seulement si cela améliore la pédagogie de la carte
8. Les champs "field1", "field2", etc. correspondent aux placeholders {{{{field_1}}}}, {{{{field_2}}}}, etc. dans le HTML
9. Assure-toi que chaque valeur de champ est du contenu pédagogique pertinent

STRUCTURE ATTENDUE (TABLEAU DE CARTES):
[
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
    }},
    {{
        "recto": {{
            "template_name": "nom_du_template",
            ...
        }},
        "verso": {{
            "template_name": "nom_du_template",
            ...
        }},
        "version": "1.0.0"
    }}
]

EXEMPLE D'IMBRICATION DANS UN TABLEAU:
[
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
]

Réponds UNIQUEMENT avec le TABLEAU JSON valide, sans texte additionnel."""

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

        # Préparer le prompt complet pour le retour
        full_prompt = prompt.format(templates=templates_description)

        # Exécuter la chaîne
        result = chain.invoke({"templates": templates_description})

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
            formatted.append(f"""
Template {i}:
- Path (à utiliser comme template_name): "{tmpl['template_name']}"
- Usage des champs: {tmpl['fields_usage']}
""")
        return "\n".join(formatted)

    def _validate_json(self, mind_map_json: Any) -> List[Dict[str, Any]]:
        """
        Valide la structure du JSON généré (tableau de cartes mentales).

        Args:
            mind_map_json: JSON à valider (doit être un tableau)

        Returns:
            Tableau JSON validé

        Raises:
            ValueError: Si le JSON est invalide
        """
        # Vérifier que c'est bien un tableau
        if not isinstance(mind_map_json, list):
            raise ValueError("Le JSON doit être un tableau de cartes mentales")

        # Vérifier que le tableau n'est pas vide
        if len(mind_map_json) == 0:
            raise ValueError("Le tableau de cartes mentales ne peut pas être vide")

        # Valider chaque carte du tableau
        validated_cards = []
        for i, card in enumerate(mind_map_json):
            if not isinstance(card, dict):
                raise ValueError(f"L'élément {i} du tableau doit être un objet")

            # Vérifier la présence des clés obligatoires
            required_keys = ["recto", "verso"]
            for key in required_keys:
                if key not in card:
                    raise ValueError(f"Clé obligatoire manquante dans la carte {i}: {key}")

            # Ajouter la version si absente
            if "version" not in card:
                card["version"] = "1.0.0"

            # Vérifier que recto et verso ont des template_name
            self._validate_structure(card["recto"], f"card[{i}].recto")
            self._validate_structure(card["verso"], f"card[{i}].verso")

            validated_cards.append(card)

        return validated_cards

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
