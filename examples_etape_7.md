# Exemples pour l'Étape 7 : Résolution et Expansion

## Exemple 1 : Groupe sans variable (simple remplacement)

### Input `group_json`
```json
{
  "template_name": "text/description_longue",
  "text": "{{irregularVerbs->strategyForIrregulars}}"
}
```

### Input `path_to_value_map`
```python
{
  "irregularVerbs->strategyForIrregulars": "Pour les irrégularités fréquentes, il est utile de mémoriser..."
}
```

### Processus
- ✅ Aucune variable détectée (`[x]`, `[y]`, `[z]`)
- ➡️ **Simple remplacement** via `_simple_replace`

### Output
```json
{
  "template_name": "text/description_longue",
  "text": "Pour les irrégularités fréquentes, il est utile de mémoriser..."
}
```

---

## Exemple 2 : Groupe avec variable `[x]` (expansion simple)

### Input `group_json`
```json
{
  "template_name": "tableaux/tableau_comparatif",
  "title": "Terminaisons",
  "col1_content": "{{conjugationPatterns->endingsByPerson[x]->person}}",
  "col2_content": "{{conjugationPatterns->endingsByPerson[x]->ar}}",
  "col3_content": "{{conjugationPatterns->endingsByPerson[x]->er}}"
}
```

### Input `path_to_value_map`
```python
{
  "conjugationPatterns->endingsByPerson[0]->person": "yo",
  "conjugationPatterns->endingsByPerson[0]->ar": "-o",
  "conjugationPatterns->endingsByPerson[0]->er": "-o",
  "conjugationPatterns->endingsByPerson[1]->person": "tú",
  "conjugationPatterns->endingsByPerson[1]->ar": "-as",
  "conjugationPatterns->endingsByPerson[1]->er": "-es",
  "conjugationPatterns->endingsByPerson[2]->person": "él/ella",
  "conjugationPatterns->endingsByPerson[2]->ar": "-a",
  "conjugationPatterns->endingsByPerson[2]->er": "-e"
}
```

### Processus

1. **Détection de variable**
   - Références trouvées : `["conjugationPatterns->endingsByPerson[x]->person", ...]`
   - Variable trouvée : `x`
   - Préfixe : `conjugationPatterns->endingsByPerson[x]`

2. **Comptage des itérations**
   - Pattern regex : `conjugationPatterns->endingsByPerson\[(\d+)\]`
   - Chemins matchés dans `path_to_value_map` :
     - `conjugationPatterns->endingsByPerson[0]->...` → indice 0
     - `conjugationPatterns->endingsByPerson[1]->...` → indice 1
     - `conjugationPatterns->endingsByPerson[2]->...` → indice 2
   - **Nombre d'itérations** : 3

3. **Expansion** (boucle `i=0` à `i=2`)

   **Itération i=0** :
   - Remplacer `[x]` par `[0]` dans toutes les références
   - `{{conjugationPatterns->endingsByPerson[x]->person}}` → `{{conjugationPatterns->endingsByPerson[0]->person}}` → `"yo"`
   - Résultat :
   ```json
   {
     "template_name": "tableaux/tableau_comparatif",
     "title": "Terminaisons",
     "col1_content": "yo",
     "col2_content": "-o",
     "col3_content": "-o"
   }
   ```

   **Itération i=1** :
   ```json
   {
     "template_name": "tableaux/tableau_comparatif",
     "title": "Terminaisons",
     "col1_content": "tú",
     "col2_content": "-as",
     "col3_content": "-es"
   }
   ```

   **Itération i=2** :
   ```json
   {
     "template_name": "tableaux/tableau_comparatif",
     "title": "Terminaisons",
     "col1_content": "él/ella",
     "col2_content": "-a",
     "col3_content": "-e"
   }
   ```

### Output final
```json
[
  {
    "template_name": "tableaux/tableau_comparatif",
    "title": "Terminaisons",
    "col1_content": "yo",
    "col2_content": "-o",
    "col3_content": "-o"
  },
  {
    "template_name": "tableaux/tableau_comparatif",
    "title": "Terminaisons",
    "col1_content": "tú",
    "col2_content": "-as",
    "col3_content": "-es"
  },
  {
    "template_name": "tableaux/tableau_comparatif",
    "title": "Terminaisons",
    "col1_content": "él/ella",
    "col2_content": "-a",
    "col3_content": "-e"
  }
]
```

**Note** : L'objet original a été dupliqué 3 fois !

---

## Exemple 3 : Groupe avec champ constant + champ avec variable

### Input `group_json`
```json
{
  "template_name": "layouts/grid/container",
  "title": "Modèles de verbes",
  "items": [
    {
      "template_name": "text/concept",
      "label": "{{verbGroups->models[x]->group}}",
      "value": "{{verbGroups->models[x]->infinitive}}"
    }
  ]
}
```

### Input `path_to_value_map`
```python
{
  "verbGroups->models[0]->group": "-ar",
  "verbGroups->models[0]->infinitive": "hablar",
  "verbGroups->models[1]->group": "-er",
  "verbGroups->models[1]->infinitive": "comer"
}
```

### Processus

1. **Détection**
   - Variable : `x`
   - Préfixe : `verbGroups->models[x]`

2. **Comptage**
   - Itérations : 2

3. **Expansion**
   - Le champ `title: "Modèles de verbes"` est constant (pas de variable)
   - Il sera **copié tel quel** dans chaque itération

