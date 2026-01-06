# Route GPT-5.1-Codex

Route API pour appeler directement GPT-5.1-codex avec LangChain via l'endpoint OpenAI `/v1/responses`.

## Endpoint

```
POST /api/utils/codex
```

## Pourquoi cette route ?

Les modèles **GPT-5.1-codex** et les modèles **O-series** (raisonnement) d'OpenAI utilisent l'endpoint `/v1/responses` au lieu du standard `/v1/chat/completions`.

Cela les rend **incompatibles avec LangChain's ChatOpenAI**, qui utilise uniquement `/v1/chat/completions`.

Cette route contourne cette limitation en appelant directement l'API OpenAI avec le bon endpoint.

> **Note importante** : L'API `/v1/responses` utilise le paramètre `input` au lieu de `messages`, mais la route accepte `messages` et fait la conversion automatiquement.

## Modèles supportés

Cette route peut appeler les modèles suivants :

### GPT-5 Codex (optimisés pour le code)
- `gpt-5.1-codex-max` - Version maximale de GPT-5.1-codex
- `gpt-5.1-codex` - Version standard (recommandé)
- `gpt-5-codex` - GPT-5 Codex
- `gpt-5.1-codex-mini` - Version mini
- `codex-mini-latest` - Dernier mini Codex

### O-Series (modèles de raisonnement)
- `o3` - O3
- `o3-deep-research` - O3 avec recherche approfondie
- `o4-mini` - O4 Mini
- `o4-mini-deep-research` - O4 Mini avec recherche
- `o3-mini` - O3 Mini

> ⚠️ **Note**: `o1-mini` est déjà supporté dans LangChain via l'endpoint standard, pas besoin d'utiliser cette route.

## Format de la requête

```json
{
  "messages": [
    {
      "role": "system",
      "content": "You are a Python expert."
    },
    {
      "role": "user",
      "content": "Write a function to calculate fibonacci numbers"
    }
  ],
  "model": "gpt-5.1-codex",
  "temperature": 0.0,
  "max_tokens": 2048
}
```

### Paramètres

| Paramètre | Type | Requis | Défaut | Description |
|-----------|------|--------|--------|-------------|
| `messages` | Array | ✅ Oui | - | Liste des messages (role: system/user/assistant, content: texte) |
| `model` | String | ❌ Non | `"gpt-5.1-codex"` | Nom du modèle Codex ou O-series à utiliser |
| `temperature` | Float | ❌ Non | `0.0` | ⚠️ **Ignoré** - Non supporté par les modèles Codex/O-series |
| `max_tokens` | Integer | ❌ Non | `2048` | ⚠️ **Ignoré** - Non supporté par l'API /v1/responses |

> **⚠️ Important** : Les modèles Codex et O-series n'acceptent ni `temperature` ni `max_tokens`. Ces paramètres sont acceptés dans la requête pour compatibilité mais ignorés lors de l'appel à l'API OpenAI.

## Format de la réponse

```json
{
  "success": true,
  "response": "def fibonacci(n):\n    if n <= 1:\n        return n\n    ...",
  "error": null,
  "raw_response": {
    "id": "resp_...",
    "object": "response",
    "created": 1234567890,
    "model": "gpt-5.1-codex",
    "choices": [...]
  }
}
```

### Champs de réponse

| Champ | Type | Description |
|-------|------|-------------|
| `success` | Boolean | `true` si la requête a réussi, `false` sinon |
| `response` | String | Le contenu de la réponse du modèle (null en cas d'erreur) |
| `error` | String | Message d'erreur (null si succès) |
| `raw_response` | Object | Réponse brute complète de l'API OpenAI (null en cas d'erreur) |

## Exemples d'utilisation

### Exemple 1: Curl simple

```bash
curl -X POST "http://localhost:8000/api/utils/codex" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "system",
        "content": "You are a Python expert."
      },
      {
        "role": "user",
        "content": "Write a function to calculate fibonacci numbers"
      }
    ],
    "model": "gpt-5.1-codex",
    "temperature": 0.0,
    "max_tokens": 2048
  }'
```

### Exemple 2: Python avec httpx

```python
import httpx
import asyncio

async def call_codex():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/utils/codex",
            json={
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a code refactoring expert."
                    },
                    {
                        "role": "user",
                        "content": "Refactor this code: ..."
                    }
                ],
                "model": "gpt-5.1-codex",
                "temperature": 0.0
            }
        )
        return response.json()

result = asyncio.run(call_codex())
print(result["response"])
```

