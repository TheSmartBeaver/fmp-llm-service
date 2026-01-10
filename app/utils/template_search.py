from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy.sql import literal_column

from app.models.db.fmp_models import CardTemplates


def fetch_similar_templates(
    db: Session,
    embedding: List[float],
    top_k: int,
    category_quotas: Optional[Dict[str, int]] = None,
    include_full_data: bool = False
) -> List[Dict[str, Any]]:
    """
    Recherche les templates les plus similaires via similarité vectorielle (pgvector).
    Permet de limiter le nombre de templates par type grammatical en effectuant plusieurs requêtes.

    Args:
        db: Session SQLAlchemy pour accéder à la DB
        embedding: Vecteur d'embedding de dimension 384
        top_k: Nombre total de résultats à retourner
        category_quotas: Dictionnaire {type_grammatical: quota} où type_grammatical est une lettre
                       correspondant à GrammarStructure (ex: {"C": 2, "I": 4, "B": 2})
                       Types possibles: C (Container), I (Item), B (Block), L (Leaf), M (Media), R (Relation), D (Decorator)
                       Le reste des templates sera égal à top_k - somme(quotas)
        include_full_data: Si True, inclut SKU et Template dans les résultats (pour l'API)

    Returns:
        Liste de dictionnaires contenant les métadonnées des templates
        Si include_full_data=False: template_name, fields_usage, short_description,
                                     full_description, similarity_distance
        Si include_full_data=True: Ajoute sku et template
    """
    # Convertir l'embedding en format string PostgreSQL array
    embedding_str = "[" + ",".join(str(float(x)) for x in embedding) + "]"

    # Utiliser SQLAlchemy ORM avec l'opérateur pgvector <=> (cosine distance)
    distance_expr = literal_column(f"\"Embedding\" <=> '{embedding_str}'::vector")

    templates = []

    # Si pas de quotas par catégorie, faire une seule requête classique
    if not category_quotas:
        # Construire la requête avec les champs de base
        query_fields = [
            CardTemplates.Path,
            CardTemplates.GrammarStructure,
            CardTemplates.TemplateFieldsUsage,
            CardTemplates.ShortSemanticRepresentation,
            CardTemplates.FullSemanticRepresentation,
            distance_expr.label("distance"),
        ]

        # Ajouter les champs additionnels si demandé
        if include_full_data:
            query_fields.insert(0, CardTemplates.SKU)
            query_fields.insert(3, CardTemplates.Template)

        query = (
            db.query(*query_fields)
            .filter(CardTemplates.Embedding.isnot(None))
            .filter(CardTemplates.IsEnabled == True)
            .order_by(distance_expr)
            .limit(top_k)
        )

        result = query.all()

        for row in result:
            # Parser le JSON pour extraire grammar
            import json
            try:
                fields_usage_json = json.loads(row.TemplateFieldsUsage)
                grammar_dict = fields_usage_json.get("grammar", {})
            except (json.JSONDecodeError, AttributeError, TypeError):
                # Fallback si le JSON est invalide ou ancien format
                grammar_dict = {}
                print(f"Warning: Invalid JSON in TemplateFieldsUsage for {row.Path}")

            template_dict = {
                "template_name": f"#{row.GrammarStructure}#{row.Path}",
                "fields_usage": grammar_dict,
                "short_description": row.ShortSemanticRepresentation,
                "full_description": row.FullSemanticRepresentation,
                "similarity_distance": float(row.distance),
            }

            if include_full_data:
                template_dict["sku"] = row.SKU
                template_dict["template"] = row.Template

            templates.append(template_dict)

        return templates

    # Calculer le quota pour les templates "autres"
    reserved_quota = sum(category_quotas.values())
    other_quota = top_k - reserved_quota

    # 1. Récupérer les templates pour chaque type grammatical spécifié
    for grammar_type, quota in category_quotas.items():
        # Construire la requête avec les champs de base
        query_fields = [
            CardTemplates.Path,
            CardTemplates.GrammarStructure,
            CardTemplates.TemplateFieldsUsage,
            CardTemplates.ShortSemanticRepresentation,
            CardTemplates.FullSemanticRepresentation,
            distance_expr.label("distance"),
        ]

        # Ajouter les champs additionnels si demandé
        if include_full_data:
            query_fields.insert(0, CardTemplates.SKU)
            query_fields.insert(3, CardTemplates.Template)

        query = (
            db.query(*query_fields)
            .filter(CardTemplates.Embedding.isnot(None))
            .filter(CardTemplates.IsEnabled == True)
            .filter(CardTemplates.GrammarStructure == grammar_type)
            .order_by(distance_expr)
            .limit(quota)
        )

        result = query.all()

        for row in result:
            # Parser le JSON pour extraire grammar
            import json
            try:
                fields_usage_json = json.loads(row.TemplateFieldsUsage)
                grammar_dict = fields_usage_json.get("grammar", {})
            except (json.JSONDecodeError, AttributeError, TypeError):
                # Fallback si le JSON est invalide ou ancien format
                grammar_dict = {}
                print(f"Warning: Invalid JSON in TemplateFieldsUsage for {row.Path}")

            template_dict = {
                "template_name": f"#{row.GrammarStructure}#{row.Path}",
                "fields_usage": grammar_dict,
                "short_description": row.ShortSemanticRepresentation,
                "full_description": row.FullSemanticRepresentation,
                "similarity_distance": float(row.distance),
            }

            if include_full_data:
                template_dict["sku"] = row.SKU
                template_dict["template"] = row.Template

            templates.append(template_dict)

    # 2. Récupérer les templates "autres" (qui n'appartiennent à aucun type grammatical spécifié)
    if other_quota > 0:
        # Construire la requête avec les champs de base
        query_fields = [
            CardTemplates.Path,
            CardTemplates.GrammarStructure,
            CardTemplates.TemplateFieldsUsage,
            CardTemplates.ShortSemanticRepresentation,
            CardTemplates.FullSemanticRepresentation,
            distance_expr.label("distance"),
        ]

        # Ajouter les champs additionnels si demandé
        if include_full_data:
            query_fields.insert(0, CardTemplates.SKU)
            query_fields.insert(3, CardTemplates.Template)

        # Construire les filtres pour exclure les types grammaticaux spécifiés
        query = (
            db.query(*query_fields)
            .filter(CardTemplates.Embedding.isnot(None))
            .filter(CardTemplates.IsEnabled == True)
        )

        # Exclure tous les types grammaticaux spécifiés
        for grammar_type in category_quotas.keys():
            query = query.filter(CardTemplates.GrammarStructure != grammar_type)

        query = query.order_by(distance_expr).limit(other_quota)

        result = query.all()

        for row in result:
            # Parser le JSON pour extraire grammar
            import json
            try:
                fields_usage_json = json.loads(row.TemplateFieldsUsage)
                grammar_dict = fields_usage_json.get("grammar", {})
            except (json.JSONDecodeError, AttributeError, TypeError):
                # Fallback si le JSON est invalide ou ancien format
                grammar_dict = {}
                print(f"Warning: Invalid JSON in TemplateFieldsUsage for {row.Path}")

            template_dict = {
                "template_name": f"#{row.GrammarStructure}#{row.Path}",
                "fields_usage": grammar_dict,
                "short_description": row.ShortSemanticRepresentation,
                "full_description": row.FullSemanticRepresentation,
                "similarity_distance": float(row.distance),
            }

            if include_full_data:
                template_dict["sku"] = row.SKU
                template_dict["template"] = row.Template

            templates.append(template_dict)

    return templates
