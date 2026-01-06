# 🚀 Quick Start - Route GPT-5.1-Codex

Guide rapide pour utiliser la nouvelle route `/api/utils/codex` qui appelle GPT-5.1-codex avec LangChain.

## ⚡ Démarrage rapide (30 secondes)

### 1. Démarrer le serveur

```bash
uvicorn app.main:app --reload
```

### 2. Tester la route

```bash
curl -X POST "http://localhost:8000/api/utils/codex" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "system", "content": "You are a Python expert."},
      {"role": "user", "content": "Write a function to calculate fibonacci"}
    ]
  }'
```

### 3. Résultat attendu

```json
{
  "success": true,
  "response": "def fibonacci(n):\n    if n <= 1:\n        return n\n    ...",
  "error": null,
  "raw_response": {...}
}
```

## 📋 Pré-requis

Assurez-vous que votre fichier `.env` contient:

```bash
OPENAI_API_KEY=sk-...
```

## 📚 Fichiers créés

| Fichier | Description |
|---------|-------------|
| [app/routers/utils/router.py](app/routers/utils/router.py) | Route FastAPI `/api/utils/codex` |
| [CODEX_ROUTE.md](CODEX_ROUTE.md) | Documentation complète de la route |
| [test_codex_route.py](test_codex_route.py) | Script de test automatique |
| [example_codex_with_langchain.py](example_codex_with_langchain.py) | Exemples d'intégration avec LangChain |

## 🎯 Cas d'usage principaux

### 1. Génération de code

```bash
curl -X POST "http://localhost:8000/api/utils/codex" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "system", "content": "You are a Python expert."},
      {"role": "user", "content": "Write a quicksort implementation"}
    ],
    "model": "gpt-5.1-codex",
    "temperature": 0.0
  }'
```

### 2. Revue de code

```bash
curl -X POST "http://localhost:8000/api/utils/codex" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "system", "content": "You are a senior code reviewer."},
      {"role": "user", "content": "Review this code:\n\ndef foo(x):\n    return x*2"}
    ],
    "model": "gpt-5.1-codex"
  }'
```

### 3. Tests unitaires

```bash
curl -X POST "http://localhost:8000/api/utils/codex" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "system", "content": "You are a pytest expert."},
      {"role": "user", "content": "Write tests for: def add(a, b): return a + b"}
    ]
  }'
```

### 4. Conversion de code

```bash
curl -X POST "http://localhost:8000/api/utils/codex" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "system", "content": "You are a multilingual programmer."},
      {"role": "user", "content": "Convert this Python to JavaScript:\n\ndef greet(name):\n    return f\"Hello, {name}!\""}
    ]
  }'
```

## 🧪 Tester avec les scripts fournis

### Test basique

```bash
python test_codex_route.py
```

Ce script teste:
- ✅ Génération de fonction Fibonacci
- ✅ Refactoring de code
- ✅ Génération de tests unitaires

### Exemples LangChain

```bash
python example_codex_with_langchain.py
```

Ce script démontre:
- ✅ Génération simple de fonction
- ✅ Conversation multi-tours
- ✅ Workflow complexe (architecture → code → tests)
- ✅ Revue de code automatique
- ✅ Conversion Python → TypeScript

## 🔧 Paramètres disponibles

| Paramètre | Type | Requis | Défaut | Description |
|-----------|------|--------|--------|-------------|
| `messages` | Array | ✅ Oui | - | Messages (role + content) |
| `model` | String | ❌ Non | `"gpt-5.1-codex"` | Modèle à utiliser |
| `temperature` | Float | ❌ Non | `0.0` | ⚠️ Ignoré (non supporté) |
| `max_tokens` | Integer | ❌ Non | `2048` | ⚠️ Ignoré (non supporté) |

> **⚠️ Note** : Les modèles Codex/O-series n'acceptent ni `temperature` ni `max_tokens`. Le modèle décide lui-même de ces paramètres.

## 🎨 Modèles disponibles

### Codex (optimisés pour le code)
- `gpt-5.1-codex` ⭐ **Recommandé**
- `gpt-5.1-codex-max`
- `gpt-5-codex`
- `gpt-5.1-codex-mini`
- `codex-mini-latest`

### O-Series (raisonnement)
- `o3`
- `o3-deep-research`
- `o4-mini`
- `o4-mini-deep-research`
- `o3-mini`

## 📖 Documentation complète

Pour plus de détails, consultez:
- [CODEX_ROUTE.md](CODEX_ROUTE.md) - Documentation complète de l'API
- [LLM_CONFIGURATION.md](LLM_CONFIGURATION.md) - Configuration globale des LLMs

## ❓ FAQ

### Quelle est la différence avec les routes existantes?

| Aspect | Routes existantes | Route Codex |
|--------|-------------------|-------------|
| Endpoint OpenAI | `/v1/chat/completions` | `/v1/responses` |
| Modèles | GPT-4, GPT-5, Gemini, Claude | Codex, O-series |
| Intégration | LangChain natif | Appel HTTP direct |
| Spécialisation | Généraliste | Code & raisonnement |

### Pourquoi ne pas utiliser LangChain directement?

LangChain's `ChatOpenAI` ne supporte que `/v1/chat/completions`. Les modèles Codex et O-series nécessitent `/v1/responses`, d'où cette route personnalisée.

### Quand utiliser GPT-5.1-codex vs GPT-5?

**Utilisez GPT-5.1-codex pour:**
- Génération de code
- Refactoring
- Tests unitaires
- Revue de code
- Conversion entre langages

**Utilisez GPT-5 pour:**
- Génération de contenu pédagogique
- Analyse de texte
- Traduction
- Conversation générale

### Les modèles O-series sont-ils supportés?

Oui! Les modèles `o3`, `o3-mini`, `o4-mini` peuvent être utilisés via cette route pour des tâches nécessitant du raisonnement approfondi.

Exception: `o1-mini` fonctionne avec l'endpoint standard et est déjà disponible dans les routes existantes.

## 🆘 Support

En cas de problème:

1. **Vérifier le serveur**: `http://localhost:8000/docs`
2. **Vérifier la clé API**: `.env` contient `OPENAI_API_KEY`
3. **Consulter les logs**: Terminal où tourne `uvicorn`

## 🎓 Exemples complets

Voir les fichiers d'exemples pour des cas d'usage détaillés:
- [test_codex_route.py](test_codex_route.py) - Tests basiques
- [example_codex_with_langchain.py](example_codex_with_langchain.py) - Intégration LangChain

## 📝 Résumé

```bash
# 1. Démarrer le serveur
uvicorn app.main:app --reload

# 2. Appeler la route
curl -X POST "http://localhost:8000/api/utils/codex" \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "Write code"}]}'

# 3. Profiter de GPT-5.1-codex! 🎉
```

---

**Prêt à coder?** Lancez `python test_codex_route.py` pour voir la magie opérer! ✨
