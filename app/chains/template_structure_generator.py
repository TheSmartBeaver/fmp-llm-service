from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sentence_transformers import SentenceTransformer
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from app.utils.template_search import fetch_similar_templates
from app.utils.structure_process import extract_json_structure
from app.chains.llm.claude_haiku_45_llm import ClaudeHaiku45Llm


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

    def generate_template_structure(
        self,
        source_json: Dict[str, Any],
        context_description: str = "",
        top_k: int = 20,
        category_quotas: Dict[str, int] = None
    ) -> Dict[str, Any]:
        """
        Génère une structure de templates à partir d'un JSON source.

        Args:
            source_json: Le JSON contenant les données à structurer
            context_description: Description optionnelle du contexte (ex: "cours d'espagnol sur les verbes")
            top_k: Nombre de templates similaires à récupérer (défaut: 20)
            category_quotas: Dictionnaire {catégorie: quota} pour limiter par catégorie
                           Ex: {"layouts/": 5, "conceptual/": 3}

        Returns:
            Dict contenant:
            - template_structure: Le JSON structuré avec les template_name et références
            - prompt: Le prompt complet envoyé au LLM
        """
        # Étape 1: Créer un embedding à partir du JSON source et du contexte
        search_text = self._create_search_text(source_json, context_description)
        embedding = self._generate_embedding(search_text)

        # Étape 2: Récupérer les templates pertinents
        templates = fetch_similar_templates(
            self.db,
            embedding,
            top_k,
            category_quotas,
            include_full_data=False
        )

        # Étape 3: Générer la structure via le LLM
        template_structure, prompt = self._generate_structure_with_llm(
            source_json, templates, context_description
        )

        return {
            "template_structure": template_structure,
            "prompt": prompt
        }

    def _create_search_text(
        self,
        source_json: Dict[str, Any],
        context_description: str
    ) -> str:
        """
        Crée un texte de recherche pour trouver des templates pertinents.

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

    def _generate_structure_with_llm(
        self,
        source_json: Dict[str, Any],
        templates: List[Dict[str, Any]],
        context_description: str
    ):
        # Extraire les chemins source avec variables [x], [y], [z]
        json_paths_with_variables = self._extract_all_json_paths(source_json, use_variables=True)

        # Générer les mappings source → destination avec le LLM
        destination_mappings = self._generate_destination_paths_with_llm(
            source_paths=json_paths_with_variables,
            templates=templates,
            context_description=context_description
        )

        json_paths_with_indices = self._extract_all_json_paths(source_json, include_indices=True)

        # Construire le JSON final
        final_json = self._build_final_json(
            source_json=source_json,
            destination_mappings=destination_mappings,
            json_paths_with_indices=json_paths_with_indices
        )

        return final_json, "TODO: prompt"

    def _extract_all_json_paths(self, data: Any, include_indices: bool = False, use_variables: bool = False) -> str:
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

    def _extract_paths_compact(self, structure: Any, use_variables: bool = False) -> str:
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
        array_vars = ['x', 'y', 'z', 'w', 'v', 'u', 't', 's', 'r', 'q']

        def is_simple_value(val: Any) -> bool:
            """Vérifie si une valeur est simple (primitive, tableau de primitives, ou objet plat)"""
            if isinstance(val, (str, int, float, bool, type(None))):
                return True
            if isinstance(val, list):
                # Tableau de primitives
                return all(isinstance(item, (str, int, float, bool, type(None))) for item in val)
            if isinstance(val, dict):
                # Objet plat (toutes les valeurs sont des primitives)
                return all(isinstance(v, (str, int, float, bool, type(None))) for v in val.values())
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
                            if isinstance(value, (dict, list)) and not is_simple_value(value):
                                extract_paths(value, new_path, array_depth + 1)
                    else:
                        # Tableau de primitives
                        array_path = f"{path}{index_notation}"
                        paths.append(array_path)

        extract_paths(structure)

        # Supprimer les doublons et trier
        unique_paths = sorted(set(paths))

        # Formater la liste des chemins
        #formatted_paths = "\n".join([f"  - {path}" for path in unique_paths])
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
            """Vérifie si une valeur est simple (primitive, tableau de primitives, ou objet plat)"""
            if isinstance(val, (str, int, float, bool, type(None))):
                return True
            if isinstance(val, list):
                # Tableau de primitives
                return all(isinstance(item, (str, int, float, bool, type(None))) for item in val)
            if isinstance(val, dict):
                # Objet plat (toutes les valeurs sont des primitives)
                return all(isinstance(v, (str, int, float, bool, type(None))) for v in val.values())
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
                            if isinstance(value, (dict, list)) and not is_simple_value(value):
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

    def _generate_destination_paths_with_llm(
        self,
        source_paths: List[str],
        templates: List[Dict[str, Any]],
        context_description: str = ""
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
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Tu es un expert en construction de structures de données pédagogiques.
Ta tâche est de mapper des chemins de données source vers des chemins de destination qui utilisent des templates HTML/pédagogiques imbriqués.

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
   - Exemple: layouts/vertical_column/container["items"][0]layouts/vertical_column/item["title"]conceptual/concept["description"]
   - Cela signifie: un container qui contient un item dont le titre contient un concept

4. **Format des chemins de destination**:
   - Commence par le template_name du premier template (ex: layouts/vertical_column/container)
   - Ajoute ["nom_du_champ"] pour accéder à un champ
   - Ajoute [index] pour les tableaux (index fixe ou variable selon la règle 1 et 2)
   - Enchaîne avec le template_name suivant, etc.
   - Exemple complet: layouts/vertical_column/container["items"][0]layouts/vertical_column/item["title"]conceptual/concept["description"]

RETOURNE un JSON avec le format exact suivant:
{{
  "chemin_source_1": "chemin_destination_1",
  "chemin_source_2": "chemin_destination_2"
}}"""),
            ("user", """Contexte: {context}

Templates disponibles:
{templates}

Chemins source à mapper:
{source_paths}

Génère les mappings en respectant STRICTEMENT les règles d'indices.""")
        ])

        # Préparer les données pour le prompt
        source_paths_formatted = "\n".join([f"  - {path}" for path in source_paths])

        # Créer la chaîne LLM avec parser JSON
        parser = JsonOutputParser()
        chain = prompt | self.llm | parser

        # Appeler le LLM
        result = chain.invoke({
            "context": context_description or "Aucun contexte spécifique fourni",
            "templates": templates_formatted,
            "source_paths": source_paths_formatted
        })

        return result

    def _convert_indices_to_variables(self, path_with_indices: str) -> tuple[str, dict[str, int]]:
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
        array_vars = ['x', 'y', 'z', 'w', 'v', 'u', 't', 's', 'r', 'q']

        # Extraire tous les indices avec leur position
        indices = []
        pattern = r'\[(\d+)\]'
        for match in re.finditer(pattern, path_with_indices):
            indices.append(int(match.group(1)))

        # Créer le mapping {variable: indice}
        var_mapping = {}
        for i, idx in enumerate(indices):
            if i < len(array_vars):
                var_mapping[array_vars[i]] = idx

        # Remplacer les indices par des variables dans le chemin
        path_with_vars = path_with_indices
        for i, var in enumerate(array_vars[:len(indices)]):
            # Remplacer le premier [nombre] trouvé par [variable]
            path_with_vars = re.sub(r'\[\d+\]', f'[{var}]', path_with_vars, count=1)

        return path_with_vars, var_mapping

    def _substitute_variables_in_destination(self, destination_path: str, var_mapping: dict[str, int]) -> str:
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
            result = re.sub(rf'\[{var}\]', f'[{idx}]', result)

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
        segments = re.split(r'(->|\[\d+\])', path)
        segments = [s for s in segments if s and s != '->']

        current = data
        for segment in segments:
            if segment.startswith('[') and segment.endswith(']'):
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
            if destination_path[i:i+2] == '["':
                # Trouver la fin du field name
                end_quote = destination_path.find('"]', i + 2)
                if end_quote != -1:
                    field_name = destination_path[i+2:end_quote]
                    segments.append({"type": "field", "value": field_name})
                    i = end_quote + 2
                    continue

            # Vérifier si on a un array index [nombre]
            if destination_path[i] == '[' and i + 1 < len(destination_path) and destination_path[i+1].isdigit():
                # Trouver la fin de l'index
                end_bracket = destination_path.find(']', i + 1)
                if end_bracket != -1:
                    index_str = destination_path[i+1:end_bracket]
                    segments.append({"type": "index", "value": int(index_str)})
                    i = end_bracket + 1
                    continue

            # Sinon, c'est un template name
            # Trouver la fin du template name (jusqu'au prochain [ ou fin)
            template_name = ""
            start = i
            while i < len(destination_path) and destination_path[i] != '[':
                i += 1

            template_name = destination_path[start:i]
            if template_name:
                segments.append({"type": "template", "value": template_name})

        return segments

    def _build_final_json(
        self,
        source_json: Dict[str, Any],
        destination_mappings: Dict[str, str],
        json_paths_with_indices: List[str]
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
            path_with_vars, var_mapping = self._convert_indices_to_variables(path_source)

            # 2. Trouver le chemin de destination correspondant
            if path_with_vars not in destination_mappings:
                # Pas de mapping pour ce chemin, on l'ignore
                continue

            destination_path = destination_mappings[path_with_vars]

            # 3. Substituer les variables dans le chemin de destination
            final_destination = self._substitute_variables_in_destination(
                destination_path,
                var_mapping
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
        self,
        root: Dict[str, Any],
        segments: List[Dict[str, Any]],
        value: Any
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
            is_last = (i == len(segments) - 1)

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
                        # On continue, le prochain segment gérera le field

                    elif next_seg["type"] == "template":
                        # Deux templates consécutifs: le premier est un wrapper
                        # On ne fait rien, le prochain segment gérera
                        if "template_name" not in current:
                            current["template_name"] = seg_value

            elif seg_type == "field":
                # Accès à un champ
                field_name = seg_value

                # Vérifier que current est bien un dict
                if not isinstance(current, dict):
                    raise ValueError(f"Cannot access field '{field_name}' on non-dict type {type(current).__name__}")

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
                    if next_seg["type"] == "index" and not isinstance(existing_value, list):
                        raise ValueError(f"Field '{field_name}' exists but is not a list (found {type(existing_value).__name__})")

                    # Si le prochain segment est un field ou template, on s'attend à un dict
                    if next_seg["type"] in ("field", "template") and not isinstance(existing_value, dict):
                        raise ValueError(f"Field '{field_name}' exists but is not a dict (found {type(existing_value).__name__})")

                # Naviguer vers ce champ
                current = current[field_name]

            elif seg_type == "index":
                # Accès à un index de tableau
                idx = seg_value

                # S'assurer que current est un tableau
                if not isinstance(current, list):
                    raise ValueError(f"Expected list but got {type(current)} for index {idx}")

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
