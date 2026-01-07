# Quick Start - Système de Corrections

Guide rapide pour utiliser et étendre le système de corrections.

## 🚀 Utilisation

Le système est **déjà intégré** dans `CourseMaterialGeneratorV2` à la ligne 143.

Lorsque vous générez des supports de cours, les corrections sont **automatiquement appliquées** :

```python
result = await generator.generate_course_material_async(user_entry)

# Les corrections ont été appliquées automatiquement
support = result["support"]  # Structure corrigée
stats = result["debug_info"]["correction_stats"]  # Statistiques

print(f"Corrections appliquées: {stats['corrections_by_corrector']}")
```

## ➕ Ajouter un nouveau correcteur

### Étape 1 : Créer le correcteur

Créez `app/chains/correctors/implementations/mon_correcteur.py` :

```python
from typing import Any
import re
from app.chains.correctors.base_corrector import BaseCorrector


class MonCorrector(BaseCorrector):
    """
    Corrige [DESCRIPTION DU PROBLÈME].

    Exemple : Remplace les valeurs opacity négatives par 1.0
    """

    # Templates concernés
    template_names = [
        "text/title",
        "text/description"
    ]

    # Pattern pour détecter l'erreur
    error_pattern = re.compile(r'"opacity"\s*:\s*-\d+')

    # Mode d'applicabilité (optionnel, par défaut "any")
    # - "any": applicable si AU MOINS UN template_name est présent
    # - "all": applicable si TOUS les template_names sont présents
    applicability_mode = "any"

    @property
    def name(self) -> str:
        return "MonCorrector"

    def apply_correction(self, json_obj: Any) -> Any:
        """Applique la correction récursivement."""
        if isinstance(json_obj, dict):
            # Vérifier si c'est un template concerné
            if json_obj.get("template_name") in self.template_names:
                # Appliquer la correction
                if "opacity" in json_obj and json_obj["opacity"] < 0:
                    json_obj["opacity"] = 1.0

            # Récursion sur tous les champs
            for key, value in json_obj.items():
                json_obj[key] = self.apply_correction(value)

        elif isinstance(json_obj, list):
            return [self.apply_correction(item) for item in json_obj]

        return json_obj
```

### Étape 2 : Exporter le correcteur

Modifiez `app/chains/correctors/implementations/__init__.py` :

```python
from app.chains.correctors.implementations.layout_spacing_corrector import (
    LayoutSpacingCorrector,
)
from app.chains.correctors.implementations.mon_correcteur import (
    MonCorrector,  # ← Ajouter ici
)

__all__ = [
    "LayoutSpacingCorrector",
    "MonCorrector",  # ← Ajouter ici
]
```

### Étape 3 : Enregistrer le correcteur

Modifiez `app/chains/course_material_generator_v2.py`, dans la méthode `_initialize_corrector_registry` :

```python
def _initialize_corrector_registry(self) -> CorrectorRegistry:
    registry = CorrectorRegistry()

    registry.register(LayoutSpacingCorrector())
    registry.register(MonCorrector())  # ← Ajouter ici

    return registry
```

### Étape 4 : Tester

```python
# Le correcteur sera automatiquement appelé si les template_names concernés sont présents
result = await generator.generate_course_material_async(user_entry)

# Vérifier les stats
stats = result["debug_info"]["correction_stats"]
print(stats["corrections_by_corrector"])
# Sortie: {'LayoutSpacingCorrector': 2, 'MonCorrector': 1}
```

## 📋 Template de correcteur

Copiez ce template pour créer rapidement un nouveau correcteur :

```python
from typing import Any
import re
from app.chains.correctors.base_corrector import BaseCorrector


class TEMPLATE_Corrector(BaseCorrector):
    """
    [DESCRIPTION DU PROBLÈME À CORRIGER]
    """

    # Liste des template_names concernés
    template_names = [
        "category/template1",
        "category/template2",
    ]

    # Pattern regex pour détecter l'erreur dans le JSON string
    # Ex: détecte "field": "invalid_pattern"
    error_pattern = re.compile(r'"FIELD_NAME"\s*:\s*"PATTERN_TO_MATCH"')

    # Mode d'applicabilité (optionnel, par défaut "any")
    # - "any": applicable si AU MOINS UN template_name est présent
    # - "all": applicable si TOUS les template_names sont présents
    applicability_mode = "any"

    @property
    def name(self) -> str:
        return "TEMPLATE_Corrector"

    def apply_correction(self, json_obj: Any) -> Any:
        """Applique la correction récursivement."""
        if isinstance(json_obj, dict):
            # Vérifier si c'est un template concerné
            if json_obj.get("template_name") in self.template_names:
                # Appliquer votre correction ici
                if "FIELD_NAME" in json_obj:
                    # Condition de correction
                    if CONDITION:
                        json_obj["FIELD_NAME"] = "VALEUR_CORRIGEE"

            # Récursion (IMPORTANT : ne pas oublier)
            for key, value in json_obj.items():
                json_obj[key] = self.apply_correction(value)

        elif isinstance(json_obj, list):
            # Récursion sur les listes
            return [self.apply_correction(item) for item in json_obj]

        return json_obj
```

