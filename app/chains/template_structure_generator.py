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
    4. Retourne un JSON qui utilise la notation {{chemin->vers->donnée}} pour référencer les données

    Notation des chemins :
    - `->` pour naviguer dans les objets (ex: `tip->memory`)
    - `[]` pour parcourir les tableaux (ex: `course_sections[]`)
    - Combinaison : `{{course_sections[]tables[]infinitive_translation}}`
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
        test1 = self._extract_all_json_paths(source_json)
        test2 = self._format_templates_for_prompt(templates)
        raise NotImplementedError("Méthode _generate_structure_with_llm non implémentée")

    def _extract_all_json_paths(self, data: Any) -> str:
        """
        Extrait récursivement tous les chemins disponibles dans un JSON.

        Utilise extract_json_structure pour obtenir une structure minimale fusionnée,
        puis extrait tous les chemins possibles.

        Args:
            data: Le JSON à analyser

        Returns:
            String formaté avec tous les chemins disponibles
        """
        # Étape 1: Obtenir la structure minimale avec extract_json_structure
        structure = extract_json_structure(data)

        # Étape 2: Extraire tous les chemins de cette structure
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
                    paths.append(f"{{{{{new_path}}}}}")

                    # Continuer la récursion
                    extract_paths(value, new_path)

            elif isinstance(obj, list):
                if len(obj) > 0:
                    # Pour les tableaux, on utilise la notation []
                    sample = obj[0]

                    if isinstance(sample, dict):
                        # Tableau d'objets
                        for key, value in sample.items():
                            # Créer le chemin avec []
                            array_path = f"{path}[]"
                            new_path = f"{array_path}{key}"

                            # Ajouter ce chemin
                            paths.append(f"{{{{{new_path}}}}}")

                            # Récursion pour les valeurs imbriquées
                            extract_paths(value, new_path)
                    else:
                        # Tableau de primitives
                        array_path = f"{path}[]"
                        paths.append(f"{{{{{array_path}}}}}")

        extract_paths(structure)

        # Supprimer les doublons et trier
        unique_paths = sorted(set(paths))

        # Formater la liste des chemins
        formatted_paths = "\n".join([f"  - {path}" for path in unique_paths])
        return formatted_paths

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
