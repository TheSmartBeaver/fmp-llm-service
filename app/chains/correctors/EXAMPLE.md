# Exemple de Correction en Action

## Exemple concret : LayoutSpacingCorrector

### Avant correction

```json
{
  "template_name": "layouts/vertical_column/container",
  "spacing": "invalid_value",
  "items": [
    {
      "template_name": "layouts/vertical_column/item",
      "title": "Section 1",
      "content": {
        "template_name": "text/title",
        "text": "Hello World"
      }
    },
    {
      "template_name": "layouts/horizontal_line/container",
      "spacing": "xyz123",
      "items": [
        {
          "template_name": "text/description",
          "text": "Description"
        }
      ]
    }
  ]
}
```

### Logs du système

```
INFO - Template_names détectés: {
  'layouts/vertical_column/container',
  'layouts/vertical_column/item',
  'layouts/horizontal_line/container',
  'text/title',
  'text/description'
}

INFO - 1/1 correcteurs applicables
DEBUG - Correcteur LayoutSpacingCorrector est applicable (templates: ['layouts/vertical_column/container', 'layouts/horizontal_line/container'])

INFO - [Iteration 1] LayoutSpacingCorrector: Erreur détectée, application de la correction

INFO - Stabilité atteinte après 2 itération(s)

INFO - Corrections terminées: {
  'total_iterations': 2,
  'corrections_by_corrector': {
    'LayoutSpacingCorrector': 1
  },
  'errors': [],
  'template_names_found': [
    'layouts/vertical_column/container',
    'layouts/vertical_column/item',
    'layouts/horizontal_line/container',
    'text/title',
    'text/description'
  ],
  'applicable_correctors_count': 1
}
```

### Après correction

```json
{
  "template_name": "layouts/vertical_column/container",
  "spacing": "1rem",  // ✅ Corrigé de "invalid_value" → "1rem"
  "items": [
    {
      "template_name": "layouts/vertical_column/item",
      "title": "Section 1",
      "content": {
        "template_name": "text/title",
        "text": "Hello World"
      }
    },
    {
      "template_name": "layouts/horizontal_line/container",
      "spacing": "1rem",  // ✅ Corrigé de "xyz123" → "1rem"
      "items": [
        {
          "template_name": "text/description",
          "text": "Description"
        }
      ]
    }
  ]
}
```

## Cas complexe : Corrections en cascade

Imaginons un correcteur qui dépend d'un autre (exemple fictif) :

### Itération 1
- `LayoutSpacingCorrector` corrige `"spacing": "bad"` → `"1rem"`
- Ce changement révèle une autre erreur pour `MarginCorrector`

### Itération 2
- `MarginCorrector` détecte que maintenant spacing="1rem" nécessite margin="0.5rem"
- Applique la correction

### Itération 3
- Aucun correcteur ne détecte d'erreur
- **Stabilité atteinte** → Arrêt

## Optimisation par template_names

### Scénario 1 : Correcteur non applicable

```json
{
  "template_name": "text/title",
  "text": "Hello"
}
```

**Résultat** : `LayoutSpacingCorrector` n'est **PAS** appelé car `text/title` n'est pas dans sa liste `template_names`.

```
INFO - Template_names détectés: {'text/title'}
INFO - 0/1 correcteurs applicables
INFO - Aucun correcteur applicable, structure inchangée
```

### Scénario 2 : Correcteur applicable

```json
{
  "template_name": "layouts/vertical_column/container",
  "spacing": "2rem"
}
```

**Résultat** : `LayoutSpacingCorrector` **EST** appelé mais ne détecte pas d'erreur (spacing valide).

```
INFO - Template_names détectés: {'layouts/vertical_column/container'}
INFO - 1/1 correcteurs applicables
DEBUG - Correcteur LayoutSpacingCorrector est applicable
INFO - Stabilité atteinte après 1 itération(s)
INFO - Corrections terminées: {
  'corrections_by_corrector': {}  // Aucune correction nécessaire
}
```

## Gestion d'erreurs

### Si un correcteur échoue

```python
class BuggyCorrector(BaseCorrector):
    def apply_correction(self, json_obj):
        raise Exception("Oops!")
```

**Résultat** :

```
ERROR - BuggyCorrector: Échec - Oops!
INFO - [Iteration 1] OtherCorrector: Erreur détectée, application de la correction
INFO - Stabilité atteinte après 2 itération(s)
INFO - Corrections terminées: {
  'corrections_by_corrector': {'OtherCorrector': 1},
  'errors': ['BuggyCorrector: Échec - Oops!']
}
```

Les autres correcteurs continuent de fonctionner normalement ! 🛡️

## Performance

### Cas réel avec 5 correcteurs enregistrés

```python
registry.register(LayoutSpacingCorrector())      # templates: layouts/*
registry.register(TextOpacityCorrector())        # templates: text/*
registry.register(ImageUrlCorrector())           # templates: media/image/*
registry.register(VideoTimeCorrector())          # templates: media/video/*
registry.register(ConceptIconCorrector())        # templates: conceptual/concept
```

**Structure à corriger** :

```json
{
  "template_name": "layouts/vertical_column/container",
  "spacing": "bad",
  "items": [
    {"template_name": "text/title", "text": "Test", "opacity": -1}
  ]
}
```

**Correcteurs appelés** : Seulement 2/5 !
- ✅ `LayoutSpacingCorrector` (layouts/vertical_column/container)
- ✅ `TextOpacityCorrector` (text/title)
- ❌ `ImageUrlCorrector` (pas de media/image/*)
- ❌ `VideoTimeCorrector` (pas de media/video/*)
- ❌ `ConceptIconCorrector` (pas de conceptual/concept)

**Gain de performance** : 60% de correcteurs non exécutés ! 🚀
