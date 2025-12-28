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
    ) -> tuple[Dict[str, Any], str]:
        """
        Utilise le LLM pour générer la structure de templates.

        Args:
            source_json: Le JSON source contenant les données
            templates: Liste des templates disponibles
            context_description: Description du contexte

        Returns:
            Tuple contenant:
            - Le JSON structuré généré
            - Le prompt complet envoyé au LLM
        """
        # Formater les templates pour le prompt
        templates_description = self._format_templates_for_prompt(templates)

        # Extraire TOUS les chemins disponibles dans le JSON source
        all_paths = self._extract_all_json_paths(source_json)

        # Créer le prompt système
        system_prompt = """Tu es un expert en structuration de données et en mapping de templates.

Ta mission est de transformer un JSON de données source en un JSON structuré basé sur des templates disponibles.

TEMPLATES DISPONIBLES:
{templates}

CHEMINS DISPONIBLES DANS LE JSON SOURCE (À TOUS MAPPER):
{all_paths}

RÈGLES CRITIQUES - À RESPECTER ABSOLUMENT:

1. ⚠️ EXHAUSTIVITÉ OBLIGATOIRE:
   - Tu DOIS mapper TOUS les chemins listés ci-dessus dans "CHEMINS DISPONIBLES"
   - Chaque chemin de la liste doit apparaître au moins une fois dans la structure finale avec la notation {{...}}
   - AUCUN chemin ne doit être oublié
   - Coche mentalement chaque chemin au fur et à mesure que tu le mappe

2. ⚠️ CHEMINS EXACTS UNIQUEMENT:
   - Tu ne peux utiliser QUE les chemins listés dans "CHEMINS DISPONIBLES" ci-dessus
   - ❌ INTERDIT d'inventer des chemins qui ne sont pas dans la liste
   - ✅ AUTORISÉ: Uniquement les chemins de la liste complète fournie ci-dessus
   - Copie-colle les chemins exactement comme ils apparaissent dans la liste

3. ⚠️ TEMPLATES ET CHAMPS EXACTS:
   - Les "template_name" doivent EXACTEMENT correspondre aux "Path" des templates disponibles
   - Les noms de champs doivent STRICTEMENT correspondre à "Usage des champs" de chaque template
   - ❌ N'invente JAMAIS de template_name ou de nom de champ

4. 🎯 STRUCTURE COMPLÈTE:
   - Crée une hiérarchie profonde et complète qui reflète TOUTES les données
   - Pour les tableaux imbriqués (ex: course_sections contient tables), crée des structures imbriquées
   - N'oublie aucun niveau de profondeur (ex: conjugation_table dans tables)

NOTATION DES CHEMINS (RAPPEL):
- {{champ}} : référence directe à la racine
- {{objet->sous_champ}} : navigation dans un objet (opérateur ->)
- {{tableau[]champ}} : parcourt un tableau (opérateur [])
- {{tableau[]sous_tableau[]champ}} : double parcours
- {{tableau[]objet->champ}} : combine tableau et objet

ALGORITHME À SUIVRE:
1. Regarde la liste "CHEMINS DISPONIBLES" ci-dessus - ce sont TOUS les chemins que tu dois mapper
2. Pour chaque chemin de la liste, trouve le template approprié pour l'afficher
3. Crée une structure imbriquée qui utilise TOUS les chemins de la liste
4. Vérifie que tu as utilisé CHAQUE chemin de la liste au moins une fois
5. N'utilise AUCUN chemin qui n'est pas dans la liste

STRUCTURE ATTENDUE:
{{
  "template_name": "nom_exact_du_template",
  "items": [
    {{
      "template_name": "autre_template",
      "field_name_1": "{{reference_reelle_du_json}}",
      "field_name_2": {{
        "template_name": "template_imbrique",
        "field_X": "{{autre_reference_reelle}}"
      }}
    }}
  ]
}}

Réponds UNIQUEMENT avec le JSON valide, sans texte additionnel."""

        user_prompt = """Voici le JSON de données source à structurer:

CONTEXTE: {context}

DONNÉES SOURCE:
```json
{source_json}
```

RAPPEL CRITIQUE:
- Mappe TOUS les chemins listés dans "CHEMINS DISPONIBLES" ci-dessus
- Utilise UNIQUEMENT les chemins de cette liste, rien d'autre
- Vérifie que chaque chemin de la liste apparaît au moins une fois dans ton JSON final

Génère un JSON structuré COMPLET en utilisant les templates disponibles."""

        # Créer le prompt template
        prompt = ChatPromptTemplate.from_messages(
            [("system", system_prompt), ("human", user_prompt)]
        )

        # Créer la chaîne avec parser JSON
        chain = prompt | self.llm | JsonOutputParser()

        # Préparer les paramètres
        import json
        source_json_str = json.dumps(source_json, ensure_ascii=False, indent=2)

        invoke_params = {
            "templates": templates_description,
            "all_paths": all_paths,
            "context": context_description or "Non spécifié",
            "source_json": source_json_str,
        }

        # Générer le prompt complet pour le retour
        full_prompt = prompt.format(**invoke_params)

        #raise NotImplementedError("LLM invocation is disabled in this environment.")
        # Exécuter la chaîne
        result = chain.invoke(invoke_params)

        return result, full_prompt

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
                    f'    "{field_name}": "{{{{reference_ou_valeur}}}}"'
                )

            example = "{\n" + f'    "template_name": "{template["template_name"]}",\n'
            example += ",\n".join(example_fields)
            example += "\n  }"
        else:
            example = "{\n" + f'    "template_name": "{template["template_name"]}",\n'
            example += '    "voir_usage_des_champs_ci_dessus": "..."\n  }'

        return example
