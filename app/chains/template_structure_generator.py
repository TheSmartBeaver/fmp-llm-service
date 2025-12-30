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

        # TODO: Utiliser destination_mappings pour construire le JSON final

        raise NotImplementedError("Méthode _generate_structure_with_llm non implémentée")

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

                    # Ajouter ce chemin à la liste
                    paths.append(new_path)

                    # Continuer la récursion
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

                            # Ajouter ce chemin
                            paths.append(new_path)

                            # Récursion pour les valeurs imbriquées avec profondeur incrémentée
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

                    # Ajouter ce chemin à la liste
                    paths.append(new_path)

                    # Continuer la récursion
                    extract_paths(value, new_path)

            elif isinstance(obj, list):
                # Pour chaque élément du tableau, créer un chemin avec son index
                for idx, item in enumerate(obj):
                    array_path = f"{path}[{idx}]"

                    if isinstance(item, dict):
                        # Tableau d'objets
                        for key, value in item.items():
                            new_path = f"{array_path}{key}"
                            paths.append(new_path)

                            # Récursion pour les valeurs imbriquées
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
