from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sentence_transformers import SentenceTransformer
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
import asyncio

from app.utils.template_search import fetch_similar_templates
from app.utils.structure_process import extract_json_structure, create_embedding_packets
from app.chains.llm.claude_haiku_45_llm import ClaudeHaiku45Llm
from app.chains.llm.open_ai_o3_mini_llm import OpenAiO3MiniLlm
from app.validation.path_group_validator import validate_path_groups
from app.utils.test import shit_path_group


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

    async def generate_template_structure(
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
        template_structure, prompt, destination_mappings, debug_info = (
            await self._generate_structure_with_llm(
                source_json, templates, context_description
            )
        )

        return {
            "template_structure": template_structure,
            "prompt": prompt,
            "destination_mappings": destination_mappings,
            "debug_info": debug_info,
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

    def _get_sample_values_for_path(self, path_with_vars: str, path_to_value_map: Dict[str, Any]) -> List[Any]:
        """
        Récupère des échantillons de valeurs pour un chemin avec variables [x], [y], [z].

        Args:
            path_with_vars: Chemin avec variables génériques (ex: "items[x]->name")
            path_to_value_map: Map des chemins concrets vers valeurs (ex: {"items[0]->name": "A", "items[1]->name": "B"})

        Returns:
            Liste d'échantillons de valeurs (max 3 exemples)

        Exemple:
            Input: "items[x]->name", {"items[0]->name": "A", "items[1]->name": "B", "items[2]->name": "C"}
            Output: ["A", "B", "C"]
        """
        import re

        # Échapper les caractères spéciaux regex sauf [x], [y], [z]
        # Remplacer [x] par un pattern qui match [0], [1], [2], etc.
        pattern = path_with_vars
        pattern = pattern.replace("->", "->")  # Garder tel quel
        pattern = re.escape(pattern)  # Échapper tout
        # Puis déséchapper et remplacer les variables
        pattern = pattern.replace(r"\[x\]", r"\[\d+\]")
        pattern = pattern.replace(r"\[y\]", r"\[\d+\]")
        pattern = pattern.replace(r"\[z\]", r"\[\d+\]")

        # Compiler le pattern
        regex = re.compile(f"^{pattern}$")

        # Trouver tous les chemins concrets qui matchent
        matching_values = []
        for concrete_path, value in path_to_value_map.items():
            if regex.match(concrete_path):
                matching_values.append(value)
                if len(matching_values) >= 3:  # Limiter à 3 exemples
                    break

        return matching_values

    def _build_json_generation_prompt(
        self,
        group: Dict[str, Any],
        templates: List[Dict[str, Any]],
        path_to_value_map: Dict[str, Any],
    ) -> tuple[ChatPromptTemplate, dict]:
        """
        Construit le prompt et les paramètres pour la génération de JSON à partir d'un groupe.

        Args:
            group: Un groupe de chemins avec format
            templates: Templates récupérés par embedding pour ce groupe
            path_to_value_map: Dictionnaire {chemin_concret: valeur} pour fournir des exemples

        Returns:
            Tuple (prompt, params) pour l'invocation du LLM
        """
        # Formater les templates pour le prompt
        templates_formatted = self._format_templates_for_prompt(templates)

        # Formater les chemins source avec des exemples de valeurs
        source_paths_lines = []
        for path in group["keys"]:
            # Récupérer des échantillons de valeurs pour ce chemin
            sample_values = self._get_sample_values_for_path(path, path_to_value_map)

            if sample_values:
                # Formater les exemples (max 3)
                examples_str = ", ".join([f'"{v}"' if isinstance(v, str) else str(v) for v in sample_values[:3]])
                source_paths_lines.append(f"  - {path}  (exemples: {examples_str})")
            else:
                # Pas d'exemples trouvés (peut arriver pour des chemins intermédiaires)
                source_paths_lines.append(f"  - {path}")

        source_paths_formatted = "\n".join(source_paths_lines)

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
- Des références aux données source au format {{{{chemin}}}} (ex: {{{{conjugation_patterns[x]->group}}}})

EXEMPLE DE SORTIE ATTENDUE:
{{
  "template_name": "XXXX",
  "items": [
    {{
      "template_name": "XXXX",
      "title": "XXXX",
      "content": "{{{{XXXX[x]->XXXX}}}}"
    }},
    {{
      "template_name": "XXXX",
      "title": "XXXX",
      "content": {{
        "template_name": "XXXX",
        "title": "XXXX {{{{XXXX[x]->XXXX}}}}",
        "description": "{{{{XXXX[x]->XXXX->XXXX}}}}"
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
     * Une référence {{{{chemin}}}} (pour les valeurs primitives)
     * Un objet avec template_name (pour imbriquer des templates)
     * Un tableau d'objets avec template_name
     * Une string

3. **Références aux données**:
   - Utilise la notation {{{{chemin}}}} pour référencer les données source
   - TOUJOURS utiliser le séparateur -> entre les parties du chemin
   - ⚠️ RÈGLE CRITIQUE pour les variables de tableau:
     * ✅ TOUJOURS utiliser les variables génériques [x], [y], [z] exactement comme dans les chemins source
     * ❌ N'utilise JAMAIS d'indices numériques [0], [1], [2], etc.
     * Si le chemin source est "media->videos[x]->label", tu DOIS écrire {{{{media->videos[x]->label}}}}
     * ❌ INTERDIT: {{{{media->videos[0]->label}}}}, {{{{media->videos[1]->label}}}}
   - ⚠️ RÈGLE CRITIQUE pour le suffixe * (références INTERMÉDIAIRES):
     * Si un chemin se termine par *, c'est une référence INTERMÉDIAIRE (contient des sous-propriétés)
     * ❌ N'utilise JAMAIS une référence * seule dans le JSON
     * ✅ Tu DOIS utiliser les sous-propriétés qui suivent
     * Exemple: Si "themes[x]*" est dans les chemins, utilise "themes[x]->label", "themes[x]->description", etc.
     * ❌ INTERDIT: "items": "{{{{themes[x]}}}}" (référence intermédiaire utilisée seule)
     * ✅ CORRECT: "title": "{{{{themes[x]->label}}}}" (sous-propriété utilisée)
   - Exemples CORRECTS:
     * {{{{course}}}} (sans variable)
     * {{{{media->videos[x]->label}}}} (avec variable [x] - CORRECT)
     * {{{{themes[x]->groups[y]->label}}}} (avec variables [x] et [y] - CORRECT)
   - Exemples INCORRECTS (à NE JAMAIS faire):
     * {{{{media->videos[0]->label}}}} ❌ (utilise [x] pas [0])
     * {{{{themes[0]->groups[1]->label}}}} ❌ (utilise [x] et [y] pas [0] et [1])
     * {{{{themes[x]}}}} ❌ si themes[x]* est marqué comme intermédiaire (utilise les sous-propriétés)

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

Chemins source disponibles pour les références {{{{chemin}}}}:
{source_paths}

{special_instructions}

⚠️ RAPPEL IMPORTANT: Utilise UNIQUEMENT les chemins ci-dessus avec leurs variables [x], [y], [z] EXACTEMENT comme indiqué.
N'utilise JAMAIS d'indices numériques [0], [1], [2] dans tes références.

Génère maintenant le JSON structuré.""",
                ),
            ]
        )

        # Ajouter des instructions spéciales pour les groupes de référence pure
        special_instructions = ""
        if group.get("is_reference_only", False):
            special_instructions = """
⚠️ ATTENTION SPÉCIALE: Ce groupe contient UNIQUEMENT une référence (ex: glossary[x], themes[x]).

RÈGLE CRITIQUE:
- Tu DOIS utiliser la référence EXACTEMENT comme fournie, SANS ajouter de propriétés
- ❌ N'invente PAS de propriétés après la référence (comme ->term, ->definition, ->label, etc.)
- ✅ Utilise SEULEMENT la référence telle quelle

Exemple CORRECT pour glossary[x]:
{
  "template_name": "layouts/vertical_column/container",
  "items": "{{glossary[x]}}"
}

Exemple INCORRECT (à NE JAMAIS faire):
{
  "template_name": "text/definition",
  "term": "{{glossary[x]->term}}",  ❌ N'invente PAS de propriétés!
  "definition": "{{glossary[x]->definition}}"
}
"""

        params = {
            "group_name": group["group_name"],
            "format_description": group["format"],
            "templates": templates_formatted,
            "source_paths": source_paths_formatted,
            "special_instructions": special_instructions,
        }

        return prompt, params

    async def _generate_json_from_group_async(
        self,
        group: Dict[str, Any],
        templates: List[Dict[str, Any]],
        path_to_value_map: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Génère le JSON structuré pour un groupe en utilisant les templates récupérés par embedding (version async).

        Args:
            group: Un groupe de chemins avec format (output de _generate_path_groups_with_llm)
            templates: Templates récupérés par embedding pour ce groupe
            path_to_value_map: Dictionnaire {chemin_concret: valeur} pour fournir des exemples au LLM

        Returns:
            Dictionnaire contenant:
                - "json": JSON structuré avec template_name et références {{{{chemin}}}}
                - "prompt": Le prompt formaté envoyé au LLM pour générer ce JSON
        """
        prompt, params = self._build_json_generation_prompt(group, templates, path_to_value_map)

        # Créer la chaîne LLM avec parser JSON
        parser = JsonOutputParser()
        chain = prompt | self.llm | parser

        # Appeler le LLM de manière asynchrone
        result = await chain.ainvoke(params)

        # VALIDATION: Vérifier que le LLM n'a pas inventé de clés fictives
        self._validate_group_json_references(result, group)

        # Formater le prompt pour le retourner
        formatted_prompt = prompt.format(**params)

        return {
            "json": result,
            "prompt": formatted_prompt
        }

    def _generate_json_from_group(
        self,
        group: Dict[str, Any],
        templates: List[Dict[str, Any]],
        path_to_value_map: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Génère le JSON structuré pour un groupe en utilisant les templates récupérés par embedding (version sync).

        Args:
            group: Un groupe de chemins avec format (output de _generate_path_groups_with_llm)
            templates: Templates récupérés par embedding pour ce groupe
            path_to_value_map: Dictionnaire {chemin_concret: valeur} pour fournir des exemples au LLM

        Returns:
            Dictionnaire contenant:
                - "json": JSON structuré avec template_name et références {{{{chemin}}}}
                - "prompt": Le prompt formaté envoyé au LLM pour générer ce JSON
        """
        # Utiliser la version async via asyncio.run
        return asyncio.run(self._generate_json_from_group_async(group, templates, path_to_value_map))

    def _add_missing_nested_references(
        self,
        path_groups: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Ajoute automatiquement les références manquantes pour les groupes imbriqués.

        Logique :
        1. Pour chaque groupe avec variables (ex: themes[x]examples[y]...),
           trouver ou créer un groupe parent avec une variable de moins (ex: themes[x]...)
           et y ajouter la référence (ex: themes[x]examples[y])

        2. Pour chaque groupe avec une variable (ex: glossary[x]...),
           trouver ou créer un groupe racine sans variable
           et y ajouter la référence (ex: glossary[x])
        """
        import re

        # Étape 1: Extraire toutes les références nécessaires et leurs préfixes parents
        references_to_add = {}  # {parent_prefix: [child_refs]}

        for group in path_groups:
            # Extraire la référence de ce groupe (jusqu'à la dernière variable)
            child_ref = self._extract_child_reference(group["keys"])

            if child_ref:
                # Trouver le préfixe parent (une variable de moins)
                parent_prefix = self._get_parent_prefix(child_ref)

                if parent_prefix not in references_to_add:
                    references_to_add[parent_prefix] = []
                if child_ref not in references_to_add[parent_prefix]:
                    references_to_add[parent_prefix].append(child_ref)

        # Étape 2: Pour chaque préfixe parent, trouver le groupe approprié ou le créer
        new_groups = []
        all_groups = path_groups.copy()

        for parent_prefix, child_refs in references_to_add.items():
            # Chercher un groupe existant qui correspond au parent
            parent_group = self._find_group_by_prefix(all_groups, parent_prefix)

            if parent_group:
                # Ajouter les références si elles n'existent pas déjà
                for child_ref in child_refs:
                    if child_ref not in parent_group["keys"]:
                        parent_group["keys"].append(child_ref)
            else:
                # Créer un nouveau groupe parent
                new_group = self._create_parent_group(parent_prefix, child_refs, all_groups)
                new_groups.append(new_group)
                all_groups.append(new_group)

        # Étape 3: Fusionner les nouveaux groupes
        result_groups = path_groups + new_groups

        # Étape 4: Gérer les cas spéciaux (regrouper les groupes frères comme media->images et media->videos)
        result_groups = self._merge_sibling_media_groups(result_groups)

        # Étape 5: Nettoyer et séparer les groupes par profondeur
        result_groups = self._clean_and_separate_groups_by_depth(result_groups)

        return result_groups

    def _clean_and_separate_groups_by_depth(
        self,
        groups: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Nettoie les groupes en séparant les clés par profondeur (nombre de variables).

        Problèmes corrigés:
        1. Les clés sans variable qui sont dans des groupes avec variables sont déplacées
           vers les groupes parents appropriés
        2. Les groupes qui mélangent des clés avec différentes profondeurs sont divisés

        Args:
            groups: Liste des groupes à nettoyer

        Returns:
            Liste des groupes nettoyés et réorganisés
        """
        import re

        new_groups = []

        for group in groups:
            # Grouper les clés par profondeur (nombre de variables)
            depth_map = {}  # {depth: [keys]}

            for key in group["keys"]:
                # Compter le nombre de variables dans la clé
                num_vars = len(re.findall(r'\[([x-z])\]', key))

                if num_vars not in depth_map:
                    depth_map[num_vars] = []
                depth_map[num_vars].append(key)

            # Si toutes les clés ont la même profondeur, garder le groupe tel quel
            if len(depth_map) == 1:
                new_groups.append(group)
                continue

            # Sinon, diviser le groupe en plusieurs groupes par profondeur
            for depth, keys in sorted(depth_map.items()):
                if not keys:
                    continue

                # Créer un nouveau groupe pour cette profondeur
                new_group = {
                    "group_name": self._generate_group_name_for_depth(group["group_name"], depth, keys[0]),
                    "keys": keys,
                    "format": self._generate_format_for_depth(group["format"], depth)
                }
                new_groups.append(new_group)

        # Étape 2: Déplacer les clés sans variable vers les groupes parents appropriés
        new_groups = self._move_no_var_keys_to_parents(new_groups)

        # Étape 3: Fusionner les groupes dupliqués (même nom et même profondeur)
        new_groups = self._merge_duplicate_groups(new_groups)

        return new_groups

    def _merge_duplicate_groups(
        self,
        groups: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Fusionne les groupes qui ont le même nom de base et la même profondeur.

        Args:
            groups: Liste des groupes

        Returns:
            Liste des groupes fusionnés
        """
        import re

        # Grouper par (nom_base, profondeur)
        group_map = {}  # {(nom_base, profondeur): [groupes]}

        for group in groups:
            # Calculer la profondeur du groupe
            if group["keys"]:
                num_vars = len(re.findall(r'\[([x-z])\]', group["keys"][0]))
            else:
                num_vars = 0

            # Utiliser le nom du groupe comme clé
            key = (group["group_name"], num_vars)

            if key not in group_map:
                group_map[key] = []
            group_map[key].append(group)

        # Fusionner les groupes dupliqués
        merged_groups = []

        for (name, _depth), group_list in group_map.items():
            if len(group_list) == 1:
                # Pas de duplication
                merged_groups.append(group_list[0])
            else:
                # Fusionner les clés
                merged_keys = []
                merged_format = group_list[0]["format"]

                for g in group_list:
                    for key in g["keys"]:
                        if key not in merged_keys:
                            merged_keys.append(key)

                merged_group = {
                    "group_name": name,
                    "keys": merged_keys,
                    "format": merged_format
                }
                merged_groups.append(merged_group)

        return merged_groups

    def _generate_group_name_for_depth(
        self,
        original_name: str,
        depth: int,
        sample_key: str
    ) -> str:
        """
        Génère un nom de groupe basé sur la profondeur.

        Args:
            original_name: Nom original du groupe
            depth: Profondeur (nombre de variables)
            sample_key: Exemple de clé pour extraire le contexte

        Returns:
            Nouveau nom de groupe
        """
        import re

        if depth == 0:
            # Pas de variable, c'est un groupe parent
            # Extraire le préfixe de la clé
            prefix = sample_key.split('->')[0] if '->' in sample_key else sample_key
            return f"Groupe {prefix.title()}"

        # Garder le nom original pour les groupes avec variables
        return original_name

    def _generate_format_for_depth(
        self,
        original_format: str,
        depth: int
    ) -> str:
        """
        Génère une description de format basée sur la profondeur.

        Args:
            original_format: Format original
            depth: Profondeur (nombre de variables)

        Returns:
            Nouveau format
        """
        if depth == 0:
            return "Groupe parent sans variable de tableau"

        return original_format

    def _move_no_var_keys_to_parents(
        self,
        groups: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Déplace les clés sans variable vers les groupes parents appropriés.

        Exemple: "examplesCollection->purpose" doit être déplacé vers
        le groupe parent "Groupe Examplescollection" qui contient "examplesCollection->examples[x]"

        Args:
            groups: Liste des groupes

        Returns:
            Liste des groupes avec les clés déplacées
        """
        import re

        # Identifier les clés sans variable qui devraient être déplacées
        keys_to_move = {}  # {key: source_group}
        parent_prefixes = {}  # {prefix: parent_group}

        # Étape 1: Identifier tous les groupes parents (qui contiennent des références)
        for group in groups:
            for key in group["keys"]:
                # Si c'est une référence (se termine par une variable)
                if re.search(r'\[([x-z])\]$', key):
                    # Extraire le préfixe parent
                    prefix = self._get_parent_prefix(key)
                    if prefix and prefix not in parent_prefixes:
                        # Chercher ou créer le groupe parent pour ce préfixe
                        parent_group = self._find_or_create_parent_group_for_prefix(groups, prefix)
                        if parent_group:
                            parent_prefixes[prefix] = parent_group

        # Étape 2: Identifier les clés sans variable qui devraient être dans des groupes parents
        for group in groups:
            keys_to_remove = []

            for key in group["keys"]:
                # Si la clé n'a pas de variable
                num_vars = len(re.findall(r'\[([x-z])\]', key))

                if num_vars == 0:
                    # Vérifier si cette clé a un groupe parent approprié
                    # Extraire le préfixe de la clé (avant le dernier ->)
                    if '->' in key:
                        prefix = key.rsplit('->', 1)[0]
                    else:
                        prefix = key

                    # Vérifier si un groupe parent existe pour ce préfixe
                    if prefix in parent_prefixes:
                        target_group = parent_prefixes[prefix]

                        # Vérifier que ce n'est pas déjà le bon groupe
                        if target_group != group:
                            # Marquer pour déplacement
                            if key not in target_group["keys"]:
                                target_group["keys"].append(key)
                            keys_to_remove.append(key)

            # Supprimer les clés qui ont été déplacées
            for key in keys_to_remove:
                group["keys"].remove(key)

        # Étape 3: Supprimer les groupes vides
        groups = [g for g in groups if g["keys"]]

        return groups

    def _find_or_create_parent_group_for_prefix(
        self,
        groups: List[Dict[str, Any]],
        prefix: str
    ) -> Dict[str, Any]:
        """
        Trouve ou crée un groupe parent pour un préfixe donné.

        Args:
            groups: Liste des groupes
            prefix: Préfixe à chercher

        Returns:
            Le groupe parent trouvé ou None
        """
        import re

        # Chercher un groupe qui contient ce préfixe sans variable
        for group in groups:
            for key in group["keys"]:
                if key == prefix or key.startswith(prefix + '->'):
                    # Vérifier que cette clé n'a pas de variable
                    if not re.search(r'\[([x-z])\]', key):
                        return group

        return None

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

    def _get_parent_prefix(self, child_ref: str) -> str:
        """
        Extrait le préfixe parent d'une référence enfant (une variable de moins).

        Exemples:
        - "themes[x]examples[y]" → "themes[x]"
        - "glossary[x]" → "" (pas de parent avec variable)
        - "examplesCollection->examples[x]" → "examplesCollection"

        Args:
            child_ref: Référence enfant (ex: "themes[x]examples[y]")

        Returns:
            Préfixe parent ou chaîne vide si pas de parent
        """
        import re

        # Trouver toutes les variables dans la référence
        vars_matches = list(re.finditer(r'\[([x-z])\]', child_ref))

        if not vars_matches:
            return ""

        if len(vars_matches) == 1:
            # Une seule variable, le parent n'a pas de variable
            # Retourner tout ce qui est avant la variable
            first_var = vars_matches[0]
            parent = child_ref[:first_var.start()]

            # Enlever la dernière partie après -> si présent
            # Ex: "media->images" → "media", "examplesCollection->examples" → "examplesCollection"
            if '->' in parent:
                parent = parent.rsplit('->', 1)[0]

            return parent

        # Plus d'une variable, retourner jusqu'à l'avant-dernière variable (incluse)
        second_to_last_var = vars_matches[-2]
        return child_ref[:second_to_last_var.end()]

    def _find_group_by_prefix(
        self,
        groups: List[Dict[str, Any]],
        prefix: str
    ) -> Dict[str, Any]:
        """
        Trouve un groupe dont les clés correspondent au préfixe donné.

        Args:
            groups: Liste des groupes
            prefix: Préfixe à chercher (ex: "themes[x]" ou "examplesCollection")

        Returns:
            Le groupe correspondant ou None
        """
        import re

        # Cas spécial: préfixe vide (groupes racine sans variable)
        if not prefix:
            return None

        # Vérifier si le préfixe contient des variables
        has_vars = bool(re.search(r'\[([x-z])\]', prefix))

        for group in groups:
            if not group["keys"]:
                continue

            first_key = group["keys"][0]

            if has_vars:
                # Le préfixe a des variables, chercher un groupe dont les clés commencent par ce préfixe
                # et qui ont exactement le même nombre de variables
                if first_key.startswith(prefix):
                    # Vérifier que first_key a le même nombre de variables que prefix
                    prefix_vars = len(re.findall(r'\[([x-z])\]', prefix))
                    key_vars = len(re.findall(r'\[([x-z])\]', first_key))
                    if prefix_vars == key_vars:
                        return group
            else:
                # Le préfixe n'a pas de variables, chercher un groupe avec ce préfixe sans variables
                if first_key.startswith(prefix) and not re.search(r'\[([x-z])\]', first_key):
                    return group

        return None

    def _create_parent_group(
        self,
        parent_prefix: str,
        child_refs: List[str],
        existing_groups: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Crée un nouveau groupe parent pour contenir les références enfants.

        Args:
            parent_prefix: Préfixe du groupe parent (ex: "themes[x]" ou "examplesCollection")
            child_refs: Références enfants à ajouter (ex: ["themes[x]examples[y]", "themes[x]groups[y]"])
            existing_groups: Groupes existants pour chercher d'autres clés liées

        Returns:
            Nouveau groupe parent
        """
        import re

        # Collecter toutes les clés qui devraient faire partie de ce groupe parent
        parent_keys = []

        # Ajouter les références enfants
        parent_keys.extend(child_refs)

        # Chercher d'autres clés dans les groupes existants qui correspondent au préfixe parent
        has_vars = bool(re.search(r'\[([x-z])\]', parent_prefix))

        for group in existing_groups:
            for key in group["keys"]:
                if has_vars:
                    # Le parent a des variables, chercher les clés avec le même préfixe et même nombre de variables
                    if key.startswith(parent_prefix):
                        prefix_vars = len(re.findall(r'\[([x-z])\]', parent_prefix))
                        key_vars = len(re.findall(r'\[([x-z])\]', key))
                        if prefix_vars == key_vars and key not in parent_keys:
                            parent_keys.append(key)
                else:
                    # Le parent n'a pas de variables
                    if key.startswith(parent_prefix) and not re.search(r'\[([x-z])\]', key) and key not in parent_keys:
                        parent_keys.append(key)

        # Générer un nom de groupe
        group_name = self._generate_group_name(parent_prefix)

        # Générer un format générique
        format_desc = f"Groupe parent pour {parent_prefix}"

        return {
            "group_name": group_name,
            "keys": parent_keys,
            "format": format_desc
        }

    def _generate_group_name(self, prefix: str) -> str:
        """
        Génère un nom de groupe à partir d'un préfixe.

        Args:
            prefix: Préfixe (ex: "themes[x]" ou "examplesCollection")

        Returns:
            Nom de groupe lisible
        """
        import re

        # Enlever les variables
        name = re.sub(r'\[[x-z]\]', '', prefix)
        # Remplacer -> par des espaces
        name = name.replace('->', ' ')
        # Capitaliser
        name = name.strip().title()

        if not name:
            name = "Root Group"

        return f"Groupe {name}"

    def _merge_sibling_media_groups(
        self,
        groups: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Fusionne les groupes frères qui devraient être ensemble.
        Par exemple: "media->images[x]" et "media->videos[x]" dans un seul groupe "media".

        Args:
            groups: Liste des groupes

        Returns:
            Liste des groupes avec les groupes frères fusionnés
        """
        import re

        # Identifier les groupes qui ne contiennent qu'une seule référence enfant
        single_ref_groups = []
        other_groups = []

        for group in groups:
            # Vérifier si le groupe ne contient qu'une seule clé et que c'est une référence
            if len(group["keys"]) == 1:
                key = group["keys"][0]
                if re.search(r'\[([x-z])\]$', key):  # Se termine par une variable
                    single_ref_groups.append(group)
                else:
                    other_groups.append(group)
            else:
                other_groups.append(group)

        # Grouper les groupes qui ont le même préfixe parent
        prefix_map = {}  # {parent_prefix: [groups]}

        for group in single_ref_groups:
            key = group["keys"][0]
            parent_prefix = self._get_parent_prefix(key)

            if parent_prefix not in prefix_map:
                prefix_map[parent_prefix] = []
            prefix_map[parent_prefix].append(group)

        # Pour chaque préfixe avec plusieurs groupes, les fusionner
        for parent_prefix, sibling_groups in prefix_map.items():
            if len(sibling_groups) > 1:
                # Fusionner ces groupes
                merged_keys = []
                for sg in sibling_groups:
                    merged_keys.extend(sg["keys"])

                merged_group = {
                    "group_name": self._generate_group_name(parent_prefix) if parent_prefix else "Root Media Group",
                    "keys": merged_keys,
                    "format": f"Groupe parent pour {parent_prefix}" if parent_prefix else "Groupe racine"
                }
                other_groups.append(merged_group)
            else:
                # Un seul groupe, le garder tel quel
                other_groups.extend(sibling_groups)

        return other_groups

    def _resolve_group_references(
        self,
        group_jsons_map: Dict[str, Dict[str, Any]],
        path_to_value_map: Dict[str, Any],
    ) -> Dict[str, Dict[str, Any]]:
        """
        Résout les références de groupes imbriqués en remplaçant les placeholders.

        Les références de type {{chemin[x]sous_chemin[y]}} (qui se terminent par une variable)
        sont remplacées par le JSON du groupe correspondant.

        Args:
            group_jsons_map: Dictionnaire {clé_de_référence: json_du_groupe}
            path_to_value_map: Dictionnaire {chemin_concret: valeur} pour vérifier les clés nécessaires

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

        # Vérification: Extraire toutes les clés présentes dans resolved_map et comparer avec path_to_value_map
        def extract_all_keys(obj, keys_set=None):
            """Extrait toutes les clés présentes dans resolved_map (récursivement)."""
            if keys_set is None:
                keys_set = set()

            if isinstance(obj, dict):
                for key, value in obj.items():
                    if key != "items":  # Ne pas ajouter "items" comme clé
                        keys_set.add(key)
                    # Descendre récursivement même si c'est "items"
                    extract_all_keys(value, keys_set)
            elif isinstance(obj, list):
                for item in obj:
                    extract_all_keys(item, keys_set)

            return keys_set

        # Extraire toutes les clés de resolved_map
        resolved_keys = extract_all_keys(resolved_map)

        # Normaliser les clés de path_to_value_map
        required_keys = {self._normalize_path_to_generic(path) for path in path_to_value_map.keys()}

        # Trouver les clés manquantes
        missing_keys = required_keys - resolved_keys

        if missing_keys:
            print(f"⚠️  AVERTISSEMENT: {len(missing_keys)} clés manquantes dans resolved_jsons_map:")
            for key in sorted(missing_keys):
                print(f"   - {key}")
            print(f"   Total de clés requises: {len(required_keys)}")
            print(f"   Total de clés présentes: {len(resolved_keys)}")
            print(f"   Taux de couverture: {((len(required_keys) - len(missing_keys)) / len(required_keys) * 100):.1f}%")
        else:
            print(f"✅ Toutes les {len(required_keys)} clés de path_to_value_map sont présentes dans resolved_jsons_map")

        return resolved_map

    def _build_final_json_incremental(
        self,
        path_to_value_map: Dict[str, Any],
        group_jsons_map: Dict[str, Any],
        verbose: bool = True
    ) -> List[Any]:
        """
        Construit le final_json de manière incrémentale à partir de path_to_value_map et group_jsons_map.

        Args:
            path_to_value_map: Dictionnaire plat avec chemins -> valeurs
            group_jsons_map: Dictionnaire avec chemins (avec variables) -> templates JSON
            verbose: Si True, affiche les logs de progression

        Returns:
            Liste de templates JSON résolus (final_json)
        """
        import re
        import copy
        import json

        final_json = []
        templates_seen = {}  # Cache: (template_id, var_mapping_tuple) -> template_instance
        template_ids = {}    # Cache: path_with_vars -> template_id (hash du template JSON)

        total_paths = len(path_to_value_map)
        processed = 0

        if verbose:
            print(f"Total de chemins à traiter: {total_paths}\n")

        for path_with_indices, value in path_to_value_map.items():
            processed += 1

            if verbose:
                print(f"\n[{processed}/{total_paths}] Traitement: {path_with_indices}")
                print(f"  Valeur: {value if len(str(value)) < 80 else str(value)[:77] + '...'}")

            # ÉTAPE 1: Convertir indices → variables
            path_with_vars, var_mapping = self._convert_indices_to_variables(path_with_indices)

            if verbose:
                print(f"  Chemin avec variables: {path_with_vars}")
                if var_mapping:
                    print(f"  Mapping des variables: {var_mapping}")

            # ÉTAPE 2: Chercher le template correspondant
            if path_with_vars not in group_jsons_map:
                if verbose:
                    print(f"  ⊘ SKIP: Aucun template trouvé pour '{path_with_vars}'")
                continue

            template = group_jsons_map[path_with_vars]

            # ÉTAPE 2.5: Identifier le template de manière unique (par son contenu JSON)
            # Si plusieurs chemins pointent vers le même template (même structure),
            # ils doivent partager la même instance
            if path_with_vars not in template_ids:
                template_id = json.dumps(template, sort_keys=True)
                template_ids[path_with_vars] = template_id
            else:
                template_id = template_ids[path_with_vars]

            # ÉTAPE 3: Vérifier si on doit créer une nouvelle instance ou réutiliser
            # La clé de cache combine le template_id ET les indices des variables
            cache_key = (template_id, tuple(sorted(var_mapping.items())))

            if cache_key in templates_seen:
                # Réutiliser l'instance existante
                template_instance = templates_seen[cache_key]
                if verbose:
                    print(f"  ♻️  Réutilisation du template existant")
            else:
                # Créer une nouvelle instance
                template_instance = copy.deepcopy(template)
                templates_seen[cache_key] = template_instance
                final_json.append(template_instance)
                if verbose:
                    print(f"  ✓ Nouveau template créé et ajouté à final_json (position {len(final_json) - 1})")

            # ÉTAPE 4: Transformer les variables en indices réels dans les placeholders
            # On ne résout PAS les placeholders, on remplace juste x,y,z par les indices réels
            if var_mapping:
                placeholders = self._find_all_placeholders(template_instance)

                if verbose and placeholders:
                    print(f"  Placeholders trouvés: {len(placeholders)} - substitution des variables...")

                for placeholder in placeholders:
                    # Extraire le chemin du placeholder
                    placeholder_path = self._extract_placeholder_path(placeholder)

                    # Substituer les variables par les indices réels
                    resolved_path = self._substitute_variables_in_path(placeholder_path, var_mapping)

                    # Créer le nouveau placeholder avec indices réels
                    new_placeholder = "{{" + resolved_path + "}}"

                    # Remplacer l'ancien placeholder par le nouveau
                    self._replace_in_template(template_instance, placeholder, new_placeholder)

                    if verbose:
                        print(f"    • {placeholder} → {new_placeholder}")

            # ÉTAPE 4.5: Transformer tous les placeholders {{chemin}} en {-{chemin}-}
            # Récupérer tous les placeholders restants dans le template
            all_placeholders = self._find_all_placeholders(template_instance)

            if verbose and all_placeholders:
                print(f"  Transformation des placeholders {{{{chemin}}}} → {{-{{chemin}}-}}: {len(all_placeholders)} trouvés")

            for placeholder in all_placeholders:
                # Extraire le chemin du placeholder (sans les {{ }})
                placeholder_path = self._extract_placeholder_path(placeholder)

                # Créer le nouveau placeholder au format {-{chemin}-}
                new_placeholder = "{-{" + placeholder_path + "}-}"

                # Remplacer l'ancien placeholder par le nouveau
                self._replace_in_template(template_instance, placeholder, new_placeholder)

                if verbose:
                    print(f"    • {placeholder} → {new_placeholder}")

            # ÉTAPE 5: Affichage incrémental
            if verbose:
                # print(f"\n  📦 Taille actuelle de final_json: {len(final_json)} templates")
                print("\n" + "=" * 80)
                print(f"{json.dumps(final_json, indent=1, ensure_ascii=False)}")
                print("\n" + "=" * 80)

        if verbose:
            print("\n" + "=" * 80)
            print(f"✅ CONSTRUCTION TERMINÉE: {len(final_json)} templates créés")
            print("=" * 80)

        return final_json

    def _convert_indices_to_variables(self, path_with_indices: str) -> tuple:
        """
        Convertit un chemin avec indices en chemin avec variables.

        Args:
            path_with_indices: Chemin avec indices réels (ex: "themes[0]->groups[1]->label")

        Returns:
            Tuple de (chemin_avec_variables, mapping_variables)
            Ex: ("themes[x]->groups[y]->label", {"x": 0, "y": 1})
        """
        import re

        var_mapping = {}
        var_names = ['x', 'y', 'z', 'w', 'v', 'u', 't', 's', 'r', 'q']
        var_index = 0

        def replace_index(match):
            nonlocal var_index
            index_value = int(match.group(1))
            var_name = var_names[var_index]
            var_mapping[var_name] = index_value
            var_index += 1
            return f"[{var_name}]"

        # Remplacer tous les [nombre] par [variable]
        path_with_vars = re.sub(r'\[(\d+)\]', replace_index, path_with_indices)

        return path_with_vars, var_mapping

    def _find_all_placeholders(self, obj: Any) -> List[str]:
        """
        Trouve tous les placeholders {{...}} dans un objet JSON (récursif).

        Args:
            obj: Objet JSON (dict, list, str, etc.)

        Returns:
            Liste de tous les placeholders trouvés
        """
        import re

        placeholders = []

        if isinstance(obj, str):
            # Chercher tous les {{...}} dans la chaîne
            # Utilise .+? (non-greedy) pour capturer tout jusqu'à }}
            matches = re.findall(r'\{\{.+?\}\}', obj)
            placeholders.extend(matches)
        elif isinstance(obj, dict):
            for value in obj.values():
                placeholders.extend(self._find_all_placeholders(value))
        elif isinstance(obj, list):
            for item in obj:
                placeholders.extend(self._find_all_placeholders(item))

        return placeholders

    def _extract_placeholder_path(self, placeholder: str) -> str:
        """
        Extrait le chemin à l'intérieur d'un placeholder.

        Args:
            placeholder: Placeholder (ex: "{{themes[x]->groups[y]->label}}")

        Returns:
            Chemin extrait (ex: "themes[x]->groups[y]->label")
        """
        # Enlever {{ et }}
        return placeholder.strip('{}').strip()

    def _substitute_variables_in_path(self, path: str, var_mapping: Dict[str, int]) -> str:
        """
        Substitue les variables par leurs valeurs dans un chemin.

        Args:
            path: Chemin avec variables (ex: "themes[x]->groups[y]->label")
            var_mapping: Mapping des variables (ex: {"x": 0, "y": 1})

        Returns:
            Chemin avec indices réels (ex: "themes[0]->groups[1]->label")
        """
        result = path
        for var_name, index_value in var_mapping.items():
            result = result.replace(f"[{var_name}]", f"[{index_value}]")
        return result

    def _replace_in_template(self, obj: Any, placeholder: str, value: Any) -> Any:
        """
        Remplace toutes les occurrences d'un placeholder par une valeur dans un objet (récursif, in-place).

        Args:
            obj: Objet JSON à modifier
            placeholder: Placeholder à remplacer (ex: "{{themes[0]->groups[1]->label}}")
            value: Valeur de remplacement

        Returns:
            Objet modifié (modification in-place)
        """
        if isinstance(obj, str):
            # Si la chaîne EST exactement le placeholder, on retourne la valeur
            if obj == placeholder:
                return value
            # Sinon on remplace le placeholder dans la chaîne
            return obj.replace(placeholder, str(value))
        elif isinstance(obj, dict):
            for key in obj:
                obj[key] = self._replace_in_template(obj[key], placeholder, value)
        elif isinstance(obj, list):
            for i in range(len(obj)):
                obj[i] = self._replace_in_template(obj[i], placeholder, value)

        return obj

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

    def _normalize_path_to_generic(self, path: str) -> str:
        """
        Normalise un chemin avec indices réels [0], [1], [2]... vers des variables génériques [x], [y], [z].

        Args:
            path: Chemin avec indices réels, ex: "themes[0]->examples[1]->conjugation[2]->form"

        Returns:
            Chemin normalisé avec variables génériques, ex: "themes[x]examples[y]conjugation[z]form"

        Exemples:
            "glossary[0]->term" → "glossary[x]term"
            "themes[0]->examples[1]->label" → "themes[x]examples[y]label"
            "media->images[0]->url" → "media->images[x]url"
        """
        import re

        # Variables génériques dans l'ordre
        generic_vars = ['x', 'y', 'z']
        var_index = 0

        def replace_index(match):
            nonlocal var_index
            if var_index < len(generic_vars):
                replacement = f"[{generic_vars[var_index]}]"
                var_index += 1
                return replacement
            else:
                # Si on dépasse x, y, z, on continue avec des indices
                return f"[{var_index}]"

        # Remplacer tous les [0], [1], [2]... par [x], [y], [z]
        normalized = re.sub(r'\[\d+\]', replace_index, path)

        return normalized

    def _is_reference_only_group(self, group: Dict[str, Any]) -> bool:
        """
        Détermine si un groupe contient UNIQUEMENT des références à d'autres groupes,
        sans propriétés détaillées.

        Un groupe de référence pure a des clés qui sont toutes des préfixes courts
        (ex: "glossary[x]", "themes[x]", "glossary[x]*") sans propriétés après (pas de ->).
        Le suffixe * est ignoré lors de l'analyse.

        Args:
            group: Le groupe à analyser

        Returns:
            True si le groupe contient uniquement des références, False sinon

        Exemples:
            - {"keys": ["glossary[x]"]} → True (référence pure)
            - {"keys": ["themes[x]*"]} → True (référence pure, * ignoré)
            - {"keys": ["glossary[x]->term", "glossary[x]->definition"]} → False (propriétés détaillées)
            - {"keys": ["course", "topicPath"]} → False (propriétés simples)
        """
        keys = group.get("keys", [])

        if not keys:
            return False

        # Un groupe de référence pure a des clés qui:
        # 1. Contiennent au moins une variable [x], [y], ou [z]
        # 2. N'ont PAS de propriétés après la variable (pas de ->)
        # Note: Le suffixe * est ignoré (enlevé avant l'analyse)

        for key in keys:
            # Enlever le suffixe * s'il existe
            key_without_star = key.rstrip('*')

            # Si la clé contient une variable
            if '[x]' in key_without_star or '[y]' in key_without_star or '[z]' in key_without_star:
                # Vérifier s'il y a des propriétés après la dernière variable
                # Ex: "glossary[x]->term" a des propriétés, "glossary[x]" n'en a pas

                # Trouver la position de la dernière variable
                import re
                last_var_match = None
                for match in re.finditer(r'\[[xyz]\]', key_without_star):
                    last_var_match = match

                if last_var_match:
                    # Vérifier s'il y a du contenu après la dernière variable
                    after_var = key_without_star[last_var_match.end():]
                    if after_var and after_var != '':
                        # Il y a des propriétés après → pas un groupe de référence pure
                        return False
            else:
                # Clé sans variable → pas un groupe de référence pure
                return False

        # Toutes les clés sont des références pures
        return True

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

    def _validate_group_json_references(
        self,
        group_json: Dict[str, Any],
        group: Dict[str, Any]
    ) -> None:
        """
        Valide que toutes les références {{...}} dans le JSON généré par le LLM
        correspondent à des clés existantes dans le groupe.

        Affiche un warning si le LLM a inventé des clés fictives.

        Args:
            group_json: Le JSON généré par le LLM
            group: Le groupe original avec ses clés valides
        """
        # Extraire toutes les références du JSON généré
        references = self._collect_all_references(group_json)

        if not references:
            return  # Aucune référence à valider

        # Normaliser les références (enlever les -> et *)
        normalized_references = set()
        for ref in references:
            # Normaliser: enlever les -> et * pour comparaison
            normalized_ref = ref.replace("->", "").replace("*", "")
            normalized_references.add(normalized_ref)

        # Normaliser les clés du groupe ET identifier les références intermédiaires
        valid_keys = group.get("keys", [])
        normalized_valid_keys = set()
        intermediate_refs = set()  # Clés marquées avec * (références intermédiaires)

        for key in valid_keys:
            # Si la clé se termine par *, c'est une référence intermédiaire
            if key.endswith("*"):
                # Enlever le * et normaliser
                normalized_key = key[:-1].replace("->", "")
                intermediate_refs.add(normalized_key)
                normalized_valid_keys.add(normalized_key)
            else:
                # Clé normale (finale)
                normalized_key = key.replace("->", "")
                normalized_valid_keys.add(normalized_key)

        # Trouver les références fictives (utilisées mais non valides)
        fictive_refs = normalized_references - normalized_valid_keys

        # Trouver les clés manquantes (valides mais non utilisées)
        missing_refs = normalized_valid_keys - normalized_references

        # Vérifier si des références intermédiaires sont utilisées seules
        intermediate_used_alone = []
        for ref in references:
            normalized_ref = ref.replace("->", "").replace("*", "")
            if normalized_ref in intermediate_refs:
                # Cette référence est marquée comme intermédiaire mais utilisée seule
                intermediate_used_alone.append(ref)

        # Afficher les warnings
        if fictive_refs or missing_refs or intermediate_used_alone:
            print(f"\n⚠️  AVERTISSEMENT dans le groupe '{group.get('format', 'Unknown')}':")

            # Warning spécial pour les références intermédiaires utilisées seules
            if intermediate_used_alone:
                print(f"\n   🔶 {len(intermediate_used_alone)} référence(s) INTERMÉDIAIRE(S) utilisée(s) seule(s):")
                print(f"      (Les références marquées * doivent utiliser leurs sous-propriétés)")
                for ref in sorted(set(intermediate_used_alone)):
                    print(f"      {{{{{ref}}}}} ← INTERMÉDIAIRE (utilisez les sous-propriétés)")

            # Clés fictives (inventées par le LLM)
            if fictive_refs:
                print(f"\n   ❌ {len(fictive_refs)} clé(s) FICTIVE(S) (inventées par le LLM):")

                # Retrouver les références originales (avec ->) pour un affichage plus clair
                original_fictive_refs = []
                for ref in references:
                    if ref.replace("->", "").replace("*", "") in fictive_refs:
                        original_fictive_refs.append(ref)

                for ref in sorted(set(original_fictive_refs)):
                    print(f"      {{{{{ref}}}}}")

            # Clés manquantes (devraient être utilisées mais ne le sont pas)
            if missing_refs:
                print(f"\n   ⚠️  {len(missing_refs)} clé(s) MANQUANTE(S) (devraient être utilisées):")

                # Retrouver les clés originales (avec -> et éventuellement *) pour un affichage plus clair
                original_missing_refs = []
                for key in valid_keys:
                    # Normaliser la clé en enlevant -> et *
                    normalized = key.replace("->", "").replace("*", "")
                    if normalized in missing_refs:
                        original_missing_refs.append(key)

                for key in sorted(original_missing_refs):
                    print(f"      {{{{{key}}}}}")

            # Clés valides pour référence
            print(f"\n   📋 Toutes les clés valides pour ce groupe ({len(valid_keys)}):")
            for key in sorted(valid_keys)[:5]:
                # Normaliser pour la comparaison
                normalized = key.replace("->", "").replace("*", "")
                used = "✅" if normalized in normalized_references else "⚪"
                print(f"      {used} {key}")
            if len(valid_keys) > 5:
                print(f"      ... et {len(valid_keys) - 5} autres")

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

    async def _generate_structure_with_llm(
        self,
        source_json: Dict[str, Any],
        templates: List[Dict[str, Any]],  # Gardé pour compatibilité mais non utilisé avec la nouvelle approche
        context_description: str,
    ):
        # Extraire les chemins source avec variables [x], [y], [z]
        json_paths_with_variables = self._extract_all_json_paths(
            source_json, use_variables=True
        )

        path_groups = []
        not_shit = True

        if not_shit:
            # NOUVELLE APPROCHE: Générer les groupes de chemins avec formats
            path_groups = self._generate_path_groups_with_llm(
                source_paths=json_paths_with_variables,
                context_description=context_description,
            )

            # Ajouter les références aux groupes imbriqués
            path_groups_before = path_groups
            path_groups = self._add_nested_group_references(path_groups)

            path_groups = self._clean_and_separate_groups_by_depth(path_groups)

            # Ajouter les références manquantes (création de groupes parents si nécessaire)
            path_groups = self._add_missing_nested_references(path_groups)

        else: 
            path_groups = shit_path_group

        # Valider les groupes (Étape 4)
        validation_warnings = validate_path_groups(path_groups)
        if validation_warnings:
            print("\n=== WARNINGS DE VALIDATION DES PATH GROUPS ===")
            print("\n".join(validation_warnings))
            print("=" * 50 + "\n")
            # Option: lever une exception si critique
            # raise ValueError("Path groups invalides")


        # Étape 5: Construire le mapping chemin → valeur AVANT la génération des JSONs
        # Cela permettra de passer des échantillons de valeurs au LLM
        path_to_value_map = self._build_path_to_value_map(source_json)

        # Pour chaque groupe, récupérer les templates par embedding et générer le JSON
        # On crée un dictionnaire {clé_de_référence: json_du_groupe} pour faciliter la résolution
        group_jsons_map = {}

        # Identifier les groupes de référence pure (nécessitent des instructions spéciales)
        reference_only_groups_count = 0

        for group in path_groups:
            if self._is_reference_only_group(group):
                reference_only_groups_count += 1
                # Marquer le groupe comme référence pure
                group["is_reference_only"] = True
            else:
                group["is_reference_only"] = False

        if reference_only_groups_count > 0:
            print(f"\n📌 INFO: {reference_only_groups_count} groupe(s) de référence pure détecté(s) (instructions spéciales)")

        # Créer une fonction async pour traiter un groupe
        async def process_group_async(group):
            # Générer l'embedding à partir de la description du format
            format_embedding = self._generate_embedding(group["format"])

            # Récupérer les templates similaires
            group_templates = fetch_similar_templates(
                self.db,
                format_embedding,
                top_k=15,  # Limiter à 8 templates par groupe pour ne pas surcharger le prompt
                include_full_data=False,
            )

            # Générer le JSON structuré pour ce groupe (appel async du LLM)
            group_json = await self._generate_json_from_group_async(
                group=group,
                templates=group_templates,
                path_to_value_map=path_to_value_map
            )

            return group_json

        # Lancer tous les appels LLM en parallèle avec asyncio.gather (pour TOUS les groupes)
        tasks = [process_group_async(group) for group in path_groups]
        group_jsons_list = await asyncio.gather(*tasks)

        # Construire group_jsons_map en extrayant les chemins {{chemin}} de chaque JSON généré
        def extract_paths_from_json(json_obj, paths_set=None):
            """Extrait récursivement tous les chemins de la forme {{chemin}} présents dans un JSON."""
            import re

            if paths_set is None:
                paths_set = set()

            if isinstance(json_obj, dict):
                for key, value in json_obj.items():
                    extract_paths_from_json(value, paths_set)
            elif isinstance(json_obj, list):
                for item in json_obj:
                    extract_paths_from_json(item, paths_set)
            elif isinstance(json_obj, str):
                # Chercher les patterns {{chemin}} dans les strings
                matches = re.findall(r'\{\{([^}]+)\}\}', json_obj)
                for match in matches:
                    paths_set.add(match)

            return paths_set

        group_jsons_map = {}
        for group_item in group_jsons_list:
            # Extraire le JSON de l'objet qui contient aussi le prompt
            group_json = group_item["json"]

            # Extraire tous les chemins {{chemin}} du JSON
            json_paths = extract_paths_from_json(group_json)

            # Ajouter chaque chemin dans group_jsons_map avec le JSON comme valeur
            for path in json_paths:
                group_jsons_map[path] = group_json

        # Résoudre les références de groupes imbriqués
        resolved_jsons_map = self._resolve_group_references(group_jsons_map, path_to_value_map)

        # Étape 7: Construire le final_json de manière incrémentale
        # Au lieu de résoudre puis combiner, on construit progressivement le JSON
        # en parcourant le path_to_value_map une seule fois
        print("\n" + "=" * 80)
        print("CONSTRUCTION INCRÉMENTALE DU FINAL_JSON")
        print("=" * 80)

        final_json_list = self._build_final_json_incremental(
            path_to_value_map=path_to_value_map,
            group_jsons_map=resolved_jsons_map,
            verbose=True  # Afficher les détails de construction
        )

        # Wrapper la liste de templates dans un container approprié
        #final_json = self._combine_group_jsons(final_json_list)
        final_json = [{"support": item} for item in final_json_list]

        # Construire le dictionnaire de retour avec toutes les informations de débogage
        debug_info = {
            "json_paths_with_variables": json_paths_with_variables,
            "path_groups": path_groups,
            "group_jsons_list": group_jsons_list,  # Liste des JSONs générés par le LLM
            "group_jsons_map": group_jsons_map,
            "resolved_jsons_map": resolved_jsons_map,
            "path_to_value_map": path_to_value_map,
        }

        # Pour la compatibilité avec l'ancienne interface, on retourne aussi un dict vide pour destination_mappings
        # (ce n'est plus pertinent avec la nouvelle approche mais on le garde pour ne pas casser l'API)
        return final_json, "TODO: prompt", {}, debug_info

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

        def is_primitive(val: Any) -> bool:
            """Vérifie si une valeur est une primitive (string, number, boolean, null)"""
            return isinstance(val, (str, int, float, bool, type(None)))

        def is_array_of_primitives(val: Any) -> bool:
            """Vérifie si une valeur est un tableau de primitives"""
            if isinstance(val, list) and len(val) > 0:
                return all(is_primitive(item) for item in val)
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

                    # Cas 1: Primitive simple (string, number, etc.)
                    if is_primitive(value):
                        paths.append(new_path)

                    # Cas 2: Tableau de primitives → ajouter [x], [y], [z]
                    elif is_array_of_primitives(value):
                        # Déterminer la notation d'index
                        if use_variables and array_depth < len(array_vars):
                            index_notation = f"[{array_vars[array_depth]}]"
                        else:
                            index_notation = "[x]"  # Par défaut utiliser [x]
                        paths.append(f"{new_path}{index_notation}")

                    # Cas 3: Objet ou tableau d'objets → continuer la récursion
                    elif isinstance(value, (dict, list)):
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
                        # La référence au tableau lui-même est INTERMÉDIAIRE (contient des sous-propriétés)
                        # On ajoute le suffixe * pour le marquer
                        array_path = f"{path}{index_notation}*"
                        paths.append(array_path)

                        for key, value in sample.items():
                            # Créer le chemin avec [] ou [x] (SANS * car on va dans les sous-propriétés)
                            array_path_for_key = f"{path}{index_notation}"
                            # IMPORTANT: Toujours utiliser -> entre l'index et la clé suivante
                            new_path = f"{array_path_for_key}->{key}"

                            # Cas 1: Primitive simple
                            if is_primitive(value):
                                paths.append(new_path)

                            # Cas 2: Tableau de primitives
                            elif is_array_of_primitives(value):
                                # Déterminer la notation pour le sous-tableau
                                if use_variables and (array_depth + 1) < len(array_vars):
                                    sub_index = f"[{array_vars[array_depth + 1]}]"
                                else:
                                    sub_index = "[y]" if index_notation == "[x]" else "[z]"
                                paths.append(f"{new_path}{sub_index}")

                            # Cas 3: Objet ou tableau d'objets
                            elif isinstance(value, (dict, list)):
                                # Si c'est un objet ou tableau d'objets, c'est une référence INTERMÉDIAIRE
                                # Ajouter le chemin avec * pour marquer comme intermédiaire
                                if isinstance(value, list) and len(value) > 0 and isinstance(value[0], dict):
                                    # Tableau d'objets imbriqué
                                    if use_variables and (array_depth + 1) < len(array_vars):
                                        sub_index = f"[{array_vars[array_depth + 1]}]"
                                    else:
                                        sub_index = "[y]" if index_notation == "[x]" else "[z]"
                                    paths.append(f"{new_path}{sub_index}*")
                                extract_paths(value, new_path, array_depth + 1)
                    else:
                        # Tableau de primitives → FINAL (pas de *)
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
