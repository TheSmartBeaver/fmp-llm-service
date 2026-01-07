# Système de Corrections de Templates

Ce module implémente un système de corrections automatiques pour les structures JSON de templates générées par le LLM.

## Architecture

### Composants principaux

1. **BaseCorrector** : Classe abstraite de base pour tous les correcteurs
2. **CorrectorRegistry** : Registre centralisé des correcteurs
3. **CorrectionQueue** : Gestionnaire de file d'attente avec itérations multiples
4. **processSeriesOfCorrections** : Fonction principale d'orchestration

### Flux de traitement

```
template_structure (JSON)
         ↓
[1] Extraction des template_names présents
         ↓
[2] Sélection des correcteurs applicables
         ↓
[3] Application en boucle (max 10 itérations)
    │
    ├─ Pour chaque correcteur:
    │   ├─ Détection (via regex)
    │   ├─ Si erreur → Correction
    │   └─ Logging
    │
    └─ Arrêt si stabilité atteinte
         ↓
template_structure corrigé + statistiques
```

## Comment créer un nouveau correcteur

### Étape 1 : Créer la classe du correcteur

Créez un fichier dans `app/chains/correctors/implementations/` :

```python
# my_corrector.py
from typing import Any
import re
from app.chains.correctors.base_corrector import BaseCorrector


class MyCorrector(BaseCorrector):
    """
    Description de ce que corrige ce correcteur.
    """

    # Liste des template_names concernés
    template_names = [
        "layouts/my_template",
        "text/my_other_template"
    ]

    # Pattern regex pour détecter l'erreur
    error_pattern = re.compile(r'"field_name"\s*:\s*"invalid_pattern"')

    # Mode d'applicabilité (optionnel, par défaut "any")
    # - "any": Le correcteur s'active si AU MOINS UN template_name est présent
    # - "all": Le correcteur s'active si TOUS les template_names sont présents
    applicability_mode = "any"

    @property
    def name(self) -> str:
        return "MyCorrector"

    def apply_correction(self, json_obj: Any) -> Any:
        """
        Applique la correction de manière récursive.
        """
        if isinstance(json_obj, dict):
            # Vérifier si ce dict est un template concerné
            if json_obj.get("template_name") in self.template_names:
                if "field_name" in json_obj:
                    # Appliquer la correction
                    json_obj["field_name"] = "corrected_value"

            # Récursion sur toutes les valeurs
            for key, value in json_obj.items():
                json_obj[key] = self.apply_correction(value)

        elif isinstance(json_obj, list):
            return [self.apply_correction(item) for item in json_obj]

        return json_obj
```

### Étape 2 : Enregistrer le correcteur

1. Ajoutez l'import dans `implementations/__init__.py` :

```python
from app.chains.correctors.implementations.my_corrector import MyCorrector

__all__ = [
    "LayoutSpacingCorrector",
    "MyCorrector",  # ← Ajouter ici
]
```

2. Enregistrez-le dans `course_material_generator_v2.py` :

```python
def _initialize_corrector_registry(self) -> CorrectorRegistry:
    registry = CorrectorRegistry()

    registry.register(LayoutSpacingCorrector())
    registry.register(MyCorrector())  # ← Ajouter ici

    return registry
```

### Étape 3 : Tester

Le correcteur sera automatiquement appelé si les `template_names` concernés sont présents dans la structure.

## Exemples de correcteurs

### LayoutSpacingCorrector

Corrige les valeurs de `spacing` invalides dans les layouts :

- **Templates concernés** : `layouts/vertical_column/container`, `layouts/horizontal_line/container`
- **Erreur détectée** : `"spacing": "invalid"` (valeur ne commençant pas par un chiffre)
- **Correction** : Remplace par `"1rem"`

**Exemple** :

```json
// Avant
{
  "template_name": "layouts/vertical_column/container",
  "spacing": "invalid_value"
}

// Après
{
  "template_name": "layouts/vertical_column/container",
  "spacing": "1rem"
}
```

## Fonctionnalités

### Modes d'applicabilité (any vs all)

Chaque correcteur peut définir son mode d'applicabilité via l'attribut `applicability_mode` :

#### Mode "any" (par défaut)
Le correcteur est applicable si **AU MOINS UN** de ses `template_names` est présent.

**Exemple** :
```python
class MyCorrector(BaseCorrector):
    template_names = ["template/a", "template/b", "template/c"]
    applicability_mode = "any"  # Par défaut
```

- Si seulement `template/a` est présent → ✅ Applicable
- Si `template/a` et `template/b` sont présents → ✅ Applicable
- Si aucun n'est présent → ❌ Non applicable

