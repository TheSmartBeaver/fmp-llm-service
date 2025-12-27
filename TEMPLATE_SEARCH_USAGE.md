# Template Search avec Quotas par Catégorie

## Vue d'ensemble

Le système de recherche de templates a été centralisé dans `app/utils/template_search.py` et supporte maintenant les **quotas par catégorie**.

## Fonction `fetch_similar_templates`

### Signature

```python
def fetch_similar_templates(
    db: Session,
    embedding: List[float],
    top_k: int,
    category_quotas: Optional[Dict[str, int]] = None,
    include_full_data: bool = False
) -> List[Dict[str, Any]]
```

### Paramètres

- **db**: Session SQLAlchemy pour accéder à la base de données
- **embedding**: Vecteur d'embedding de dimension 384
- **top_k**: Nombre total de templates à retourner
- **category_quotas** (optionnel): Dictionnaire `{catégorie: quota}` où la catégorie correspond au début du `Path`
  - Exemple: `{"Basic": 3, "Advanced": 5}`
  - Le reste des templates sera: `top_k - somme(quotas)`
- **include_full_data** (optionnel): Si `True`, inclut les champs `sku` et `template` (nécessaire pour l'API)

### Valeur de retour

Liste de dictionnaires avec les clés suivantes:
- **template_name**: Path du template
- **fields_usage**: Description des champs
- **short_description**: Description courte
- **full_description**: Description complète
- **similarity_distance**: Distance cosinus
- **sku** (si `include_full_data=True`)
- **template** (si `include_full_data=True`)

## Utilisation

### 1. Dans les générateurs (sans quotas)

```python
from app.utils.template_search import fetch_similar_templates

# Dans CourseMaterialGenerator ou MindMapGenerator
templates = fetch_similar_templates(
    db=self.db,
    embedding=embedding,
    top_k=15
)
```

### 2. Avec quotas par catégorie

```python
templates = fetch_similar_templates(
    db=self.db,
    embedding=embedding,
    top_k=15,
    category_quotas={
        "Basic": 3,
        "Advanced": 5,
        "Interactive": 2
    }
)
# Résultat: 3 Basic + 5 Advanced + 2 Interactive + 5 autres = 15 templates
```

### 3. API `/search-similar` avec quotas

**Requête POST** vers `/embedding/search-similar`:

```json
{
  "text": "explain photosynthesis",
  "top_n": 10,
  "app_user_sku": "123e4567-e89b-12d3-a456-426614174000",
  "category_quotas": {
    "Basic": 3,
    "Advanced": 2
  },
  "include_full_data": false
}
```

**Paramètres**:
- `include_full_data` (optionnel, défaut: `false`): Si `true`, inclut les champs `sku` et `template` dans la réponse

**Résultat**: 3 templates Basic + 2 templates Advanced + 5 autres = 10 templates au total

#### Réponse avec `include_full_data=false` (par défaut)
```json
{
  "results": [
    {
      "sku": null,
      "path": "Basic/SimpleText",
      "template": null,
      "full_semantic_representation": "...",
      "short_semantic_representation": "...",
      "similarity_score": 0.95
    }
  ]
}
```

#### Réponse avec `include_full_data=true`
```json
{
  "results": [
    {
      "sku": "123e4567-e89b-12d3-a456-426614174000",
      "path": "Basic/SimpleText",
      "template": "<div>...</div>",
      "full_semantic_representation": "...",
      "short_semantic_representation": "...",
      "similarity_score": 0.95
    }
  ]
}
```

## Comportement des requêtes SQL

Le système effectue **plusieurs requêtes SQL** pour optimiser la recherche:

1. **Une requête par catégorie spécifiée** dans `category_quotas`
   - Filtre: `Path LIKE 'Basic%'`
   - Limite: quota de la catégorie

2. **Une requête pour les templates "autres"**
   - Filtre: exclusion de toutes les catégories spécifiées
   - Limite: `top_k - somme(quotas)`

## Fichiers modifiés

- **app/utils/template_search.py**: Fonction centralisée
- **app/chains/course_material_generator.py**: Utilise `fetch_similar_templates`
- **app/chains/mind_map_generator.py**: Utilise `fetch_similar_templates`
- **app/routers/embedding/router.py**: Utilise `fetch_similar_templates` avec support des quotas
- **app/models/dto/embedding/search_similar_dto.py**: Ajout du champ `category_quotas`

## Exemples de catégories

Les catégories correspondent au **début du Path** dans la base de données. Exemples:

- `Basic/SimpleText`
- `Basic/ImageWithCaption`
- `Advanced/InteractiveQuiz`
- `Advanced/VideoPlayer`
- `Interactive/DragAndDrop`

Pour cibler tous les templates "Basic", utilisez: `{"Basic": 5}`
