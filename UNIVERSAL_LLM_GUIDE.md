# Guide UniversalLLM - Wrapper Universel pour Tous les Modèles

## 🎯 Problème résolu

Avant `UniversalLLM`, vous deviez :
- Utiliser `LLMModelFactory` pour les modèles LangChain (Gemini, Claude, GPT standard)
- Appeler manuellement la route `/api/utils/codex` pour les modèles Codex/O-series
- Gérer deux API différentes selon le modèle

**Avec `UniversalLLM`**, vous avez :
- ✅ Une interface unique pour **tous** les modèles
- ✅ Auto-détection du type de modèle
- ✅ Compatible avec les chaînes LangChain (LCEL)
- ✅ Fonctionne avec `JsonOutputParser` et autres parsers

## 📦 Installation

Aucune dépendance supplémentaire nécessaire ! Le wrapper utilise les librairies déjà présentes.

## 🚀 Utilisation rapide

### Exemple 1 : Utilisation simple

```python
from app.chains.llm.universal_llm import create_universal_llm
from app.chains.llm.llm_factory import LLMModel

# Modèle LangChain standard (Gemini)
llm = create_universal_llm(LLMModel.GEMINI_2_5_FLASH)
response = await llm.ainvoke("What is 2+2?")
print(response)  # "4"

# Modèle Codex (auto-détecté)
llm_codex = create_universal_llm("gpt-5.1-codex")
code = await llm_codex.ainvoke("Write a fibonacci function in Python")
print(code)  # Le code Python généré
```

### Exemple 2 : Dans une chaîne LangChain (LCEL)

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

# Définir le prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    ("user", "{question}")
])

# Créer la chaîne avec N'IMPORTE QUEL modèle
llm = create_universal_llm(LLMModel.CLAUDE_HAIKU_4_5_20251001)
chain = prompt | llm

# Utiliser
result = await chain.ainvoke({"question": "Explain Python in one sentence"})
```

### Exemple 3 : Avec JsonOutputParser (comme dans course_material_generator_v2)

```python
from langchain_core.output_parsers import JsonOutputParser

# Prompt qui demande du JSON
prompt = ChatPromptTemplate.from_messages([
    ("system", "Return a JSON object with keys: title, content"),
    ("user", "Topic: {topic}")
])

# Fonctionne avec N'IMPORTE QUEL modèle !
llm = create_universal_llm(LLMModel.GEMINI_2_5_FLASH)
# ou
llm = create_universal_llm("gpt-5.1-codex")

chain = prompt | llm | JsonOutputParser()
result = await chain.ainvoke({"topic": "Python variables"})
# result est un dict Python parsé
```

## 🔧 Comment l'utiliser dans CourseMaterialGeneratorV2

### Avant (ne fonctionnait pas avec Codex)

```python
class CourseMaterialGeneratorV2:
    def __init__(self, db_session, embedding_model, llm_config):
        # ❌ Ne supporte que les modèles LangChain
        self.pedagogical_llm = LLMModelFactory.get_llm(
            llm_config.get_pedagogical_json_model()
        )
```

### Après (fonctionne avec TOUS les modèles)

```python
from app.chains.llm.universal_llm import create_universal_llm

class CourseMaterialGeneratorV2:
    def __init__(self, db_session, embedding_model, llm_config=None):
        llm_config = llm_config or LLMConfigDto()

        # ✅ Supporte TOUS les modèles (LangChain + Codex)
        model = llm_config.get_pedagogical_json_model()

        if isinstance(model, LLMModel):
            # C'est un enum LangChain
            self.pedagogical_llm = create_universal_llm(model)
        else:
            # C'est un string (peut-être Codex)
            self.pedagogical_llm = create_universal_llm(model)

        # Le reste du code fonctionne exactement pareil !
        # chain = prompt | self.pedagogical_llm | JsonOutputParser()
```

### Version encore plus simple

```python
from app.chains.llm.universal_llm import UniversalLLM

class CourseMaterialGeneratorV2:
    def __init__(self, db_session, embedding_model, llm_config=None):
        llm_config = llm_config or LLMConfigDto()

        # ✅ UniversalLLM gère automatiquement enum ou string
        model_id = llm_config.get_pedagogical_json_model()

        self.pedagogical_llm = UniversalLLM(
            model=model_id if isinstance(model_id, LLMModel) else None,
            model_name=model_id if isinstance(model_id, str) else None
        )