### Output
```json
[
  {
    "template_name": "layouts/grid/container",
    "title": "Modèles de verbes",  // ← Copié
    "items": [
      {
        "template_name": "text/concept",
        "label": "-ar",
        "value": "hablar"
      }
    ]
  },
  {
    "template_name": "layouts/grid/container",
    "title": "Modèles de verbes",  // ← Copié
    "items": [
      {
        "template_name": "text/concept",
        "label": "-er",
        "value": "comer"
      }
    ]
  }
]
```

**Question** : Est-ce le comportement souhaité ? Ou faut-il éviter de dupliquer les champs constants ?

---

## Exemple 4 : Groupe avec référence imbriquée (variable `[y]`)

### Input `group_json` (DÉJÀ RÉSOLU par étape 6)
```json
{
  "template_name": "layouts/vertical_column/container",
  "items": [
    {
      "template_name": "text/titre",
      "text": "{{irregularVerbs->examples[x]->verb}}"
    },
    {
      "template_name": "tableaux/tableau",
      "rows": [
        {
          "person": "{{irregularVerbs->examples[x]->conjugations[y]->person}}",
          "form": "{{irregularVerbs->examples[x]->conjugations[y]->form}}"
        }
      ]
    }
  ]
}
```

**ATTENTION** : Ce cas ne peut PAS arriver selon les contraintes !

Grâce à la validation (étape 4), un groupe ne peut pas contenir à la fois :
- `{{irregularVerbs->examples[x]->verb}}` (profondeur 1)
- `{{irregularVerbs->examples[x]->conjugations[y]->person}}` (profondeur 2)

### Ce qui arrivera en réalité

Deux groupes séparés :

**Groupe 1** : `irregularVerbs->examples[x]`
```json
{
  "template_name": "layouts/vertical_column/container",
  "items": [
    {
      "template_name": "text/titre",
      "text": "{{irregularVerbs->examples[x]->verb}}"
    },
    "{{irregularVerbs->examples[x]->conjugations[y]}}"  // ← Référence à un autre groupe
  ]
}
```

**Groupe 2** : `irregularVerbs->examples[x]->conjugations[y]`
```json
{
  "template_name": "tableaux/tableau",
  "rows": [
    {
      "person": "{{irregularVerbs->examples[x]->conjugations[y]->person}}",
      "form": "{{irregularVerbs->examples[x]->conjugations[y]->form}}"
    }
  ]
}
```

### Résolution du Groupe 2 (avec `[y]`)

#### Input `path_to_value_map`
```python
{
  "irregularVerbs->examples[0]->conjugations[0]->person": "yo",
  "irregularVerbs->examples[0]->conjugations[0]->form": "soy",
  "irregularVerbs->examples[0]->conjugations[1]->person": "tú",
  "irregularVerbs->examples[0]->conjugations[1]->form": "eres"
}
```

**Note** : À ce stade, on résout SEULEMENT `[y]` car on traite le groupe pour `x=0` (déjà instancié)

#### Processus
- Variable : `y`
- Préfixe : `irregularVerbs->examples[0]->conjugations[y]` (avec `[x]` déjà remplacé par `[0]`)
- Itérations : 2

#### Output
```json
[
  {
    "template_name": "tableaux/tableau",
    "rows": [
      {
        "person": "yo",
        "form": "soy"
      }
    ]
  },
  {
    "template_name": "tableaux/tableau",
    "rows": [
      {
        "person": "tú",
        "form": "eres"
      }
    ]
  }
]
```

### Résolution du Groupe 1 (avec `[x]`)

Quand on résout le Groupe 1, la référence `{{irregularVerbs->examples[x]->conjugations[y]}}` pointe vers le JSON du Groupe 2 (déjà résolu).

Mais **PROBLÈME** : Quand on remplace `[x]` par `[0]`, la référence devient :
```
{{irregularVerbs->examples[0]->conjugations[y]}}
```

Elle se termine par `[y]` → C'est une **référence de groupe**, pas une valeur !

**Solution** : Dans `_replace_variable_with_index`, quand une référence se termine par `[x-z]`, on la garde telle quelle (elle sera résolue récursivement).

---

## Exemple 5 : Références inline dans du texte

### Input `group_json`
```json
{
  "template_name": "text/explication",
  "text": "Le verbe {{verbGroups->models[x]->infinitive}} signifie {{verbGroups->models[x]->translation}} en français."
}
```

### Input `path_to_value_map`
```python
{
  "verbGroups->models[0]->infinitive": "hablar",
  "verbGroups->models[0]->translation": "parler",
  "verbGroups->models[1]->infinitive": "comer",
  "verbGroups->models[1]->translation": "manger"
}
```

### Processus
- Variable : `x`
- Itérations : 2

### Output
```json
[
  {
    "template_name": "text/explication",
    "text": "Le verbe hablar signifie parler en français."
  },
  {
    "template_name": "text/explication",
    "text": "Le verbe comer signifie manger en français."
  }
]
```

**Note** : La fonction `_replace_inline_references` gère les multiples références dans un même texte.

---

## Questions pour l'implémentation

1. **Duplication des champs constants** (Exemple 3) :
   - Doit-on copier les champs sans variable dans chaque itération ?
   - Ou faut-il les extraire au niveau supérieur ?

2. **Références imbriquées** (Exemple 4) :
   - Comment gérer l'expansion récursive quand on a `[x]` puis `[y]` ?
   - Dans quel ordre résoudre les groupes ?

3. **Optimisation** :
   - Faut-il pré-calculer toutes les références ou le faire à la volée ?
   - Comment éviter de recalculer plusieurs fois les mêmes chemins ?

4. **Cas limites** :
   - Que faire si une référence `{{chemin[x]}}` ne trouve aucune correspondance dans `path_to_value_map` ?
   - Faut-il lever une erreur ou garder la référence telle quelle ?
