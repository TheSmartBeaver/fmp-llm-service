# Guide de l'enum AllLLMModels

## 🎯 Pourquoi cet enum ?

L'enum `AllLLMModels` centralise **TOUS** les 45 modèles LLM supportés par l'application dans un seul endroit, offrant :

- ✅ **Auto-complétion** dans votre IDE
- ✅ **Validation automatique** dans FastAPI
- ✅ **Type safety** en Python
- ✅ **Documentation intégrée** de tous les modèles disponibles

## 📦 Modèles disponibles

### Total : 45 modèles

- **5 modèles** Google Gemini
- **8 modèles** OpenAI GPT-5 Series
- **5 modèles** OpenAI GPT-5 Codex ⭐ (via UniversalLLM)
- **6 modèles** OpenAI GPT-4 Series
- **2 modèles** OpenAI Realtime
- **6 modèles** OpenAI O-Series ⭐ (dont 5 via UniversalLLM)
- **3 modèles** OpenAI Search
- **7 modèles** Anthropic Claude 3 Series
- **3 modèles** Anthropic Claude 4 Series

## 🚀 Utilisation

### 1. Dans un DTO Pydantic

```python
from pydantic import BaseModel
from app.models.dto.llm_config.all_llm_models import AllLLMModels

class MyConfig(BaseModel):
    model: AllLLMModels  # Auto-complétion de tous les modèles !

# Usage
config = MyConfig(model=AllLLMModels.GPT_5_1_CODEX)
```

### 2. Dans une route FastAPI

```python
from fastapi import APIRouter
from app.models.dto.llm_config.all_llm_models import AllLLMModels

router = APIRouter()

@router.post("/generate")
async def generate(
    model: AllLLMModels  # Validation automatique + doc Swagger
):
    return {"model": model.value}
```

### 3. Avec LLMConfigDto

```python
from app.models.dto.llm_config.llm_config_dto import LLMConfigDto
from app.models.dto.llm_config.all_llm_models import AllLLMModels

# Utilisation de l'enum (recommandé)
config = LLMConfigDto(
    pedagogical_json_model=AllLLMModels.GPT_5_1_CODEX,
    group_json_model=AllLLMModels.GEMINI_2_5_FLASH,
    path_groups_model=AllLLMModels.CLAUDE_HAIKU_4_5_20251001
)

# Ou avec des strings (compatible)
config = LLMConfigDto(
    pedagogical_json_model="gpt-5.1-codex",
    group_json_model="gemini-2.5-flash",
    path_groups_model="claude-haiku-4-5-20251001"
)
```

### 4. Vérifier si un modèle est Codex

```python
from app.models.dto.llm_config.all_llm_models import AllLLMModels, is_codex_model

model = AllLLMModels.GPT_5_1_CODEX

if is_codex_model(model):
    print("Ce modèle utilise la route Codex")
else:
    print("Ce modèle utilise LangChain standard")
```

## 📝 Exemples complets

### Exemple 1 : Génération de cours avec Codex

```python
from app.models.dto.llm_config.llm_config_dto import LLMConfigDto
from app.models.dto.llm_config.all_llm_models import AllLLMModels
from app.chains.course_material_generator_v2 import CourseMaterialGeneratorV2

# Configuration avec auto-complétion
llm_config = LLMConfigDto(
    pedagogical_json_model=AllLLMModels.GPT_5_1_CODEX,  # Génération de code
    group_json_model=AllLLMModels.O3_MINI,              # Raisonnement
    path_groups_model=AllLLMModels.GEMINI_2_5_FLASH    # Rapidité
)

# Utilisation
generator = CourseMaterialGeneratorV2(db, embedding_model, llm_config)
result = await generator.generate_course_material_async(user_entry, top_k=20)
```

### Exemple 2 : Route FastAPI avec validation

```python
from fastapi import APIRouter, Body
from app.models.dto.llm_config.all_llm_models import AllLLMModels

router = APIRouter()

@router.post("/generate")
async def generate_content(
    model: AllLLMModels = Body(..., description="Modèle LLM à utiliser")
):
    """
    Génère du contenu avec le modèle spécifié.

    L'auto-complétion et la validation sont automatiques grâce à l'enum !
    """
    # UniversalLLM gère automatiquement Codex et LangChain
    from app.chains.llm.universal_llm import create_universal_llm

    llm = create_universal_llm(model.value)
    response = await llm.ainvoke("Générer du contenu...")

    return {"model": model.value, "response": response}
```

