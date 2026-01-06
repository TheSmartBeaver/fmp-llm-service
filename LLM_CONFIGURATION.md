# Configuration des modèles LLM

Cette fonctionnalité permet de sélectionner dynamiquement les modèles LLM utilisés pour les différentes étapes de génération de supports de cours.

## Architecture

### 1. Fichiers créés

- **[app/chains/llm/llm_factory.py](app/chains/llm/llm_factory.py)** : Factory pattern pour instancier les LLMs
  - `LLMModel` (Enum) : Liste tous les modèles disponibles (60+ modèles)
  - `LLMModelFactory` : Crée des instances de LLM basées sur l'enum

- **[app/chains/llm/anthropic_llm.py](app/chains/llm/anthropic_llm.py)** : Wrapper générique pour Anthropic
  - `AnthropicLLM` : Classe qui accepte n'importe quel nom de modèle Claude

- **[app/chains/llm/openai_llm.py](app/chains/llm/openai_llm.py)** : Wrapper générique pour OpenAI
  - `OpenAILLM` : Classe qui accepte n'importe quel nom de modèle OpenAI

- **[app/chains/llm/google_llm.py](app/chains/llm/google_llm.py)** : Wrapper générique pour Google
  - `GoogleLLM` : Classe qui accepte n'importe quel nom de modèle Gemini

- **[app/models/dto/llm_config/llm_config_dto.py](app/models/dto/llm_config/llm_config_dto.py)** : DTO de configuration
  - `LLMConfigDto` : Permet de spécifier 3 modèles différents

### 2. Fichiers modifiés

- **[app/chains/course_material_generator_v2.py](app/chains/course_material_generator_v2.py)** : Accepte `llm_config` dans le constructeur
- **[app/chains/template_structure_generator.py](app/chains/template_structure_generator.py)** : Accepte `llm_config` dans le constructeur
- **[app/routers/course_material/router.py](app/routers/course_material/router.py)** : Routes `/generate_v2` et `/generate_CELERY` acceptent `llm_config`
- **[app/workers/tasks.py](app/workers/tasks.py)** : Tâche Celery supporte la configuration LLM

## Modèles disponibles

### Google Gemini (5 modèles)
- `gemini-2.5-flash-lite` → Gemini 2.5 Flash Lite
- `gemini-2.5-flash` → Gemini 2.5 Flash **(défaut)**
- `gemini-3-flash-preview` → Gemini 3 Flash Preview
- `gemini-2.0-flash` → Gemini 2.0 Flash
- `gemini-2.0-flash-lite` → Gemini 2.0 Flash Lite

### OpenAI - GPT-5 Series (8 modèles)
- `gpt-5.2` → GPT-5.2
- `gpt-5.1` → GPT-5.1
- `gpt-5` → GPT-5
- `gpt-5-mini` → GPT-5 Mini
- `gpt-5-nano` → GPT-5 Nano
- `gpt-5.2-chat-latest` → GPT-5.2 Chat Latest
- `gpt-5.1-chat-latest` → GPT-5.1 Chat Latest
- `gpt-5-chat-latest` → GPT-5 Chat Latest

### OpenAI - GPT-5 Codex (5 modèles)
⚠️ **Note**: Modèles optimisés pour le code (temperature=0.0, max_tokens=2048)
- `gpt-5.1-codex-max` → GPT-5.1 Codex Max
- `gpt-5.1-codex` → GPT-5.1 Codex
- `gpt-5-codex` → GPT-5 Codex
- `gpt-5.1-codex-mini` → GPT-5.1 Codex Mini
- `codex-mini-latest` → Codex Mini Latest

### OpenAI - GPT-4 Series (6 modèles)
- `gpt-4.1` → GPT-4.1
- `gpt-4.1-mini` → GPT-4.1 Mini
- `gpt-4.1-nano` → GPT-4.1 Nano
- `gpt-4o` → GPT-4o
- `gpt-4o-2024-05-13` → GPT-4o (version spécifique)
- `gpt-4o-mini` → GPT-4o Mini

### OpenAI - Realtime Models (2 modèles)
- `gpt-realtime-mini` → GPT Realtime Mini
- `gpt-4o-mini-realtime-preview` → GPT-4o Mini Realtime Preview

### OpenAI - O-Series / Reasoning Models (6 modèles)
⚠️ **Note**: Ces modèles utilisent une configuration spéciale (pas de temperature, pas de streaming)
- `o3` → O3
- `o3-deep-research` → O3 Deep Research
- `o4-mini` → O4 Mini
- `o4-mini-deep-research` → O4 Mini Deep Research
- `o3-mini` → O3 Mini
- `o1-mini` → O1 Mini

### OpenAI - Search Models (3 modèles)
- `gpt-5-search-api` → GPT-5 Search API
- `gpt-4o-mini-search-preview` → GPT-4o Mini Search Preview
- `gpt-4o-search-preview` → GPT-4o Search Preview

