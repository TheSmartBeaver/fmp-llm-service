# 🛡️ Guide de validation et détection des hallucinations

Ce document explique comment utiliser les outils de validation pour détecter et diagnostiquer les hallucinations du LLM dans la génération de supports de cours.

## 🚀 Démarrage rapide

### Exécuter tous les tests de validation

```bash
./run_all_validation_tests.sh
```

Cela exécutera les 5 tests principaux et affichera un rapport complet.

### Exécuter un test spécifique

```bash
# Test 1: Validation du formatage des chemins
.venv/bin/python test_extract_paths_improvements.py

# Test 2: Validation de la couverture des clés
.venv/bin/python test_resolve_group_references.py

# Test 3: Détection des clés fictives
.venv/bin/python test_fictive_keys_validation.py

# Test 4: Validation du prompt amélioré
.venv/bin/python test_prompt_improvements.py

# Test 5: Test intégré complet
.venv/bin/python test_all_improvements.py
```

## 📊 Types d'hallucinations détectées

### 1. Indices numériques au lieu de variables

**Problème**: Le LLM utilise `[0]`, `[1]`, `[2]` au lieu de `[x]`, `[y]`, `[z]`

**Exemple d'erreur**:
```json
{
  "video": "{{media->videos[0]->label}}"  ❌
}
```

**Correction attendue**:
```json
{
  "video": "{{media->videos[x]->label}}"  ✅
}
```

**Comment détecter**:
- La validation `_validate_group_json_references()` détecte automatiquement
- Warning affiché: `⚠️ Le LLM a inventé 1 clé(s) fictive(s): {{media->videos[0]->label}}`

### 2. Clés fictives inventées

**Problème**: Le LLM invente des propriétés qui n'existent pas

**Exemple d'erreur**:
```json
{
  "term": "{{glossary[x]->term}}",
  "example": "{{glossary[x]->example}}"  ❌ N'existe pas!
}
```

**Comment détecter**:
- Comparaison automatique avec les clés valides du groupe
- Warning affiché avec liste des clés valides

### 3. Clés ambiguës (manque [x])

**Problème**: Le LLM ne précise pas qu'il s'agit d'un tableau

**Exemple d'erreur**:
```json
{
  "tips": "{{learningStrategies->concreteTips}}"  ❌ Devrait être concreteTips[x]
}
```

**Correction attendue**:
```json
{
  "tips": "{{learningStrategies->concreteTips[x]}}"  ✅
}
```

### 4. Chemins mal formatés (manque ->)

**Problème**: Le séparateur `->` manque entre propriétés

**Exemple d'erreur**:
```
themes[x]groups[y]label  ❌
```

**Correction attendue**:
```
themes[x]->groups[y]->label  ✅
```

## 🔍 Comprendre les warnings

### Warning de couverture

```
⚠️  AVERTISSEMENT: 37 clés manquantes dans resolved_jsons_map:
   - examplesCollection->examples[x]->notes
   - glossary[x]->definition
   ...
   Total de clés requises: 42
   Total de clés présentes: 6
   Taux de couverture: 11.9%
```

**Signification**: `resolved_jsons_map` ne couvre que 11.9% des clés nécessaires.

**Actions**:
1. Vérifier que `path_groups` contient tous les groupes nécessaires
2. S'assurer que le LLM génère un JSON pour chaque groupe
3. Vérifier les `category_quotas` (peut-être trop restrictifs)

### Warning de clés fictives

```
⚠️  AVERTISSEMENT: Le LLM a inventé 2 clé(s) fictive(s) dans le groupe 'Glossaire':
   ❌ {{glossary[x]->example}}
   ❌ {{glossary[x]->pronunciation}}

   Clés valides pour ce groupe:
   ✅ glossary[x]->definition
   ✅ glossary[x]->term
```

**Signification**: Le LLM a utilisé des clés qui n'existent pas dans les données source.

**Actions**:
1. Vérifier que les chemins source sont bien passés au LLM
2. Améliorer le prompt si nécessaire
3. Vérifier que `_extract_all_json_paths()` génère les bons chemins