```

## 📚 API Complète

### Classe `UniversalLLM`

```python
UniversalLLM(
    model: Optional[LLMModel] = None,           # Enum pour modèles LangChain
    model_name: Optional[str] = None,           # String pour Codex ou custom
    use_codex_route: Optional[bool] = None,     # Force Codex (auto-détecté si None)
    api_base_url: str = "http://localhost:8000", # URL de l'API
    timeout: int = 120,                          # Timeout en secondes
    **kwargs                                     # Args pour BaseChatModel
)
```

### Fonction helper `create_universal_llm`

```python
create_universal_llm(
    model_identifier: Union[str, LLMModel],  # Enum ou string
    api_base_url: str = "http://localhost:8000",
    **kwargs
) -> UniversalLLM
```

### Méthodes disponibles

```python
# Invocation synchrone
response: str = llm.invoke("prompt")

# Invocation asynchrone (recommandé)
response: str = await llm.ainvoke("prompt")

# Avec messages LangChain
from langchain_core.messages import HumanMessage, SystemMessage

messages = [
    SystemMessage(content="You are helpful"),
    HumanMessage(content="Hello")
]
response = await llm.ainvoke(messages)

# Dans une chaîne LCEL
chain = prompt | llm | output_parser
result = await chain.ainvoke(inputs)
```

## 🎨 Modèles supportés

### Via LangChain (utilise LLMModelFactory)

**Anthropic Claude** :
- `LLMModel.CLAUDE_HAIKU_4_5_20251001`
- `LLMModel.CLAUDE_SONNET_4_5_20250929`
- `LLMModel.CLAUDE_OPUS_4_5`
- ... (tous les modèles Claude)

**Google Gemini** :
- `LLMModel.GEMINI_2_5_FLASH` (défaut)
- `LLMModel.GEMINI_3_FLASH_PREVIEW`
- ... (tous les modèles Gemini)

**OpenAI GPT** :
- `LLMModel.GPT_5_2`
- `LLMModel.GPT_5_MINI`
- `LLMModel.GPT_4O`
- `LLMModel.O1_MINI`
- ... (tous les modèles GPT standard)

### Via route Codex (utilise /api/utils/codex)

**Codex** (auto-détecté) :
- `"gpt-5.1-codex"` ⭐ Recommandé
- `"gpt-5.1-codex-max"`
- `"gpt-5-codex"`
- `"gpt-5.1-codex-mini"`
- `"codex-mini-latest"`

**O-Series** (auto-détecté) :
- `"o3"`
- `"o3-mini"`
- `"o3-deep-research"`
- `"o4-mini"`
- `"o4-mini-deep-research"`

## 💡 Cas d'usage réels

### Cas 1 : Génération pédagogique avec choix de modèle

```python
from app.chains.llm.universal_llm import create_universal_llm
from app.chains.llm.llm_factory import LLMModel

# Configuration
models_config = {
    "fast": LLMModel.GEMINI_2_5_FLASH,
    "quality": LLMModel.CLAUDE_SONNET_4_5_20250929,
    "code": "gpt-5.1-codex",  # Codex pour génération de code
}

# Choisir selon le besoin
mode = "quality"  # ou "fast", "code"

llm = create_universal_llm(models_config[mode])

# Utiliser de la même manière
prompt = ChatPromptTemplate.from_messages([...])
chain = prompt | llm | JsonOutputParser()
result = await chain.ainvoke(inputs)
```

### Cas 2 : A/B Testing de modèles

```python
async def compare_models(question: str):
    """Compare les réponses de plusieurs modèles"""

    models = {
        "Gemini": LLMModel.GEMINI_2_5_FLASH,
        "Claude": LLMModel.CLAUDE_HAIKU_4_5_20251001,
        "GPT": LLMModel.GPT_5_MINI,
        "Codex": "gpt-5.1-codex",
    }

    results = {}

    for name, model_id in models.items():
        llm = create_universal_llm(model_id)
        response = await llm.ainvoke(question)
        results[name] = response

    return results

# Usage
responses = await compare_models("Write a quicksort in Python")
for model, answer in responses.items():
    print(f"\n{model}:\n{answer}")
