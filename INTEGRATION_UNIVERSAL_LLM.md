# Intégration de UniversalLLM dans CourseMaterialGeneratorV2

Ce guide explique comment modifier `CourseMaterialGeneratorV2` pour supporter **tous** les modèles LLM, y compris Codex et O-series.

## 🎯 Objectif

Permettre à `CourseMaterialGeneratorV2` d'utiliser n'importe quel modèle (Gemini, Claude, GPT, **Codex**, O-series) de manière transparente.

## 📝 Modifications à apporter

### Étape 1 : Import du wrapper

**Fichier** : `app/chains/course_material_generator_v2.py`

```python
# Ajouter cet import en haut du fichier
from app.chains.llm.universal_llm import create_universal_llm
```

### Étape 2 : Modifier le constructeur

**Avant** (ligne 54-56) :

```python
# LLM pour la génération du JSON pédagogique
self.pedagogical_llm = LLMModelFactory.get_llm(
    self.llm_config.get_pedagogical_json_model()
)
```

**Après** :

```python
# LLM pour la génération du JSON pédagogique
# ✅ Supporte maintenant TOUS les modèles (LangChain + Codex + O-series)
pedagogical_model = self.llm_config.get_pedagogical_json_model()
self.pedagogical_llm = create_universal_llm(pedagogical_model)
```

### Étape 3 : C'est tout !

Le reste du code fonctionne **exactement pareil** ! Les chaînes LangChain comme :

```python
chain = prompt | self.pedagogical_llm | JsonOutputParser()
```

fonctionnent avec **tous** les modèles maintenant.

## 🔧 Code complet modifié

Voici le constructeur `__init__` complet avec la modification :

```python
def __init__(
    self,
    db_session: Session,
    embedding_model: SentenceTransformer,
    llm_config: Optional[LLMConfigDto] = None,
):
    """
    Args:
        db_session: Session SQLAlchemy pour accéder à la DB
        embedding_model: Modèle sentence-transformers pour les embeddings
        llm_config: Configuration optionnelle des modèles LLM à utiliser
    """
    self.db = db_session
    self.embedding_model = embedding_model
    self.llm_config = llm_config or LLMConfigDto()

    # LLM pour la génération du JSON pédagogique
    # ✅ Utilise UniversalLLM pour supporter TOUS les modèles
    pedagogical_model = self.llm_config.get_pedagogical_json_model()
    self.pedagogical_llm = create_universal_llm(pedagogical_model)

    # Créer le TemplateStructureGenerator avec la config LLM
    self.template_structure_generator = TemplateStructureGenerator(
        db_session=db_session,
        embedding_model=embedding_model,
        llm_config=self.llm_config,
    )
```

## 🎨 Utilisation avec Codex

Une fois la modification faite, vous pouvez utiliser Codex :

```python
from app.models.dto.llm_config.llm_config_dto import LLMConfigDto
from app.chains.course_material_generator_v2 import CourseMaterialGeneratorV2

# Configuration avec Codex pour la génération pédagogique
llm_config = LLMConfigDto(
    pedagogical_json_model="gpt-5.1-codex",  # ✅ Fonctionne maintenant !
    group_json_model=LLMModel.GEMINI_2_5_FLASH,
    path_groups_model=LLMModel.GPT_5_MINI
)

generator = CourseMaterialGeneratorV2(
    db_session=db,
    embedding_model=embedding_model,
    llm_config=llm_config
)

# Générer le matériel de cours
result = await generator.generate_course_material_async(
    user_entry=user_entry,
    top_k=20
)
```

## ⚠️ Important : Type de `pedagogical_json_model`

Le type du champ `pedagogical_json_model` dans `LLMConfigDto` doit accepter **à la fois** `LLMModel` enum **et** `str` pour Codex.

### Option 1 : Modifier `LLMConfigDto`

**Fichier** : `app/models/dto/llm_config/llm_config_dto.py`

```python
from typing import Optional, Union
from app.chains.llm.llm_factory import LLMModel

class LLMConfigDto:
    def __init__(
        self,
        pedagogical_json_model: Optional[Union[LLMModel, str]] = None,
        group_json_model: Optional[Union[LLMModel, str]] = None,
        path_groups_model: Optional[Union[LLMModel, str]] = None,
    ):
        self.pedagogical_json_model = pedagogical_json_model or LLMModel.GEMINI_2_5_FLASH
        self.group_json_model = group_json_model or LLMModel.GEMINI_2_5_FLASH
        self.path_groups_model = path_groups_model or LLMModel.GEMINI_2_5_FLASH

    def get_pedagogical_json_model(self) -> Union[LLMModel, str]:
        return self.pedagogical_json_model

    def get_group_json_model(self) -> Union[LLMModel, str]:
        return self.group_json_model

    def get_path_groups_model(self) -> Union[LLMModel, str]:
        return self.path_groups_model
```