### Anthropic - Claude 3 Series (7 modèles)
- `claude-3-haiku-20240307` → Claude 3 Haiku
- `claude-3-5-haiku-20241022` → Claude 3.5 Haiku
- `claude-haiku-4-5-20251001` → Claude Haiku 4.5
- `claude-3-sonnet-20240229` → Claude 3 Sonnet
- `claude-3-5-sonnet-20240620` → Claude 3.5 Sonnet
- `claude-3-5-sonnet-20241022` → Claude 3.5 Sonnet (Oct 2024)
- `claude-3-7-sonnet-20250219` → Claude 3.7 Sonnet

### Anthropic - Claude 4 Series (3 modèles)
- `claude-sonnet-4-20250514` → Claude Sonnet 4
- `claude-sonnet-4-5-20250929` → Claude Sonnet 4.5
- `claude-opus-4-5` → Claude Opus 4.5

**Total : 45+ modèles disponibles**

## Les 3 fonctions configurables

1. **`pedagogical_json_model`** : Pour `_generate_pedagogical_json`
   - Génère le JSON pédagogique enrichi à partir des données utilisateur

2. **`group_json_model`** : Pour `_generate_json_from_group_async`
   - Génère les JSONs structurés pour chaque groupe de chemins

3. **`path_groups_model`** : Pour `_generate_path_groups_with_llm`
   - Regroupe les chemins source selon leur nature sémantique

## Utilisation

### Route `/generate_v2` (Synchrone)

```bash
curl -X POST "http://localhost:8000/course_material/generate_v2" \
  -H "Content-Type: application/json" \
  -H "X-Auth-Uid: user123" \
  -d '{
    "llm_config": {
      "pedagogical_json_model": "gemini-2.5-flash",
      "group_json_model": "claude-haiku-4-5-20251001",
      "path_groups_model": "gpt-5-mini"
    },
    "context_entry": {
      "course": "Mathématiques",
      "topic_path": "Algèbre > Équations"
    },
    "book_scan_entry": [],
    "diction_entry": [
      {
        "order": 1,
        "text_blocs": ["Contenu du cours..."]
      }
    ],
    "img_entry": [],
    "video_entry": []
  }'
```

### Route `/generate_CELERY` (Asynchrone)

```bash
curl -X POST "http://localhost:8000/course_material/generate_CELERY" \
  -H "Content-Type: application/json" \
  -H "X-Auth-Uid: user123" \
  -d '{
    "llm_config": {
      "pedagogical_json_model": "claude-sonnet-4-5-20250929",
      "group_json_model": "gemini-2.5-flash",
      "path_groups_model": "gpt-5.2"
    },
    "context_entry": {
      "course": "Python",
      "topic_path": "Programmation > Bases"
    },
    "book_scan_entry": [],
    "diction_entry": [
      {
        "order": 1,
        "text_blocs": ["Variables, types, opérateurs..."]
      }
    ],
    "img_entry": [],
    "video_entry": []
  }'
```

### Avec des valeurs par défaut (optionnel)

Si `llm_config` n'est pas fourni ou si certains modèles ne sont pas spécifiés, le système utilisera automatiquement `gemini-2-5-flash` comme modèle par défaut.

```bash
# Sans llm_config → utilise gemini-2-5-flash partout
curl -X POST "http://localhost:8000/course_material/generate_v2" \
  -H "Content-Type: application/json" \
  -H "X-Auth-Uid: user123" \
  -d '{
    "context_entry": {...},
    ...
  }'
```

```bash
# Avec llm_config partiel → gemini-2.5-flash pour les non-spécifiés
curl -X POST "http://localhost:8000/course_material/generate_v2" \
  -H "Content-Type: application/json" \
  -H "X-Auth-Uid: user123" \
  -d '{
    "llm_config": {
      "pedagogical_json_model": "claude-haiku-4-5-20251001"
      # group_json_model et path_groups_model utiliseront gemini-2.5-flash
    },
    "context_entry": {...},
    ...
  }'
```

## Exemple en Python

```python
from app.models.dto.llm_config.llm_config_dto import LLMConfigDto
from app.models.dto.user_entry.user_entry_dto import UserEntryDto
from app.chains.course_material_generator_v2 import CourseMaterialGeneratorV2
from app.chains.llm.llm_factory import LLMModel

# Configuration LLM personnalisée
llm_config = LLMConfigDto(
    pedagogical_json_model=LLMModel.GEMINI_2_5_FLASH,
    group_json_model=LLMModel.CLAUDE_HAIKU_4_5_20251001,
    path_groups_model=LLMModel.GPT_5_MINI
)

# Créer le générateur avec la config
generator = CourseMaterialGeneratorV2(
    db_session=db,
    embedding_model=embedding_model,
    llm_config=llm_config
)

# Générer le support de cours
result = await generator.generate_course_material_async(
    user_entry=user_entry,
    top_k=20
)
```

## Avantages

✅ **Flexibilité** : Choisir le meilleur modèle pour chaque tâche
✅ **Performance** : Optimiser coût/qualité selon les besoins
✅ **Extensibilité** : Facile d'ajouter de nouveaux modèles
✅ **Rétrocompatibilité** : Fonctionne sans modification du code existant
✅ **Type safety** : L'enum évite les erreurs de typage
