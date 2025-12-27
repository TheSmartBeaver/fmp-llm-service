from typing import List, Dict, Any
import asyncio
from sqlalchemy.orm import Session
from sentence_transformers import SentenceTransformer
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from app.utils.template_search import fetch_similar_templates


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
        1. Génère des paires informations-format intermédiaires à partir des raw_data
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
        # Étape 1: Générer les paires informations-format intermédiaires
        info_format_pairs, info_format_prompt = self._generate_info_format_pairs(raw_data)

        # Étape 2 & 3: Pour chaque paire, récupérer les templates et générer la carte EN PARALLÈLE
        all_mind_maps = []
        generation_prompts = []

        # Créer une liste de coroutines pour l'exécution parallèle
        tasks = []
        for info_format_pair in info_format_pairs:
            # Calculer l'embedding pour cette paire (question + information + format)
            pair_text = f"{info_format_pair['question']} {info_format_pair['information']} {info_format_pair['format']}"
            embedding = self._generate_embedding(pair_text)

            # Récupérer les templates pertinents pour cette paire
            templates = fetch_similar_templates(self.db, embedding, top_k, { "layouts/": 3, "text/": 5}, True)

            # Créer une tâche asynchrone pour générer la carte mentale
            tasks.append(self._generate_single_card_from_info_format_async(info_format_pair, templates))

        # Exécuter toutes les tâches en parallèle
        # Utiliser get_event_loop() avec run_until_complete pour compatibilité avec Celery
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            # Si pas de loop, en créer un nouveau
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        results = loop.run_until_complete(asyncio.gather(*tasks))

        # Extraire les résultats
        for mind_map, gen_prompt in results:
            all_mind_maps.append(mind_map)
            generation_prompts.append(gen_prompt)

        # Préparer le prompt complet pour le retour
        full_prompt = f"=== PROMPT DE GÉNÉRATION DES PAIRES INFORMATIONS-FORMAT ===\n{info_format_prompt}\n\n=== PROMPTS DE GÉNÉRATION DES CARTES ===\n" + "\n\n---\n\n".join(generation_prompts)

        # Étape 4: Valider le JSON de toutes les cartes
        validated_json = self._validate_json(all_mind_maps)

        return {
            "mind_map": validated_json,
            "prompt": full_prompt
        }

    def _generate_info_format_pairs(self, raw_data: str) -> tuple[List[Dict[str, str]], str]:
        """
        Génère des triplets question-information-format intermédiaires à partir des données brutes.

        Args:
            raw_data: Informations pédagogiques brutes

        Returns:
            Tuple contenant:
            - Liste de dictionnaires avec les clés 'question', 'information' et 'format'
            - Le prompt complet envoyé au LLM
        """
        # Créer le prompt système
        system_prompt = """Tu es un expert en pédagogie. Ton rôle est d'analyser du contenu éducatif brut et de le transformer en triplets question-information-format pertinents.

RÈGLES IMPORTANTES:
1. "question" : la question dont l'information est la réponse la plus complète et représentative possible
2. "information" : le contenu pédagogique qui répond à la question (COURT et FOCALISÉ)
3. "format" : comment cette information devrait être structurée/présentée
4. Chaque triplet doit être indépendant et autonome
5. ⚠️ DÉCOUPAGE OBLIGATOIRE : crée PLUSIEURS triplets (ne pas hésiter !) pour éviter des cartes mentales trop grosses
6. ⚠️ PRIVILÉGIE TOUJOURS la création de PLUSIEURS petites cartes focalisées plutôt qu'une seule carte surchargée
7. Si le contenu source est riche, découpe-le en PLUSIEURS questions/informations focalisées (3-5 triplets minimum pour un contenu riche)
8. Une information trop volumineuse = plusieurs triplets au lieu d'un seul
9. Chaque information devrait tenir sur 2-4 phrases maximum (au-delà = découper en plusieurs triplets)
10. Les formats peuvent être : définition, liste, comparaison, chronologie, processus, explication structurelle, schéma conceptuel, etc.

EXEMPLES DE FORMATS:
- "définition scientifique avec processus chimique"
- "chronologie avec dates et événements majeurs"
- "comparaison avec critères (mutabilité, performance, usage)"
- "liste de causes avec catégorisation"
- "explication structurelle avec étapes séquentielles"
- "description pathologique avec symptômes énumérés"
- "définition technique avec syntaxe et exemples de méthodes"

EXEMPLE DE DÉCOUPAGE (BON):
Contenu source volumineux sur la Révolution française → créer 3 triplets :
1. Question sur les causes → information sur les causes → format liste
2. Question sur la période → information sur les dates → format temporel
3. Question sur les événements → information sur les événements majeurs → format chronologie

STRUCTURE ATTENDUE (TABLEAU JSON):
[
    {{
        "question": "Question dont l'information est la réponse complète",
        "information": "Contenu pédagogique qui répond à la question",
        "format": "Description du format de présentation souhaité"
    }},
    {{
        "question": "Autre question focalisée",
        "information": "Autre contenu pédagogique pertinent",
        "format": "Autre format de présentation"
    }}
]

Réponds UNIQUEMENT avec le TABLEAU JSON valide, sans texte additionnel."""

        user_prompt = """Voici le contenu pédagogique à analyser:

{raw_data}

Génère les triplets question-information-format au format JSON. N'oublie pas de découper en PLUSIEURS triplets si le contenu est riche !"""

        # Créer le prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", user_prompt)
        ])

        # Créer la chaîne avec parser JSON
        chain = prompt | self.llm | JsonOutputParser()

        # Préparer le prompt complet pour le retour
        full_prompt = prompt.format(raw_data=raw_data)

        # Exécuter la chaîne
        result = chain.invoke({"raw_data": raw_data})

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

    def _build_single_card_prompt_and_chain(self, info_format_pair: Dict[str, str], templates: List[Dict[str, Any]]) -> tuple[Any, str]:
        """
        Construit le prompt et la chaîne LangChain pour générer une carte mentale unique.
        Méthode utilitaire pour éviter la duplication de code entre sync et async.

        Args:
            info_format_pair: Dictionnaire contenant 'question', 'information' et 'format'
            templates: Liste des templates disponibles avec leurs métadonnées

        Returns:
            Tuple contenant:
            - La chaîne LangChain configurée (prompt | llm | parser)
            - Le prompt complet formaté pour le retour
        """
        # Préparer la liste des templates pour le prompt
        templates_description = self._format_templates_for_prompt(templates)

        # Créer le prompt système
        system_prompt = """Tu es un expert en pédagogie et en création de cartes mentales éducatives.

Ton rôle est de transformer UN triplet question-information-format en UNE carte mentale structurée au format JSON.

TEMPLATES DISPONIBLES:
{templates}

RÈGLES IMPORTANTES:
1. Tu dois créer UN JSON avec DEUX parties: "recto" et "verso"
2. "recto" doit présenter la QUESTION de manière visuelle et engageante
3. "verso" doit développer l'INFORMATION (la réponse) complète selon le FORMAT spécifié
4. Chaque partie utilise des templates (briques HTML) identifiés par "template_name"
5. ⚠️ CRITIQUE: Les "template_name" doivent EXACTEMENT correspondre aux "Path" des templates disponibles ci-dessus (copie-colle exact)
6. ⚠️ CRITIQUE: Les noms de champs (field_name_X) doivent STRICTEMENT correspondre à ceux décrits dans "Usage des champs" de chaque template
7. ❌ N'INVENTE JAMAIS de template_name ou de nom de champ qui n'est pas explicitement listé dans les templates disponibles
8. Tu peux imbriquer les structures (objets dans objets, tableaux, etc.) pour créer une carte riche
9. Utilise l'imbrication seulement si cela améliore la pédagogie de la carte
10. Assure-toi que chaque valeur de champ est du contenu pédagogique pertinent
11. Le FORMAT spécifié doit guider ton choix de templates et la structure de la carte
12. IMPORTANT : Si l'information fournie est TROP VOLUMINEUSE pour tenir dans une carte claire et digeste, tu dois quand même créer UNE carte mais en synthétisant au maximum. L'idéal est que l'information soit déjà bien découpée en amont (plusieurs triplets au lieu d'un seul)

STRUCTURE ATTENDUE (UN SEUL OBJET JSON):
{{
    "recto": {{
        "template_name": "COPIE EXACTE du Path d'un template listé ci-dessus",
        "nom_de_champ_exact": "présentation visuelle de la question ou objet imbriqué",
        "autre_nom_exact": "contenu ou tableau",
        ...
    }},
    "verso": {{
        "template_name": "COPIE EXACTE du Path d'un template listé ci-dessus",
        "nom_de_champ_exact": "développement complet de l'information (réponse) selon le format",
        ...
    }},
    "version": "1.0.0"
}}

ATTENTION: Les noms des champs ("nom_de_champ_exact", "autre_nom_exact") doivent provenir UNIQUEMENT de la description "Usage des champs" du template choisi. N'invente JAMAIS de noms génériques comme "field_name_1" ou "field_name_2".

EXEMPLE D'IMBRICATION:
Si la question est "Comment fonctionne la photosynthèse ?"
l'information est "La photosynthèse est le processus par lequel les plantes vertes convertissent l'énergie lumineuse en énergie chimique..."
et le format est "explication structurelle avec étapes séquentielles":

{{
    "recto": {{
        "template_name": "question_template",
        "field_name_1": "Comment fonctionne la photosynthèse ?",
        "field_name_2": {{
            "template_name": "hint_template",
            "field_name_1": "Pense aux plantes et à la lumière"
        }}
    }},
    "verso": {{
        "template_name": "sequential_steps_template",
        "field_name_1": "Processus de photosynthèse:",
        "field_name_2": [
            {{
                "template_name": "step_item",
                "field_name_1": "Capture de la lumière par la chlorophylle dans les chloroplastes"
            }},
            {{
                "template_name": "step_item",
                "field_name_1": "Conversion de l'énergie lumineuse en énergie chimique"
            }},
            {{
                "template_name": "step_item",
                "field_name_1": "Production de glucose (C6H12O6) et libération d'oxygène (O2)"
            }}
        ]
    }},
    "version": "1.0.0"
}}

Réponds UNIQUEMENT avec l'OBJET JSON valide, sans texte additionnel."""

        user_prompt = """Voici le triplet question-information-format à transformer en carte mentale:

QUESTION: {question}

INFORMATION: {information}

FORMAT: {format}

Génère le JSON de la carte mentale en utilisant les templates disponibles. Le recto doit présenter la question, le verso doit développer l'information selon le format spécifié."""

        # Créer le prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", user_prompt)
        ])

        # Créer la chaîne avec parser JSON
        chain = prompt | self.llm | JsonOutputParser()

        # Préparer le prompt complet pour le retour
        full_prompt = prompt.format(
            templates=templates_description,
            question=info_format_pair['question'],
            information=info_format_pair['information'],
            format=info_format_pair['format']
        )

        # Préparer les paramètres d'invocation
        invoke_params = {
            "templates": templates_description,
            "question": info_format_pair['question'],
            "information": info_format_pair['information'],
            "format": info_format_pair['format']
        }

        return chain, full_prompt, invoke_params

    async def _generate_single_card_from_info_format_async(self, info_format_pair: Dict[str, str], templates: List[Dict[str, Any]]) -> tuple[Dict[str, Any], str]:
        """
        Génère une carte mentale unique à partir d'un triplet question-information-format (VERSION ASYNCHRONE).

        Args:
            info_format_pair: Dictionnaire contenant 'question', 'information' et 'format'
            templates: Liste des templates disponibles avec leurs métadonnées

        Returns:
            Tuple contenant:
            - Dict JSON contenant une carte mentale structurée
            - Le prompt complet envoyé au LLM
        """
        chain, full_prompt, invoke_params = self._build_single_card_prompt_and_chain(info_format_pair, templates)

        # Exécuter la chaîne de manière ASYNCHRONE
        result = await chain.ainvoke(invoke_params)

        return result, full_prompt

    def _generate_single_card_from_info_format(self, info_format_pair: Dict[str, str], templates: List[Dict[str, Any]]) -> tuple[Dict[str, Any], str]:
        """
        Génère une carte mentale unique à partir d'un triplet question-information-format (VERSION SYNCHRONE - LEGACY).

        Args:
            info_format_pair: Dictionnaire contenant 'question', 'information' et 'format'
            templates: Liste des templates disponibles avec leurs métadonnées

        Returns:
            Tuple contenant:
            - Dict JSON contenant une carte mentale structurée
            - Le prompt complet envoyé au LLM
        """
        chain, full_prompt, invoke_params = self._build_single_card_prompt_and_chain(info_format_pair, templates)

        # Exécuter la chaîne de manière SYNCHRONE
        result = chain.invoke(invoke_params)

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
8. Les champs "field_name_1", "field_name_2", etc. correspondent aux placeholders {{{{field_1}}}}, {{{{field_2}}}}, etc. dans le HTML
9. Assure-toi que chaque valeur de champ est du contenu pédagogique pertinent

