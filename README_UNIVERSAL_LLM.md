# 🎯 UniversalLLM - Wrapper Universel pour TOUS les Modèles LLM

## Vue d'ensemble

**UniversalLLM** est un wrapper qui permet d'utiliser **tous les modèles LLM** (LangChain + Codex + O-series) avec **une interface unique**, compatible avec les chaînes LangChain et les output parsers.

### Problème résolu

✅ **Avant** : Impossible d'utiliser Codex dans `CourseMaterialGeneratorV2` car LangChain ne supporte pas l'endpoint `/v1/responses`

✅ **Après** : Utilisez **n'importe quel modèle** (Gemini, Claude, GPT, Codex, O-series) avec **la même interface**

## 🚀 Quick Start (30 secondes)

### Installation

Aucune dépendance supplémentaire ! Les fichiers sont déjà créés.

### Utilisation basique

```python
from app.chains.llm.universal_llm import create_universal_llm
from app.chains.llm.llm_factory import LLMModel

# Modèle LangChain standard
llm = create_universal_llm(LLMModel.GEMINI_2_5_FLASH)
response = await llm.ainvoke("What is 2+2?")

# Modèle Codex (auto-détecté)
llm_codex = create_universal_llm("gpt-5.1-codex")
code = await llm_codex.ainvoke("Write a fibonacci function")
```

### Dans CourseMaterialGeneratorV2

```python
from app.chains.llm.universal_llm import create_universal_llm

class CourseMaterialGeneratorV2:
    def __init__(self, db_session, embedding_model, llm_config=None):
        # Une seule ligne à changer !
        pedagogical_model = llm_config.get_pedagogical_json_model()
        self.pedagogical_llm = create_universal_llm(pedagogical_model)

        # Le reste fonctionne exactement pareil
        # chain = prompt | self.pedagogical_llm | JsonOutputParser()
```

## 📦 Fichiers créés

| Fichier | Description |
|---------|-------------|
| [app/chains/llm/universal_llm.py](app/chains/llm/universal_llm.py) | Classe `UniversalLLM` et helper `create_universal_llm` |
| [test_universal_llm.py](test_universal_llm.py) | Tests complets (6 scénarios) |
| [UNIVERSAL_LLM_GUIDE.md](UNIVERSAL_LLM_GUIDE.md) | Guide complet d'utilisation |
| [INTEGRATION_UNIVERSAL_LLM.md](INTEGRATION_UNIVERSAL_LLM.md) | Guide d'intégration dans CourseMaterialGeneratorV2 |
| [README_UNIVERSAL_LLM.md](README_UNIVERSAL_LLM.md) | Ce fichier |

## 🎨 Modèles supportés

### 34 modèles LangChain

**Anthropic Claude** :
- `LLMModel.CLAUDE_HAIKU_4_5_20251001` ⭐ Recommandé
- `LLMModel.CLAUDE_SONNET_4_5_20250929`
- `LLMModel.CLAUDE_OPUS_4_5`

**Google Gemini** :
- `LLMModel.GEMINI_2_5_FLASH` (défaut)
- `LLMModel.GEMINI_3_FLASH_PREVIEW`

**OpenAI GPT** :
- `LLMModel.GPT_5_2`
- `LLMModel.GPT_5_MINI`
- `LLMModel.GPT_4O`
- `LLMModel.O1_MINI`

### 10 modèles Codex/O-series

**Codex** (via route `/api/utils/codex`) :
- `"gpt-5.1-codex"` ⭐ Recommandé
- `"gpt-5.1-codex-max"`
- `"gpt-5-codex"`

**O-Series** :
- `"o3"`
- `"o3-mini"`
- `"o4-mini"`

**Total** : **44 modèles disponibles** avec une seule interface !

## 🔧 Fonctionnalités

### ✅ Interface unique

```python
# Même code pour tous les modèles
llm = create_universal_llm(model)
response = await llm.ainvoke("prompt")
```

### ✅ Compatible LangChain LCEL

```python
chain = prompt | llm | JsonOutputParser()
result = await chain.ainvoke(inputs)
```

### ✅ Auto-détection Codex

```python
# Détecté automatiquement comme Codex
llm = create_universal_llm("gpt-5.1-codex")
llm = create_universal_llm("o3-mini")
```

### ✅ Support async/sync

```python
# Async (recommandé)
response = await llm.ainvoke("prompt")

# Sync (si nécessaire)
response = llm.invoke("prompt")
```

## 📊 Exemples d'utilisation

### Exemple 1 : Génération simple

```python
llm = create_universal_llm(LLMModel.GEMINI_2_5_FLASH)
response = await llm.ainvoke("Explain Python in one sentence")
```

### Exemple 2 : Avec JsonOutputParser

```python
from langchain_core.output_parsers import JsonOutputParser

prompt = ChatPromptTemplate.from_messages([
    ("system", "Return JSON with keys: title, content"),
    ("user", "{topic}")
])

llm = create_universal_llm("gpt-5.1-codex")  # Fonctionne avec Codex !
chain = prompt | llm | JsonOutputParser()

result = await chain.ainvoke({"topic": "Python variables"})
# result est un dict Python
```

