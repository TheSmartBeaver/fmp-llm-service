from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sentence_transformers import SentenceTransformer
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from app.utils.template_search import fetch_similar_templates
from app.utils.structure_process import extract_json_structure, create_embedding_packets
from app.chains.llm.claude_haiku_45_llm import ClaudeHaiku45Llm
from app.chains.llm.open_ai_o3_mini_llm import OpenAiO3MiniLlm


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

    def _generate_structure_with_llm(
        self,
        source_json: Dict[str, Any],
        templates: List[Dict[str, Any]],
        context_description: str,
    ):
        # Extraire les chemins source avec variables [x], [y], [z]
        json_paths_with_variables = self._extract_all_json_paths(
            source_json, use_variables=True
        )

        # Générer les mappings source → destination avec le LLM
        destination_mappings = self._generate_destination_paths_with_llm(
            source_paths=json_paths_with_variables,
            templates=templates,
            context_description=context_description,
        )

        # destination_mappings = {
        #     "learning_objective": 'layouts/vertical_column/container["items"][0]text/description_longue["text"]',
        #     "course_sections[x]section_title": 'layouts/vertical_column/container["items"][1]layouts/vertical_column/item["title"]text/titre_secondaire["text"]',
        #     "course_sections[x]section_description": 'layouts/vertical_column/container["items"][1]layouts/vertical_column/item["content"]text/description_longue["text"]',
        #     "course_sections[x]key_concepts[y]concept_name": 'layouts/vertical_column/container["items"][1]layouts/vertical_column/item["content"]layouts/vertical_column/container["items"][y]conceptual/concept["title"]',
        #     "course_sections[x]key_concepts[y]explanation": 'layouts/vertical_column/container["items"][1]layouts/vertical_column/item["content"]layouts/vertical_column/container["items"][y]conceptual/concept["description"]',
        #     "course_sections[x]key_concepts[y]examples": 'layouts/vertical_column/container["items"][1]layouts/vertical_column/item["content"]layouts/vertical_column/container["items"][y]text/liste_exemples["items"]',
        #     "course_sections[x]key_concepts[y]related_media": 'layouts/vertical_column/container["items"][1]layouts/vertical_column/item["content"]layouts/vertical_column/container["items"][y]text/detail_technique["text"]',
        #     "course_sections[x]additional_notes": 'layouts/vertical_column/container["items"][2]text/contexte["text"]',
        # }

        # Valider les destination_mappings
        validation_errors = self._validate_destination_mappings(destination_mappings)
        if validation_errors:
            import warnings
            for error in validation_errors:
                warnings.warn(f"\n⚠️  VALIDATION ERROR in destination_mappings:\n{error}\n")

        json_paths_with_indices = self._extract_all_json_paths(
            source_json, include_indices=True
        )

        # Construire le JSON final
        final_json = self._build_final_json(
            source_json=source_json,
            destination_mappings=destination_mappings,
            json_paths_with_indices=json_paths_with_indices,
        )

        return final_json, "TODO: prompt", destination_mappings

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
            """Vérifie si une valeur est simple (primitive, tableau de primitives, ou objet plat)"""
            if isinstance(val, (str, int, float, bool, type(None))):
                return True
            if isinstance(val, list):
                # Tableau de primitives
                return all(
                    isinstance(item, (str, int, float, bool, type(None)))
                    for item in val
                )
            if isinstance(val, dict):
                # Objet plat (toutes les valeurs sont des primitives)
                return all(
                    isinstance(v, (str, int, float, bool, type(None)))
                    for v in val.values()
                )
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
            """Vérifie si une valeur est simple (primitive, tableau de primitives, ou objet plat)"""
            if isinstance(val, (str, int, float, bool, type(None))):
                return True
            if isinstance(val, list):
                # Tableau de primitives
                return all(
                    isinstance(item, (str, int, float, bool, type(None)))
                    for item in val
                )
            if isinstance(val, dict):
                # Objet plat (toutes les valeurs sont des primitives)
                return all(
                    isinstance(v, (str, int, float, bool, type(None)))
                    for v in val.values()
                )
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

