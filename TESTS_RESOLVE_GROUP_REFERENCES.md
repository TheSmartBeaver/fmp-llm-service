# Tests pour `_resolve_group_references`

Ce document explique comment tester et comprendre la fonction `_resolve_group_references` qui résout les références de groupes imbriqués dans les templates JSON.

## 📚 Vue d'ensemble

La fonction `_resolve_group_references` prend en entrée:

1. **`group_jsons_map`**: Un dictionnaire de groupes de templates JSON qui peuvent contenir des références à d'autres groupes
2. **`path_to_value_map`**: Un dictionnaire contenant toutes les valeurs du JSON pédagogique original

Elle retourne un dictionnaire où toutes les références `{{groupe[x]}}` ont été remplacées par les structures JSON complètes des groupes correspondants.

## 🎯 Cas d'usage

Cette fonction est utilisée dans le pipeline de génération de templates:

```
JSON Pédagogique
      ↓
  LLM génère group_jsons_map (avec références {{...}})
      ↓
  _resolve_group_references (remplace les références)
      ↓
  Templates JSON complets et résolus
```

## 🧪 Tests disponibles

### 1. Test simple avec exemples concrets

**Fichier**: [`tests/test_resolve_simple_example.py`](tests/test_resolve_simple_example.py)

**Utilisation**:
```bash
python3 tests/test_resolve_simple_example.py
```

**Ce qu'il fait**:
- Montre 4 exemples simples et concrets de substitution
- Affiche clairement l'INPUT, le TRAITEMENT et l'OUTPUT
- Explique chaque substitution étape par étape

**Exemples**:
1. Substitution basique (un template référence un autre)
2. Substitution avec plusieurs niveaux
3. Substitution dans un tableau
4. Référence récursive (un groupe qui se référence lui-même)

**Idéal pour**: Comprendre le concept de base

---

### 2. Test avec exemples visuels

**Fichier**: [`tests/test_resolve_examples.py`](tests/test_resolve_examples.py)

**Utilisation**:
```bash
python3 tests/test_resolve_examples.py
```

**Ce qu'il fait**:
- Utilise les données réelles du dossier `_resolve_group_references`
- Montre 3 exemples de substitution avec les vraies données
- Affiche des statistiques et un résumé

**Idéal pour**: Voir des exemples réels du projet

---

### 3. Test détaillé avec toutes les étapes

**Fichier**: [`tests/test_resolve_group_references_detailed.py`](tests/test_resolve_group_references_detailed.py)

**Utilisation**:
```bash
python3 tests/test_resolve_group_references_detailed.py
```

**Ce qu'il fait**:
- Charge les données de test réelles (53 groupes, 204 chemins)
- Affiche TOUTES les étapes de résolution:
  - **ÉTAPE 1**: Analyse des références (187 références trouvées)
  - **ÉTAPE 2**: Résolution groupe par groupe
  - **ÉTAPE 3**: Résumé de chaque substitution (185 substitutions)
  - **ÉTAPE 4**: Vérification des clés manquantes

**Output**:
- Terminal: Affichage détaillé de toutes les étapes
- Fichier: `tests/_resolve_group_references/resolved_output.json` (245 Ko)

**Idéal pour**: Déboguer ou comprendre en profondeur

---

### 4. Test de validation des clés

**Fichier**: [`tests/test_resolve_group_references.py`](tests/test_resolve_group_references.py)

**Utilisation**:
```bash
python3 tests/test_resolve_group_references.py
```

**Ce qu'il fait**:
- Teste que la fonction détecte les clés manquantes
- Compare avec un `group_jsons_map` incomplet vs complet

**Idéal pour**: Vérifier la validation

---

## 📁 Données de test

Les données de test réelles se trouvent dans [`tests/_resolve_group_references/`](tests/_resolve_group_references/):

- **`group_jsons_map.json`** (42 Ko): 53 groupes de templates
- **`path_to_value_map.json`** (20 Ko): 204 chemins avec valeurs
- **`resolved_output.json`** (245 Ko): Résultat après résolution
- **`README.md`**: Documentation détaillée des données

## 📖 Comprendre les substitutions

### Exemple simple

