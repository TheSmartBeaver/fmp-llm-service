# Mise à jour : Modes d'applicabilité des correcteurs

## 🎯 Résumé

Le système de corrections a été enrichi avec **deux modes d'applicabilité** pour les correcteurs :
- **"any"** (par défaut) : Le correcteur s'active si AU MOINS UN de ses template_names est présent
- **"all"** : Le correcteur s'active si TOUS ses template_names sont présents

## 📝 Modifications apportées

### 1. [base_corrector.py](app/chains/correctors/base_corrector.py)

**Ajouts** :
- Import de `Literal` pour le typage
- Attribut `applicability_mode: Literal["any", "all"] = "any"`
- Méthode `is_applicable(template_names_present: Set[str]) -> bool`

```python
# Nouvel attribut
applicability_mode: Literal["any", "all"] = "any"

# Nouvelle méthode
def is_applicable(self, template_names_present: Set[str]) -> bool:
    """Détermine si le correcteur est applicable."""
    if not self.template_names:
        return False

    corrector_templates = set(self.template_names)

    if self.applicability_mode == "all":
        return corrector_templates.issubset(template_names_present)
    else:
        return bool(corrector_templates.intersection(template_names_present))
```

### 2. [corrector_registry.py](app/chains/correctors/corrector_registry.py)

**Modification** de `get_applicable_correctors()` :

```python
# Avant
if any(tn in template_names for tn in corrector.template_names):
    applicable.append(corrector)

# Après
if corrector.is_applicable(template_names):
    applicable.append(corrector)
```

Le registre utilise maintenant la méthode `is_applicable()` du correcteur, qui respecte son mode.

### 3. [layout_spacing_corrector.py](app/chains/correctors/implementations/layout_spacing_corrector.py)

**Ajout** de l'attribut explicite (pour documentation) :

```python
# Mode d'applicabilité : le correcteur s'active si AU MOINS UN template est présent
applicability_mode = "any"
```

### 4. Documentation mise à jour

**Fichiers modifiés** :
- [README.md](app/chains/correctors/README.md) - Section "Modes d'applicabilité" ajoutée
- [QUICKSTART.md](app/chains/correctors/QUICKSTART.md) - Section et checklist mises à jour
- [APPLICABILITY_MODES.md](app/chains/correctors/APPLICABILITY_MODES.md) - **Nouveau** guide complet

### 5. Tests

**Nouveau fichier** : [test_applicability_modes.py](tests/test_applicability_modes.py)

Tests complets pour :
- Mode "any" avec un seul template
- Mode "any" avec tous les templates
- Mode "any" sans match
- Mode "all" avec un seul template (non applicable)
- Mode "all" avec tous les templates (applicable)
- Mode "all" avec templates extras
- Intégration avec CorrectorRegistry
- processSeriesOfCorrections avec les deux modes

**Résultats** : ✅ Tous les tests passent

## 🔧 Utilisation

### Mode "any" (par défaut)

```python
class MyCorrector(BaseCorrector):
    template_names = ["template/a", "template/b", "template/c"]
    applicability_mode = "any"  # Optionnel, c'est la valeur par défaut
    error_pattern = re.compile(r'...')

    # ...
```

**Applicable si** :
- ✅ Au moins un template présent
- ❌ Aucun template présent

### Mode "all"

```python
class CoherenceCorrector(BaseCorrector):
    template_names = ["template/header", "template/footer"]
    applicability_mode = "all"  # Requis pour mode "all"
    error_pattern = re.compile(r'...')

    # ...
```

**Applicable si** :
- ✅ TOUS les templates présents
- ❌ Un ou plusieurs templates manquants

## 📊 Cas d'usage

### Mode "any" - Corrections indépendantes

Utilisez quand le correcteur peut agir sur chaque template **indépendamment** :

- **LayoutSpacingCorrector** : Corrige le spacing de n'importe quel layout
- **TextOpacityCorrector** : Corrige l'opacité de n'importe quel texte
- **ImageUrlCorrector** : Corrige les URLs d'images

### Mode "all" - Validation de cohérence

Utilisez quand le correcteur vérifie la **cohérence entre templates** :

- **HeaderFooterConsistencyCorrector** : Vérifie que header et footer ont le même style
- **FormValidationCorrector** : Vérifie qu'un form_input a un form_submit
- **NavigationStructureCorrector** : Vérifie la cohérence menu/item/link

## 🧪 Exemples de tests