### Exemple 3: JavaScript/TypeScript

```javascript
const response = await fetch('http://localhost:8000/api/utils/codex', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    messages: [
      {
        role: 'system',
        content: 'You are a JavaScript expert.'
      },
      {
        role: 'user',
        content: 'Write a React hook for data fetching'
      }
    ],
    model: 'gpt-5.1-codex',
    temperature: 0.0,
    max_tokens: 2048
  })
});

const data = await response.json();
console.log(data.response);
```

### Exemple 4: Tests unitaires automatiques

```bash
curl -X POST "http://localhost:8000/api/utils/codex" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "system",
        "content": "You are an expert in writing unit tests with pytest."
      },
      {
        "role": "user",
        "content": "Write pytest unit tests for this function:\n\ndef calculate_discount(price, discount_percentage):\n    if discount_percentage < 0 or discount_percentage > 100:\n        raise ValueError(\"Discount must be between 0 and 100\")\n    return price * (1 - discount_percentage / 100)"
      }
    ],
    "model": "gpt-5.1-codex"
  }'
```

## Cas d'usage recommandés

### 1. Génération de code
Les modèles Codex excellent dans la génération de code:
- Fonctions Python, JavaScript, TypeScript
- Scripts de traitement de données
- Algorithmes optimisés

### 2. Refactoring
Améliorer du code existant:
- Simplification de logique complexe
- Amélioration de la lisibilité
- Optimisation des performances

### 3. Tests unitaires
Génération automatique de tests:
- pytest (Python)
- Jest/Vitest (JavaScript)
- JUnit (Java)

### 4. Documentation
Génération de docstrings et commentaires:
- Docstrings Python (Google, NumPy, Sphinx style)
- JSDoc (JavaScript)
- JavaDoc (Java)

### 5. Conversion de code
Traduire du code entre langages:
- Python → JavaScript
- JavaScript → TypeScript
- SQL → Python (ORM)

## Configuration

Assurez-vous que la clé API OpenAI est configurée dans votre fichier `.env`:

```bash
OPENAI_API_KEY=sk-...
```

## Gestion des erreurs

### Erreur 500: OPENAI_API_KEY non configurée

```json
{
  "detail": "OPENAI_API_KEY not configured"
}
```

**Solution**: Ajoutez `OPENAI_API_KEY` dans votre fichier `.env`

### Erreur API OpenAI

```json
{
  "success": false,
  "response": null,
  "error": "API Error 401: Invalid API key",
  "raw_response": null
}
```

**Solution**: Vérifiez que votre clé API est valide

### Timeout

```json
{
  "success": false,
  "response": null,
  "error": "Request timeout",
  "raw_response": null
}
```

**Solution**: Le timeout par défaut est de 120 secondes. Réessayez ou réduisez `max_tokens`.

## Test

Utilisez le script de test fourni:

```bash
python test_codex_route.py
```

Ce script teste:
1. Génération de fonction Fibonacci
2. Refactoring de code
3. Génération de tests unitaires

## Différences avec LangChain standard

| Aspect | LangChain (ChatOpenAI) | Cette route |
|--------|------------------------|-------------|
| Endpoint | `/v1/chat/completions` | `/v1/responses` |
| Modèles supportés | GPT-4, GPT-4o, GPT-5, o1-mini | Codex, O-series (sauf o1-mini) |
| Intégration | Natif LangChain | Appel HTTP direct |
| Streaming | ✅ Supporté | ❌ Non supporté |
| Tools/Functions | ✅ Supporté | ❌ Non supporté |

## Notes importantes

1. **Pas de streaming**: Cette route ne supporte pas le streaming de réponses
2. **Timeout**: Par défaut 120 secondes, peut nécessiter ajustement pour les requêtes longues
3. **Rate limiting**: Respectez les limites de l'API OpenAI
4. **Coûts**: Les modèles Codex peuvent avoir des tarifs différents des modèles GPT standard

## Liens utiles

- [Documentation OpenAI API](https://platform.openai.com/docs/api-reference)
- [LangChain Documentation](https://python.langchain.com/)
- [Configuration LLM du projet](LLM_CONFIGURATION.md)