**AVANT**:
```json
{
  "section": {
    "template_name": "section",
    "header": "{{titre}}",
    "content": "Contenu"
  },
  "titre": {
    "template_name": "text/titre",
    "text": "Mon Titre"
  }
}
```

**APRÈS résolution**:
```json
{
  "section": {
    "template_name": "section",
    "header": {
      "template_name": "text/titre",
      "text": "Mon Titre"
    },
    "content": "Contenu"
  },
  "titre": {
    "template_name": "text/titre",
    "text": "Mon Titre"
  }
}
```

**Explication**: La référence `{{titre}}` a été remplacée par la structure JSON complète du groupe `titre`.

### Types de références

1. **Simple**: `{{course}}` → groupe 'course'
2. **Imbriquée**: `{{summary->title}}` → groupe 'summary->title'
3. **Avec indices**: `{{themes[x]->groups[y]->label}}` → groupe avec indices
4. **Récursive**: Un groupe qui se référence lui-même

## 🔍 Statistiques sur les données réelles

Avec les données de test actuelles:

- **53 groupes** dans `group_jsons_map`
- **204 chemins** dans `path_to_value_map`
- **187 références** `{{...}}` détectées
- **185 substitutions** effectuées

## 📝 Ordre d'exécution recommandé

Pour comprendre progressivement:

1. **D'abord**: `test_resolve_simple_example.py` → Comprendre le concept
2. **Ensuite**: `test_resolve_examples.py` → Voir des exemples réels
3. **Enfin**: `test_resolve_group_references_detailed.py` → Voir tous les détails

## 🎓 Concepts clés

### 1. Qu'est-ce qu'une "référence de groupe"?

Une référence de groupe est une chaîne de caractères:
- Qui commence par `{{` et finit par `}}`
- Dont le contenu (sans les `{{` et `}}`) correspond à une clé dans `group_jsons_map`

Exemples:
- `{{course}}` → si 'course' existe dans `group_jsons_map`
- `{{summary->title}}` → si 'summary->title' existe dans `group_jsons_map`

### 2. Pourquoi résoudre les références?

Le LLM génère des templates qui utilisent des références pour éviter la duplication. Par exemple:

```json
{
  "glossary[x]->term": {
    "text": "{{glossary[x]->term}}: {{glossary[x]->definition}}"
  }
}
```

Cette référence sera remplacée par la vraie valeur au moment de l'instanciation.

### 3. Résolution récursive

La fonction résout récursivement:
- Dans les dictionnaires (pour chaque valeur)
- Dans les listes (pour chaque élément)
- Dans les chaînes (si c'est une référence)

Cela permet de gérer des structures imbriquées complexes.

## ⚠️ Points d'attention

1. **Références circulaires**: Un groupe qui se référence lui-même crée une structure infinie
2. **Clés manquantes**: Si un groupe référence une clé qui n'existe pas, la référence reste inchangée
3. **Profondeur**: La résolution peut créer des structures très profondes

## 🔧 Déboguer

Si vous avez un problème:

1. Vérifiez que la clé existe dans `group_jsons_map`
2. Exécutez `test_resolve_group_references_detailed.py` pour voir toutes les substitutions
3. Consultez `resolved_output.json` pour voir le résultat final
4. Vérifiez les warnings pour les clés manquantes

## 📚 Ressources

- [Code source de la fonction](app/chains/template_structure_generator.py#L1202)
- [Documentation des données de test](tests/_resolve_group_references/README.md)
- [Tests unitaires](tests/test_resolve_group_references.py)

## 💡 Utilisation dans le code

```python
from app.chains.template_structure_generator import TemplateStructureGenerator

generator = TemplateStructureGenerator(db_session=None, embedding_model=None)

# Construire path_to_value_map à partir du JSON pédagogique
path_to_value_map = generator._build_path_to_value_map(pedagogical_json)

# Résoudre les références
resolved_map = generator._resolve_group_references(
    group_jsons_map,
    path_to_value_map
)

# resolved_map contient maintenant tous les groupes avec références résolues
```

## 🎯 Résultat attendu

Après résolution:
- ✅ Toutes les références `{{...}}` sont remplacées par les structures JSON
- ✅ Les clés de `path_to_value_map` sont présentes dans les templates
- ✅ Le résultat peut être utilisé pour l'instanciation finale