```python
# Test mode "any"
corrector = AnyModeCorrector()
corrector.template_names = ["a", "b", "c"]
corrector.applicability_mode = "any"

assert corrector.is_applicable({"a"}) is True         # ✅ Un seul suffit
assert corrector.is_applicable({"a", "b"}) is True    # ✅ Plusieurs aussi
assert corrector.is_applicable({"x"}) is False        # ❌ Aucun match

# Test mode "all"
corrector = AllModeCorrector()
corrector.template_names = ["a", "b"]
corrector.applicability_mode = "all"

assert corrector.is_applicable({"a"}) is False        # ❌ Il manque "b"
assert corrector.is_applicable({"a", "b"}) is True    # ✅ Tous présents
assert corrector.is_applicable({"a", "b", "c"}) is True  # ✅ OK avec extras
```

## 🔄 Rétrocompatibilité

✅ **100% rétrocompatible**

Les correcteurs existants continuent de fonctionner sans modification :
- `applicability_mode` a une valeur par défaut de `"any"`
- Le comportement par défaut est identique à l'ancienne implémentation
- Tous les tests existants passent

## 📈 Performance

Aucun impact négatif sur les performances :

**Avant** :
```python
# Vérification inline
if any(tn in template_names for tn in corrector.template_names):
    # O(n*m) où n=templates du correcteur, m=templates présents
```

**Après** :
```python
# Vérification via méthode
if corrector.is_applicable(template_names):
    # Mode "any": O(n) via intersection de sets
    # Mode "all": O(n) via issubset de sets
```

→ Amélioration avec l'utilisation de **sets** pour les opérations ensemblistes.

## 📚 Documentation

### Guides disponibles

1. **[README.md](app/chains/correctors/README.md)** - Documentation complète du système
2. **[QUICKSTART.md](app/chains/correctors/QUICKSTART.md)** - Guide de démarrage rapide
3. **[APPLICABILITY_MODES.md](app/chains/correctors/APPLICABILITY_MODES.md)** - Guide détaillé des modes (nouveau)
4. **[EXAMPLE.md](app/chains/correctors/EXAMPLE.md)** - Exemples concrets

### Checklist de création d'un correcteur

- [ ] Créer le fichier du correcteur dans `implementations/`
- [ ] Définir `template_names` (liste des templates concernés)
- [ ] Définir `error_pattern` (regex de détection)
- [ ] **[NOUVEAU]** Définir `applicability_mode` ("any" ou "all", optionnel)
- [ ] Implémenter `name` (nom du correcteur)
- [ ] Implémenter `apply_correction` (logique de correction + récursion)
- [ ] Ajouter l'import dans `implementations/__init__.py`
- [ ] Enregistrer dans `_initialize_corrector_registry()`
- [ ] Tester avec un cas réel

## ✅ Validation

### Tests exécutés

```bash
# Tests du système de base
PYTHONPATH=. .venv/bin/python tests/manual_test_correctors.py
✅ TOUS LES TESTS SONT PASSÉS !

# Tests des modes d'applicabilité
PYTHONPATH=. .venv/bin/python tests/test_applicability_modes.py
✅ TOUS LES TESTS SONT PASSÉS !

# Compilation
python3 -m py_compile app/chains/correctors/base_corrector.py
python3 -m py_compile app/chains/correctors/corrector_registry.py
✅ Compilation réussie
```

### Résultats

- ✅ 14 tests passés sur les modes d'applicabilité
- ✅ 6 tests de base passés (rétrocompatibilité)
- ✅ Aucune régression
- ✅ Code compile sans erreur

## 🚀 Prochaines étapes

Pour ajouter un correcteur avec mode "all" :

```python
# 1. Créer le correcteur
class MyCoherenceCorrector(BaseCorrector):
    template_names = ["template/a", "template/b"]
    applicability_mode = "all"  # ← Définir le mode
    error_pattern = re.compile(r'...')

    @property
    def name(self):
        return "MyCoherenceCorrector"

    def apply_correction(self, json_obj):
        # Logique de correction...
        return json_obj

# 2. L'enregistrer
registry.register(MyCoherenceCorrector())

# 3. Il ne s'activera que si template/a ET template/b sont présents !
```

---

## 📞 Questions ?

Consultez :
- [APPLICABILITY_MODES.md](app/chains/correctors/APPLICABILITY_MODES.md) pour le guide complet
- [README.md](app/chains/correctors/README.md) pour la documentation générale
- [QUICKSTART.md](app/chains/correctors/QUICKSTART.md) pour débuter rapidement
