from typing import List, Dict, Any, Optional
import asyncio
import json
from sqlalchemy.orm import Session
from sentence_transformers import SentenceTransformer
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from app.utils.template_search import fetch_similar_templates
from app.chains.llm.universal_llm import create_universal_llm


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
            llm: Modèle LangChain pour la génération de cartes (gpt-5.1-codex-mini)
            embedding_model: Modèle sentence-transformers pour les embeddings
        """
        self.db = db_session
        self.llm = llm  # Pour _build_single_card_prompt_and_chain (gpt-5.1-codex-mini)
        self.embedding_model = embedding_model
        # LLM séparé pour _generate_info_format_pairs (gpt-5-mini)
        self.info_format_llm = create_universal_llm("gpt-5-mini")
        # LLM pour filtrer les techniques d'apprentissage (gpt-5-nano)
        self.filter_llm = create_universal_llm("gpt-5-nano")

    def generate_mind_map(self, raw_data: str, top_k: int = 12, additional_instructions: str = "") -> Dict[str, Any]:
        """
        Génère un tableau de cartes mentales à partir de données brutes.

        Nouveau workflow:
        1. Génère des paires informations-format intermédiaires à partir des raw_data
        2. Pour chaque paire, calcule l'embedding et récupère les templates pertinents
        3. Génère une carte mentale pour chaque paire avec ses templates spécifiques

        Args:
            raw_data: Informations pédagogiques brutes à transformer en cartes
            top_k: Nombre de templates similaires à récupérer par paire (défaut: 15)
            additional_instructions: Instructions supplémentaires pour guider la création des triplets

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
        # Utiliser get_event_loop() avec run_until_complete pour compatibilité avec Celery
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            # Si pas de loop, en créer un nouveau
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(self._generate_mind_map_async(raw_data, top_k, additional_instructions))

    async def _generate_mind_map_async(self, raw_data: str, top_k: int = 12, additional_instructions: str = "") -> Dict[str, Any]:
        """
        Version asynchrone de generate_mind_map.

        Args:
            raw_data: Données pédagogiques brutes
            top_k: Nombre de templates similaires à récupérer par paire
            additional_instructions: Instructions supplémentaires pour guider la création des triplets
        """
        # Étape 0: Filtrer les références aux techniques d'apprentissage
        filtered_raw_data = await self._filter_learning_techniques(raw_data)

        # Étape 1: Générer les paires informations-format intermédiaires
        info_format_pairs, info_format_prompt = await self._generate_info_format_pairs(filtered_raw_data, additional_instructions)

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
        results = await asyncio.gather(*tasks)

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

    async def _filter_learning_techniques(self, raw_data: str) -> str:
        """
        Filtre les références aux techniques d'apprentissage dans les données brutes.

        Args:
            raw_data: Informations pédagogiques brutes

        Returns:
            Les données filtrées sans les références aux techniques d'apprentissage
        """
        system_prompt = """Tu es un assistant qui filtre le contenu éducatif.

Ton rôle est de SUPPRIMER toute référence aux techniques d'apprentissage du texte fourni, tout en conservant le contenu pédagogique factuel.

ÉLÉMENTS À SUPPRIMER:
- Références aux cartes mentales, mind maps, flashcards
- Mentions de techniques de mémorisation (répétition espacée, mnémotechniques, etc.)
- Conseils d'apprentissage ou de révision
- Instructions sur comment apprendre ou retenir l'information
- Références aux méthodes pédagogiques (active recall, interleaving, etc.)
- Toute métainstruction sur l'apprentissage"""

        user_prompt = """Voici le contenu à filtrer:

{raw_data}

Retourne le contenu sans les références aux techniques d'apprentissage."""

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", user_prompt)
        ])

        chain = prompt | self.filter_llm

        result = await chain.ainvoke({"raw_data": raw_data})

        return result.content

    async def _generate_info_format_pairs(self, raw_data: str, additional_instructions: str = "") -> tuple[List[Dict[str, str]], str]:
        """
        Génère des triplets question-information-format intermédiaires à partir des données brutes.

        Args:
            raw_data: Informations pédagogiques brutes
            additional_instructions: Instructions supplémentaires pour guider la création des triplets

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

{additional_instructions_block}
Génère les triplets question-information-format au format JSON. N'oublie pas de découper en PLUSIEURS triplets si le contenu est riche !"""

        # Créer le prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", user_prompt)
        ])

        # Créer la chaîne avec parser JSON - utilise info_format_llm (gpt-5-mini)
        chain = prompt | self.info_format_llm | JsonOutputParser()

        # Préparer le bloc d'instructions supplémentaires
        additional_instructions_block = ""
        if additional_instructions and additional_instructions.strip():
            additional_instructions_block = f"\nINSTRUCTIONS SUPPLÉMENTAIRES POUR LA CRÉATION DES TRIPLETS:\nLes instructions suivantes doivent guider ta façon de découper et formuler les triplets question-information-format:\n{additional_instructions}\n"

        # Préparer le prompt complet pour le retour
        full_prompt = prompt.format(raw_data=raw_data, additional_instructions_block=additional_instructions_block)

        # Exécuter la chaîne de manière ASYNCHRONE
        result = await chain.ainvoke({"raw_data": raw_data, "additional_instructions_block": additional_instructions_block})

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

    async def _generate_single_card_from_info_format_async(self, info_format_pair: Dict[str, str], templates: List[Dict[str, Any]], max_retries: int = 2) -> tuple[Dict[str, Any], str]:
        """
        Génère une carte mentale unique à partir d'un triplet question-information-format (VERSION ASYNCHRONE).
        Inclut une correction automatique par LLM en cas d'erreur (max 2 tentatives).

        Args:
            info_format_pair: Dictionnaire contenant 'question', 'information' et 'format'
            templates: Liste des templates disponibles avec leurs métadonnées
            max_retries: Nombre maximum de tentatives (défaut: 2)

        Returns:
            Tuple contenant:
            - Dict JSON contenant une carte mentale structurée
            - Le prompt complet envoyé au LLM
        """
        chain, full_prompt, invoke_params = self._build_single_card_prompt_and_chain(info_format_pair, templates)

        last_error = None
        last_result = None

        for attempt in range(max_retries):
            try:
                # Exécuter la chaîne de manière ASYNCHRONE
                result = await chain.ainvoke(invoke_params)

                # Valider la structure de la carte
                self._validate_single_card(result)

                return result, full_prompt

            except Exception as e:
                last_error = str(e)
                last_result = result if 'result' in dir() else None
                print(f"⚠️ Tentative {attempt + 1}/{max_retries} échouée: {last_error}")

                if attempt < max_retries - 1:
                    # Tenter une correction par LLM
                    result = await self._auto_correct_card(
                        info_format_pair, templates, last_result, last_error
                    )
                    if result:
                        try:
                            self._validate_single_card(result)
                            print(f"✅ Correction automatique réussie à la tentative {attempt + 1}")
                            return result, full_prompt
                        except Exception as correction_error:
                            print(f"⚠️ Correction échouée: {correction_error}")
                            continue

        # Si toutes les tentatives ont échoué, lever l'erreur
        raise ValueError(f"Échec après {max_retries} tentatives. Dernière erreur: {last_error}")

    def _validate_single_card(self, card: Dict[str, Any]) -> None:
        """
        Valide la structure d'une carte unique.

        Args:
            card: La carte à valider

        Raises:
            ValueError: Si la carte est invalide
        """
        if not isinstance(card, dict):
            raise ValueError("La carte doit être un objet")

        required_keys = ["recto", "verso"]
        for key in required_keys:
            if key not in card:
                raise ValueError(f"Clé obligatoire manquante: {key}")

        # Vérifier que recto et verso ont des template_name
        if not isinstance(card.get("recto"), dict) or "template_name" not in card.get("recto", {}):
            raise ValueError("recto doit contenir un template_name")
        if not isinstance(card.get("verso"), dict) or "template_name" not in card.get("verso", {}):
            raise ValueError("verso doit contenir un template_name")

    async def _auto_correct_card(
        self,
        info_format_pair: Dict[str, str],
        templates: List[Dict[str, Any]],
        failed_result: Any,
        error_message: str
    ) -> Optional[Dict[str, Any]]:
        """
        Tente de corriger une carte mal formée via LLM.

        Args:
            info_format_pair: Les données d'entrée originales
            templates: Les templates disponibles
            failed_result: Le résultat échoué (peut être None)
            error_message: Le message d'erreur

        Returns:
            La carte corrigée ou None si la correction échoue
        """
        templates_description = self._format_templates_for_prompt(templates)

        correction_prompt = f"""Le JSON suivant a été généré mais contient une erreur:

ERREUR: {error_message}

JSON GÉNÉRÉ (peut être incomplet ou mal formé):
{json.dumps(failed_result, indent=2, ensure_ascii=False) if failed_result else "Aucun résultat"}

DONNÉES D'ENTRÉE:
- Question: {info_format_pair['question']}
- Information: {info_format_pair['information']}
- Format: {info_format_pair['format']}

TEMPLATES DISPONIBLES:
{templates_description}

CORRIGE le JSON pour qu'il respecte STRICTEMENT cette structure:
{{
    "recto": {{
        "template_name": "chemin/du/template",
        ...autres champs du template...
    }},
    "verso": {{
        "template_name": "chemin/du/template",
        ...autres champs du template...
    }},
    "version": "1.0.0"
}}

Réponds UNIQUEMENT avec le JSON corrigé, sans texte additionnel."""

        prompt = ChatPromptTemplate.from_messages([
            ("system", "Tu es un expert en correction de JSON. Corrige le JSON fourni pour qu'il respecte la structure attendue."),
            ("human", correction_prompt)
        ])

        chain = prompt | self.llm | JsonOutputParser()

        try:
            corrected = await chain.ainvoke({})
            return corrected
        except Exception as e:
            print(f"❌ Erreur lors de la correction automatique: {e}")
            return None

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
        # fields_usage est maintenant un dictionnaire {field_name: description}
        fields_usage = template.get('fields_usage', {})

        # Vérifier que fields_usage est bien un dictionnaire
        if isinstance(fields_usage, dict) and fields_usage:
            # Créer un exemple JSON avec les vrais noms de champs
            example_fields = []
            for field_name in list(fields_usage.keys())[:3]:  # Limiter à 3 champs pour la lisibilité
                example_fields.append(f'    "{field_name}": "valeur du contenu pédagogique"')

            example = "{\n" + f'    "template_name": "{template["template_name"]}",\n'
            example += ",\n".join(example_fields)
            example += "\n  }"
        else:
            # Fallback si fields_usage n'est pas un dict ou est vide
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

    def modify_flashcard(self, flashcard_json: str, modification_instructions: str, top_k: int = 12) -> Dict[str, Any]:
        """
        Modifie une flashcard existante selon les instructions fournies.

        Workflow:
        1. Parse le JSON de la flashcard existante
        2. Calcule l'embedding à partir du contenu de la carte
        3. Récupère les templates pertinents via recherche vectorielle
        4. Appelle le LLM avec la carte existante + instructions pour la modifier
        5. Valide et retourne la carte modifiée

        Args:
            flashcard_json: JSON string de la carte mentale à modifier
            modification_instructions: Instructions décrivant les modifications à apporter
            top_k: Nombre de templates similaires à récupérer (défaut: 12)

        Returns:
            Dict contenant:
            - mind_map: La carte mentale modifiée (structure recto/verso/version)
            - prompt: Le prompt complet envoyé au LLM
        """
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(
            self._modify_flashcard_async(flashcard_json, modification_instructions, top_k)
        )

    async def _modify_flashcard_async(self, flashcard_json: str, modification_instructions: str, top_k: int = 12) -> Dict[str, Any]:
        """
        Version asynchrone de modify_flashcard.

        Args:
            flashcard_json: JSON string de la carte mentale à modifier
            modification_instructions: Instructions de modification
            top_k: Nombre de templates similaires à récupérer
        """
        # Étape 1: Parser le JSON de la flashcard existante
        try:
            existing_card = json.loads(flashcard_json)
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON de flashcard invalide: {str(e)}")

        # Valider la structure de base de la carte existante
        self._validate_single_card(existing_card)

        # Étape 2: Extraire le contenu textuel de la carte pour l'embedding
        card_text = self._extract_text_from_card(existing_card)
        combined_text = f"{card_text} {modification_instructions}"
        embedding = self._generate_embedding(combined_text)

        # Étape 3: Récupérer les templates pertinents
        templates = fetch_similar_templates(
            self.db, embedding, top_k, {"layouts/": 3, "text/": 5}, True
        )

        # Étape 4: Générer la carte modifiée via LLM
        modified_card, full_prompt = await self._generate_modified_card_async(
            existing_card, modification_instructions, templates
        )

        # Étape 5: Valider la carte modifiée
        self._validate_single_card(modified_card)

        return {
            "mind_map": modified_card,
            "prompt": full_prompt
        }

    def _extract_text_from_card(self, card: Dict[str, Any]) -> str:
        """
        Extrait le contenu textuel d'une carte pour générer un embedding.

        Args:
            card: Carte mentale au format dict

        Returns:
            String contenant tout le texte de la carte
        """
        texts = []

        def extract_recursive(obj):
            if isinstance(obj, str):
                texts.append(obj)
            elif isinstance(obj, dict):
                for key, value in obj.items():
                    if key != "template_name" and key != "version":
                        extract_recursive(value)
            elif isinstance(obj, list):
                for item in obj:
                    extract_recursive(item)

        extract_recursive(card.get("recto", {}))
        extract_recursive(card.get("verso", {}))

        return " ".join(texts)

    async def _generate_modified_card_async(
        self,
        existing_card: Dict[str, Any],
        modification_instructions: str,
        templates: List[Dict[str, Any]],
        max_retries: int = 2
    ) -> tuple[Dict[str, Any], str]:
        """
        Génère une carte modifiée à partir d'une carte existante et des instructions.

        Args:
            existing_card: Carte mentale existante (dict)
            modification_instructions: Instructions de modification
            templates: Liste des templates disponibles
            max_retries: Nombre maximum de tentatives

        Returns:
            Tuple contenant:
            - La carte modifiée
            - Le prompt complet envoyé au LLM
        """
        templates_description = self._format_templates_for_prompt(templates)

        system_prompt = """Tu es un expert en pédagogie et en modification de cartes mentales éducatives.

Ton rôle est de MODIFIER une carte mentale existante selon les instructions fournies.

TEMPLATES DISPONIBLES:
{templates}

RÈGLES IMPORTANTES:
1. Tu dois MODIFIER la carte existante, pas en créer une nouvelle de zéro
2. Respecte la structure JSON avec "recto", "verso" et "version"
3. "recto" présente la QUESTION de manière visuelle
4. "verso" développe la RÉPONSE/INFORMATION
5. ⚠️ CRITIQUE: Les "template_name" doivent EXACTEMENT correspondre aux "Path" des templates disponibles
6. ⚠️ CRITIQUE: Les noms de champs doivent STRICTEMENT correspondre à ceux décrits dans "Usage des champs"
7. Tu peux changer les templates si les instructions le demandent ou si c'est pertinent
8. Conserve ce qui n'est pas concerné par les modifications demandées
9. Assure-toi que le contenu modifié reste pédagogiquement cohérent

STRUCTURE ATTENDUE:
{{
    "recto": {{
        "template_name": "COPIE EXACTE du Path d'un template",
        "nom_de_champ_exact": "contenu modifié",
        ...
    }},
    "verso": {{
        "template_name": "COPIE EXACTE du Path d'un template",
        "nom_de_champ_exact": "contenu modifié",
        ...
    }},
    "version": "1.0.0"
}}

Réponds UNIQUEMENT avec l'OBJET JSON de la carte modifiée, sans texte additionnel."""

        user_prompt = """Voici la carte mentale existante à modifier:

{existing_card_json}

INSTRUCTIONS DE MODIFICATION:
{modification_instructions}

Génère le JSON de la carte mentale MODIFIÉE selon les instructions ci-dessus."""

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", user_prompt)
        ])

        chain = prompt | self.llm | JsonOutputParser()

        existing_card_json = json.dumps(existing_card, indent=2, ensure_ascii=False)

        full_prompt = prompt.format(
            templates=templates_description,
            existing_card_json=existing_card_json,
            modification_instructions=modification_instructions
        )

        invoke_params = {
            "templates": templates_description,
            "existing_card_json": existing_card_json,
            "modification_instructions": modification_instructions
        }

        last_error = None

        for attempt in range(max_retries):
            try:
                result = await chain.ainvoke(invoke_params)
                self._validate_single_card(result)
                return result, full_prompt

            except Exception as e:
                last_error = str(e)
                print(f"⚠️ Tentative {attempt + 1}/{max_retries} échouée: {last_error}")

                if attempt < max_retries - 1:
                    # Tenter une correction
                    result = await self._auto_correct_modified_card(
                        existing_card, modification_instructions, templates,
                        result if 'result' in dir() else None, last_error
                    )
                    if result:
                        try:
                            self._validate_single_card(result)
                            print(f"✅ Correction automatique réussie à la tentative {attempt + 1}")
                            return result, full_prompt
                        except Exception as correction_error:
                            print(f"⚠️ Correction échouée: {correction_error}")
                            continue

        raise ValueError(f"Échec après {max_retries} tentatives. Dernière erreur: {last_error}")

    async def _auto_correct_modified_card(
        self,
        existing_card: Dict[str, Any],
        modification_instructions: str,
        templates: List[Dict[str, Any]],
        failed_result: Any,
        error_message: str
    ) -> Optional[Dict[str, Any]]:
        """
        Tente de corriger une carte modifiée mal formée via LLM.

        Args:
            existing_card: Carte originale
            modification_instructions: Instructions de modification
            templates: Templates disponibles
            failed_result: Résultat échoué
            error_message: Message d'erreur

        Returns:
            La carte corrigée ou None
        """
        templates_description = self._format_templates_for_prompt(templates)

        correction_prompt = f"""Le JSON suivant a été généré mais contient une erreur:

ERREUR: {error_message}

JSON GÉNÉRÉ (peut être incomplet ou mal formé):
{json.dumps(failed_result, indent=2, ensure_ascii=False) if failed_result else "Aucun résultat"}

CARTE ORIGINALE:
{json.dumps(existing_card, indent=2, ensure_ascii=False)}

INSTRUCTIONS DE MODIFICATION:
{modification_instructions}

TEMPLATES DISPONIBLES:
{templates_description}

CORRIGE le JSON pour qu'il respecte STRICTEMENT cette structure:
{{
    "recto": {{
        "template_name": "chemin/du/template",
        ...autres champs du template...
    }},
    "verso": {{
        "template_name": "chemin/du/template",
        ...autres champs du template...
    }},
    "version": "1.0.0"
}}

Réponds UNIQUEMENT avec le JSON corrigé, sans texte additionnel."""

        prompt = ChatPromptTemplate.from_messages([
            ("system", "Tu es un expert en correction de JSON. Corrige le JSON fourni pour qu'il respecte la structure attendue."),
            ("human", correction_prompt)
        ])

        chain = prompt | self.llm | JsonOutputParser()

        try:
            corrected = await chain.ainvoke({})
            return corrected
        except Exception as e:
            print(f"❌ Erreur lors de la correction automatique: {e}")
            return None
