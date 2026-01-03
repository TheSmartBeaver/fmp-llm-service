# 🔧 Correction: Hallucinations sur les groupes de référence pure

## 📋 Problème identifié

Après les premières améliorations, il restait des hallucinations sur les **groupes de référence pure**:

```
⚠️  AVERTISSEMENT: Le LLM a inventé 2 clé(s) fictive(s) dans le groupe 'Groupe parent pour glossary':
   ❌ {{glossary[x]->term}}
   ❌ {{glossary[x]->definition}}

   Clés valides pour ce groupe:
   ✅ glossary[x]
```

### Qu'est-ce qu'un groupe de référence pure ?

Un **groupe de référence pure** est un groupe créé automatiquement par `_add_missing_nested_references()` qui contient **seulement une référence** à un groupe enfant, sans propriétés détaillées.

**Exemples:**
- `{"keys": ["glossary[x]"]}` → Référence pure
- `{"keys": ["themes[x]"]}` → Référence pure
- `{"keys": ["themes[x]->examples[y]->conjugation[z]"]}` → Référence pure

Ces groupes servent à **structurer l'imbrication** des données, mais ne contiennent pas de propriétés détaillées.

### Pourquoi le LLM inventait des propriétés ?

Le LLM recevait:
```
Chemins source disponibles:
  - glossary[x]
```

Et générait:
```json
{
  "template_name": "text/definition",
  "term": "{{glossary[x]->term}}",      ❌ Inventé!
  "definition": "{{glossary[x]->definition}}"  ❌ Inventé!
}
```

Au lieu de:
```json
{
  "template_name": "layouts/vertical_column/container",
  "items": "{{glossary[x]}}"  ✅ Correct!
}
```

## ✅ Solution implémentée

### 1. Détection des groupes de référence pure

**Nouvelle méthode:** `_is_reference_only_group()` (lignes 1349-1401)

```python
def _is_reference_only_group(self, group: Dict[str, Any]) -> bool:
    """
    Détermine si un groupe contient UNIQUEMENT des références à d'autres groupes,
    sans propriétés détaillées.

    Exemples:
        - {"keys": ["glossary[x]"]} → True (référence pure)
        - {"keys": ["glossary[x]->term", "glossary[x]->definition"]} → False (propriétés)
    """
    keys = group.get("keys", [])

    for key in keys:
        if '[x]' in key or '[y]' in key or '[z]' in key:
            # Vérifier s'il y a des propriétés après la dernière variable
            last_var_match = None
            for match in re.finditer(r'\[[xyz]\]', key):
                last_var_match = match

            if last_var_match:
                after_var = key[last_var_match.end():]
                if after_var and after_var != '':
                    return False  # Il y a des propriétés → pas référence pure
        else:
            return False  # Pas de variable → pas référence pure

    return True  # Toutes les clés sont des références pures
```

**Test:** `test_reference_only_groups.py` ✅ 9 cas de test

### 2. Instructions spéciales dans le prompt

**Modification:** `_build_json_generation_prompt()` (lignes 366-389)

Quand un groupe est détecté comme référence pure (`is_reference_only: true`), le prompt contient des instructions spéciales:

```
⚠️ ATTENTION SPÉCIALE: Ce groupe contient UNIQUEMENT une référence (ex: glossary[x], themes[x]).

RÈGLE CRITIQUE:
- Tu DOIS utiliser la référence EXACTEMENT comme fournie, SANS ajouter de propriétés
- ❌ N'invente PAS de propriétés après la référence (comme ->term, ->definition, ->label, etc.)
- ✅ Utilise SEULEMENT la référence telle quelle

Exemple CORRECT pour glossary[x]:
{
  "template_name": "layouts/vertical_column/container",
  "items": "{{glossary[x]}}"
}

Exemple INCORRECT (à NE JAMAIS faire):
{
  "template_name": "text/definition",
  "term": "{{glossary[x]->term}}",  ❌ N'invente PAS de propriétés!
  "definition": "{{glossary[x]->definition}}"
}
```

**Test:** `test_reference_group_prompt.py` ✅ 5/5 vérifications

### 3. Marquage des groupes

**Modification:** `_generate_structure_with_llm()` (lignes 1805-1817)

