# Feature: Prompts dans group_jsons_list

## Résumé

Chaque objet dans `group_jsons_list` contient maintenant le prompt LLM qui a été utilisé pour le générer, permettant un meilleur débogage et traçabilité.

## Structure de group_jsons_list

Avant cette modification, `group_jsons_list` contenait directement les JSONs générés :

```python
group_jsons_list = [
    {
        "template_name": "layouts/vertical_column/container",
        "items": [...]
    },
    {
        "template_name": "text/explication",
        "text": "{{course.description}}"
    }
]
```

Maintenant, chaque élément est un dictionnaire avec deux clés :

```python
group_jsons_list = [
    {
        "json": {
            "template_name": "layouts/vertical_column/container",
            "items": [...]
        },
        "prompt": "Tu es un expert en structuration de templates...\n\nFormat du groupe:\n..."
    },
    {
        "json": {
            "template_name": "text/explication",
            "text": "{{course.description}}"
        },
        "prompt": "Tu es un expert en structuration de templates...\n\nFormat du groupe:\n..."
    }
]
```

## Accès via l'API

### API 1: `/api/utils/generate-template-structure`

L'API `/api/utils/generate-template-structure` retourne maintenant `debug_info` dans sa réponse :

### Requête

```json
POST /api/utils/generate-template-structure
{
    "source_json": {
        "course": {
            "title": "Python Programming",
            "description": "Learn Python from scratch"
        }
    },
    "context_description": "Course material",
    "top_k": 20
}
```

### Réponse

```json
{
    "success": true,
    "template_structure": {
        "template_name": "layouts/vertical_column/container",
        "items": [...]
    },
    "prompt": "...",
    "debug_info": {
        "json_paths_with_variables": [...],
        "path_groups": [...],
        "group_jsons_list": [
            {
                "json": {
                    "template_name": "...",
                    ...
                },
                "prompt": "Le prompt complet envoyé au LLM pour ce groupe"
            }
        ],
        "group_jsons_map": {...},
        "resolved_jsons_map": {...},
        "path_to_value_map": {...},
        "final_resolved_jsons_map": {...}
    }
}
```

### API 2: `/api/course_material/generate_v2`

L'API `/api/course_material/generate_v2` retourne également `group_jsons_list` directement dans la réponse :

#### Requête

```json
POST /api/course_material/generate_v2
Headers:
  X-Auth-Uid: user123
{
    "context_entry": "Cours de Python pour débutants",
    "text_entry": "Apprendre les bases de Python...",
    "medias_entry": []
}
```

#### Réponse

```json
{
    "success": true,
    "supports": [{
        "support": {
            "template_name": "layouts/vertical_column/container",
            "items": [...]
        }
    }],
    "templates_used": 20,
    "prompt": "=== ÉTAPE 1: GÉNÉRATION DU JSON PÉDAGOGIQUE ===\n...",
    "pedagogical_json": {...},
    "destination_mappings": {...},
    "json_paths_with_variables": [...],
    "path_groups": [...],
    "group_jsons_list": [
        {
            "json": {
                "template_name": "layouts/vertical_column/container",
                ...
            },
            "prompt": "Tu es un expert en structuration de templates...\n\nFormat du groupe:\n..."
        }
    ],
    "group_jsons_map": {...},
    "resolved_jsons_map": {...},
    "path_to_value_map": {...},
    "final_resolved_jsons_map": {...}
}
```

## Utilisation

### Exemple 1: Afficher tous les prompts utilisés

```python
result = await generator.generate_template_structure(
    source_json=my_json,
    context_description="Course material"
)

debug_info = result.get("debug_info", {})
group_jsons_list = debug_info.get("group_jsons_list", [])

for i, group_item in enumerate(group_jsons_list):
    print(f"\n=== Groupe {i + 1} ===")
    print(f"Template: {group_item['json'].get('template_name')}")
    print(f"\nPrompt utilisé:")
    print(group_item['prompt'])
```

### Exemple 2: Déboguer un groupe spécifique

```python
# Trouver le groupe qui a généré un template spécifique
target_template = "layouts/vertical_column/container"

for group_item in group_jsons_list:
    if group_item['json'].get('template_name') == target_template:
        print(f"Prompt utilisé pour générer {target_template}:")
        print(group_item['prompt'])
        break
```

### Exemple 3: Analyser la qualité des prompts

```python
# Statistiques sur les prompts
for i, group_item in enumerate(group_jsons_list):
    prompt = group_item['prompt']
    json_output = group_item['json']

    print(f"Groupe {i + 1}:")
    print(f"  Longueur du prompt: {len(prompt)} caractères")
    print(f"  Nombre de lignes: {len(prompt.split('\\n'))}")
    print(f"  Template généré: {json_output.get('template_name')}")
```

## Modifications apportées

### 1. template_structure_generator.py

**Fonction `_generate_json_from_group_async` (ligne 409)**
- Retourne maintenant un dictionnaire `{"json": ..., "prompt": ...}` au lieu du JSON seul
- Le prompt est formaté avec `prompt.format(**params)` pour obtenir le texte complet

**Fonction `_generate_json_from_group` (ligne 447)**
- Mise à jour pour correspondre à la nouvelle signature de la fonction async

**Traitement de group_jsons_list (ligne 1967)**
- Extraction du JSON avec `group_item["json"]` au lieu d'utiliser directement `group_json`

### 2. routers/utils/router.py

**Modèle `TemplateStructureResponse` (ligne 77)**
- Ajout du champ optionnel `debug_info: Optional[Dict[str, Any]] = None`

**Endpoint `/generate-template-structure` (ligne 153)**
- Retourne maintenant `debug_info` dans la réponse avec `debug_info=result.get("debug_info")`

### 3. routers/course_material/router.py

**Modèle `CourseMaterialResponse` (ligne 39)**
- Ajout du champ `group_jsons_list: list = None` pour exposer les JSONs avec leurs prompts

**Endpoint `/generate_v2` (ligne 314)**
- Retourne maintenant `group_jsons_list` extrait de `debug_info` : `group_jsons_list=debug_info.get("group_jsons_list")`

## Cas d'usage

1. **Débogage**: Comprendre pourquoi un certain template a été choisi
2. **Optimisation**: Analyser les prompts pour améliorer leur efficacité
3. **Traçabilité**: Suivre exactement ce qui a été envoyé au LLM pour chaque groupe
4. **Tests**: Vérifier que les prompts sont corrects et complets
5. **Documentation**: Générer automatiquement de la documentation sur le processus de génération

## Compatibilité

Cette modification est **rétrocompatible** :
- Le champ `debug_info` dans l'API est optionnel
- L'ancien code qui n'utilisait pas `debug_info` continue de fonctionner
- Seul le code qui accède à `group_jsons_list` doit être mis à jour pour extraire `group_item["json"]`