**Cas d'usage** : Correcteurs qui peuvent agir sur plusieurs types de templates indépendamment.

#### Mode "all"
Le correcteur est applicable si **TOUS** ses `template_names` sont présents.

**Exemple** :
```python
class ComplexCorrector(BaseCorrector):
    template_names = ["template/header", "template/footer"]
    applicability_mode = "all"
```

- Si seulement `template/header` est présent → ❌ Non applicable
- Si `template/header` et `template/footer` sont présents → ✅ Applicable
- Si aucun n'est présent → ❌ Non applicable

**Cas d'usage** : Correcteurs qui nécessitent la présence simultanée de plusieurs templates pour fonctionner (ex: vérifier la cohérence entre header et footer).

### Optimisation par template_names

Seuls les correcteurs applicables (selon leur mode) sont exécutés, optimisant ainsi les performances.

### Itérations multiples

Le système applique les correcteurs en boucle (max 10 itérations) car :
- Une correction peut en révéler une autre
- Les correcteurs peuvent dépendre les uns des autres

Le système s'arrête automatiquement quand plus aucune correction n'est appliquée.

### Gestion d'erreurs robuste

Si un correcteur échoue :
- L'erreur est loggée
- Les autres correcteurs continuent leur travail
- Pas de blocage du processus

### Logging complet

Chaque action est loggée :
- Template_names détectés
- Correcteurs applicables
- Détections d'erreurs
- Applications de corrections
- Erreurs rencontrées

### Statistiques détaillées

Retourne un dict de stats :

```python
{
    "total_iterations": 3,
    "corrections_by_corrector": {
        "LayoutSpacingCorrector": 2,
        "MyCorrector": 1
    },
    "errors": [],
    "template_names_found": ["layouts/vertical_column/container", ...],
    "applicable_correctors_count": 2
}
```

## API

### processSeriesOfCorrections

```python
def processSeriesOfCorrections(
    template_structure: Union[Dict, List],
    registry: CorrectorRegistry,
    max_iterations: int = 10
) -> Tuple[Union[Dict, List], Dict[str, Any]]
```

**Paramètres** :
- `template_structure` : Structure JSON à corriger
- `registry` : Registre contenant les correcteurs
- `max_iterations` : Nombre max d'itérations (défaut: 10)

**Retour** :
- Tuple `(structure_corrigée, statistiques)`

## Bonnes pratiques

### 1. Regex précise

Votre regex doit détecter l'erreur de manière précise sans faux positifs :

```python
# ✅ BON - détecte spacing non-numérique
error_pattern = re.compile(r'"spacing"\s*:\s*"[^0-9]')

# ❌ MAUVAIS - trop large, faux positifs
error_pattern = re.compile(r'"spacing"')
```

### 2. Correction idempotente

Votre correcteur doit être idempotent : l'appliquer plusieurs fois donne le même résultat.

```python
# ✅ BON - idempotent
if spacing and not spacing[0].isdigit():
    json_obj["spacing"] = "1rem"

# ❌ MAUVAIS - pas idempotent
json_obj["spacing"] = json_obj["spacing"] + "_fixed"
```

### 3. Récursion complète

Parcourez toute la structure (dict et list) :

```python
# ✅ BON - récursion complète
if isinstance(json_obj, dict):
    # Correction
    for key, value in json_obj.items():
        json_obj[key] = self.apply_correction(value)
elif isinstance(json_obj, list):
    return [self.apply_correction(item) for item in json_obj]
```

### 4. Logging informatif

Utilisez un nom descriptif pour faciliter le debugging :

```python
@property
def name(self) -> str:
    return "LayoutSpacingCorrector"  # Descriptif et unique
```

## Tests

Pour tester un correcteur :

```python
from app.chains.correctors import CorrectorRegistry, processSeriesOfCorrections
from app.chains.correctors.implementations import MyCorrector

# Créer un registre de test
registry = CorrectorRegistry()
registry.register(MyCorrector())

# Structure de test
test_structure = {
    "template_name": "layouts/my_template",
    "field_name": "invalid_value"
}

# Appliquer les corrections
corrected, stats = processSeriesOfCorrections(test_structure, registry)

print(f"Corrections appliquées: {stats['corrections_by_corrector']}")
print(f"Structure corrigée: {corrected}")
```

## Intégration

Le système est intégré à la ligne 143 de `course_material_generator_v2.py` :

```python
# Appliquer les corrections sur la structure de templates
template_structure, correction_stats = processSeriesOfCorrections(
    template_structure, self.corrector_registry
)

# Les stats sont ajoutées aux debug_info
debug_info["correction_stats"] = correction_stats
```

Les statistiques sont ensuite disponibles dans le retour de `generate_course_material_async()`.
