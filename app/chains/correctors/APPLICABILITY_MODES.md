# Modes d'Applicabilité des Correcteurs

Guide complet sur les modes d'applicabilité "any" vs "all".

## Vue d'ensemble

Chaque correcteur peut définir comment il détermine s'il est applicable en fonction des `template_names` présents dans la structure JSON.

Deux modes sont disponibles via l'attribut `applicability_mode` :

1. **"any"** (par défaut) - Au moins un template_name requis
2. **"all"** - Tous les template_names requis

## Mode "any" (par défaut)

### Définition

Le correcteur est applicable si **AU MOINS UN** de ses `template_names` est présent dans la structure.

### Syntaxe

```python
class MyCorrector(BaseCorrector):
    template_names = ["template/a", "template/b", "template/c"]
    applicability_mode = "any"  # Par défaut, peut être omis
```

### Comportement

| Templates présents | Applicable ? |
|-------------------|--------------|
| `template/a` | ✅ Oui |
| `template/b` | ✅ Oui |
| `template/c` | ✅ Oui |
| `template/a` + `template/b` | ✅ Oui |
| Tous présents | ✅ Oui |
| Aucun présent | ❌ Non |
| Autres templates | ❌ Non |

### Cas d'usage

✅ **Utilisez "any" quand** :
- Le correcteur peut agir sur plusieurs types de templates **indépendamment**
- Chaque template peut être corrigé séparément
- La présence d'un seul template suffit pour déclencher le correcteur

#### Exemples concrets

**LayoutSpacingCorrector**
```python
class LayoutSpacingCorrector(BaseCorrector):
    template_names = [
        "layouts/vertical_column/container",
        "layouts/horizontal_line/container"
    ]
    applicability_mode = "any"
```

Raison : Peut corriger le spacing d'un vertical_column sans avoir besoin d'un horizontal_line.

**TextOpacityCorrector**
```python
class TextOpacityCorrector(BaseCorrector):
    template_names = [
        "text/title",
        "text/description",
        "text/paragraph"
    ]
    applicability_mode = "any"
```

Raison : Peut corriger l'opacité de n'importe quel type de texte indépendamment.

## Mode "all"

### Définition

Le correcteur est applicable si **TOUS** ses `template_names` sont présents dans la structure.

### Syntaxe

```python
class MyCorrector(BaseCorrector):
    template_names = ["template/header", "template/footer"]
    applicability_mode = "all"
```

### Comportement

| Templates présents | Applicable ? |
|-------------------|--------------|
| `template/header` seulement | ❌ Non |
| `template/footer` seulement | ❌ Non |
| `template/header` + `template/footer` | ✅ Oui |
| Tous + autres templates | ✅ Oui |
| Aucun présent | ❌ Non |

### Cas d'usage

✅ **Utilisez "all" quand** :
- Le correcteur vérifie la **cohérence entre plusieurs templates**
- Tous les templates doivent être présents pour que la correction ait du sens
- Le correcteur fait des vérifications croisées entre templates

#### Exemples concrets

**HeaderFooterConsistencyCorrector**
```python
class HeaderFooterConsistencyCorrector(BaseCorrector):
    """Vérifie que le header et le footer ont le même style."""
    template_names = [
        "layouts/header",
        "layouts/footer"
    ]
    applicability_mode = "all"
    error_pattern = re.compile(r'...')
```

Raison : Ne peut vérifier la cohérence que si les deux templates sont présents.

**FormValidationCorrector**
```python
class FormValidationCorrector(BaseCorrector):
    """Vérifie que le form_input a un form_submit associé."""
    template_names = [
        "forms/input",
        "forms/submit"
    ]
    applicability_mode = "all"
    error_pattern = re.compile(r'...')
```

Raison : La validation nécessite la présence des deux types de templates.

**NavigationStructureCorrector**
```python
class NavigationStructureCorrector(BaseCorrector):
    """Assure la cohérence entre nav_menu, nav_item et nav_link."""
    template_names = [
        "navigation/menu",
        "navigation/item",
        "navigation/link"
    ]
    applicability_mode = "all"
    error_pattern = re.compile(r'...')
```

Raison : La structure complète de navigation doit être présente pour valider.

## Implémentation interne

### Méthode `is_applicable()`

La classe `BaseCorrector` fournit une méthode `is_applicable()` qui implémente la logique :

```python
def is_applicable(self, template_names_present: Set[str]) -> bool:
    if not self.template_names:
        return False

    corrector_templates = set(self.template_names)

    if self.applicability_mode == "all":
        # TOUS les template_names du correcteur doivent être présents
        return corrector_templates.issubset(template_names_present)
    else:
        # AU MOINS UN template_name doit être présent
        return bool(corrector_templates.intersection(template_names_present))
```