### Exemple 3 : Boucle sur tous les modèles Codex

```python
from app.models.dto.llm_config.all_llm_models import AllLLMModels, CODEX_MODELS

# Tester tous les modèles Codex
for model in CODEX_MODELS:
    print(f"Testing {model.value}...")
    llm = create_universal_llm(model.value)
    # Test...
```

## 🔍 Référence des modèles

### Modèles Codex (5)
```python
AllLLMModels.GPT_5_1_CODEX_MAX      # "gpt-5.1-codex-max"
AllLLMModels.GPT_5_1_CODEX          # "gpt-5.1-codex" ⭐ Recommandé
AllLLMModels.GPT_5_CODEX            # "gpt-5-codex"
AllLLMModels.GPT_5_1_CODEX_MINI     # "gpt-5.1-codex-mini"
AllLLMModels.CODEX_MINI_LATEST      # "codex-mini-latest"
```

### Modèles O-Series (6)
```python
AllLLMModels.O1_MINI                # "o1-mini" (LangChain compatible)
AllLLMModels.O3                     # "o3"
AllLLMModels.O3_MINI                # "o3-mini" ⭐ Recommandé
AllLLMModels.O3_DEEP_RESEARCH       # "o3-deep-research"
AllLLMModels.O4_MINI                # "o4-mini"
AllLLMModels.O4_MINI_DEEP_RESEARCH  # "o4-mini-deep-research"
```

### Modèles Gemini (5)
```python
AllLLMModels.GEMINI_2_5_FLASH       # "gemini-2.5-flash" ⭐ Recommandé
AllLLMModels.GEMINI_2_5_FLASH_LITE  # "gemini-2.5-flash-lite"
AllLLMModels.GEMINI_3_FLASH_PREVIEW # "gemini-3-flash-preview"
AllLLMModels.GEMINI_2_0_FLASH       # "gemini-2.0-flash"
AllLLMModels.GEMINI_2_0_FLASH_LITE  # "gemini-2.0-flash-lite"
```

### Modèles Claude (10)
```python
# Claude 3 Series
AllLLMModels.CLAUDE_HAIKU_4_5_20251001    # ⭐ Recommandé
AllLLMModels.CLAUDE_3_5_HAIKU_20241022
AllLLMModels.CLAUDE_3_HAIKU_20240307
# ... et 7 autres

# Claude 4 Series
AllLLMModels.CLAUDE_SONNET_4_5_20250929   # ⭐ Recommandé
AllLLMModels.CLAUDE_SONNET_4_20250514
AllLLMModels.CLAUDE_OPUS_4_5
```

### Modèles GPT (16)
```python
# GPT-5 Series
AllLLMModels.GPT_5_2                # "gpt-5.2"
AllLLMModels.GPT_5_MINI             # "gpt-5-mini" ⭐ Recommandé
# ... et 6 autres

# GPT-4 Series
AllLLMModels.GPT_4O                 # "gpt-4o"
AllLLMModels.GPT_4O_MINI            # "gpt-4o-mini"
# ... et 4 autres
```

## 📊 Swagger / OpenAPI

Lorsque vous utilisez `AllLLMModels` dans une route FastAPI, la documentation Swagger affiche automatiquement :

- ✅ Liste déroulante avec **tous** les modèles
- ✅ Descriptions de chaque modèle
- ✅ Validation côté client
- ✅ Exemples d'utilisation

## 🔗 Voir aussi

- [LLM_CONFIGURATION.md](LLM_CONFIGURATION.md) - Configuration globale LLM
- [README_UNIVERSAL_LLM.md](README_UNIVERSAL_LLM.md) - Wrapper UniversalLLM
- [UNIVERSAL_LLM_GUIDE.md](UNIVERSAL_LLM_GUIDE.md) - Guide d'utilisation UniversalLLM

---

**Version** : 1.0.0
**Date** : 2026-01-06
**Total modèles** : 45
