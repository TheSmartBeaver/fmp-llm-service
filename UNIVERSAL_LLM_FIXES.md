# UniversalLLM - Corrections et Fixes

## 📋 Résumé des corrections

Ce document liste toutes les corrections apportées au wrapper `UniversalLLM` pour le rendre production-ready.

**Date** : 2026-01-06
**Version** : 1.0.0
**Status** : ✅ Production ready

---

## 🔧 Corrections appliquées

### 1. Fix Pydantic validation pour CODEX_MODELS

**Erreur** :
```
pydantic.errors.PydanticUserError: A non-annotated attribute was detected: `CODEX_MODELS = {...}`.
All model fields require a type annotation
```

**Solution** : Ajout de l'annotation `ClassVar[set]`
```python
from typing import ClassVar

class UniversalLLM(BaseChatModel):
    CODEX_MODELS: ClassVar[set] = {
        "gpt-5.1-codex-max",
        "gpt-5.1-codex",
        # ...
    }
```

**Fichier** : [app/chains/llm/universal_llm.py](app/chains/llm/universal_llm.py#L43-L54)

---

### 2. Fix compatibilité LangChain LCEL - invoke() parameters

**Erreur** :
```
TypeError: invoke() takes 2 positional arguments but 3 were given
```

**Cause** : Les chaînes LCEL appellent `invoke(input, config)` mais notre override acceptait seulement `invoke(input, **kwargs)`

**Solution** : Suppression des méthodes `invoke()` et `ainvoke()` custom
- Laisse la classe parente `BaseChatModel` gérer ces méthodes
- Parent appelle correctement nos méthodes `_generate()` et `_agenerate()`

**Fichier** : [app/chains/llm/universal_llm.py](app/chains/llm/universal_llm.py#L143-L191)

---

### 3. Fix gestion async/sync - Suppression de nest_asyncio

**Erreur** :
```
ModuleNotFoundError: No module named 'nest_asyncio'
```

**Solution** : Gestion manuelle de l'event loop dans `_generate()`
```python
def _generate(self, messages, stop=None, run_manager=None, **kwargs):
    if not self.use_codex_route:
        # Déléguer au LLM LangChain sous-jacent
        return self.llm._generate(messages, stop, run_manager, **kwargs)
    else:
        # Pour Codex, vérifier si on est dans un event loop actif
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                raise RuntimeError(
                    f"Cannot use synchronous invoke() with Codex model '{self.model_name}' "
                    f"inside an async context. Please use ainvoke() instead."
                )
        except RuntimeError as e:
            if "no running event loop" not in str(e).lower():
                raise

        # Si pas de boucle active, utiliser asyncio.run
        return asyncio.run(self._agenerate(messages, stop, run_manager, **kwargs))
```

**Fichier** : [app/chains/llm/universal_llm.py](app/chains/llm/universal_llm.py#L143-L176)

---

### 4. Fix validation FastAPI - Support des strings Codex

**Erreur** :
```
"msg": "Input should be 'gemini-2.5-flash-lite', 'gemini-2.5-flash', ... or 'claude-opus-4-5'"
```

**Cause** : `LLMConfigDto` acceptait seulement `LLMModel` enum, pas les strings comme "gpt-5.1-codex"

**Solution** : Modification de `LLMConfigDto` pour accepter `Union[AllLLMModels, LLMModel, str]`
```python
class LLMConfigDto(BaseModel):
    pedagogical_json_model: Optional[Union[AllLLMModels, LLMModel, str]] = Field(
        default=None,
        description="Modèle LLM pour la génération du JSON pédagogique..."
    )

    def get_pedagogical_json_model(self) -> Union[AllLLMModels, LLMModel, str]:
        if self.pedagogical_json_model:
            if isinstance(self.pedagogical_json_model, AllLLMModels):
                return self.pedagogical_json_model.value
            return self.pedagogical_json_model
        return LLMModelFactory.get_default_model()
```

**Fichier** : [app/models/dto/llm_config/llm_config_dto.py](app/models/dto/llm_config/llm_config_dto.py#L25-L47)

---

### 5. Création de AllLLMModels enum

**Besoin** : Enum au niveau route pour auto-complétion de TOUS les modèles (LangChain + Codex + O-series)

**Solution** : Création de `AllLLMModels` enum avec 45 modèles
```python
class AllLLMModels(str, Enum):
    # Google Gemini (5 modèles)
    GEMINI_2_5_FLASH = "gemini-2.5-flash"

    # OpenAI GPT-5 Codex (5 modèles)
    GPT_5_1_CODEX = "gpt-5.1-codex"

    # OpenAI O-Series (6 modèles)
    O3_MINI = "o3-mini"

    # Anthropic Claude (10 modèles)
    CLAUDE_HAIKU_4_5_20251001 = "claude-haiku-4-5-20251001"

    # ... Total 45 modèles

CODEX_MODELS = {
    AllLLMModels.GPT_5_1_CODEX,
    AllLLMModels.O3_MINI,
    # ... 10 modèles Codex/O-series
}

def is_codex_model(model: AllLLMModels) -> bool:
    return model in CODEX_MODELS
```

**Fichiers** :
- [app/models/dto/llm_config/all_llm_models.py](app/models/dto/llm_config/all_llm_models.py) (nouveau)
- [ALL_LLM_MODELS_GUIDE.md](ALL_LLM_MODELS_GUIDE.md) (documentation)

---

### 6. Fix asyncio.run() dans event loop actif

**Erreur** :
```
RuntimeError: asyncio.run() cannot be called from a running event loop
```

**Cause** : `_generate()` appelait `asyncio.run()` depuis une route FastAPI async (event loop déjà actif)

**Solution** : Conversion de `_generate_pedagogical_json()` en async
```python
# Avant (sync)
def _generate_pedagogical_json(self, user_entry):
    result = chain.invoke(inputs)
    return result

# Après (async)
async def _generate_pedagogical_json(self, user_entry):
    result = await chain.ainvoke(inputs)
    return result
```

**Fichiers** :
- [app/chains/course_material_generator_v2.py](app/chains/course_material_generator_v2.py#L254-L333)

---

### 7. Fix connexion circulaire - Route interne → API directe

**Erreur** :
```
httpx.ConnectError: All connection attempts failed
```

**Cause** : `UniversalLLM` appelait `http://localhost:8000/api/utils/codex` depuis le même serveur (dépendance circulaire)

**Solution** : Appel direct à l'API OpenAI `https://api.openai.com/v1/responses`
```python
async def _generate_via_codex_route(self, messages, ...):
    import os

    # Récupérer la clé API OpenAI
    api_key = os.getenv("OPENAI_API_KEY")

    # Appel direct à l'API OpenAI
    endpoint = "https://api.openai.com/v1/responses"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=self.timeout) as client:
        response = await client.post(endpoint, json=payload, headers=headers)
        # ...
```

**Fichier** : [app/chains/llm/universal_llm.py](app/chains/llm/universal_llm.py#L232-L280)

---

### 8. Fix parsing réponse /v1/responses

**Erreur** :
```
ValueError: Unexpected response format from OpenAI API: {'id': 'resp_...', 'object': 'response',
'output': [{'type': 'reasoning', ...}, {'type': 'message', 'content': [...]}]}
```

**Cause** : L'API `/v1/responses` retourne un format différent avec `output` array au lieu de `choices` array

**Format attendu (incorrect)** :
```json
{
  "choices": [
    {"message": {"content": "..."}}
  ]
}
```

**Format réel** :
```json
{
  "output": [
    {"type": "reasoning", "summary": []},
    {"type": "message", "content": [{"type": "text", "text": "..."}]}
  ]
}
```

**Solution** : Parsing de l'array `output` au lieu de `choices`
```python
result = response.json()
response_text = None

if "output" in result:
    # Parcourir l'array output pour trouver le message
    for output_item in result["output"]:
        if output_item.get("type") == "message":
            # Extraire le contenu du message
            content_items = output_item.get("content", [])
            if content_items and len(content_items) > 0:
                # Le contenu peut être un dict avec 'text' ou directement du texte
                first_content = content_items[0]
                if isinstance(first_content, dict):
                    response_text = first_content.get("text", "")
                else:
                    response_text = str(first_content)
            break

if response_text is None:
    raise ValueError(f"Unexpected response format from OpenAI API: {result}")
```

**Fichier** : [app/chains/llm/universal_llm.py](app/chains/llm/universal_llm.py#L287-L309)

**Test** : [test_codex_parsing.py](test_codex_parsing.py)

---

## ✅ Résultat final

### Fichiers créés
1. ✅ [app/chains/llm/universal_llm.py](app/chains/llm/universal_llm.py) - Wrapper universel
2. ✅ [app/models/dto/llm_config/all_llm_models.py](app/models/dto/llm_config/all_llm_models.py) - Enum complet
3. ✅ [ALL_LLM_MODELS_GUIDE.md](ALL_LLM_MODELS_GUIDE.md) - Documentation enum
4. ✅ [UNIVERSAL_LLM_FIXES.md](UNIVERSAL_LLM_FIXES.md) - Ce fichier

### Fichiers modifiés
1. ✅ [app/models/dto/llm_config/llm_config_dto.py](app/models/dto/llm_config/llm_config_dto.py) - Support Union types
2. ✅ [app/chains/course_material_generator_v2.py](app/chains/course_material_generator_v2.py) - Async + UniversalLLM
3. ✅ [app/chains/template_structure_generator.py](app/chains/template_structure_generator.py) - UniversalLLM

### Fonctionnalités
- ✅ Support de **45 modèles** avec une seule interface
- ✅ Auto-détection Codex/O-series
- ✅ Compatible LangChain LCEL
- ✅ Compatible JsonOutputParser
- ✅ Validation FastAPI avec enum
- ✅ Auto-complétion IDE
- ✅ Gestion async/sync correcte
- ✅ Pas de dépendance circulaire

### Tests validés
- ✅ Parsing réponse `/v1/responses`
- ✅ Modèles LangChain (Gemini, Claude, GPT)
- ✅ Chaînes LCEL
- ✅ JsonOutputParser

---

## 🚀 Utilisation

```python
from app.chains.llm.universal_llm import create_universal_llm
from app.models.dto.llm_config.all_llm_models import AllLLMModels

# Modèle LangChain
llm = create_universal_llm(AllLLMModels.GEMINI_2_5_FLASH)

# Modèle Codex (auto-détecté)
llm_codex = create_universal_llm(AllLLMModels.GPT_5_1_CODEX)

# String également supporté
llm_str = create_universal_llm("o3-mini")

# Utilisation uniforme
response = await llm.ainvoke("What is 2+2?")
```

---

## 📊 Comparaison avant/après

| Aspect | Avant | Après |
|--------|-------|-------|
| Modèles supportés | 34 (LangChain) | 45 (LangChain + Codex + O-series) |
| Interface | 2 différentes | 1 seule |
| Validation FastAPI | Enum partiel | Enum complet (45 modèles) |
| Auto-complétion | Partielle | Complète |
| Gestion async | Problématique | ✅ Correcte |
| Dépendance circulaire | ❌ Oui | ✅ Non |
| Parsing réponse API | ❌ Incorrect | ✅ Correct |

---

**Status final** : ✅ **Production ready** - Tous les modèles fonctionnent avec une interface unique.