### Intégration dans CorrectorRegistry

Le registre appelle automatiquement `is_applicable()` pour chaque correcteur :

```python
def get_applicable_correctors(self, template_names: Set[str]) -> List[BaseCorrector]:
    applicable = []
    for corrector in self._correctors:
        if corrector.is_applicable(template_names):
            applicable.append(corrector)
    return applicable
```

## Exemples complets

### Exemple 1 : Mode "any" en action

```python
from app.chains.correctors import CorrectorRegistry, processSeriesOfCorrections

registry = CorrectorRegistry()
registry.register(LayoutSpacingCorrector())  # Mode "any"

structure = {
    "template_name": "layouts/vertical_column/container",
    "spacing": "invalid",
    "items": [
        {"template_name": "text/title", "text": "Hello"}
    ]
}

# LayoutSpacingCorrector sera applicable car "layouts/vertical_column/container" est présent
# (même si "layouts/horizontal_line/container" n'est pas présent)
corrected, stats = processSeriesOfCorrections(structure, registry)

print(stats["applicable_correctors_count"])  # 1
print(corrected["spacing"])  # "1rem"
```

### Exemple 2 : Mode "all" en action

```python
class HeaderFooterCorrector(BaseCorrector):
    template_names = ["layouts/header", "layouts/footer"]
    applicability_mode = "all"
    error_pattern = re.compile(r'"style"\s*:\s*"inconsistent"')

    @property
    def name(self):
        return "HeaderFooterCorrector"

    def apply_correction(self, json_obj):
        # Logique de correction...
        return json_obj

registry = CorrectorRegistry()
registry.register(HeaderFooterCorrector())

# Scénario 1 : Seulement header présent
structure1 = [
    {"template_name": "layouts/header", "style": "inconsistent"}
]

corrected1, stats1 = processSeriesOfCorrections(structure1, registry)
print(stats1["applicable_correctors_count"])  # 0 - Non applicable

# Scénario 2 : Header ET footer présents
structure2 = [
    {"template_name": "layouts/header", "style": "inconsistent"},
    {"template_name": "layouts/footer", "style": "inconsistent"}
]

corrected2, stats2 = processSeriesOfCorrections(structure2, registry)
print(stats2["applicable_correctors_count"])  # 1 - Applicable !
```

## Choix du bon mode

### Utilisez "any" si...

- ✅ Chaque template peut être traité indépendamment
- ✅ La correction d'un template n'affecte pas les autres
- ✅ Il n'y a pas de dépendances entre les templates

### Utilisez "all" si...

- ✅ Vous vérifiez des relations entre templates
- ✅ Tous les templates doivent être présents pour la correction
- ✅ Vous faites de la validation de cohérence
- ✅ Les templates forment un ensemble logique

## Tests

Exemple de tests pour les deux modes :

```python
def test_any_mode():
    corrector = AnyModeCorrector()
    corrector.template_names = ["a", "b", "c"]
    corrector.applicability_mode = "any"

    assert corrector.is_applicable({"a"}) is True
    assert corrector.is_applicable({"a", "b"}) is True
    assert corrector.is_applicable({"x"}) is False

def test_all_mode():
    corrector = AllModeCorrector()
    corrector.template_names = ["a", "b"]
    corrector.applicability_mode = "all"

    assert corrector.is_applicable({"a"}) is False
    assert corrector.is_applicable({"a", "b"}) is True
    assert corrector.is_applicable({"a", "b", "c"}) is True
```

## Performance

Le mode d'applicabilité est **évalué avant l'exécution** du correcteur, ce qui optimise les performances :

```
1. Extraction des template_names présents (une seule fois)
   ↓
2. Pour chaque correcteur : is_applicable() → O(n) où n = nombre de template_names
   ↓
3. Seuls les correcteurs applicables sont exécutés
```

Avec 100 correcteurs enregistrés mais seulement 5 applicables, vous économisez 95% d'exécutions inutiles !

## Résumé

| Critère | Mode "any" | Mode "all" |
|---------|-----------|-----------|
| Condition | AU MOINS 1 template présent | TOUS les templates présents |
| Défaut | ✅ Oui | ❌ Non |
| Usage typique | Corrections indépendantes | Validations de cohérence |
| Exemple | Corriger spacing dans layouts | Vérifier header + footer |

---

Pour plus d'informations, consultez :
- [README.md](README.md) - Documentation complète
- [QUICKSTART.md](QUICKSTART.md) - Guide de démarrage rapide
