# Différences entre /v1/chat/completions et /v1/responses

Ce document explique les différences entre l'endpoint standard OpenAI `/v1/chat/completions` et l'endpoint spécial `/v1/responses` utilisé par les modèles Codex et O-series.

## 📋 Tableau comparatif

| Aspect | `/v1/chat/completions` | `/v1/responses` |
|--------|------------------------|-----------------|
| **Modèles supportés** | GPT-4, GPT-4o, GPT-5, o1-mini | Codex, O-series (o3, o4-mini, etc.) |
| **Paramètre messages** | ✅ `messages` | ❌ Utilise `input` à la place |
| **max_tokens** | ✅ Supporté | ❌ Non supporté |
| **temperature** | ✅ Supporté | ❌ Non supporté |
| **Streaming** | ✅ Supporté (`stream: true`) | ❓ Non testé |
| **Function calling** | ✅ Supporté (`tools`) | ❌ Non supporté |
| **Compatible LangChain** | ✅ Oui (ChatOpenAI) | ❌ Non |

## 🔧 Différences de paramètres

### Exemple avec /v1/chat/completions

```json
{
  "model": "gpt-4o",
  "messages": [
    {"role": "user", "content": "Hello"}
  ],
  "temperature": 0.7,
  "max_tokens": 100
}
```

### Exemple avec /v1/responses

```json
{
  "model": "gpt-5.1-codex",
  "input": [
    {"role": "user", "content": "Hello"}
  ]
  // temperature et max_tokens ne sont PAS supportés
}
```

## ⚠️ Points d'attention

### 1. Paramètre `input` vs `messages`

L'API `/v1/responses` utilise `input` au lieu de `messages`. Notre route `/api/utils/codex` fait la conversion automatiquement :

```python
# Ce que vous envoyez
{
  "messages": [...]
}

# Ce que la route envoie à OpenAI
{
  "input": [...]
}
```

### 2. Pas de `max_tokens`

L'API `/v1/responses` **ne permet pas** de limiter la longueur de la réponse. Le modèle décide lui-même quand s'arrêter.

**Conséquence** : Les réponses peuvent être plus longues que prévu. Pensez au timeout.

### 3. Pas de contrôle de temperature

Les modèles Codex et O-series n'acceptent **pas** le paramètre `temperature`. Ils utilisent leurs propres heuristiques internes pour générer du code ou raisonner, qui sont généralement déterministes.

### 4. Pas de function calling

L'endpoint `/v1/responses` ne supporte pas les `tools` ou `functions`. Impossible d'utiliser le function calling avec Codex ou O-series via cette API.

## 🎯 Quand utiliser quel endpoint ?

### Utilisez `/v1/chat/completions` (routes standard) pour :
- ✅ Génération de contenu pédagogique
- ✅ Conversations générales
- ✅ Tasks nécessitant function calling
- ✅ Contrôle strict de la longueur (`max_tokens`)
- ✅ Streaming de réponses

### Utilisez `/v1/responses` (route `/api/utils/codex`) pour :
- ✅ Génération de code optimisée (Codex)
- ✅ Raisonnement approfondi (O-series)
- ✅ Tasks où la qualité prime sur le contrôle de longueur
- ✅ Utilisation des modèles de pointe (o3, o4-mini)

## 📊 Modèles et endpoints

### Modèles sur /v1/chat/completions
- GPT-4 (toutes versions)
- GPT-4o (toutes versions)
- GPT-5 (sauf Codex)
- o1-mini ✅ (exception dans les O-series)
- Gemini (via route dédiée)
- Claude (via route dédiée)

### Modèles sur /v1/responses
- GPT-5.1-codex (toutes versions)
- GPT-5-codex
- o3, o3-mini, o3-deep-research
- o4-mini, o4-mini-deep-research

## 🔍 Format de réponse

### /v1/chat/completions

```json
{
  "id": "chatcmpl-...",
  "object": "chat.completion",
  "created": 1234567890,
  "model": "gpt-4o",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "La réponse..."
      },
      "finish_reason": "stop"
    }
  ]
}
```

### /v1/responses

```json
{
  "id": "resp-...",
  "object": "response",
  "created": 1234567890,
  "model": "gpt-5.1-codex",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "La réponse..."
      },
      "finish_reason": "stop"
    }
  ]
}
```

> Le format de réponse est très similaire, la principale différence est `"object": "response"` au lieu de `"chat.completion"`.

## 💡 Recommandations

### Pour la génération de code

**Meilleur choix** : `gpt-5.1-codex` via `/api/utils/codex`
- Optimisé spécifiquement pour le code
- Meilleure compréhension des patterns de code
- Pas besoin de limiter `max_tokens` car le code a une longueur naturelle

**Alternative** : `gpt-5-mini` ou `gpt-4o` via routes standard
- Si vous avez besoin de function calling
- Si vous devez streamer la réponse
- Si vous avez besoin de contrôler `max_tokens`

### Pour le raisonnement complexe

**Meilleur choix** : `o3-mini` ou `o4-mini` via `/api/utils/codex`
- Raisonnement approfondi
- Meilleure logique

**Alternative** : `o1-mini` via routes standard
- Compatible LangChain
- Supporte les outils LangChain

## 📚 Ressources

- [Documentation OpenAI API](https://platform.openai.com/docs/api-reference)
- [Route Codex - Documentation](CODEX_ROUTE.md)
- [Quick Start Codex](QUICKSTART_CODEX.md)
- [Configuration LLM](LLM_CONFIGURATION.md)

## 🔄 Historique des découvertes

### 2026-01-06
1. **Découverte** : L'API `/v1/responses` utilise `input` au lieu de `messages`
   - **Solution** : Conversion automatique dans la route

2. **Découverte** : Le paramètre `max_tokens` n'est pas supporté
   - **Solution** : Paramètre retiré du payload envoyé à l'API

3. **Découverte** : `temperature` n'est **pas du tout supporté** par les modèles Codex/O-series
   - **Solution** : Paramètre retiré du payload envoyé à l'API

---

**Dernière mise à jour** : 2026-01-06