```python
# Identifier les groupes de référence pure
for group in path_groups:
    if self._is_reference_only_group(group):
        group["is_reference_only"] = True  # Marquer le groupe
    else:
        group["is_reference_only"] = False

# Info pour debugging
print(f"📌 INFO: {count} groupe(s) de référence pure détecté(s) (instructions spéciales)")
```

## 📊 Impact

### Avant
```
⚠️  AVERTISSEMENT: Le LLM a inventé 2 clé(s) fictive(s):
   ❌ {{glossary[x]->term}}
   ❌ {{glossary[x]->definition}}
```

### Après (attendu)
```
✅ JSON généré correctement:
{
  "template_name": "layouts/vertical_column/container",
  "items": "{{glossary[x]}}"
}
```

## 🧪 Tests créés

### 1. `test_reference_only_groups.py`

Teste la détection de groupes de référence pure avec 9 cas:
- ✅ `glossary[x]` → Référence pure
- ✅ `themes[x]` → Référence pure
- ✅ `themes[x]->examples[y]` → Référence pure
- ✅ `themes[x]->examples[y]->conjugation[z]` → Référence pure
- ❌ `glossary[x]->term, glossary[x]->definition` → Pas référence pure
- ❌ `course, topicPath` → Pas référence pure
- Et 3 autres cas

### 2. `test_reference_group_prompt.py`

Vérifie que le prompt contient les instructions spéciales:
- ✅ Instructions "ATTENTION SPÉCIALE" présentes
- ✅ Interdiction explicite d'inventer des propriétés
- ✅ Exemple CORRECT fourni
- ✅ Exemple INCORRECT fourni
- ✅ Pas d'instructions spéciales pour groupes normaux

## 📁 Fichiers modifiés

1. **app/chains/template_structure_generator.py**
   - Ligne 1349-1401: Nouvelle méthode `_is_reference_only_group()`
   - Ligne 366-389: Instructions spéciales dans le prompt
   - Ligne 1805-1817: Marquage des groupes de référence pure

2. **run_all_validation_tests.sh**
   - Ajout de `test_reference_group_prompt.py` (test #5)

3. **Tests créés**
   - `test_reference_only_groups.py` (9 cas)
   - `test_reference_group_prompt.py` (5 vérifications)

## 🎯 Cas d'usage

### Groupe de référence: `glossary[x]`

**Prompt reçu par le LLM:**
```
Chemins source:
  - glossary[x]

⚠️ ATTENTION SPÉCIALE: Ce groupe contient UNIQUEMENT une référence.
- ❌ N'invente PAS de propriétés (->term, ->definition, etc.)
- ✅ Utilise SEULEMENT {{glossary[x]}}
```

**JSON généré (attendu):**
```json
{
  "template_name": "layouts/vertical_column/container",
  "items": "{{glossary[x]}}"
}
```

### Groupe normal: `glossary[x]->term, glossary[x]->definition`

**Prompt reçu par le LLM:**
```
Chemins source:
  - glossary[x]->term
  - glossary[x]->definition

(Pas d'instructions spéciales)
```

**JSON généré:**
```json
{
  "template_name": "text/definition",
  "term": "{{glossary[x]->term}}",
  "definition": "{{glossary[x]->definition}}"
}
```

## 🚀 Résultat attendu

Les hallucinations sur les groupes de référence pure devraient **disparaître complètement** car:

1. ✅ Le LLM sait qu'il s'agit d'un groupe spécial (ATTENTION SPÉCIALE)
2. ✅ Interdiction explicite d'inventer des propriétés
3. ✅ Exemple CORRECT montrant comment utiliser la référence
4. ✅ Exemple INCORRECT montrant ce qu'il ne faut PAS faire

## 📝 Prochaines étapes

1. ✅ Tester avec de vraies données API `/generate_v2`
2. ✅ Vérifier que les warnings de clés fictives diminuent
3. ✅ Monitorer les types d'erreurs restantes
4. ✅ Ajuster le prompt si nécessaire basé sur les résultats réels

## ✅ Validation

```bash
./run_all_validation_tests.sh
```

**Résultat attendu:** 6/6 tests réussis