### Exemple 3 : Changer de modèle facilement

```python
models = [
    LLMModel.GEMINI_2_5_FLASH,
    LLMModel.CLAUDE_HAIKU_4_5_20251001,
    "gpt-5.1-codex",
]

for model in models:
    llm = create_universal_llm(model)
    response = await llm.ainvoke("What is AI?")
    print(f"{model}: {response}")
```

## 🧪 Tests

Exécutez les tests pour vérifier que tout fonctionne :

```bash
# Démarrer le serveur FastAPI d'abord
uvicorn app.main:app --reload

# Dans un autre terminal
python test_universal_llm.py
```

Les tests couvrent :
1. ✅ Modèles LangChain (Gemini, Claude, GPT)
2. ✅ Modèles Codex (gpt-5.1-codex)
3. ✅ Chaînes LangChain (LCEL)
4. ✅ JsonOutputParser
5. ✅ Changement de modèle dynamique
6. ✅ Simulation CourseMaterialGeneratorV2

## 📖 Documentation

| Document | Temps de lecture | Contenu |
|----------|------------------|---------|
| [UNIVERSAL_LLM_GUIDE.md](UNIVERSAL_LLM_GUIDE.md) | 15 min | Guide complet avec exemples |
| [INTEGRATION_UNIVERSAL_LLM.md](INTEGRATION_UNIVERSAL_LLM.md) | 10 min | Intégration dans CourseMaterialGeneratorV2 |
| [test_universal_llm.py](test_universal_llm.py) | 5 min | Exemples de code exécutables |

## 🎯 Pour CourseMaterialGeneratorV2

### Modification à faire

**Une seule ligne** à changer dans le constructeur :

```python
# Avant
self.pedagogical_llm = LLMModelFactory.get_llm(pedagogical_model)

# Après
self.pedagogical_llm = create_universal_llm(pedagogical_model)
```

### Utilisation avec Codex

```python
llm_config = LLMConfigDto(
    pedagogical_json_model="gpt-5.1-codex",  # ✅ Fonctionne maintenant !
    group_json_model=LLMModel.GEMINI_2_5_FLASH,
    path_groups_model=LLMModel.CLAUDE_HAIKU_4_5_20251001
)
```

## 💡 Cas d'usage recommandés

### Pour génération pédagogique

```python
LLMConfigDto(
    pedagogical_json_model=LLMModel.CLAUDE_HAIKU_4_5_20251001  # Qualité
)
```

### Pour génération de code

```python
LLMConfigDto(
    pedagogical_json_model="gpt-5.1-codex"  # Optimisé pour le code
)
```

### Pour rapidité

```python
LLMConfigDto(
    pedagogical_json_model=LLMModel.GEMINI_2_5_FLASH  # Rapide + économique
)
```

## ⚠️ Important

### Configuration requise

Pour les modèles Codex/O-series, le serveur FastAPI doit être démarré :

```bash
uvicorn app.main:app --reload
```

### URL personnalisée

Si votre serveur n'est pas sur `localhost:8000` :

```python
llm = create_universal_llm(
    "gpt-5.1-codex",
    api_base_url="http://your-server:8000"
)
```

## 📊 Comparaison

| Aspect | LLMModelFactory | UniversalLLM |
|--------|-----------------|--------------|
| Modèles LangChain | ✅ 34 modèles | ✅ 34 modèles |
| Modèles Codex | ❌ Non supportés | ✅ 5 modèles |
| Modèles O-series | ⚠️ Seulement o1-mini | ✅ 6 modèles (o1-mini + 5) |
| Interface | Enum uniquement | Enum + String |
| Compatibilité LCEL | ✅ | ✅ |
| Auto-détection | ❌ | ✅ |

## 🚀 Résumé

**UniversalLLM** = **44 modèles** avec **1 seule interface**

```python
# ❌ Avant : 2 façons différentes
if is_codex:
    # Appel HTTP manuel...
else:
    llm = LLMModelFactory.get_llm(model)

# ✅ Après : 1 seule façon pour TOUT
llm = create_universal_llm(model)
response = await llm.ainvoke("prompt")
```

## 🔗 Liens utiles

- [CODEX_ROUTE.md](CODEX_ROUTE.md) - Route Codex dédiée
- [LLM_CONFIGURATION.md](LLM_CONFIGURATION.md) - Configuration globale LLMs
- [API_RESPONSES_DIFFERENCES.md](API_RESPONSES_DIFFERENCES.md) - Différences API

---

**Version** : 1.0.0
**Date** : 2026-01-06
**Status** : ✅ Production ready

**Prêt à utiliser TOUS les modèles ?** → Lisez [UNIVERSAL_LLM_GUIDE.md](UNIVERSAL_LLM_GUIDE.md) ! 🚀