### Option 2 : Wrapper intelligent dans `create_universal_llm`

Le wrapper `create_universal_llm` gère déjà automatiquement `LLMModel` enum ou `str`, donc si `LLMConfigDto` retourne l'un ou l'autre, ça fonctionne !

```python
# Fonctionne avec enum
pedagogical_model = LLMModel.GEMINI_2_5_FLASH
llm = create_universal_llm(pedagogical_model)  # ✅

# Fonctionne avec string
pedagogical_model = "gpt-5.1-codex"
llm = create_universal_llm(pedagogical_model)  # ✅
```

## 📊 Comparaison avant/après

### Avant

```python
# ❌ Seulement modèles LangChain
llm_config = LLMConfigDto(
    pedagogical_json_model=LLMModel.GEMINI_2_5_FLASH,  # OK
    # pedagogical_json_model="gpt-5.1-codex",  # ❌ Ne fonctionne pas
)
```

### Après

```python
# ✅ TOUS les modèles
llm_config = LLMConfigDto(
    pedagogical_json_model=LLMModel.GEMINI_2_5_FLASH,  # ✅ OK
    # ou
    pedagogical_json_model="gpt-5.1-codex",  # ✅ OK maintenant !
    # ou
    pedagogical_json_model=LLMModel.CLAUDE_HAIKU_4_5_20251001,  # ✅ OK
)
```

## 🔄 Modification de `TemplateStructureGenerator`

Si `TemplateStructureGenerator` utilise aussi des LLMs, appliquez la même modification :

**Fichier** : `app/chains/template_structure_generator.py`

```python
from app.chains.llm.universal_llm import create_universal_llm

class TemplateStructureGenerator:
    def __init__(self, db_session, embedding_model, llm_config=None):
        self.llm_config = llm_config or LLMConfigDto()

        # Modifier les lignes qui créent les LLMs
        self.group_json_llm = create_universal_llm(
            self.llm_config.get_group_json_model()
        )

        self.path_groups_llm = create_universal_llm(
            self.llm_config.get_path_groups_model()
        )
```

## 🧪 Tests

### Test 1 : Avec modèle LangChain (pas de changement)

```python
llm_config = LLMConfigDto(
    pedagogical_json_model=LLMModel.GEMINI_2_5_FLASH
)

generator = CourseMaterialGeneratorV2(db, embedding_model, llm_config)
result = await generator.generate_course_material_async(user_entry)

# ✅ Fonctionne comme avant
```

### Test 2 : Avec Codex (nouveau !)

```python
llm_config = LLMConfigDto(
    pedagogical_json_model="gpt-5.1-codex"
)

generator = CourseMaterialGeneratorV2(db, embedding_model, llm_config)
result = await generator.generate_course_material_async(user_entry)

# ✅ Fonctionne maintenant !
```

### Test 3 : Mix de modèles

```python
llm_config = LLMConfigDto(
    pedagogical_json_model="gpt-5.1-codex",  # Codex
    group_json_model=LLMModel.GEMINI_2_5_FLASH,  # Gemini
    path_groups_model=LLMModel.CLAUDE_HAIKU_4_5_20251001  # Claude
)

# ✅ Chaque LLM utilise le bon endpoint automatiquement
```

## 📝 Checklist de migration

- [ ] Ajouter l'import `from app.chains.llm.universal_llm import create_universal_llm`
- [ ] Remplacer `LLMModelFactory.get_llm()` par `create_universal_llm()`
- [ ] (Optionnel) Modifier `LLMConfigDto` pour accepter `Union[LLMModel, str]`
- [ ] Tester avec un modèle LangChain (doit fonctionner comme avant)
- [ ] Tester avec Codex (`"gpt-5.1-codex"`)
- [ ] S'assurer que le serveur FastAPI est démarré pour les tests Codex

## 💡 Pourquoi c'est mieux ?

| Aspect | Avant | Après |
|--------|-------|-------|
| Modèles supportés | 34 (LangChain) | 44 (LangChain + Codex + O-series) |
| Code à modifier | Beaucoup (2 chemins différents) | Minimal (1 ligne) |
| Maintenance | Difficile (2 APIs) | Facile (1 interface) |
| Flexibilité | Limitée | Maximale |

## 🚀 Résumé

**Une seule ligne à changer** dans `CourseMaterialGeneratorV2` :

```python
# Avant
self.pedagogical_llm = LLMModelFactory.get_llm(pedagogical_model)

# Après
self.pedagogical_llm = create_universal_llm(pedagogical_model)
```

Et vous pouvez maintenant utiliser **n'importe quel modèle** (Gemini, Claude, GPT, Codex, O-series) de manière totalement transparente ! 🎉

---

**Version** : 1.0.0
**Date** : 2026-01-06