STRUCTURE ATTENDUE (TABLEAU DE CARTES):
[
    {{
        "recto": {{
            "template_name": "nom_du_template",
            "field_name_1": "contenu ou objet imbriqué",
            "field_name_2": "contenu ou tableau",
            ...
        }},
        "verso": {{
            "template_name": "nom_du_template",
            "field_name_1": "contenu",
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
            "field_name_1": "Qu'est-ce que la photosynthèse?",
            "field_name_2": {{
                "template_name": "hint_template",
                "field_name_1": "Pense aux plantes et à la lumière"
            }}
        }},
        "verso": {{
            "template_name": "answer_list_template",
            "field_name_1": "La photosynthèse est:",
            "field_name_2": [
                {{
                    "template_name": "bullet_point",
                    "field_name_1": "Un processus de conversion d'énergie lumineuse"
                }},
                {{
                    "template_name": "bullet_point",
                    "field_name_1": "Réalisée par les plantes vertes"
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
            String formaté décrivant chaque template avec structure JSON attendue
        """
        formatted = []
        for i, tmpl in enumerate(templates, 1):
            # Créer un exemple de structure JSON pour ce template
            json_example = self._create_template_json_example(tmpl)

            formatted.append(f"""
Template {i}:
- Path (à utiliser EXACTEMENT comme template_name): "{tmpl['template_name']}"
- Usage des champs: {tmpl['fields_usage']}
- Description courte: {tmpl['short_description']}
- Exemple de structure JSON attendue:
{json_example}
""")
        return "\n".join(formatted)

    def _create_template_json_example(self, template: Dict[str, Any]) -> str:
        """
        Crée un exemple de structure JSON pour un template donné.

        Args:
            template: Métadonnées du template

        Returns:
            String contenant un exemple de structure JSON
        """
        # Parser le TemplateFieldsUsage pour extraire les noms de champs
        # Format attendu: "field_1: description, field_2: description, ..."
        fields_usage = template.get('fields_usage', '')

        # Essayer d'extraire les noms de champs (avant le ':' ou la première espace)
        import re
        field_matches = re.findall(r'(\w+)\s*:', fields_usage)

        if field_matches:
            # Créer un exemple JSON avec les vrais noms de champs
            example_fields = []
            for field_name in field_matches[:3]:  # Limiter à 3 champs pour la lisibilité
                example_fields.append(f'    "{field_name}": "valeur du contenu pédagogique"')

            example = "{\n" + f'    "template_name": "{template["template_name"]}",\n'
            example += ",\n".join(example_fields)
            example += "\n  }"
        else:
            # Fallback si on ne peut pas parser
            example = "{\n" + f'    "template_name": "{template["template_name"]}",\n'
            example += '    "voir_usage_des_champs_ci_dessus": "..."\n  }'

        return example

    def _validate_json(self, mind_map_json: Any, templates: List[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Valide la structure du JSON généré (tableau de cartes mentales).

        Args:
            mind_map_json: JSON à valider (doit être un tableau)
            templates: (Optionnel) Liste des templates pour validation stricte

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

        # Créer un set de template_names valides si fourni
        valid_template_names = None
        if templates:
            valid_template_names = {tmpl['template_name'] for tmpl in templates}

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
            self._validate_structure(card["recto"], f"card[{i}].recto", valid_template_names)
            self._validate_structure(card["verso"], f"card[{i}].verso", valid_template_names)

            validated_cards.append(card)

        return validated_cards

    def _validate_structure(self, obj: Any, path: str, valid_template_names: set = None):
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
                if valid_template_names is not None and template_name not in valid_template_names:
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
