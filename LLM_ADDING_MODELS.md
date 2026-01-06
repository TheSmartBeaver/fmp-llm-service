# Guide : Ajouter de nouveaux modèles LLM

Ce guide explique comment ajouter de nouveaux modèles LLM au système de configuration.

## Architecture du système

Le système utilise 4 types de wrappers LLM selon le provider et les caractéristiques du modèle :

1. **AnthropicLLM** (`app/chains/llm/anthropic_llm.py`) - Pour tous les modèles Claude
2. **OpenAILLM** (`app/chains/llm/openai_llm.py`) - Pour les modèles OpenAI standards (GPT-4, GPT-5, Codex, etc.)
3. **OpenAIReasoningLLM** (`app/chains/llm/openai_reasoning_llm.py`) - Pour les modèles O-series (O1, O3, O4)
4. **GoogleLLM** (`app/chains/llm/google_llm.py`) - Pour tous les modèles Gemini

## Ajouter un nouveau modèle

### Étape 1 : Ajouter le modèle à l'enum

Éditez [app/chains/llm/llm_factory.py](app/chains/llm/llm_factory.py) et ajoutez le modèle dans la section appropriée de l'enum `LLMModel` :

```python
class LLMModel(str, Enum):
    # ... modèles existants ...

    # Ajoutez votre nouveau modèle ici
    NOUVEAU_MODELE = "nom-exact-du-modele"
```

**Important** : La valeur de l'enum doit être **exactement** le nom du modèle tel qu'attendu par l'API du provider.

### Étape 2 : Ajouter le modèle au bon set dans la factory

Dans la classe `LLMModelFactory`, ajoutez votre modèle au set approprié :

#### Pour un modèle Anthropic (Claude) :
```python
_ANTHROPIC_MODELS = {
    # ... modèles existants ...
    LLMModel.NOUVEAU_MODELE,
}
```

#### Pour un modèle Google (Gemini) :
```python
_GOOGLE_MODELS = {
    # ... modèles existants ...
    LLMModel.NOUVEAU_MODELE,
}
```

#### Pour un modèle OpenAI de raisonnement (O-series) :
```python
_OPENAI_REASONING_MODELS = {
    # ... modèles existants ...
    LLMModel.NOUVEAU_MODELE,
}
```

#### Pour un modèle OpenAI standard (GPT, Codex, etc.) :
**Rien à faire !** Les modèles OpenAI standards sont gérés par défaut. Si le modèle n'est pas dans les sets `_ANTHROPIC_MODELS`, `_GOOGLE_MODELS` ou `_OPENAI_REASONING_MODELS`, il sera automatiquement traité comme un modèle OpenAI standard.

### Étape 3 : Tester la compilation

```bash
python3 -m py_compile app/chains/llm/llm_factory.py
python3 -m py_compile app/models/dto/llm_config/llm_config_dto.py
```

### Étape 4 : Mettre à jour la documentation

1. **[LLM_CONFIGURATION.md](LLM_CONFIGURATION.md)** - Ajoutez le modèle dans la section "Modèles disponibles"
2. **[LLM_MODELS_EXAMPLES.md](LLM_MODELS_EXAMPLES.md)** - Si pertinent, ajoutez des exemples d'utilisation

## Cas particuliers

### Ajouter un nouveau provider (ex: Cohere, Mistral)

Si vous devez ajouter un provider complètement nouveau :

1. **Créer une classe wrapper** (ex: `CohereLLM`) :

```python
# app/chains/llm/cohere_llm.py
import os
from dotenv import find_dotenv, load_dotenv
from langchain_cohere import ChatCohere  # Hypothétique
from langchain_core.language_models.chat_models import BaseChatModel


class CohereLLM:
    def __init__(self, model_name: str, temperature: float = 0.7, timeout: int = 100):
        load_dotenv(find_dotenv())
        self.chat = ChatCohere(
            model=model_name,
            api_key=os.getenv("COHERE_API_KEY"),
            temperature=temperature,
            timeout=timeout
        )

    def get_llm(self) -> BaseChatModel:
        return self.chat
```

2. **Importer dans la factory** :

```python
# app/chains/llm/llm_factory.py
from app.chains.llm.cohere_llm import CohereLLM
```

3. **Créer un set de modèles** :

```python
_COHERE_MODELS = {
    LLMModel.COHERE_COMMAND_R,
    LLMModel.COHERE_COMMAND_R_PLUS,
}
```

4. **Ajouter une condition dans `get_llm()`** :

```python
@staticmethod
def get_llm(model: LLMModel) -> BaseChatModel:
    if model in LLMModelFactory._ANTHROPIC_MODELS:
        return AnthropicLLM(model.value).get_llm()
    elif model in LLMModelFactory._GOOGLE_MODELS:
        return GoogleLLM(model.value).get_llm()
    elif model in LLMModelFactory._COHERE_MODELS:
        return CohereLLM(model.value).get_llm()
    # ... etc
```

### Modèles avec configuration spéciale

Si un modèle nécessite une configuration spéciale (comme les modèles O-series) :

1. Créez une classe wrapper dédiée (voir `OpenAIReasoningLLM`)
2. Ajoutez un set dédié dans la factory
3. Documentez les particularités dans les commentaires et la documentation

## Variables d'environnement requises

Assurez-vous que les clés API appropriées sont définies dans le fichier `.env` :

```bash
# .env
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GEMINI_API_KEY=...
# Ajoutez d'autres clés selon les providers utilisés
```

## Tests recommandés

Après avoir ajouté un nouveau modèle, testez :

1. **Compilation** : `python3 -m py_compile app/chains/llm/llm_factory.py`
2. **Instanciation** : Vérifiez que le modèle peut être instancié sans erreur
3. **Utilisation** : Testez avec une génération simple sur `/generate_v2`

Exemple de test manuel :

```bash
curl -X POST "http://localhost:8000/course_material/generate_v2" \
  -H "Content-Type: application/json" \
  -H "X-Auth-Uid: test-user" \
  -d '{
    "llm_config": {
      "pedagogical_json_model": "votre-nouveau-modele"
    },
    "context_entry": {
      "course": "Test",
      "topic_path": "Test"
    },
    "book_scan_entry": [],
    "diction_entry": [{"order": 1, "text_blocs": ["Test simple"]}],
    "img_entry": [],
    "video_entry": []
  }'
```

## Bonnes pratiques

1. **Nommage** : Utilisez des noms d'enum en SNAKE_CASE majuscules (ex: `GPT_5_MINI`)
2. **Valeurs** : Les valeurs doivent être exactement celles attendues par l'API (ex: `"gpt-5-mini"`)
3. **Organisation** : Groupez les modèles par provider et par série dans l'enum
4. **Documentation** : Documentez toujours les modèles avec des caractéristiques spéciales
5. **Tests** : Testez au moins une fois chaque nouveau modèle avant de pousser en production

## Dépannage

### Erreur "Model not found"
- Vérifiez que le nom du modèle dans l'enum correspond exactement au nom attendu par l'API
- Vérifiez que la clé API est correctement configurée

### Erreur "This model is only supported in..."
- Certains modèles utilisent des endpoints spéciaux (comme les O-series)
- Créez une classe wrapper dédiée avec la configuration appropriée

### Le modèle ne s'initialise pas
- Vérifiez que le package langchain correspondant est installé (`langchain-openai`, `langchain-anthropic`, `langchain-google-genai`)
- Vérifiez les logs pour voir les erreurs d'initialisation