## 🎯 Modes d'applicabilité

### Mode "any" (par défaut)
Le correcteur s'active si **AU MOINS UN** de ses template_names est présent.

```python
class AnyModeCorrector(BaseCorrector):
    template_names = ["template/a", "template/b", "template/c"]
    applicability_mode = "any"  # Par défaut
```

✅ Applicable si : `template/a` présent
✅ Applicable si : `template/a` + `template/b` présents
❌ Non applicable si : aucun présent

**Cas d'usage** : Correcteurs qui peuvent agir sur plusieurs types de templates indépendamment.

### Mode "all"
Le correcteur s'active si **TOUS** ses template_names sont présents.

```python
class AllModeCorrector(BaseCorrector):
    template_names = ["template/header", "template/footer"]
    applicability_mode = "all"
```

❌ Non applicable si : seulement `template/header` présent
✅ Applicable si : `template/header` + `template/footer` présents
❌ Non applicable si : aucun présent

**Cas d'usage** : Correcteurs qui vérifient la cohérence entre plusieurs templates qui doivent être présents ensemble.

## 🎯 Exemples de patterns regex

```python
# Détecter une valeur de string non numérique
re.compile(r'"spacing"\s*:\s*"[^0-9]')

# Détecter un nombre négatif
re.compile(r'"opacity"\s*:\s*-\d+')

# Détecter une URL invalide (pas http/https)
re.compile(r'"url"\s*:\s*"(?!https?://)')

# Détecter un boolean en string au lieu de boolean
re.compile(r'"enabled"\s*:\s*"(true|false)"')

# Détecter un champ vide
re.compile(r'"title"\s*:\s*""')
```

## ✅ Checklist de création

- [ ] Créer le fichier du correcteur dans `implementations/`
- [ ] Définir `template_names` (liste des templates concernés)
- [ ] Définir `error_pattern` (regex de détection)
- [ ] Définir `applicability_mode` ("any" ou "all", optionnel)
- [ ] Implémenter `name` (nom du correcteur)
- [ ] Implémenter `apply_correction` (logique de correction + récursion)
- [ ] Ajouter l'import dans `implementations/__init__.py`
- [ ] Enregistrer dans `_initialize_corrector_registry()`
- [ ] Tester avec un cas réel

## 🔍 Debugging

### Voir les logs

```python
import logging
logging.basicConfig(level=logging.INFO)

# Les logs du système s'afficheront :
# INFO - Template_names détectés: {...}
# INFO - 2/5 correcteurs applicables
# INFO - [Iteration 1] MonCorrector: Erreur détectée, application de la correction
# INFO - Stabilité atteinte après 2 itération(s)
```

### Tester un correcteur isolément

```python
from app.chains.correctors.implementations import MonCorrector

corrector = MonCorrector()

# Tester la détection
json_str = '{"template_name": "text/title", "opacity": -1}'
print(corrector.detect_error(json_str))  # True si erreur détectée

# Tester la correction
structure = {"template_name": "text/title", "opacity": -1}
corrected = corrector.apply_correction(structure)
print(corrected)  # {"template_name": "text/title", "opacity": 1.0}
```

## 📊 Statistiques retournées

```python
{
    "total_iterations": 2,              # Nombre d'itérations effectuées
    "corrections_by_corrector": {       # Corrections par correcteur
        "LayoutSpacingCorrector": 3,
        "MonCorrector": 1
    },
    "errors": [],                       # Erreurs rencontrées (si un correcteur échoue)
    "template_names_found": [           # Template_names détectés
        "layouts/vertical_column/container",
        "text/title"
    ],
    "applicable_correctors_count": 2    # Nombre de correcteurs applicables
}
```

## 🎓 Ressources

- **Documentation complète** : [`README.md`](README.md)
- **Exemples détaillés** : [`EXAMPLE.md`](EXAMPLE.md)
- **Implémentation** : [`IMPLEMENTATION_CORRECTORS.md`](../../IMPLEMENTATION_CORRECTORS.md)

## 💡 Bonnes pratiques

1. **Regex précise** : Évitez les faux positifs
2. **Idempotence** : Appliquer 2 fois doit donner le même résultat
3. **Récursion complète** : Parcourez dict ET list
4. **Nom descriptif** : Utilisez un nom clair pour le debugging
5. **Testez isolément** : Vérifiez détection + correction séparément

---

**Questions ?** Consultez la documentation complète dans [`README.md`](README.md)