## 🛠️ Utilisation dans le code

### 1. Validation automatique lors de la génération

```python
# Dans _generate_json_from_group_async (ligne 390)
result = await chain.ainvoke(params)

# VALIDATION: Vérifier que le LLM n'a pas inventé de clés fictives
self._validate_group_json_references(result, group)

return result
```

La validation s'exécute **automatiquement** à chaque génération de JSON par le LLM.

### 2. Validation manuelle

```python
from app.chains.template_structure_generator import TemplateStructureGenerator

generator = TemplateStructureGenerator(db_session=db, embedding_model=model)

# Créer un groupe de test
group = {
    "format": "Mon groupe",
    "keys": ["glossary[x]->term", "glossary[x]->definition"]
}

# JSON généré par le LLM
llm_json = {
    "template_name": "text/definition",
    "term": "{{glossary[x]->term}}",
    "example": "{{glossary[x]->example}}"  # Clé fictive!
}

# Valider
generator._validate_group_json_references(llm_json, group)
# Affiche: ⚠️ Le LLM a inventé 1 clé(s) fictive(s): {{glossary[x]->example}}
```

### 3. Normalisation des chemins

```python
# Normaliser un chemin avec indices réels vers variables génériques
path = "glossary[0]->term"
normalized = generator._normalize_path_to_generic(path)
# Résultat: "glossary[x]->term"
```

## 📈 Monitoring de la qualité

### Vérifier le taux de couverture

Après chaque génération via l'API `/generate_v2`, vérifier dans les logs:

```
⚠️  AVERTISSEMENT: X clés manquantes dans resolved_jsons_map
   Taux de couverture: Y%
```

**Objectif**: Taux de couverture > 90%

### Compter les hallucinations

Surveiller le nombre de warnings de clés fictives:

```
⚠️  AVERTISSEMENT: Le LLM a inventé X clé(s) fictive(s)
```

**Objectif**: 0 clé fictive (ou très peu)

## 🎯 Checklist de débogage

Si vous voyez beaucoup d'hallucinations:

- [ ] Vérifier que `_extract_all_json_paths()` génère les bons chemins
- [ ] Exécuter `test_extract_paths_improvements.py` pour valider
- [ ] Vérifier le prompt dans `_build_json_generation_prompt()`
- [ ] Exécuter `test_prompt_improvements.py` pour valider le prompt
- [ ] Vérifier que les clés source sont bien affichées au LLM
- [ ] Ajuster les `category_quotas` si nécessaire
- [ ] Vérifier que `path_groups` contient tous les groupes nécessaires

## 📚 Documentation complémentaire

- **[FINAL_SUMMARY.md](FINAL_SUMMARY.md)**: Résumé exécutif de toutes les améliorations
- **[IMPROVEMENTS_SUMMARY.md](IMPROVEMENTS_SUMMARY.md)**: Documentation technique détaillée

## 🆘 Résolution de problèmes

### "39 clés manquantes" après génération

**Cause**: `path_groups` ne contient pas tous les groupes nécessaires

**Solution**:
1. Exécuter `test_path_groups_coverage.py` pour analyser
2. Vérifier que le LLM de génération de `path_groups` fonctionne bien
3. Ajuster le prompt de génération de `path_groups` si nécessaire

### Le LLM continue d'utiliser [0], [1], [2]

**Cause**: Le prompt n'est peut-être pas assez explicite

**Solution**:
1. Exécuter `test_prompt_improvements.py` pour vérifier
2. Vérifier que les 6 vérifications passent
3. Si nécessaire, renforcer encore le prompt avec plus d'exemples

### Clés fictives persistantes

**Cause**: Le LLM n'a pas accès aux bonnes clés source ou les ignore

**Solution**:
1. Vérifier que `group["keys"]` contient bien toutes les clés
2. Vérifier que le prompt affiche ces clés au LLM
3. Ajouter plus d'exemples "INCORRECTS" dans le prompt

## ✅ Tests de régression

Avant chaque déploiement, exécuter:

```bash
./run_all_validation_tests.sh
```

**Résultat attendu**: `✅ Tests réussis: 5/5`