```

### Cas 3 : Fallback automatique

```python
async def generate_with_fallback(prompt: str, models_priority: list):
    """Essaie plusieurs modèles jusqu'à ce que l'un fonctionne"""

    for model_id in models_priority:
        try:
            llm = create_universal_llm(model_id)
            result = await llm.ainvoke(prompt)
            return result, model_id
        except Exception as e:
            print(f"❌ {model_id} failed: {e}")
            continue

    raise Exception("All models failed")

# Usage
priority = [
    LLMModel.CLAUDE_SONNET_4_5_20250929,  # Meilleur d'abord
    LLMModel.GPT_5_MINI,                   # Fallback 1
    LLMModel.GEMINI_2_5_FLASH,            # Fallback 2
]

result, used_model = await generate_with_fallback("Question?", priority)
print(f"Réponse de {used_model}: {result}")
```

## 🔍 Auto-détection des modèles Codex

Le wrapper détecte automatiquement si un modèle nécessite la route Codex basé sur son nom :

```python
# Auto-détecté comme Codex ✅
llm = create_universal_llm("gpt-5.1-codex")
llm = create_universal_llm("o3-mini")

# Auto-détecté comme LangChain ✅
llm = create_universal_llm(LLMModel.GEMINI_2_5_FLASH)

# Forçage manuel possible
llm = UniversalLLM(model_name="custom-model", use_codex_route=True)
```

## ⚠️ Important

### Configuration requise pour Codex

Pour que les modèles Codex fonctionnent, le serveur FastAPI doit être démarré :

```bash
uvicorn app.main:app --reload
```

L'URL par défaut est `http://localhost:8000`. Si différente :

```python
llm = create_universal_llm(
    "gpt-5.1-codex",
    api_base_url="http://your-server:8000"
)
```

### Async vs Sync

Préférez toujours `ainvoke` (async) à `invoke` (sync) pour de meilleures performances :

```python
# ✅ Recommandé
response = await llm.ainvoke("prompt")

# ⚠️ OK mais moins performant
response = llm.invoke("prompt")
```

### JsonOutputParser

Le `JsonOutputParser` peut échouer si le modèle ne retourne pas du JSON valide. Ajoutez un try/except :

```python
chain = prompt | llm | JsonOutputParser()

try:
    result = await chain.ainvoke(inputs)
except Exception as e:
    print(f"Erreur de parsing JSON: {e}")
    # Fallback ou retry
```

## 📊 Comparaison avant/après

### Avant (code dupliqué)

```python
# Pour modèles LangChain
if model in ["gemini", "claude", "gpt"]:
    llm = LLMModelFactory.get_llm(model_enum)
    result = llm.invoke(messages)

# Pour modèles Codex
elif model in ["codex", "o-series"]:
    async with httpx.AsyncClient() as client:
        response = await client.post("/api/utils/codex", json=payload)
        result = response.json()["response"]
```

### Après (code unifié)

```python
# Pour TOUS les modèles
llm = create_universal_llm(model)
result = await llm.ainvoke(messages)
```

## 🧪 Tests

Exécutez les tests pour vérifier que tout fonctionne :

```bash
python test_universal_llm.py
```

Les tests couvrent :
1. Modèles LangChain (Gemini, Claude, GPT)
2. Modèles Codex (gpt-5.1-codex)
3. Chaînes LangChain (LCEL)
4. JsonOutputParser
5. Changement de modèle dynamique
6. Simulation CourseMaterialGeneratorV2

## 📖 Documentation complète

- [CODEX_ROUTE.md](CODEX_ROUTE.md) - Route Codex dédiée
- [LLM_CONFIGURATION.md](LLM_CONFIGURATION.md) - Configuration globale des LLMs
- [API_RESPONSES_DIFFERENCES.md](API_RESPONSES_DIFFERENCES.md) - Différences API OpenAI

## 💡 Résumé

**UniversalLLM** vous permet d'utiliser **tous les modèles** (LangChain + Codex + O-series) avec **une seule interface**, compatible avec les chaînes LangChain et les output parsers.

**Un seul changement de ligne** suffit pour passer de Gemini à Claude à GPT-5.1-codex ! 🚀

```python
# Avant
pedagogical_llm = LLMModelFactory.get_llm(model)  # ❌ Codex non supporté

# Après
pedagogical_llm = create_universal_llm(model)  # ✅ Tous modèles supportés
```

---

**Version** : 1.0.0
**Date** : 2026-01-06
**Auteur** : Claude Sonnet 4.5