5. **⚠️ STRATÉGIE ANTI-CHEVAUCHEMENT (CRITIQUE)**:

   RÈGLE D'OR: Utilise `layouts/vertical_column/container["items"]` avec des indices FIXES pour séparer les groupes de données.

   **STRATÉGIE RECOMMANDÉE**: Structure à 3 niveaux avec indices fixes

   ❌ ERREUR TYPIQUE - Partager le même champ/index:
   {{
     "course_sections[x]section_description": 'container["items"][x]layouts/item["content"]text/description["text"]',
     "course_sections[x]key_concepts[y]name": 'container["items"][x]layouts/item["content"]layouts/container["items"][y]...'
   }}
   → Conflit sur ["content"] qui reçoit 2 templates différents

   ✅ SOLUTION - Utilise layouts/vertical_column/container avec indices fixes:
   {{
     "course_sections[x]section_description": 'container["items"][x]layouts/vertical_column/container["items"][0]text/description["text"]',
     "course_sections[x]key_concepts[y]name": 'container["items"][x]layouts/vertical_column/container["items"][1]layouts/vertical_column/container["items"][y]conceptual/concept["title"]'
   }}
   → Pas de conflit : section_description à [0], key_concepts à [1]

   **Structure hiérarchique**:
   - Niveau 1: layouts/vertical_column/container["items"][0 ou 1] → sépare learning_objective vs course_sections
   - Niveau 2: ...["items"][x]layouts/vertical_column/container["items"][0, 1, 2, ...] → sépare title, description, key_concepts, notes
   - Niveau 3: ...["items"][y] → itère sur les key_concepts

6. **PROCESSUS DE GÉNÉRATION ÉTAPE PAR ÉTAPE**:

   Pour chaque chemin source:
   a) Identifie le préfixe (ex: "course_sections[x]key_concepts[y]")
   b) Vérifie les autres chemins avec le même préfixe
   c) Choisis UN template commun pour ce préfixe
   d) Assigne des chemins de destination en utilisant ce template commun
   e) Double-vérifie qu'aucun conflit n'existe avec les chemins déjà générés

7. **EXEMPLE COMPLET DE MAPPING VALIDE**:

   Chemins sources:
   - "learning_objective"
   - "course_sections[x]section_title"
   - "course_sections[x]section_description"
   - "course_sections[x]key_concepts[y]concept_name"
   - "course_sections[x]additional_notes"

   Mapping CORRECT (avec stratégie d'indices fixes):
   {{
     "learning_objective": 'layouts/vertical_column/container["items"][0]text/description["text"]',
     "course_sections[x]section_title": 'layouts/vertical_column/container["items"][1]layouts/vertical_column/container["items"][x]layouts/vertical_column/container["items"][0]text/titre["text"]',
     "course_sections[x]section_description": 'layouts/vertical_column/container["items"][1]layouts/vertical_column/container["items"][x]layouts/vertical_column/container["items"][1]text/description["text"]',
     "course_sections[x]key_concepts[y]concept_name": 'layouts/vertical_column/container["items"][1]layouts/vertical_column/container["items"][x]layouts/vertical_column/container["items"][2]layouts/vertical_column/container["items"][y]conceptual/concept["title"]',
     "course_sections[x]additional_notes": 'layouts/vertical_column/container["items"][1]layouts/vertical_column/container["items"][x]text/notes["text"]'
   }}

   Pourquoi c'est CORRECT:
   - Niveau 1: learning_objective à [0], course_sections à [1]
   - Niveau 2 (dans chaque course_section [x]): title à [0], description à [1], key_concepts à [2]
   - Niveau 3: key_concepts utilise layouts/vertical_column/container["items"][y]
   - additional_notes n'utilise pas de conteneur car il n'a pas besoin d'indices fixes
   - AUCUN conflit: chaque groupe a son propre indice fixe

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

   Niveau 1 - Racine: layouts/vertical_column/container["items"][indice_fixe]
   - [0] = learning_objective
   - [1] = conteneur pour course_sections

   Niveau 2 - Dans course_sections [x]: ...["items"][x]layouts/vertical_column/container["items"][indice_fixe]
   - [0] = section_title
   - [1] = section_description
   - [2] = conteneur pour key_concepts
   - [3] = additional_notes (si applicable)

   Niveau 3 - Dans key_concepts [y]: ...["items"][2]layouts/vertical_column/container["items"][y]conceptual/concept
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

        return result

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
            new_segments.extend(segments[conflict_len:])

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

RAPPEL DE LA RÈGLE CRITIQUE:
Un même emplacement (champ ou index) NE PEUT recevoir qu'UN SEUL template.
Si deux chemins partagent le même index variable (ex: [y]), ils DOIVENT utiliser le même template.""",
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
     "course_sections[x]section_description": 'container["items"][x]layouts/item["content"]text/description["text"]',
     "course_sections[x]key_concepts[y]name": 'container["items"][x]layouts/item["content"]layouts/container["items"][y]concept["title"]'
   }}

   ✅ APRÈS (CORRIGÉ avec indices fixes):
   {{
     "course_sections[x]section_description": 'container["items"][x]layouts/vertical_column/container["items"][0]text/description["text"]',
     "course_sections[x]key_concepts[y]name": 'container["items"][x]layouts/vertical_column/container["items"][1]layouts/vertical_column/container["items"][y]conceptual/concept["title"]'
   }}

   Explication: Utilise layouts/vertical_column/container["items"] avec indices fixes: [0] pour description, [1] pour key_concepts

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

Étape 4: Génère le JSON CORRIGÉ complet

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
