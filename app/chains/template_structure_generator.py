from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sentence_transformers import SentenceTransformer
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from app.utils.template_search import fetch_similar_templates
from app.utils.structure_process import extract_json_structure, create_embedding_packets
from app.chains.llm.claude_haiku_45_llm import ClaudeHaiku45Llm
from app.chains.llm.open_ai_o3_mini_llm import OpenAiO3MiniLlm
from app.validation.path_group_validator import validate_path_groups


class TemplateStructureGenerator:
    """
    Générateur qui transforme un JSON de données source en JSON structuré basé sur des templates.

    Le workflow :
    1. Reçoit un JSON de données source (ex: course_sections avec tables de conjugaison)
    2. Utilise fetch_similar_templates pour récupérer les templates pertinents
    3. Demande au LLM de mapper les données vers une structure de templates
    4. Retourne un JSON qui utilise la notation chemin->vers->donnée pour référencer les données

    Notation des chemins :
    - `->` pour naviguer dans les objets (ex: `tip->memory`)
    - `[]` pour parcourir les tableaux (ex: `course_sections[]`)
    - Combinaison : `course_sections[]tables[]infinitive_translation`
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
        self.llm = ClaudeHaiku45Llm().get_llm()
        # Utiliser un modèle plus puissant (O3-mini avec raisonnement) pour les corrections
        self.correction_llm = OpenAiO3MiniLlm().get_llm()

    def generate_template_structure(
        self,
        source_json: Dict[str, Any],
        context_description: str = "",
        top_k_per_packet: int = 12,
        category_quotas: Dict[str, int] = None,
    ) -> Dict[str, Any]:
        """
        Génère une structure de templates à partir d'un JSON source.

        Utilise plusieurs embeddings ciblés (macro et micro) pour trouver des templates pertinents.

        Args:
            source_json: Le JSON contenant les données à structurer
            context_description: Description optionnelle du contexte (ex: "cours d'espagnol sur les verbes")
            top_k_per_packet: Nombre de templates similaires à récupérer par paquet d'embedding (défaut: 10)
            category_quotas: Dictionnaire {catégorie: quota} pour limiter par catégorie
                           Ex: {"layouts/": 5, "conceptual/": 3}

        Returns:
            Dict contenant:
            - template_structure: Le JSON structuré avec les template_name et références
            - prompt: Le prompt complet envoyé au LLM
        """
        # Étape 1: Créer les paquets d'embedding à partir du JSON source
        packets = create_embedding_packets(source_json)

        # Étape 2: Pour chaque paquet, faire une recherche et collecter les templates
        all_templates = {}  # Dict pour dédupliquer: {template_name: template_data}

        for packet in packets:
            # Créer le texte de recherche en combinant le contexte et les clés du paquet
            search_text = self._create_search_text_from_packet(
                packet, context_description
            )

            # Générer l'embedding
            embedding = self._generate_embedding(search_text)

            # Rechercher les templates
            templates = fetch_similar_templates(
                self.db,
                embedding,
                top_k_per_packet,
                category_quotas,
                include_full_data=False,
            )

            # Ajouter à la collection (déduplique automatiquement par template_name)
            for tmpl in templates:
                if tmpl["template_name"] not in all_templates:
                    all_templates[tmpl["template_name"]] = tmpl

        # Convertir en liste
        templates = list(all_templates.values())

        # Étape 3: Générer la structure via le LLM
        template_structure, prompt, destination_mappings = (
            self._generate_structure_with_llm(
                source_json, templates, context_description
            )
        )

        # return {
        #     "template_structure": {
        #         "template_name": "layouts/vertical_column/container",
        #         "items": [
        #             {
        #                 "template_name": "text/explication",
        #                 "text": "Comprendre en profondeur les cinq principes SOLID et savoir comment ils se complètent pour améliorer la lisibilité, la maintenabilité et l'évolutivité du code. L'objectif est d'apprendre non seulement la définition de chaque principe, mais aussi leur justification pratique, les situations où les appliquer, les modèles de conception qui facilitent leur mise en œuvre, ainsi que les compromis et limites possibles afin de pouvoir concevoir des systèmes équilibrés et faciles à faire évoluer. À la fin, l'apprenant devra être capable d'identifier les violations des principes SOLID dans un code existant et de proposer des refactorings appropriés qui conservent le comportement tout en améliorant la structure et le couplage du logiciel.",
        #             },
        #             {
        #                 "template_name": "layouts/tree_left_right/container",
        #                 "items": [
        #                     {
        #                         "template_name": "layouts/tree_left_right/item",
        #                         "content": {
        #                             "template_name": "text/explication",
        #                             "text": "Les principes SOLID regroupent cinq règles de conception orientée objet qui visent à rendre le code plus propre, modulable et durable dans le temps. Ils ne sont pas des lois strictes à appliquer à la lettre dans tous les cas, mais des guides conceptuels qui aident à réduire le couplage, augmenter la cohésion et faciliter les tests et l'évolution du logiciel. Cette section présente le contexte historique et pratique des principes, pourquoi ils sont utiles dans des projets de taille moyenne à grande, et comment les appliquer progressivement lors de l'architecture ou du refactoring.",
        #                         },
        #                         "title": "Introduction aux principes SOLID",
        #                     }
        #                 ],
        #             },
        #             {
        #                 "template_name": "layouts/horizontal_line/container",
        #                 "items": [
        #                     {
        #                         "template_name": "layouts/grid/item",
        #                         "title": {
        #                             "template_name": "conceptual/concept",
        #                             "title": "Single Responsibility Principle (SRP) - Principe de responsabilité unique",
        #                         },
        #                         "content": {
        #                             "template_name": "text/liste_exemples",
        #                             "items": [
        #                                 "Une classe UserService qui gère à la fois la logique métier des utilisateurs et la persistance en base devrait être scindée en UserService (logique métier) et UserRepository (accès aux données). Cette séparation permet de modifier la stratégie de stockage sans toucher à la logique métier.",
        #                                 "Une classe ReportGenerator qui compile des données, formate un document et l'envoie par email enfreint SRP. On la refactorise en DataCollector, ReportFormatter et EmailSender pour isoler les raisons de changement et faciliter le test unitaire de chaque responsabilité.",
        #                             ],
        #                             "text": "Le principe de responsabilité unique stipule qu'une classe ou un module ne doit avoir qu'une seule raison de changer, c'est-à-dire une et une seule responsabilité métier. L'idée est de séparer les préoccupations pour limiter l'impact des modifications : si une classe a plusieurs responsabilités, une modification liée à l'une d'elles peut provoquer des régressions dans les autres. En pratique, appliquer SRP conduit à des classes plus petites et plus cohésives, plus simples à tester et à comprendre. SRP facilite également l'adhésion aux autres principes SOLID, par exemple en rendant plus simple l'extension sans modification (OCP) et en limitant les interfaces superficielles.",
        #                         },
        #                     }
        #                 ],
        #             },
        #             {
        #                 "template_name": "layouts/tree_left_right/container",
        #                 "items": [
        #                     {
        #                         "template_name": "layouts/tree_left_right/item",
        #                         "content": {
        #                             "template_name": "text/explication",
        #                             "text": "Les principes SOLID sont complémentaires mais parfois couteux à appliquer de manière trop stricte : trop de petites classes ou d'abstractions peuvent conduire à une complexité excessive (sur-ingénierie). Il est donc conseillé d'appliquer ces principes de manière pragmatique et itérative, en commençant par identifier les points de fragilité du code puis en refactorant par petites étapes. De plus, certains concepts se renforcent mutuellement : par exemple SRP facilite OCP en isolant les responsabilités, et DIP facilite OCP en permettant d'ajouter des implémentations sans modifier les dépendants. Enfin, l'utilisation conjointe de tests automatisés, de revues de code et de patterns de conception aidants (Factory, Strategy, Decorator, Adapter) accélère la mise en œuvre efficace des principes SOLID dans des projets réels.",
        #                         },
        #                     }
        #                 ],
        #             },
        #         ],
        #         "version": "1.0.0",
        #     },
        #     "prompt": "FAKE PROMPT",
        # }

        return {
            "template_structure": template_structure,
            "prompt": prompt,
            "destination_mappings": destination_mappings,
        }

    def _create_search_text_from_packet(
        self, packet: Dict[str, Any], context_description: str
    ) -> str:
        """
        Crée un texte de recherche à partir d'un paquet d'embedding.

        Args:
            packet: Paquet contenant type, keys, text, context
            context_description: Description du contexte général

        Returns:
            String pour la recherche de templates
        """
        search_parts = []

        # Ajouter le contexte général s'il existe
        if context_description:
            search_parts.append(context_description)

        # Ajouter le contexte du paquet (chemin dans la structure)
        if packet["context"]:
            search_parts.append(f"Contexte: {packet['context']}")

        # Ajouter le type de paquet
        if packet["type"] == "macro":
            search_parts.append("Structure globale:")
        else:
            search_parts.append("Détails de contenu:")

        # Ajouter le texte du paquet (les clés)
        search_parts.append(packet["text"])

        return " ".join(search_parts)

    def _create_search_text(
        self, source_json: Dict[str, Any], context_description: str
    ) -> str:
        """
        Crée un texte de recherche pour trouver des templates pertinents.
        (Ancienne méthode conservée pour compatibilité)

        Args:
            source_json: Le JSON source
            context_description: Description du contexte

        Returns:
            String pour la recherche de templates
        """
        # Extraire les clés principales du JSON pour la recherche
        import json

        json_summary = json.dumps(source_json, ensure_ascii=False, indent=2)[:500]

        search_parts = []
        if context_description:
            search_parts.append(context_description)
        search_parts.append(f"Structure de données: {json_summary}")

        return " ".join(search_parts)

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

    def _generate_json_from_group(
        self,
        group: Dict[str, Any],
        templates: List[Dict[str, Any]],
        source_json: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Génère le JSON structuré pour un groupe en utilisant les templates récupérés par embedding.

        Args:
            group: Un groupe de chemins avec format (output de _generate_path_groups_with_llm)
            templates: Templates récupérés par embedding pour ce groupe
            source_json: Le JSON source complet

        Returns:
            JSON structuré avec template_name et références {{chemin}}
            Exemple:
            {
                "template_name": "XXXX",
                "items": [
                    {
                        "template_name": "XXXX",
                        "title": "XXXX",
                        "content": "{{XXXX}}"
                    }
                ]
            }
        """
        # Formater les templates pour le prompt
        templates_formatted = self._format_templates_for_prompt(templates)

        # Formater les chemins source
        source_paths_formatted = "\n".join([f"  - {path}" for path in group["keys"]])

        # Construire le prompt
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """Tu es un expert en construction de structures de données pédagogiques.
Ta tâche est de créer un JSON structuré qui utilise des templates HTML/pédagogiques imbriqués
pour représenter des données de cartes mentales.

⚠️ FORMAT DE SORTIE:
Tu DOIS retourner un JSON structuré avec:
- Un champ "template_name" obligatoire pour chaque objet
- Les champs définis dans "Usage des champs" du template
- Des références aux données source au format {{chemin}} (ex: {{conjugation_patterns[x]group}})

EXEMPLE DE SORTIE ATTENDUE:
{{
  "template_name": "XXXX",
  "items": [
    {{
      "template_name": "XXXX",
      "title": "XXXX",
      "content": "{{XXXX[x]XXXX}}"
    }},
    {{
      "template_name": "XXXX",
      "title": "XXXX",
      "content": {{
        "template_name": "XXXX",
        "title": "XXXX {{XXXX[x]XXXX}}",
        "description": "{{XXXX[x]XXXX->XXXX}}"
      }}
    }}
  ]
}}

⚠️ RÈGLES CRITIQUES:

1. **Champs autorisés**:
   - Tu NE PEUX utiliser QUE les champs définis dans "Usage des champs" du template

2. **Structure des objets**:
   - Chaque objet DOIT avoir un champ "template_name"
   - Les champs peuvent contenir soit:
     * Une référence {{chemin}} (pour les valeurs primitives)
     * Un objet avec template_name (pour imbriquer des templates)
     * Un tableau d'objets avec template_name
     * Une string

3. **Références aux données**:
   - Utilise la notation {{chemin}} pour référencer les données source
   - Conserve les variables [x], [y] dans les chemins si présentes
   - Exemples:
     * {{XXXX}} (sans variable)
     * {{XXXX[x]XXXX}} (avec variable [x])
     * {{XXXX[x]XXXX[y]}} (avec variables [x] et [y])

4. **Imbrication des templates**:
   - Tu DOIS imbriquer plusieurs templates de manière sémantiquement cohérente
   - Exemple: un container contient des items, chaque item peut contenir un concept, etc.

5. **Utilisation complète des champs**:
   - Quand tu choisis un template, tu DOIS remplir TOUS ses champs obligatoires

RETOURNE UNIQUEMENT le JSON structuré, sans explication.""",
                ),
                (
                    "user",
                    """Groupe à traiter: {group_name}
Format attendu: {format_description}

Templates disponibles (sélectionnés par embedding):
{templates}

Chemins source disponibles pour les références {{chemin}}:
{source_paths}

Génère maintenant le JSON structuré.""",
                ),
            ]
        )

        # Créer la chaîne LLM avec parser JSON
        parser = JsonOutputParser()
        chain = prompt | self.llm | parser

        # Appeler le LLM
        result = chain.invoke(
            {
                "group_name": group["group_name"],
                "format_description": group["format"],
                "templates": templates_formatted,
                "source_paths": source_paths_formatted,
            }
        )

        return result

    def _add_nested_group_references(
        self,
        path_groups: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Ajoute des clés de référence pour les groupes imbriqués.

        Détecte les relations parent-enfant entre les groupes et ajoute une clé de référence
        dans le groupe parent pour pointer vers le groupe enfant.

        Exemple:
        - Groupe parent: "conjugation_patterns[x]group", "conjugation_patterns[x]model"
        - Groupe enfant: "conjugation_patterns[x]forms[y]person", "conjugation_patterns[x]forms[y]spanish"
        - Ajout dans parent: "conjugation_patterns[x]forms[y]" (référence vers le groupe enfant)

        Args:
            path_groups: Liste des groupes générés par le LLM

        Returns:
            Liste des groupes avec références ajoutées
        """
        import re

        # Créer une copie des groupes pour modification
        updated_groups = []

        for group in path_groups:
            # Copier le groupe
            updated_group = dict(group)
            updated_keys = list(group["keys"])

            # Pour chaque autre groupe, vérifier s'il est un sous-groupe
            for other_group in path_groups:
                if other_group["group_name"] == group["group_name"]:
                    continue

                # Extraire le préfixe commun entre ce groupe et l'autre
                # Ex: "conjugation_patterns[x]" est le préfixe de "conjugation_patterns[x]forms[y]"
                common_prefix = self._find_common_array_prefix(
                    group["keys"], other_group["keys"]
                )

                if common_prefix and self._is_child_group(group["keys"], other_group["keys"], common_prefix):
                    # Trouver la clé de référence à ajouter
                    # C'est le préfixe du groupe enfant jusqu'à sa dernière variable
                    child_reference = self._extract_child_reference(other_group["keys"])

                    if child_reference and child_reference not in updated_keys:
                        updated_keys.append(child_reference)

            updated_group["keys"] = updated_keys
            updated_groups.append(updated_group)

        return updated_groups

    def _find_common_array_prefix(
        self,
        parent_keys: List[str],
        child_keys: List[str],
    ) -> str:
        """
        Trouve le préfixe commun avec variables entre deux ensembles de clés.

        Args:
            parent_keys: Clés du groupe parent potentiel
            child_keys: Clés du groupe enfant potentiel

        Returns:
            Préfixe commun incluant les variables, ou chaîne vide si aucun
        """
        import re

        if not parent_keys or not child_keys:
            return ""

        # Prendre la première clé de chaque groupe pour comparer
        parent_key = parent_keys[0]
        child_key = child_keys[0]

        # Trouver toutes les positions des variables dans les deux clés
        # Ex: "conjugation_patterns[x]group" → positions de [x]
        #     "conjugation_patterns[x]forms[y]person" → positions de [x] et [y]

        parent_vars = list(re.finditer(r'\[([x-z])\]', parent_key))
        child_vars = list(re.finditer(r'\[([x-z])\]', child_key))

        # Le groupe enfant doit avoir au moins autant de variables que le parent
        if len(child_vars) <= len(parent_vars):
            return ""

        # Vérifier que les N premières variables du parent correspondent à celles de l'enfant
        for i in range(len(parent_vars)):
            if parent_vars[i].group(1) != child_vars[i].group(1):
                return ""

        # IMPORTANT: Vérifier que le texte AVANT la dernière variable du parent est identique
        if parent_vars:
            last_parent_var = parent_vars[-1]
            prefix_end = last_parent_var.end()

            # Extraire le texte avant la dernière variable du parent (inclusivement)
            parent_prefix = parent_key[:prefix_end]
            child_prefix = child_key[:prefix_end]

            # Les préfixes doivent être identiques
            if parent_prefix != child_prefix:
                return ""

            return parent_prefix

        return ""

    def _is_child_group(
        self,
        parent_keys: List[str],
        child_keys: List[str],
        common_prefix: str,
    ) -> bool:
        """
        Vérifie si child_keys représente un sous-groupe de parent_keys.

        Args:
            parent_keys: Clés du groupe parent
            child_keys: Clés du groupe enfant potentiel
            common_prefix: Préfixe commun trouvé

        Returns:
            True si c'est un sous-groupe
        """
        if not common_prefix:
            return False

        # Vérifier que toutes les clés du groupe enfant commencent par le préfixe
        for child_key in child_keys:
            if not child_key.startswith(common_prefix):
                return False

        # Vérifier qu'aucune clé du parent ne commence par le préfixe suivi d'autre chose
        # (sinon ce serait le même groupe, pas un parent-enfant)
        for parent_key in parent_keys:
            if parent_key.startswith(common_prefix):
                # Si la clé parent continue après le préfixe avec autre chose qu'une variable,
                # ce n'est pas une relation parent-enfant
                remainder = parent_key[len(common_prefix):]
                if remainder and not remainder.startswith('['):
                    return False

        return True

    def _extract_child_reference(self, child_keys: List[str]) -> str:
        """
        Extrait la clé de référence à partir des clés d'un groupe enfant.

        La clé de référence est le chemin jusqu'à la dernière variable du groupe enfant.

        Args:
            child_keys: Clés du groupe enfant

        Returns:
            Clé de référence (ex: "conjugation_patterns[x]forms[y]")
        """
        import re

        if not child_keys:
            return ""

        # Prendre la première clé comme représentative
        child_key = child_keys[0]

        # Trouver toutes les variables
        vars_matches = list(re.finditer(r'\[([x-z])\]', child_key))

        if not vars_matches:
            return ""

        # Prendre jusqu'à la dernière variable (incluse)
        last_var = vars_matches[-1]
        reference = child_key[:last_var.end()]

        return reference

    def _resolve_group_references(
        self,
        group_jsons_map: Dict[str, Dict[str, Any]],
    ) -> Dict[str, Dict[str, Any]]:
        """
        Résout les références de groupes imbriqués en remplaçant les placeholders.

        Les références de type {{chemin[x]sous_chemin[y]}} (qui se terminent par une variable)
        sont remplacées par le JSON du groupe correspondant.

        Args:
            group_jsons_map: Dictionnaire {clé_de_référence: json_du_groupe}

        Returns:
            Dictionnaire avec les références résolues
        """
        import re
        import json

        def is_group_reference(ref_string: str) -> bool:
            """
            Vérifie si une string de référence {{...}} pointe vers un groupe.
            Un groupe se termine par une variable sans champ après: {{chemin[x]}} ou {{chemin[x]sous[y]}}
            """
            # Extraire le contenu entre {{ et }}
            match = re.match(r'^\{\{(.+)\}\}$', ref_string.strip())
            if not match:
                return False

            content = match.group(1)

            # Vérifier si c'est une clé de groupe connue
            return content in group_jsons_map

        def resolve_in_value(value: Any) -> Any:
            """Résout récursivement les références dans une valeur."""
            if isinstance(value, str):
                # Vérifier si c'est une référence de groupe
                if is_group_reference(value):
                    # Extraire le contenu entre {{ et }}
                    content = re.match(r'^\{\{(.+)\}\}$', value.strip()).group(1)

                    # Retourner directement le JSON du groupe
                    if content in group_jsons_map:
                        return group_jsons_map[content]

                return value

            elif isinstance(value, dict):
                # Résoudre récursivement dans les dictionnaires
                return {k: resolve_in_value(v) for k, v in value.items()}

            elif isinstance(value, list):
                # Résoudre récursivement dans les listes
                return [resolve_in_value(item) for item in value]

            else:
                return value

        # Résoudre les références dans tous les groupes
        resolved_map = {}
        for key, group_json in group_jsons_map.items():
            resolved_map[key] = resolve_in_value(group_json)

        return resolved_map

    def _build_path_to_value_map(self, source_json: Dict[str, Any]) -> Dict[str, Any]:
        """
        Construit un dictionnaire qui mappe chaque chemin concret vers sa valeur.

        Utilise la notation avec indices réels [0], [1], [2]... pour les tableaux.

        Args:
            source_json: Le JSON source avec les données réelles

        Returns:
            Dictionnaire {chemin_concret: valeur}

        Exemple:
            Input: {"metadata": {"course": "Espagnol"}, "items": [{"name": "A"}, {"name": "B"}]}
            Output: {
                "metadata->course": "Espagnol",
                "items[0]->name": "A",
                "items[1]->name": "B"
            }
        """
        path_to_value_map = {}

        def traverse(obj, current_path=""):
            """Traverse récursivement l'objet pour construire le mapping."""
            if isinstance(obj, dict):
                for key, value in obj.items():
                    new_path = f"{current_path}->{key}" if current_path else key

                    if isinstance(value, (dict, list)):
                        # Continuer la traversée pour les structures complexes
                        traverse(value, new_path)
                    else:
                        # Valeur primitive (string, number, bool, None)
                        path_to_value_map[new_path] = value

            elif isinstance(obj, list):
                for idx, item in enumerate(obj):
                    new_path = f"{current_path}[{idx}]"

                    if isinstance(item, (dict, list)):
                        # Continuer la traversée pour les structures complexes
                        traverse(item, new_path)
                    else:
                        # Valeur primitive dans un tableau
                        path_to_value_map[new_path] = item

        traverse(source_json)
        return path_to_value_map

    def _collect_all_references(self, obj: Any) -> List[str]:
        """
        Collecte toutes les références {{...}} dans un objet.

        Args:
            obj: L'objet à analyser (dict, list, str, etc.)

        Returns:
            Liste des chemins référencés (sans les accolades)
            Ex: ["conjugationPatterns->endingsByPerson[x]->person", ...]
        """
        import re

        references = []

        def traverse(o):
            if isinstance(o, str):
                # Chercher toutes les occurrences de {{...}}
                matches = re.findall(r'\{\{([^}]+)\}\}', o)
                references.extend(matches)
            elif isinstance(o, dict):
                for value in o.values():
                    traverse(value)
            elif isinstance(o, list):
                for item in o:
                    traverse(item)

        traverse(obj)
        return references

    def _count_iterations_for_prefix(
        self,
        prefix_with_var: str,
        path_to_value_map: Dict[str, Any]
    ) -> int:
        """
        Compte combien d'indices existent pour un préfixe avec variable.

        Args:
            prefix_with_var: Préfixe avec variable, ex "conjugationPatterns->endingsByPerson[x]"
            path_to_value_map: Map des chemins concrets vers valeurs

        Returns:
            Nombre d'itérations nécessaires

        Exemple:
            prefix_with_var = "conjugationPatterns->endingsByPerson[x]"
            path_to_value_map contient:
                "conjugationPatterns->endingsByPerson[0]->person"
                "conjugationPatterns->endingsByPerson[1]->person"
                "conjugationPatterns->endingsByPerson[2]->person"
            → Retourne 3
        """
        import re

        # Créer un pattern regex en remplaçant [x/y/z] par (\d+)
        pattern = re.escape(prefix_with_var)
        pattern = pattern.replace(r'\[x\]', r'\[(\d+)\]')
        pattern = pattern.replace(r'\[y\]', r'\[(\d+)\]')
        pattern = pattern.replace(r'\[z\]', r'\[(\d+)\]')

        # Trouver tous les indices qui matchent
        indices = set()
        for path in path_to_value_map.keys():
            match = re.match(pattern, path)
            if match:
                idx = int(match.group(1))
                indices.add(idx)

        # Le nombre d'itérations est max + 1 (car indices commencent à 0)
        return max(indices) + 1 if indices else 0

    def _replace_inline_references(
        self,
        text: str,
        path_to_value_map: Dict[str, Any]
    ) -> str:
        """
        Remplace les références inline dans un texte.

        Ex: "Titre: {{metadata->course}}" → "Titre: Mini cours d'espagnol"

        Args:
            text: Texte contenant des références {{...}}
            path_to_value_map: Map des valeurs

        Returns:
            Texte avec références remplacées
        """
        import re

        def replacer(match):
            path = match.group(1)
            value = path_to_value_map.get(path, match.group(0))
            return str(value)

        return re.sub(r'\{\{([^}]+)\}\}', replacer, text)

    def _simple_replace(
        self,
        obj: Any,
        path_to_value_map: Dict[str, Any]
    ) -> Any:
        """
        Remplace simplement les références {{chemin}} par leurs valeurs.
        Utilisé quand il n'y a PAS de variables [x], [y], [z].

        Args:
            obj: L'objet à traiter
            path_to_value_map: Map des valeurs

        Returns:
            Objet avec références remplacées
        """
        import re

        if isinstance(obj, str):
            if obj.startswith('{{') and obj.endswith('}}'):
                path = obj[2:-2]  # Extraire le chemin
                # Récupérer la valeur
                return path_to_value_map.get(path, obj)
            else:
                # Peut contenir des références inline
                return self._replace_inline_references(obj, path_to_value_map)

        elif isinstance(obj, dict):
            return {
                key: self._simple_replace(value, path_to_value_map)
                for key, value in obj.items()
            }

        elif isinstance(obj, list):
            return [
                self._simple_replace(item, path_to_value_map)
                for item in obj
            ]

        else:
            return obj

    def _replace_variable_with_index(
        self,
        obj: Any,
        var_name: str,
        index: int,
        path_to_value_map: Dict[str, Any]
    ) -> Any:
        """
        Remplace toutes les occurrences de [var_name] par [index] et récupère les valeurs.

        Args:
            obj: L'objet à traiter
            var_name: Nom de la variable ('x', 'y', ou 'z')
            index: Indice concret (0, 1, 2, ...)
            path_to_value_map: Map des valeurs

        Returns:
            Objet avec variable remplacée par l'indice et valeurs résolues
        """
        import re

        if isinstance(obj, str):
            if obj.startswith('{{') and obj.endswith('}}'):
                path = obj[2:-2]
                # Remplacer la variable par l'indice
                concrete_path = path.replace(f'[{var_name}]', f'[{index}]')

                # Vérifier si c'est une référence à un groupe imbriqué
                # (se termine par une variable différente)
                if re.search(r'\[[x-z]\]$', concrete_path):
                    # C'est une référence de groupe, ne pas résoudre maintenant
                    # (sera résolu récursivement)
                    return f'{{{{{concrete_path}}}}}'

                # Récupérer la valeur
                value = path_to_value_map.get(concrete_path)
                if value is None:
                    # Warning: référence non trouvée
                    print(f"⚠️ Référence non trouvée: {concrete_path}")
                    return obj  # Garder la référence telle quelle
                return value
            else:
                # Références inline
                def replacer(match):
                    path = match.group(1)
                    concrete_path = path.replace(f'[{var_name}]', f'[{index}]')
                    value = path_to_value_map.get(concrete_path, match.group(0))
                    return str(value)
                return re.sub(r'\{\{([^}]+)\}\}', replacer, obj)

        elif isinstance(obj, dict):
            return {
                key: self._replace_variable_with_index(
                    value, var_name, index, path_to_value_map
                )
                for key, value in obj.items()
            }

        elif isinstance(obj, list):
            return [
                self._replace_variable_with_index(
                    item, var_name, index, path_to_value_map
                )
                for item in obj
            ]

        else:
            return obj

    def _resolve_group_json(
        self,
        group_json: Dict[str, Any],
        path_to_value_map: Dict[str, Any]
    ) -> Any:
        """
        Résout un group_json en remplaçant les références par les valeurs.

        Grâce aux contraintes validées à l'étape 4:
        - Tous les chemins avec variables partagent le même préfixe
        - Tous les chemins ont la même profondeur de variable

        Args:
            group_json: JSON avec références {{chemin[x]}}
            path_to_value_map: Map chemin concret → valeur

        Returns:
            - Si pas de variable: JSON avec valeurs remplacées
            - Si variable: Liste de JSON (un par itération)
        """
        import re

        # Collecter toutes les références {{...}} dans le group_json
        references = self._collect_all_references(group_json)

        # Déterminer s'il y a une variable à résoudre
        variable_in_group = None
        prefix_with_var = None

        for ref in references:
            var_match = re.search(r'\[([x-z])\]', ref)
            if var_match:
                variable_in_group = var_match.group(1)  # 'x', 'y', ou 'z'
                # Extraire le préfixe jusqu'à la variable (incluse)
                prefix_with_var = ref[:var_match.end()]
                break

        # CAS 1: Pas de variable → simple remplacement
        if not variable_in_group:
            return self._simple_replace(group_json, path_to_value_map)

        # CAS 2: Avec variable → expansion
        # Compter combien d'itérations nécessaires
        num_iterations = self._count_iterations_for_prefix(
            prefix_with_var,
            path_to_value_map
        )

        if num_iterations == 0:
            print(f"⚠️ Aucune itération trouvée pour le préfixe: {prefix_with_var}")
            return group_json  # Retourner tel quel

        # Dupliquer et résoudre pour chaque itération
        expanded_list = []
        for i in range(num_iterations):
            # Remplacer toutes les occurrences de [variable] par [i]
            item = self._replace_variable_with_index(
                group_json,
                variable_in_group,
                i,
                path_to_value_map
            )
            expanded_list.append(item)

        return expanded_list

    def _combine_group_jsons(
        self,
        group_jsons: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Combine plusieurs JSONs de groupes dans une structure finale cohérente.

        Args:
            group_jsons: Liste des JSONs générés pour chaque groupe

        Returns:
            JSON final combiné dans un container global
        """
        # Si un seul groupe, le retourner directement
        if len(group_jsons) == 1:
            return group_jsons[0]

        # Sinon, créer un container vertical qui contient tous les groupes
        return {
            "template_name": "layouts/vertical_column/container",
            "items": group_jsons,
            "version": "1.0.0"
        }

    def _generate_structure_with_llm(
        self,
        source_json: Dict[str, Any],
        templates: List[Dict[str, Any]],  # Gardé pour compatibilité mais non utilisé avec la nouvelle approche
        context_description: str,
    ):
        # Extraire les chemins source avec variables [x], [y], [z]
        json_paths_with_variables = self._extract_all_json_paths(
            source_json, use_variables=True
        )

        # NOUVELLE APPROCHE: Générer les groupes de chemins avec formats
        path_groups = self._generate_path_groups_with_llm(
            source_paths=json_paths_with_variables,
            context_description=context_description,
        )

        # Ajouter les références aux groupes imbriqués
        path_groups_before = path_groups
        path_groups = self._add_nested_group_references(path_groups)

        # Valider les groupes (Étape 4)
        validation_warnings = validate_path_groups(path_groups)
        if validation_warnings:
            print("\n=== WARNINGS DE VALIDATION DES PATH GROUPS ===")
            print("\n".join(validation_warnings))
            print("=" * 50 + "\n")
            # Option: lever une exception si critique
            # raise ValueError("Path groups invalides")


        # Pour chaque groupe, récupérer les templates par embedding et générer le JSON
        # On crée un dictionnaire {clé_de_référence: json_du_groupe} pour faciliter la résolution
        group_jsons_map = {}

        for group in path_groups:
            # Générer l'embedding à partir de la description du format
            format_embedding = self._generate_embedding(group["format"])

            # Récupérer les templates similaires
            group_templates = fetch_similar_templates(
                self.db,
                format_embedding,
                top_k=8,  # Limiter à 8 templates par groupe pour ne pas surcharger le prompt
                include_full_data=False,
            )

            # Générer le JSON structuré pour ce groupe
            group_json = self._generate_json_from_group(
                group=group,
                templates=group_templates,
                source_json=source_json,
            )

            # Extraire la clé de référence pour ce groupe (son "chemin d'accès")
            # C'est le préfixe jusqu'à la dernière variable
            group_reference = self._extract_child_reference(group["keys"])
            if not group_reference:
                # Si pas de variable, utiliser la première clé
                group_reference = group["keys"][0] if group["keys"] else group["group_name"]

            group_jsons_map[group_reference] = group_json

        # Résoudre les références de groupes imbriqués
        resolved_jsons_map = self._resolve_group_references(group_jsons_map)

        # Étape 6: Construire le mapping chemin → valeur avec indices réels
        path_to_value_map = self._build_path_to_value_map(source_json)

        # Étape 7: Résoudre les valeurs pour chaque groupe (expansion)
        final_resolved_jsons_map = {}
        for ref, group_json in resolved_jsons_map.items():
            final_group = self._resolve_group_json(group_json, path_to_value_map)
            final_resolved_jsons_map[ref] = final_group

        # Identifier le(s) groupe(s) racine(s) (ceux qui ne sont pas référencés par d'autres)
        # Pour simplifier, on prend les groupes avec le moins de variables
        import re
        root_groups = []
        min_vars = float('inf')

        for ref, json_data in final_resolved_jsons_map.items():
            num_vars = len(re.findall(r'\[[x-z]\]', ref))
            if num_vars < min_vars:
                min_vars = num_vars
                root_groups = [(ref, json_data)]
            elif num_vars == min_vars:
                root_groups.append((ref, json_data))

        # Combiner les groupes racines
        root_jsons = [json_data for _, json_data in root_groups]
        final_json = self._combine_group_jsons(group_jsons=root_jsons)

        # Pour la compatibilité avec l'ancienne interface, on retourne aussi un dict vide pour destination_mappings
        # (ce n'est plus pertinent avec la nouvelle approche mais on le garde pour ne pas casser l'API)
        return final_json, "TODO: prompt", {}

    def _extract_all_json_paths(
        self, data: Any, include_indices: bool = False, use_variables: bool = False
    ) -> str:
        """
        Extrait récursivement tous les chemins disponibles dans un JSON.

        Utilise extract_json_structure pour obtenir une structure minimale fusionnée,
        puis extrait tous les chemins possibles.

        Args:
            data: Le JSON à analyser
            include_indices: Si True, retourne tous les chemins avec les index réels des tableaux
                           (ex: course_sections[0]description, course_sections[1]description)
                           Si False (défaut), utilise la notation compactée [] ou [x], [y], [z]
                           (ex: course_sections[]description ou course_sections[x]description)
            use_variables: Si True et include_indices=False, utilise [x], [y], [z] pour les tableaux
                          (ex: course_sections[x]lessons[y]title)

        Returns:
            String formaté avec tous les chemins disponibles
        """
        if include_indices:
            # Mode avec indices: extraire tous les chemins du JSON original
            return self._extract_paths_with_indices(data)
        else:
            # Mode compact: utiliser extract_json_structure pour fusionner
            structure = extract_json_structure(data)
            return self._extract_paths_compact(structure, use_variables=use_variables)

    def _extract_paths_compact(
        self, structure: Any, use_variables: bool = False
    ) -> str:
        """
        Extrait les chemins en notation compactée avec [] ou avec des variables [x], [y], [z].

        Args:
            structure: La structure JSON fusionnée
            use_variables: Si True, utilise [x], [y], [z] pour les tableaux imbriqués.
                          Si False, utilise [] (défaut)

        Returns:
            String formaté avec tous les chemins compactés
        """
        paths = []
        # Variables pour les niveaux d'imbrication de tableaux
        array_vars = ["x", "y", "z", "w", "v", "u", "t", "s", "r", "q"]

        def is_simple_value(val: Any) -> bool:
            """Vérifie si une valeur est simple (primitive ou tableau de primitives)"""
            if isinstance(val, (str, int, float, bool, type(None))):
                return True
            if isinstance(val, list):
                # Tableau de primitives
                return all(
                    isinstance(item, (str, int, float, bool, type(None)))
                    for item in val
                )
            # Les objets ne sont jamais considérés comme simples
            return False

        def extract_paths(obj: Any, path: str = "", array_depth: int = 0):
            if isinstance(obj, dict):
                # Parcourir les clés de l'objet
                for key, value in obj.items():
                    # Créer le chemin pour cette clé
                    if path:
                        # Si on est dans un chemin existant, utiliser ->
                        new_path = f"{path}->{key}"
                    else:
                        # Racine
                        new_path = key

                    # Ajouter ce chemin SEULEMENT si la valeur est simple
                    if is_simple_value(value):
                        paths.append(new_path)

                    # Continuer la récursion pour les objets/tableaux complexes
                    if isinstance(value, (dict, list)) and not is_simple_value(value):
                        extract_paths(value, new_path, array_depth)

            elif isinstance(obj, list):
                if len(obj) > 0:
                    # Pour les tableaux, on utilise la notation [] ou [x], [y], etc.
                    sample = obj[0]

                    # Déterminer la notation d'index
                    if use_variables and array_depth < len(array_vars):
                        index_notation = f"[{array_vars[array_depth]}]"
                    else:
                        index_notation = "[]"

                    if isinstance(sample, dict):
                        # Tableau d'objets
                        for key, value in sample.items():
                            # Créer le chemin avec [] ou [x]
                            array_path = f"{path}{index_notation}"
                            new_path = f"{array_path}{key}"

                            # Ajouter ce chemin SEULEMENT si la valeur est simple
                            if is_simple_value(value):
                                paths.append(new_path)

                            # Récursion pour les valeurs imbriquées avec profondeur incrémentée
                            if isinstance(value, (dict, list)) and not is_simple_value(
                                value
                            ):
                                extract_paths(value, new_path, array_depth + 1)
                    else:
                        # Tableau de primitives
                        array_path = f"{path}{index_notation}"
                        paths.append(array_path)

        extract_paths(structure)

        # Supprimer les doublons et trier
        unique_paths = sorted(set(paths))

        # Formater la liste des chemins
        # formatted_paths = "\n".join([f"  - {path}" for path in unique_paths])
        return unique_paths

    def _extract_paths_with_indices(self, data: Any) -> str:
        """
        Extrait tous les chemins avec les index réels des tableaux.

        Args:
            data: Le JSON original

        Returns:
            String formaté avec tous les chemins incluant les index
        """
        paths = []

        def is_simple_value(val: Any) -> bool:
            """Vérifie si une valeur est simple (primitive ou tableau de primitives)"""
            if isinstance(val, (str, int, float, bool, type(None))):
                return True
            if isinstance(val, list):
                # Tableau de primitives
                return all(
                    isinstance(item, (str, int, float, bool, type(None)))
                    for item in val
                )
            # Les objets ne sont jamais considérés comme simples
            return False

        def extract_paths(obj: Any, path: str = ""):
            if isinstance(obj, dict):
                # Parcourir les clés de l'objet
                for key, value in obj.items():
                    # Créer le chemin pour cette clé
                    if path:
                        # Si on est dans un chemin existant, utiliser ->
                        new_path = f"{path}->{key}"
                    else:
                        # Racine
                        new_path = key

                    # Ajouter ce chemin SEULEMENT si la valeur est simple
                    if is_simple_value(value):
                        paths.append(new_path)

                    # Continuer la récursion pour les objets/tableaux complexes
                    if isinstance(value, (dict, list)) and not is_simple_value(value):
                        extract_paths(value, new_path)

            elif isinstance(obj, list):
                # Pour chaque élément du tableau, créer un chemin avec son index
                for idx, item in enumerate(obj):
                    array_path = f"{path}[{idx}]"

                    if isinstance(item, dict):
                        # Tableau d'objets
                        for key, value in item.items():
                            new_path = f"{array_path}{key}"

                            # Ajouter ce chemin SEULEMENT si la valeur est simple
                            if is_simple_value(value):
                                paths.append(new_path)

                            # Récursion pour les valeurs imbriquées
                            if isinstance(value, (dict, list)) and not is_simple_value(
                                value
                            ):
                                extract_paths(value, new_path)
                    else:
                        # Tableau de primitives
                        paths.append(array_path)

        extract_paths(data)

        # Supprimer les doublons et trier
        unique_paths = sorted(set(paths))

        # Formater la liste des chemins
        # formatted_paths = "\n".join([f"  - {path}" for path in unique_paths])
        return unique_paths

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
            formatted.append(
                f"""
Template {i}:
- Path (à utiliser EXACTEMENT comme template_name): "{tmpl['template_name']}"
- Usage des champs: {tmpl['fields_usage']}
"""
            )
        return "\n".join(formatted)

    def _validate_destination_mappings(
        self, destination_mappings: Dict[str, str]
    ) -> List[str]:
        """
        Valide les destination mappings pour détecter les chevauchements interdits.

        Un chevauchement se produit quand deux chemins sources différents assignent
        des templates différents au même emplacement. Deux cas sont détectés:

        Cas 1 - Conflit dans un tableau (field -> index -> template):
            "course_sections[x]key_concepts[y]concept_name": "...["items"][y]conceptual/concept["title"]"
            "course_sections[x]key_concepts[y]examples": "...["items"][y]text/liste_exemples["items"]"
            Ces deux chemins vont vers le même index [y] mais avec des templates différents.

        Cas 2 - Conflit dans un champ (field -> template):
            "course_sections[x]section_description": '...["content"]text/description_longue["text"]'
            "course_sections[x]key_concepts[y]concept_name": '...["content"]layouts/container["items"][y]...'
            Le champ ["content"] reçoit deux templates différents (text/description_longue vs layouts/container).

        Args:
            destination_mappings: Les mappings source -> destination à valider

        Returns:
            Liste des erreurs détectées (vide si tout est OK)
        """
        import re
        errors = []

        # Regrouper les chemins par leur "préfixe de conteneur"
        # Ex: "...["items"][y]conceptual/concept["title"]" -> préfixe = '...["items"][y]'
        container_groups = {}

        for source_path, dest_path in destination_mappings.items():
            # Extraire tous les segments du chemin de destination
            segments = self._parse_destination_path(dest_path)

            # Trouver les positions où on a un conflit potentiel:
            # 1. field -> index -> template (objets dans un tableau)
            # 2. field -> template (objet directement dans un champ)
            for i in range(len(segments) - 1):
                template_index = -1
                prefix_end = -1

                # Cas 1: field -> index -> template
                if (
                    i < len(segments) - 2
                    and segments[i]["type"] == "field"
                    and segments[i + 1]["type"] == "index"
                    and segments[i + 2]["type"] == "template"
                ):
                    template_index = i + 2
                    prefix_end = i + 2  # Inclure jusqu'à l'index

                # Cas 2: field -> template (sans index)
                elif (
                    segments[i]["type"] == "field"
                    and segments[i + 1]["type"] == "template"
                ):
                    template_index = i + 1
                    prefix_end = i + 1  # Inclure jusqu'au field

                # Si on a trouvé un pattern à valider
                if template_index > 0:
                    # Reconstruire le préfixe jusqu'au point de conflit
                    prefix_parts = []
                    for j in range(prefix_end):
                        seg = segments[j]
                        if seg["type"] == "template":
                            prefix_parts.append(seg["value"])
                        elif seg["type"] == "field":
                            prefix_parts.append(f'["{seg["value"]}"]')
                        elif seg["type"] == "index":
                            # Garder l'index tel quel (nombre ou variable)
                            idx = seg["value"]
                            prefix_parts.append(f"[{idx}]")

                    prefix = "".join(prefix_parts)
                    template_name = segments[template_index]["value"]

                    # Enregistrer ce préfixe + template
                    if prefix not in container_groups:
                        container_groups[prefix] = []
                    container_groups[prefix].append(
                        {
                            "source_path": source_path,
                            "dest_path": dest_path,
                            "template": template_name,
                        }
                    )

        # Vérifier les conflits: même préfixe mais templates différents
        for prefix, items in container_groups.items():
            templates_at_prefix = {}
            for item in items:
                template = item["template"]
                if template not in templates_at_prefix:
                    templates_at_prefix[template] = []
                templates_at_prefix[template].append(item["source_path"])

            # Si on a plusieurs templates différents au même préfixe, c'est un conflit
            if len(templates_at_prefix) > 1:
                template_list = ", ".join(
                    [f'"{t}"' for t in templates_at_prefix.keys()]
                )
                source_paths = [item["source_path"] for item in items]
                errors.append(
                    f"Chevauchement détecté au préfixe '{prefix}':\n"
                    f"  Templates en conflit: {template_list}\n"
                    f"  Chemins sources concernés: {', '.join(source_paths)}\n"
                    f"  ⚠️  Ces chemins sources pointent vers le même index mais avec des templates différents,\n"
                    f"      ce qui causera un écrasement. Utilisez des index différents ou imbriquez les templates."
                )

        return errors

    def _validate_no_double_indices(self, destination_mappings: Dict[str, str]):
        """
        Valide qu'aucun chemin de destination ne contient des indices consécutifs.

        Des indices consécutifs comme ["items"][1][4] sont invalides et causent
        des erreurs lors de l'insertion de valeurs.

        Args:
            destination_mappings: Les mappings à valider

        Raises:
            ValueError: Si des indices doubles sont détectés
        """
        import warnings

        for source_path, dest_path in destination_mappings.items():
            segments = self._parse_destination_path(dest_path)

            # Chercher des indices consécutifs
            for i in range(len(segments) - 1):
                if segments[i]["type"] == "index" and segments[i+1]["type"] == "index":
                    error_msg = (
                        f"Double index détecté dans le mapping:\n"
                        f"  Source: '{source_path}'\n"
                        f"  Destination: '{dest_path}'\n"
                        f"  Indices consécutifs aux positions {i} et {i+1}: "
                        f"{segments[i]} -> {segments[i+1]}\n"
                        f"  Ceci est invalide. Les indices doivent être séparés par un template ou un champ."
                    )
                    warnings.warn(f"\n⚠️  {error_msg}\n")

    def _generate_path_groups_with_llm(
        self,
        source_paths: List[str],
        context_description: str = "",
    ) -> List[Dict[str, Any]]:
        """
        Génère des groupes de chemins avec description de format en utilisant le LLM.

        Cette fonction demande au LLM de regrouper les chemins source selon leur nature
        sémantique et de fournir une description de format pour chaque groupe.

        Args:
            source_paths: Liste des chemins source avec variables (ex: ['learning_objective', 'course_sections[x]section_id'])
            context_description: Description du contexte pour aider le LLM

        Returns:
            Liste de groupes au format:
            [
                {
                    "group_name": "informations_personnelles",
                    "keys": ["personne.nom", "personne.age"],
                    "format": "structure simple clé-valeur pour données personnelles"
                }
            ]
        """
        # Construire le prompt
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """Tu es un expert en analyse de structures de données de cartes mentales.
Ta tâche est de regrouper des chemins de données (source_paths) selon leur nature sémantique
et de proposer le meilleur format pour représenter chaque groupe.

RÈGLES CRITIQUES:

1. **Regroupement STRICT par niveau de profondeur de tableaux**:
   ⚠️ RÈGLE ABSOLUE: TOUS les chemins d'un groupe DOIVENT avoir EXACTEMENT le même nombre de variables [x], [y], [z]
   ❌ INTERDIT - Mélanger des profondeurs différentes
   ✅ CORRECT - Séparer par profondeur

2. **Regroupement par préfixe COMPLET**:
   - Les chemins avec la même profondeur DOIVENT aussi avoir le même préfixe jusqu'à la dernière variable
3. **Description du format**:
   - Utilise une phrase COURTE pour décrire le format
   - Sois CONCRET et DESCRIPTIF (évite les termes génériques)


RETOURNE un JSON avec le format exact suivant (UNIQUEMENT le JSON, sans explication):
[
  {{
    "group_name": "nom_du_groupe",
    "keys": ["chemin1", "chemin2", ...],
    "format": "description courte du format"
  }}
]""",
                ),
                (
                    "user",
                    """Contexte: {context}

Chemins source à regrouper (morceaux de cartes mentales):
{source_paths}

Génère les groupes avec leurs formats.""",
                ),
            ]
        )

        # Préparer les données pour le prompt
        source_paths_formatted = "\n".join([f"  - {path}" for path in source_paths])

        # Créer la chaîne LLM avec parser JSON
        parser = JsonOutputParser()
        chain = prompt | self.llm | parser

        # Appeler le LLM
        result = chain.invoke(
            {
                "context": context_description or "Aucun contexte spécifique fourni",
                "source_paths": source_paths_formatted,
            }
        )

        return result

    def _generate_destination_paths_with_llm(
        self,
        source_paths: List[str],
        templates: List[Dict[str, Any]],
        context_description: str = "",
    ) -> Dict[str, str]:
        """
        Génère les chemins de destination pour chaque chemin source en utilisant le LLM.

        Cette fonction demande au LLM de créer des chemins de destination qui:
        - Imbriquent plusieurs templates de manière sémantiquement cohérente
        - Respectent les règles d'indices (variables vs fixes)
        - Mappent les données source vers les champs appropriés des templates

        Args:
            source_paths: Liste des chemins source avec variables (ex: ['learning_objective', 'course_sections[x]section_id'])
            templates: Liste des templates disponibles avec leurs métadonnées
            context_description: Description du contexte pour aider le LLM

        Returns:
            Dict mappant chaque chemin source vers son chemin de destination
            Ex: {
                "learning_objective": "layouts/vertical_column/container[\"items\"][0]layouts/vertical_column/item[\"title\"]conceptual/concept[\"description\"]",
                "course_sections[x]section_id": "layouts/vertical_column/container[\"items\"][0]layouts/vertical_column/container[\"items\"][x]layouts/vertical_column/item[\"title\"]conceptual/concept[\"title\"]"
            }
        """
        templates_formatted = self._format_templates_for_prompt(templates)

        # Construire le prompt
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """Tu es un expert en construction de structures de données pédagogiques.
Ta tâche est de mapper des chemins de données source vers des chemins de destination qui utilisent des templates HTML/pédagogiques imbriqués.

⚠️ RÈGLE CRITIQUE 1 - CHAMPS AUTORISÉS ET OBLIGATOIRES:
Tu NE PEUX utiliser que les champs (fields) explicitement définis dans "Usage des champs" de chaque template.
- ✅ AUTORISÉ: Si "Usage des champs" mentionne "title", tu peux utiliser ["title"]
- ❌ INTERDIT: Inventer des champs qui n'existent pas dans le template (ex: ["header1"], ["row1_col1"] si non mentionnés)
- ❌ INTERDIT: Utiliser des champs génériques comme ["content"], ["items"] s'ils ne sont pas dans "Usage des champs"
- ⚠️ OBLIGATION: Quand tu choisis d'utiliser un template, tu DOIS utiliser TOUS les champs (fields) listés dans "Usage des champs"
  - Si un template a les champs ["title", "content", "footer"], tu DOIS mapper des données vers ces 3 champs
  - Ne laisse AUCUN champ non utilisé - chaque champ doit recevoir une donnée du JSON source
  - Si tu ne peux pas remplir tous les champs d'un template, choisis un AUTRE template plus adapté

⚠️ RÈGLE CRITIQUE 2 - STRUCTURE DES CHEMINS:
TOUS les champs (sauf le dernier champ de valeur primitive) doivent TOUJOURS contenir un objet avec template_name, JAMAIS une valeur primitive directe.
- ❌ INTERDIT: layouts/horizontal_line/container["items"][0]layouts/horizontal_line/item["title"] → "Mon titre"
- ✅ CORRECT: layouts/horizontal_line/container["items"][0]layouts/horizontal_line/item["title"]text/titre["text"] → "Mon titre"
- ❌ INTERDIT: layouts/vertical_column/item["content"] → "Contenu direct"
- ✅ CORRECT: layouts/vertical_column/item["content"]text/explication["text"] → "Contenu direct"
- ❌ INTERDIT: tableaux/ligne_cle_valeur["value"] → "Ma valeur"
- ✅ CORRECT: tableaux/ligne_cle_valeur["value"]text/titre["text"] → "Ma valeur"
- RÈGLE GÉNÉRALE: Un chemin de destination doit TOUJOURS se terminer par un template de contenu final (text/*, conceptual/*, temporal/*, procedural/*, etc.) suivi d'un champ de valeur primitive (["text"], ["title"], ["description"], ["duration"], ["content"], etc.)

RÈGLES CRITIQUES POUR LES INDICES:

1. **Chemins source SANS variable** (ex: learning_objective):
   - Utilise des indices FIXES dans le chemin de destination: [0], [1], [2], etc.
   - Chaque chemin source sans variable doit avoir son propre indice fixe unique
   - Exemple: si tu as 3 chemins sans variable, utilise [0] pour le premier, [1] pour le deuxième, [2] pour le troisième

2. **Chemins source AVEC variable** (ex: course_sections[x]section_id):
   - Utilise la MÊME variable dans le chemin de destination
   - La variable [x] dans le source doit apparaître comme [x] dans la destination
   - La variable [y] dans le source doit apparaître comme [y] dans la destination
   - Exemple: course_sections[x]lessons[y]title → ...["items"][x]...["items"][y]...

3. **Imbrication des templates**:
   - Tu peux (et dois) imbriquer plusieurs templates pour créer une structure cohérente
   - Exemple: layouts/XXXX/container["items"][0]layouts/XXXX/item["title"]conceptual/concept["description"]
   - Cela signifie: un container qui contient un item dont le titre contient un concept

4. **Format des chemins de destination**:
   - Commence par le template_name du premier template (ex: layouts/XXXX/container)
   - Ajoute ["nom_du_champ"] pour accéder à un champ (UNIQUEMENT les champs listés dans "Usage des champs" du template!)
   - Ajoute [index] pour les tableaux (index fixe ou variable selon la règle 1 et 2)
   - Enchaîne avec le template_name suivant, etc.
   - Exemple complet: layouts/XXXX/container["items"][0]layouts/XXXX/item["title"]conceptual/concept["description"]
   - ⚠️ VÉRIFIE que chaque ["champ"] existe bien dans "Usage des champs" du template avant de l'utiliser!

5. **⚠️ STRATÉGIE ANTI-CHEVAUCHEMENT (CRITIQUE)**:

   RÈGLE D'OR: Utilise `layouts/XXXX/container["items"]` avec des indices FIXES pour séparer les groupes de données.

   **STRATÉGIE RECOMMANDÉE**: Structure à 3 niveaux avec indices fixes

   ❌ ERREUR TYPIQUE - Partager le même champ/index:
   {{
     "course_sections[x]section_description": 'container["items"][x]layouts/item["content"]text/description["text"]',
     "course_sections[x]key_concepts[y]name": 'container["items"][x]layouts/item["content"]layouts/container["items"][y]...'
   }}
   → Conflit sur ["content"] qui reçoit 2 templates différents

   ✅ SOLUTION - Utilise layouts/XXXX/container avec indices fixes:
   {{
     "course_sections[x]section_description": 'container["items"][x]layouts/XXXX/container["items"][0]text/description["text"]',
     "course_sections[x]key_concepts[y]name": 'container["items"][x]layouts/XXXX/container["items"][1]layouts/XXXX/container["items"][y]conceptual/concept["title"]'
   }}
   → Pas de conflit : section_description à [0], key_concepts à [1]

   **Structure hiérarchique**:
   - Niveau 1: layouts/XXXX/container["items"][0 ou 1] → sépare learning_objective vs course_sections
   - Niveau 2: ...["items"][x]layouts/XXXX/container["items"][0, 1, 2, ...] → sépare title, description, key_concepts, notes
   - Niveau 3: ...["items"][y] → itère sur les key_concepts

6. **PROCESSUS DE GÉNÉRATION ÉTAPE PAR ÉTAPE**:

   Pour chaque chemin source:
   a) Identifie le préfixe (ex: "course_sections[x]key_concepts[y]")
   b) Vérifie les autres chemins avec le même préfixe
   c) Choisis UN template commun pour ce préfixe
   d) VÉRIFIE que le template possède bien les champs dont tu as besoin dans "Usage des champs"
   e) Assigne des chemins de destination en utilisant UNIQUEMENT les champs autorisés du template
   f) ASSURE-TOI que le chemin se termine par un template de contenu final (text/*, conceptual/*, temporal/*, procedural/*, etc.) suivi d'un champ de valeur primitive
   g) VÉRIFIE que le chemin ne se termine PAS simplement par un champ comme ["value"], ["title"], ["content"] sans template de contenu avant
   h) Double-vérifie qu'aucun conflit n'existe avec les chemins déjà générés

7. **EXEMPLE COMPLET DE MAPPING VALIDE**:

   Chemins sources:
   - "learning_objective"
   - "course_sections[x]section_title"
   - "course_sections[x]section_description"
   - "course_sections[x]key_concepts[y]concept_name"
   - "course_sections[x]additional_notes"

   Mapping CORRECT (avec stratégie d'indices fixes):
   {{
     "learning_objective": 'layouts/XXXX/container["items"][0]text/description["text"]',
     "course_sections[x]section_title": 'layouts/XXXX/container["items"][1]layouts/XXXX/container["items"][x]layouts/XXXX/container["items"][0]text/titre["text"]',
     "course_sections[x]section_description": 'layouts/XXXX/container["items"][1]layouts/XXXX/container["items"][x]layouts/XXXX/container["items"][1]text/description["text"]',
     "course_sections[x]key_concepts[y]concept_name": 'layouts/XXXX/container["items"][1]layouts/XXXX/container["items"][x]layouts/XXXX/container["items"][2]layouts/XXXX/container["items"][y]conceptual/concept["title"]',
     "course_sections[x]additional_notes": 'layouts/XXXX/container["items"][1]layouts/XXXX/container["items"][x]text/notes["text"]'
   }}

   Pourquoi c'est CORRECT:
   - Niveau 1: learning_objective à [0], course_sections à [1]
   - Niveau 2 (dans chaque course_section [x]): title à [0], description à [1], key_concepts à [2]
   - Niveau 3: key_concepts utilise layouts/XXXX/container["items"][y]
   - additional_notes n'utilise pas de conteneur car il n'a pas besoin d'indices fixes
   - AUCUN conflit: chaque groupe a son propre indice fixe

⚠️ VALIDATION FINALE AVANT DE RETOURNER:
Pour chaque chemin de destination généré:
1. Extraire tous les ["champs"] utilisés
2. Vérifier que chaque champ existe dans "Usage des champs" du template correspondant
3. Si un champ n'existe pas, CHANGER de template ou CORRIGER le chemin
4. VÉRIFIER que le chemin ne se termine PAS par un simple champ sans template de contenu final
   - ❌ INVALIDE: ...tableaux/ligne_cle_valeur["value"]
   - ❌ INVALIDE: ...layouts/XXXX/item["title"]
   - ✅ VALIDE: ...tableaux/ligne_cle_valeur["value"]text/titre["text"]
   - ✅ VALIDE: ...layouts/XXXX/item["title"]conceptual/concept["title"]
5. VÉRIFIER que le dernier template du chemin est bien un template de contenu (text/*, conceptual/*, temporal/*, procedural/*, tableaux/*, comparison/*, logical_relations/*), suivi d'un champ de valeur primitive
6. Si le chemin se termine incorrectement, AJOUTER un template de contenu approprié avant le champ final

RETOURNE un JSON avec le format exact suivant (UNIQUEMENT le JSON, sans explication):
{{
  "chemin_source_1": "chemin_destination_1",
  "chemin_source_2": "chemin_destination_2"
}}""",
                ),
                (
                    "user",
                    """Contexte: {context}

Templates disponibles:
{templates}

Chemins source à mapper:
{source_paths}

INSTRUCTIONS (STRATÉGIE ANTI-CHEVAUCHEMENT):

1. **Regroupe les chemins** par niveaux de variables:
   - Groupe A: chemins sans variable (ex: "learning_objective")
   - Groupe B: chemins avec [x] seulement (ex: "course_sections[x]section_title")
   - Groupe C: chemins avec [x][y] (ex: "course_sections[x]key_concepts[y]*")

2. **Applique la structure à 3 niveaux**:

   Niveau 1 - Racine: layouts/XXXX/container["items"][indice_fixe]
   - [0] = learning_objective
   - [1] = conteneur pour course_sections

   Niveau 2 - Dans course_sections [x]: ...["items"][x]layouts/XXXX/container["items"][indice_fixe]
   - [0] = section_title
   - [1] = section_description
   - [2] = conteneur pour key_concepts
   - [3] = additional_notes (si applicable)

   Niveau 3 - Dans key_concepts [y]: ...["items"][2]layouts/XXXX/container["items"][y]conceptual/concept
   - Utilise le même template pour tous les chemins key_concepts[y]*

3. **Génère les mappings** en suivant cette structure hiérarchique

Génère maintenant les mappings.""",
                ),
            ]
        )

        # Préparer les données pour le prompt
        source_paths_formatted = "\n".join([f"  - {path}" for path in source_paths])

        # Créer la chaîne LLM avec parser JSON
        parser = JsonOutputParser()
        chain = prompt | self.llm | parser

        # Appeler le LLM
        result = chain.invoke(
            {
                "context": context_description or "Aucun contexte spécifique fourni",
                "templates": templates_formatted,
                "source_paths": source_paths_formatted,
            }
        )

        # Valider les mappings générés par le LLM
        validation_errors = self._validate_destination_mappings(result)

        # Si des erreurs sont détectées, essayer de les corriger automatiquement avec Python
        if validation_errors:
            import warnings
            warnings.warn(
                f"\n⚠️  Erreurs de chevauchement détectées. Tentative de correction automatique...\n"
            )

            # Essayer d'abord la correction automatique Python
            result = self._auto_fix_overlaps(result, source_paths)

            # Revalider après correction automatique
            validation_errors = self._validate_destination_mappings(result)

            # Vérifier qu'il n'y a pas de double indices après la correction
            self._validate_no_double_indices(result)

            if not validation_errors:
                warnings.warn(
                    f"\n✅  Correction automatique réussie ! Tous les chevauchements ont été résolus.\n"
                )
            else:
                # Si la correction automatique échoue, fallback sur LLM
                warnings.warn(
                    f"\n⚠️  Correction automatique partielle. Tentative de correction avec LLM O3-mini...\n"
                )

                max_llm_attempts = 1
                for attempt in range(max_llm_attempts):
                    result = self._correct_destination_mappings_with_llm(
                        result, validation_errors, templates_formatted, source_paths_formatted, context_description
                    )

                    validation_errors = self._validate_destination_mappings(result)
                    if not validation_errors:
                        break

                if validation_errors:
                    error_msg = "\n".join(validation_errors)
                    warnings.warn(
                        f"\n⚠️  ERREURS PERSISTANTES:\n{error_msg}\n"
                        f"Les mappings seront utilisés mais peuvent causer des écrasements de données.\n"
                    )

        # Validation finale des double indices (qu'il y ait eu correction ou non)
        self._validate_no_double_indices(result)

        return result

    def _remove_double_indices(self, mappings: Dict[str, str]) -> Dict[str, str]:
        """
        Supprime les indices doubles dans les chemins de destination.

        Si un chemin contient des indices consécutifs comme ["items"][1][4],
        cette fonction supprime le deuxième indice.

        Args:
            mappings: Les mappings potentiellement problématiques

        Returns:
            Mappings nettoyés sans indices doubles
        """
        cleaned_mappings = {}

        for source_path, dest_path in mappings.items():
            segments = self._parse_destination_path(dest_path)

            # Filtrer les indices doubles en conservant le premier
            cleaned_segments = []
            i = 0
            while i < len(segments):
                segment = segments[i]
                cleaned_segments.append(segment)

                # Si c'est un index, vérifier le suivant
                if segment["type"] == "index" and i + 1 < len(segments):
                    next_seg = segments[i + 1]
                    # Si le suivant est aussi un index, le sauter
                    if next_seg["type"] == "index":
                        import warnings
                        warnings.warn(
                            f"\n⚠️  Double index détecté et corrigé dans '{source_path}':\n"
                            f"  Indices [{segment['value']}][{next_seg['value']}] -> [{segment['value']}]\n"
                        )
                        i += 2  # Sauter le double index
                        continue

                i += 1

            # Reconstruire le chemin nettoyé
            cleaned_path = self._reconstruct_path_from_segments(cleaned_segments)
            cleaned_mappings[source_path] = cleaned_path

        return cleaned_mappings

    def _auto_fix_overlaps(
        self, mappings: Dict[str, str], source_paths: List[str]
    ) -> Dict[str, str]:
        """
        Corrige automatiquement les chevauchements en appliquant la stratégie des indices fixes.

        Args:
            mappings: Les mappings générés avec des conflits potentiels
            source_paths: Liste des chemins sources

        Returns:
            Mappings corrigés sans chevauchements
        """
        import re

        fixed_mappings = dict(mappings)  # Copie pour modification

        # Itérer jusqu'à ce qu'il n'y ait plus de conflits
        # (maximum 10 itérations pour éviter les boucles infinies)
        max_iterations = 10
        for iteration in range(max_iterations):
            # 1. Détecter les conflits au niveau DESTINATION
            conflicts = self._detect_destination_conflicts(fixed_mappings)

            if not conflicts:
                # Plus de conflits, on a terminé
                import warnings
                warnings.warn(f"Correction terminée après {iteration} itération(s)")
                break

            # 2. Pour chaque groupe de chemins en conflit, appliquer la correction
            for conflict_prefix, conflicting_sources in conflicts.items():
                # Extraire les mappings concernés
                dest_paths = {src: fixed_mappings[src] for src in conflicting_sources}

                # Appliquer la stratégie des indices fixes
                fixed_group = self._apply_fixed_index_strategy(dest_paths, conflict_prefix)

                # Mettre à jour les mappings corrigés
                fixed_mappings.update(fixed_group)
        else:
            # Si on sort de la boucle sans break, c'est qu'on a atteint max_iterations
            import warnings
            warnings.warn(f"⚠️ Correction arrêtée après {max_iterations} itérations (max atteint)")

        # Nettoyage final: supprimer les éventuels indices doubles
        fixed_mappings = self._remove_double_indices(fixed_mappings)

        return fixed_mappings

    def _detect_destination_conflicts(
        self, destination_mappings: Dict[str, str]
    ) -> Dict[str, List[str]]:
        """
        Détecte les conflits au niveau des chemins de destination.

        Returns:
            Dict {préfixe_en_conflit: [liste des source_paths concernés]}
        """
        import re

        # Regrouper les chemins par leur "préfixe de conteneur"
        container_groups = {}

        for source_path, dest_path in destination_mappings.items():
            segments = self._parse_destination_path(dest_path)

            # Trouver les positions où on a un conflit potentiel
            for i in range(len(segments) - 1):
                template_index = -1
                prefix_end = -1

                # Cas 1: field -> index -> template
                if (
                    i < len(segments) - 2
                    and segments[i]["type"] == "field"
                    and segments[i + 1]["type"] == "index"
                    and segments[i + 2]["type"] == "template"
                ):
                    template_index = i + 2
                    prefix_end = i + 2

                # Cas 2: field -> template (sans index)
                elif (
                    segments[i]["type"] == "field"
                    and segments[i + 1]["type"] == "template"
                ):
                    template_index = i + 1
                    prefix_end = i + 1

                if template_index > 0:
                    # Reconstruire le préfixe jusqu'au point de conflit
                    prefix_parts = []
                    for j in range(prefix_end):
                        seg = segments[j]
                        if seg["type"] == "template":
                            prefix_parts.append(seg["value"])
                        elif seg["type"] == "field":
                            prefix_parts.append(f'["{seg["value"]}"]')
                        elif seg["type"] == "index":
                            idx = seg["value"]
                            prefix_parts.append(f"[{idx}]")

                    prefix = "".join(prefix_parts)
                    template_name = segments[template_index]["value"]

                    if prefix not in container_groups:
                        container_groups[prefix] = []
                    container_groups[prefix].append(
                        {
                            "source_path": source_path,
                            "template": template_name,
                        }
                    )

        # Identifier les conflits: même préfixe mais templates différents
        conflicts = {}

        for prefix, items in container_groups.items():
            templates_at_prefix = set(item["template"] for item in items)

            # Si on a plusieurs templates différents au même préfixe, c'est un conflit
            if len(templates_at_prefix) > 1:
                source_paths = [item["source_path"] for item in items]
                conflicts[prefix] = source_paths

        return conflicts

    def _group_source_paths_by_prefix(self, source_paths: List[str]) -> Dict[str, List[str]]:
        """
        Regroupe les chemins sources par préfixe commun.

        Ex: "course_sections[x]section_title" et "course_sections[x]section_description"
            → groupe "course_sections[x]"

        Returns:
            Dict {préfixe: [liste de chemins]}
        """
        import re

        groups = {}

        for path in source_paths:
            # Extraire le préfixe jusqu'à la dernière variable ou jusqu'au dernier champ
            # Ex: "course_sections[x]key_concepts[y]name" → préfixe = "course_sections[x]key_concepts[y]"
            #     "course_sections[x]section_title" → préfixe = "course_sections[x]"

            # Trouver toutes les variables
            vars_matches = list(re.finditer(r'\[([x-z])\]', path))

            if vars_matches:
                # Prendre jusqu'après la dernière variable
                last_var_end = vars_matches[-1].end()
                prefix = path[:last_var_end]
            else:
                # Pas de variable, c'est un chemin simple
                prefix = "_no_vars_"

            if prefix not in groups:
                groups[prefix] = []
            groups[prefix].append(path)

        return groups

    def _group_has_overlap(self, dest_paths: Dict[str, str]) -> bool:
        """
        Vérifie si un groupe de chemins de destination a des chevauchements.

        Returns:
            True si des chevauchements sont détectés
        """
        # Extraire les préfixes de destination (jusqu'au dernier template avant le champ final)
        dest_prefixes = {}

        for src_path, dest_path in dest_paths.items():
            # Parser le chemin de destination
            segments = self._parse_destination_path(dest_path)

            # Trouver le dernier template
            template_positions = [
                i for i, seg in enumerate(segments) if seg["type"] == "template"
            ]

            if template_positions:
                last_template_idx = template_positions[-1]
                # Construire le préfixe jusqu'au dernier template
                prefix_segments = segments[:last_template_idx + 1]

                prefix_str = self._reconstruct_path_from_segments(prefix_segments)

                if prefix_str not in dest_prefixes:
                    dest_prefixes[prefix_str] = []
                dest_prefixes[prefix_str].append(segments[last_template_idx]["value"])

        # Vérifier s'il y a des templates différents au même préfixe
        for prefix, templates in dest_prefixes.items():
            if len(set(templates)) > 1:
                return True

        return False

    def _reconstruct_path_from_segments(self, segments: List[Dict[str, Any]]) -> str:
        """Reconstruit un chemin de destination à partir de segments."""
        parts = []
        for seg in segments:
            if seg["type"] == "template":
                parts.append(seg["value"])
            elif seg["type"] == "field":
                parts.append(f'["{seg["value"]}"]')
            elif seg["type"] == "index":
                idx = seg["value"]
                if isinstance(idx, int):
                    parts.append(f"[{idx}]")
                else:
                    parts.append(f"[{idx}]")
        return "".join(parts)

    def _apply_fixed_index_strategy(
        self, dest_paths: Dict[str, str], conflict_prefix: str
    ) -> Dict[str, str]:
        """
        Applique la stratégie des indices fixes pour résoudre les conflits.

        Stratégie: Insérer layouts/vertical_column/container["items"][idx] après le préfixe de conflit.

        Args:
            dest_paths: Mappings source → destination pour ce groupe en conflit
            conflict_prefix: Le préfixe de destination où se trouve le conflit

        Returns:
            Mappings corrigés avec indices fixes
        """
        import re

        fixed_mappings = {}

        # Parser le préfixe de conflit pour savoir où couper
        conflict_segments = self._parse_destination_path(conflict_prefix)
        conflict_len = len(conflict_segments)

        # Trier les chemins sources pour avoir un ordre déterministe
        sorted_sources = sorted(dest_paths.keys())

        # Pour chaque chemin source, reconstruire le chemin de destination
        for idx, src_path in enumerate(sorted_sources):
            dest_path = dest_paths[src_path]
            segments = self._parse_destination_path(dest_path)

            # Stratégie :
            # - Préfixe de conflit (garder tel quel)
            # - Insérer layouts/vertical_column/container["items"][idx]
            # - Reste après le préfixe (ce qui vient après le conflit)

            new_segments = []

            # 1. Garder le préfixe de conflit tel quel
            new_segments.extend(conflict_segments)

            # 2. Insérer le conteneur avec indice fixe
            new_segments.append({"type": "template", "value": "layouts/vertical_column/container"})
            new_segments.append({"type": "field", "value": "items"})
            new_segments.append({"type": "index", "value": idx})

            # 3. Ajouter les segments après le préfixe de conflit
            remaining_segments = segments[conflict_len:]

            # BUGFIX: Skip leading index if it would create a double-index pattern
            # (e.g., ["items"][1][4] is invalid, should be ["items"][1]template["field"][4])
            if remaining_segments and remaining_segments[0]["type"] == "index":
                # Skip this index segment to avoid double-index pattern
                remaining_segments = remaining_segments[1:]

            new_segments.extend(remaining_segments)

            # Reconstruire le chemin
            fixed_dest = self._reconstruct_path_from_segments(new_segments)
            fixed_mappings[src_path] = fixed_dest

        return fixed_mappings

    def _find_common_prefix_length(self, segments_list: List[List[Dict[str, Any]]]) -> int:
        """
        Trouve la longueur du préfixe commun entre plusieurs listes de segments.

        Returns:
            Nombre de segments communs au début
        """
        if not segments_list or len(segments_list) < 2:
            return 0

        min_len = min(len(segs) for segs in segments_list)

        common_len = 0
        for i in range(min_len):
            # Vérifier si tous les segments à la position i sont identiques
            first_seg = segments_list[0][i]
            all_same = all(
                segs[i]["type"] == first_seg["type"] and segs[i]["value"] == first_seg["value"]
                for segs in segments_list[1:]
            )

            if all_same:
                common_len += 1
            else:
                break

        return common_len

    def _correct_destination_mappings_with_llm(
        self,
        invalid_mappings: Dict[str, str],
        validation_errors: List[str],
        templates_formatted: str,
        source_paths_formatted: str,
        context_description: str,
    ) -> Dict[str, str]:
        """
        Demande au LLM de corriger les mappings invalides en pointant du doigt les erreurs spécifiques.

        Args:
            invalid_mappings: Les mappings générés qui contiennent des erreurs
            validation_errors: Liste des erreurs de validation détectées
            templates_formatted: Les templates disponibles (formatés)
            source_paths_formatted: Les chemins sources (formatés)
            context_description: Description du contexte

        Returns:
            Mappings corrigés
        """
        # Formater les erreurs pour le prompt
        errors_formatted = "\n".join([f"  ❌ {err}" for err in validation_errors])

        # Formater les mappings invalides pour le prompt
        import json
        invalid_mappings_formatted = json.dumps(invalid_mappings, indent=2, ensure_ascii=False)

        # Construire le prompt de correction
        correction_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """Tu es un expert en correction de structures de données.
Tu as généré des mappings qui contiennent des ERREURS DE CHEVAUCHEMENT.

RAPPEL DES RÈGLES CRITIQUES:
1. Un même emplacement (champ ou index) NE PEUT recevoir qu'UN SEUL template.
   Si deux chemins partagent le même index variable (ex: [y]), ils DOIVENT utiliser le même template.

2. ⚠️ CHAMPS AUTORISÉS:
   Tu NE PEUX utiliser que les champs (fields) explicitement définis dans "Usage des champs" de chaque template.
   - ✅ AUTORISÉ: Si "Usage des champs" mentionne "title", tu peux utiliser ["title"]
   - ❌ INTERDIT: Inventer des champs qui n'existent pas (ex: ["header1"], ["row1_col1"] si non mentionnés)
   - ❌ INTERDIT: Utiliser ["content"], ["items"] s'ils ne sont pas dans "Usage des champs" du template

3. ⚠️ STRUCTURE DES CHEMINS:
   TOUS les champs (sauf le dernier champ de valeur primitive) doivent TOUJOURS contenir un objet avec template_name, JAMAIS une valeur directe.
   - ❌ INTERDIT: layouts/horizontal_line/item["title"] → "Mon titre"
   - ✅ CORRECT: layouts/horizontal_line/item["title"]text/titre["text"] → "Mon titre"
   - ❌ INTERDIT: tableaux/ligne_cle_valeur["value"] → "Ma valeur"
   - ✅ CORRECT: tableaux/ligne_cle_valeur["value"]text/titre["text"] → "Ma valeur"
   - Un chemin doit TOUJOURS se terminer par un template de contenu final (text/*, conceptual/*, temporal/*, procedural/*, tableaux/*, comparison/*, logical_relations/*) suivi d'un champ de valeur primitive""",
                ),
                (
                    "user",
                    """Voici les mappings INVALIDES que tu as générés:

{invalid_mappings}

ERREURS DÉTECTÉES:
{errors}

Chemins source à mapper:
{source_paths}

COMMENT CORRIGER (ÉTAPE PAR ÉTAPE):

Étape 1: Identifie les groupes de chemins en conflit dans les erreurs ci-dessus

Étape 2: Pour CHAQUE groupe identifié dans les erreurs:
   a) Tous les chemins "key_concepts[y]*" DOIVENT avoir le même template à ["items"][y]
   b) Tous les chemins "course_sections[x]*" (sans key_concepts) DOIVENT utiliser des champs SÉPARÉS

Étape 3: Applique ces corrections:

   EXEMPLE DE CORRECTION 1:
   ❌ AVANT (INVALIDE - conflit sur ["content"]):
   {{
     "course_sections[x]section_description": 'container["items"][x]layouts/XXXX/item["content"]text/description["text"]',
     "course_sections[x]key_concepts[y]name": 'container["items"][x]layouts/XXXX/item["content"]layouts/XXXX/container["items"][y]conceptual/concept["title"]'
   }}

   ✅ APRÈS (CORRIGÉ avec indices fixes):
   {{
     "course_sections[x]section_description": 'container["items"][x]layouts/XXXX/container["items"][0]text/description["text"]',
     "course_sections[x]key_concepts[y]name": 'container["items"][x]layouts/XXXX/container["items"][1]layouts/XXXX/container["items"][y]conceptual/concept["title"]'
   }}

   Explication: Utilise layouts/XXXX/container["items"] avec indices fixes: [0] pour description, [1] pour key_concepts

   EXEMPLE DE CORRECTION 2:
   ❌ AVANT (INVALIDE - templates différents au même [y]):
   {{
     "key_concepts[y]name": '...["items"][y]conceptual/concept["title"]',
   }}

   ✅ APRÈS (CORRIGÉ):
   {{
     "key_concepts[y]name": '...["items"][y]conceptual/concept["title"]'
   }}

   Explication: TOUS utilisent le même template "conceptual/concept" à ["items"][y]

Étape 4: VALIDE que tous les ["champs"] utilisés existent dans "Usage des champs" des templates

Étape 5: VALIDE que les chemins ne se terminent PAS par un simple champ sans template de contenu final
   - Si un chemin se termine par ["champ"] sans template de contenu, AJOUTE un template approprié
   - ❌ INVALIDE: tableaux/ligne_cle_valeur["value"]
   - ✅ VALIDE: tableaux/ligne_cle_valeur["value"]text/titre["text"]
   - ❌ INVALIDE: layouts/horizontal_line/item["title"]
   - ✅ VALIDE: layouts/horizontal_line/item["title"]text/titre["text"]

Étape 6: Génère le JSON CORRIGÉ complet

RETOURNE UNIQUEMENT le JSON, sans explication:""",
                ),
            ]
        )

        # Créer la chaîne LLM avec parser JSON
        # Utiliser le correction_llm (O3-mini) au lieu de llm (Haiku) pour plus de puissance de raisonnement
        parser = JsonOutputParser()
        chain = correction_prompt | self.correction_llm | parser

        # Appeler le LLM
        corrected_result = chain.invoke(
            {
                "invalid_mappings": invalid_mappings_formatted,
                "errors": errors_formatted,
                "templates": templates_formatted,
                "source_paths": source_paths_formatted,
                "context": context_description or "Aucun contexte spécifique fourni",
            }
        )

        return corrected_result

    def _convert_indices_to_variables(
        self, path_with_indices: str
    ) -> tuple[str, dict[str, int]]:
        """
        Convertit un chemin avec indices réels en chemin avec variables et retourne le mapping.

        Args:
            path_with_indices: Chemin avec indices réels (ex: "course_sections[0]lessons[1]title")

        Returns:
            Tuple (chemin_avec_variables, mapping_variables)
            Ex: ("course_sections[x]lessons[y]title", {x: 0, y: 1})
        """
        import re

        # Variables pour les niveaux d'imbrication
        array_vars = ["x", "y", "z", "w", "v", "u", "t", "s", "r", "q"]

        # Extraire tous les indices avec leur position
        indices = []
        pattern = r"\[(\d+)\]"
        for match in re.finditer(pattern, path_with_indices):
            indices.append(int(match.group(1)))

        # Créer le mapping {variable: indice}
        var_mapping = {}
        for i, idx in enumerate(indices):
            if i < len(array_vars):
                var_mapping[array_vars[i]] = idx

        # Remplacer les indices par des variables dans le chemin
        path_with_vars = path_with_indices
        for i, var in enumerate(array_vars[: len(indices)]):
            # Remplacer le premier [nombre] trouvé par [variable]
            path_with_vars = re.sub(r"\[\d+\]", f"[{var}]", path_with_vars, count=1)

        return path_with_vars, var_mapping

    def _substitute_variables_in_destination(
        self, destination_path: str, var_mapping: dict[str, int]
    ) -> str:
        """
        Substitue les variables dans un chemin de destination par leurs valeurs réelles.

        Args:
            destination_path: Chemin avec variables (ex: "container[\"items\"][x]concept[\"title\"]")
            var_mapping: Mapping des variables vers indices (ex: {x: 0, y: 1})

        Returns:
            Chemin avec indices substitués (ex: "container[\"items\"][0]concept[\"title\"]")
        """
        import re

        result = destination_path
        for var, idx in var_mapping.items():
            # Remplacer [variable] par [indice]
            result = re.sub(rf"\[{var}\]", f"[{idx}]", result)

        return result

    def _get_value_from_path(self, data: Any, path: str) -> Any:
        """
        Récupère une valeur dans un JSON en suivant un chemin.

        Args:
            data: Le JSON source
            path: Chemin avec indices (ex: "course_sections[0]lessons[1]title")

        Returns:
            La valeur trouvée
        """
        import re

        # Séparer le chemin en segments
        # Ex: "course_sections[0]lessons[1]title" → ["course_sections", "[0]", "lessons", "[1]", "title"]
        segments = re.split(r"(->|\[\d+\])", path)
        segments = [s for s in segments if s and s != "->"]

        current = data
        for segment in segments:
            if segment.startswith("[") and segment.endswith("]"):
                # C'est un index de tableau
                idx = int(segment[1:-1])
                current = current[idx]
            else:
                # C'est une clé d'objet
                current = current[segment]

        return current

    def _parse_destination_path(self, destination_path: str) -> List[Dict[str, Any]]:
        """
        Parse un chemin de destination en segments structurés.

        Args:
            destination_path: Chemin de destination (ex: "layouts/vertical_column/container[\"items\"][0]conceptual/concept[\"title\"]")

        Returns:
            Liste de segments avec leur type et valeur
            Ex: [
                {"type": "template", "value": "layouts/vertical_column/container"},
                {"type": "field", "value": "items"},
                {"type": "index", "value": 0},
                {"type": "template", "value": "conceptual/concept"},
                {"type": "field", "value": "title"}
            ]
        """
        import re

        segments = []

        # Pattern pour détecter les différents éléments
        # 1. Template name: commence par une lettre et contient des /
        # 2. Field access: ["nom_du_champ"]
        # 3. Array index: [nombre]

        # On va scanner le chemin caractère par caractère
        i = 0
        while i < len(destination_path):
            # Vérifier si on a un field access ["..."]
            if destination_path[i : i + 2] == '["':
                # Trouver la fin du field name
                end_quote = destination_path.find('"]', i + 2)
                if end_quote != -1:
                    field_name = destination_path[i + 2 : end_quote]
                    segments.append({"type": "field", "value": field_name})
                    i = end_quote + 2
                    continue

            # Vérifier si on a un array index [nombre] ou [variable]
            if (
                destination_path[i] == "["
                and i + 1 < len(destination_path)
                and (destination_path[i + 1].isdigit() or destination_path[i + 1].isalpha())
            ):
                # Trouver la fin de l'index
                end_bracket = destination_path.find("]", i + 1)
                if end_bracket != -1:
                    index_str = destination_path[i + 1 : end_bracket]
                    # Si c'est un nombre, convertir en int, sinon garder comme string (variable)
                    if index_str.isdigit():
                        segments.append({"type": "index", "value": int(index_str)})
                    else:
                        # C'est une variable (x, y, z, etc.)
                        segments.append({"type": "index", "value": index_str})
                    i = end_bracket + 1
                    continue

            # Sinon, c'est un template name
            # Trouver la fin du template name (jusqu'au prochain [ ou fin)
            template_name = ""
            start = i
            while i < len(destination_path) and destination_path[i] != "[":
                i += 1

            template_name = destination_path[start:i]
            if template_name:
                segments.append({"type": "template", "value": template_name})

        return segments

    def _build_final_json(
        self,
        source_json: Dict[str, Any],
        destination_mappings: Dict[str, str],
        json_paths_with_indices: List[str],
    ) -> Dict[str, Any]:
        """
        Construit le JSON final en utilisant les mappings de destination.

        Args:
            source_json: Le JSON source contenant les données
            destination_mappings: Mappings source (avec variables) → destination
            json_paths_with_indices: Liste de tous les chemins source avec indices réels

        Returns:
            Le JSON final structuré avec les templates
        """
        result = {}

        for path_source in json_paths_with_indices:
            # 1. Convertir le chemin avec indices en chemin avec variables
            path_with_vars, var_mapping = self._convert_indices_to_variables(
                path_source
            )

            # 2. Trouver le chemin de destination correspondant
            if path_with_vars not in destination_mappings:
                # Pas de mapping pour ce chemin, on l'ignore
                continue

            destination_path = destination_mappings[path_with_vars]

            # 3. Substituer les variables dans le chemin de destination
            final_destination = self._substitute_variables_in_destination(
                destination_path, var_mapping
            )

            # 4. Récupérer la valeur source
            source_value = self._get_value_from_path(source_json, path_source)

            # 5. Parser le chemin de destination
            segments = self._parse_destination_path(final_destination)

            # 6. Construire la structure et insérer la valeur
            try:
                self._insert_value_in_structure(result, segments, source_value)
            except Exception as e:
                # Ajouter du contexte à l'erreur
                raise ValueError(
                    f"Error inserting value for path '{path_source}' -> '{final_destination}': {str(e)}"
                ) from e

        return result

    def _insert_value_in_structure(
        self, root: Dict[str, Any], segments: List[Dict[str, Any]], value: Any
    ):
        """
        Insère une valeur dans la structure JSON en suivant les segments du chemin.

        Cette fonction navigue ou crée la structure selon les segments et insère la valeur finale.

        Args:
            root: Le dictionnaire racine où insérer
            segments: Liste des segments du chemin (template, field, index)
            value: La valeur à insérer à la fin du chemin
        """
        current = root

        for i, segment in enumerate(segments):
            seg_type = segment["type"]
            seg_value = segment["value"]

            # Déterminer si c'est le dernier segment
            is_last = i == len(segments) - 1

            if seg_type == "template":
                # Un template doit être ajouté comme template_name
                # On doit vérifier le segment suivant pour savoir comment structurer

                if is_last:
                    # Le template est la dernière chose, donc la valeur va directement dedans
                    # On crée un objet avec template_name
                    if not isinstance(current, dict):
                        raise ValueError(f"Expected dict but got {type(current)}")

                    # Si current est vide ou n'a pas de template_name, on l'ajoute
                    if "template_name" not in current:
                        current["template_name"] = seg_value
                else:
                    # Il y a d'autres segments après, on doit déterminer la structure
                    next_seg = segments[i + 1]

                    if next_seg["type"] == "field":
                        # Le template est suivi d'un field, on crée la structure
                        # Si current n'a pas encore de template_name, on l'ajoute
                        if "template_name" not in current:
                            current["template_name"] = seg_value
                        elif current["template_name"] != seg_value:
                            # AVERTISSEMENT: on essaie d'insérer un template différent au même endroit
                            import warnings
                            warnings.warn(
                                f"\n⚠️  TEMPLATE CONFLICT lors de l'insertion:\n"
                                f"  Template existant: '{current['template_name']}'\n"
                                f"  Template à insérer: '{seg_value}'\n"
                                f"  Segment actuel: {i}/{len(segments)-1}\n"
                                f"  Ceci causera un écrasement de données!\n"
                                f"  Vérifiez les destination_mappings pour éviter les chevauchements.\n"
                            )
                        # On continue, le prochain segment gérera le field

                    elif next_seg["type"] == "template":
                        # Deux templates consécutifs: le premier est un wrapper
                        # On ne fait rien, le prochain segment gérera
                        if "template_name" not in current:
                            current["template_name"] = seg_value
                        elif current["template_name"] != seg_value:
                            import warnings
                            warnings.warn(
                                f"\n⚠️  TEMPLATE CONFLICT lors de l'insertion:\n"
                                f"  Template existant: '{current['template_name']}'\n"
                                f"  Template à insérer: '{seg_value}'\n"
                                f"  Segment actuel: {i}/{len(segments)-1}\n"
                                f"  Ceci causera un écrasement de données!\n"
                            )

            elif seg_type == "field":
                # Accès à un champ
                field_name = seg_value

                # Vérifier que current est bien un dict
                if not isinstance(current, dict):
                    raise ValueError(
                        f"Cannot access field '{field_name}' on non-dict type {type(current).__name__}"
                    )

                # Créer le champ s'il n'existe pas
                if field_name not in current:
                    # Déterminer le type à créer en regardant le segment suivant
                    if not is_last:
                        next_seg = segments[i + 1]
                        if next_seg["type"] == "index":
                            # Le prochain est un index, donc on crée un tableau
                            current[field_name] = []
                        else:
                            # Sinon un objet
                            current[field_name] = {}
                    else:
                        # Dernier segment: on met la valeur directement
                        current[field_name] = self._process_value(value)
                        return
                elif not is_last:
                    # Le champ existe déjà, vérifier qu'on peut naviguer dedans
                    existing_value = current[field_name]
                    next_seg = segments[i + 1]

                    # Si le prochain segment est un index, on s'attend à une liste
                    if next_seg["type"] == "index" and not isinstance(
                        existing_value, list
                    ):
                        raise ValueError(
                            f"Field '{field_name}' exists but is not a list (found {type(existing_value).__name__})"
                        )

                    # Si le prochain segment est un field ou template, on s'attend à un dict
                    if next_seg["type"] in ("field", "template") and not isinstance(
                        existing_value, dict
                    ):
                        raise ValueError(
                            f"Field '{field_name}' exists but is not a dict (found {type(existing_value).__name__})"
                        )

                # Naviguer vers ce champ
                current = current[field_name]

            elif seg_type == "index":
                # Accès à un index de tableau
                idx = seg_value

                # S'assurer que current est un tableau
                if not isinstance(current, list):
                    raise ValueError(
                        f"Expected list but got {type(current)} for index {idx}"
                    )

                # Étendre le tableau si nécessaire
                while len(current) <= idx:
                    current.append({})

                # Naviguer vers cet index
                current = current[idx]

        # Si on arrive ici et qu'on n'a pas encore inséré la valeur, c'est qu'on doit l'insérer maintenant
        # Cela arrive quand le dernier segment est un template
        # Dans ce cas, on suppose que la valeur va dans un champ par défaut ou remplace le dict
        # Pour simplifier, on va ajouter la valeur comme contenu si c'est pertinent
        # Mais en général, cela ne devrait pas arriver avec notre structure

    def _process_value(self, value: Any) -> Any:
        """
        Traite une valeur avant de l'insérer dans la structure finale.

        Si la valeur est un objet ou un tableau complexe, cette fonction
        la copie profondément pour éviter les références partagées.

        Args:
            value: La valeur à traiter (peut être primitif, dict, list, etc.)

        Returns:
            La valeur traitée, prête à être insérée
        """
        import copy

        # Pour les types primitifs (str, int, float, bool, None), on retourne tel quel
        if isinstance(value, (str, int, float, bool, type(None))):
            return value

        # Pour les objets et tableaux, on fait une copie profonde
        # pour éviter les références partagées qui pourraient causer des problèmes
        return copy.deepcopy(value)
