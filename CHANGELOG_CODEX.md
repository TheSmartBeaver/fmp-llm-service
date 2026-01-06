# Changelog - Route GPT-5.1-Codex

## 2026-01-06 - Ajout de la route `/api/utils/codex`

### 🎯 Objectif

Permettre l'utilisation de GPT-5.1-codex et des modèles O-series via une route dédiée, contournant l'incompatibilité avec LangChain's ChatOpenAI.

### 📝 Problème résolu

Les modèles **GPT-5.1-codex** et la majorité des **O-series** (sauf o1-mini) utilisent l'endpoint OpenAI `/v1/responses` au lieu de `/v1/chat/completions`, ce qui les rend incompatibles avec LangChain's ChatOpenAI.

Cette route permet de les appeler directement via l'API OpenAI tout en conservant une interface simple et cohérente avec le reste du projet.

### ✨ Nouveautés

#### 1. Nouvelle route API

**Endpoint** : `POST /api/utils/codex`

**Fichier modifié** : [app/routers/utils/router.py](app/routers/utils/router.py)

**Fonctionnalités** :
- ✅ Appel direct à l'API OpenAI `/v1/responses`
- ✅ Support de tous les modèles Codex (5 modèles)
- ✅ Support des modèles O-series (5 modèles)
- ✅ Gestion d'erreurs complète
- ✅ Timeout configurable (120s par défaut)
- ✅ Réponse structurée avec `success`, `response`, `error`, `raw_response`

#### 2. Modèles supplémentaires disponibles

**Total : 10 nouveaux modèles**

**GPT-5 Codex (5 modèles)** :
- `gpt-5.1-codex-max`
- `gpt-5.1-codex` ⭐ Recommandé
- `gpt-5-codex`
- `gpt-5.1-codex-mini`
- `codex-mini-latest`

**O-Series (5 modèles)** :
- `o3`
- `o3-deep-research`
- `o4-mini`
- `o4-mini-deep-research`
- `o3-mini`

> Note: `o1-mini` reste disponible via LangChain standard

#### 3. Documentation complète

**Nouveaux fichiers créés** :

| Fichier | Taille | Description |
|---------|--------|-------------|
| [CODEX_ROUTE.md](CODEX_ROUTE.md) | 7.9 KB | Documentation complète de la route |
| [QUICKSTART_CODEX.md](QUICKSTART_CODEX.md) | 6.1 KB | Guide de démarrage rapide |
| [test_codex_route.py](test_codex_route.py) | 4.6 KB | Script de test automatique |
| [example_codex_with_langchain.py](example_codex_with_langchain.py) | 8.5 KB | Exemples d'intégration LangChain |
| [CHANGELOG_CODEX.md](CHANGELOG_CODEX.md) | Ce fichier | Changelog détaillé |

**Fichiers mis à jour** :

| Fichier | Modifications |
|---------|---------------|
| [LLM_CONFIGURATION.md](LLM_CONFIGURATION.md) | Ajout section Codex et mise à jour O-series |
| [app/routers/utils/router.py](app/routers/utils/router.py) | Ajout route `/codex` et modèles Pydantic |

### 🚀 Utilisation

#### Exemple basique (curl)

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

#### Exemple Python

```python
import httpx
import asyncio

async def test_codex():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/utils/codex",
            json={
                "messages": [
                    {"role": "user", "content": "Write a quicksort in Python"}
                ],
                "model": "gpt-5.1-codex"
            }
        )
        result = response.json()
        print(result["response"])

asyncio.run(test_codex())
```

### 📊 Récapitulatif des modèles

#### Avant cette mise à jour
- **34 modèles** disponibles via LangChain (factory LLM)
- Codex et O-series (sauf o1-mini) marqués comme "non supportés"

#### Après cette mise à jour
- **34 modèles** via LangChain (inchangé)
- **10 modèles supplémentaires** via route `/api/utils/codex`
- **Total : 44 modèles disponibles** dans l'écosystème

### 🎯 Cas d'usage recommandés

#### GPT-5.1-codex
- ✅ Génération de code (Python, JavaScript, TypeScript, etc.)
- ✅ Refactoring de code
- ✅ Génération de tests unitaires (pytest, Jest, JUnit)
- ✅ Revue de code automatique
- ✅ Conversion entre langages
- ✅ Documentation de code (docstrings, JSDoc)

#### Modèles O-series
- ✅ Raisonnement complexe
- ✅ Résolution de problèmes mathématiques
- ✅ Analyse approfondie
- ✅ Recherche et synthèse (deep-research)

### 🔧 Configuration requise

1. **Environnement** : Fichier `.env` avec `OPENAI_API_KEY`
2. **Dépendances** : `httpx` (déjà inclus dans le projet)
3. **Serveur** : FastAPI démarré (`uvicorn app.main:app`)

### ✅ Tests

Trois niveaux de tests disponibles :

1. **Test manuel** : `curl` (voir QUICKSTART_CODEX.md)
2. **Test automatique** : `python test_codex_route.py`
3. **Exemples avancés** : `python example_codex_with_langchain.py`

### 📈 Impact

#### Performance
- ✅ Timeout configurable (120s par défaut)
- ✅ Appels asynchrones (httpx.AsyncClient)
- ✅ Pas d'overhead LangChain

#### Compatibilité
- ✅ Rétrocompatible (aucune modification des routes existantes)
- ✅ API cohérente avec le reste du projet
- ✅ Format de réponse standardisé

#### Maintenabilité
- ✅ Code bien documenté (docstrings complètes)
- ✅ Gestion d'erreurs robuste
- ✅ Tests fournis
- ✅ Documentation exhaustive

### 🔮 Améliorations futures possibles

1. **Streaming** : Support du streaming de réponses
2. **Caching** : Cache des réponses fréquentes
3. **Rate limiting** : Limitation du nombre de requêtes
4. **Métriques** : Suivi des performances et coûts
5. **Batch processing** : Traitement par lots

### 📚 Références

- [Documentation OpenAI API](https://platform.openai.com/docs/api-reference)
- [Documentation LangChain](https://python.langchain.com/)
- [Configuration LLM du projet](LLM_CONFIGURATION.md)

### 👥 Contributeurs

- Date : 2026-01-06
- Créé avec Claude Sonnet 4.5

### 📝 Notes techniques

#### Choix d'implémentation

1. **Appel direct vs LangChain** : Nécessité d'appeler directement l'API OpenAI car l'endpoint `/v1/responses` n'est pas supporté par ChatOpenAI de LangChain.

2. **httpx vs requests** : Utilisation de `httpx` pour le support asynchrone natif, cohérent avec FastAPI.

3. **Route séparée** : Décision de créer une route dédiée plutôt que de modifier la factory LLM pour :
   - Maintenir la séparation des responsabilités
   - Éviter la complexité dans la factory
   - Permettre une API plus flexible pour ces modèles spéciaux

4. **Format de réponse** : Structure `{success, response, error, raw_response}` pour :
   - Gestion d'erreurs explicite
   - Debug facilité avec `raw_response`
   - Cohérence avec les autres routes du projet

5. **Conversion messages → input** : L'API `/v1/responses` utilise `input` au lieu de `messages`. La route accepte `messages` (format standard) et fait la conversion automatiquement pour faciliter l'utilisation.

### ⚠️ Limitations connues

1. **Pas de streaming** : L'implémentation actuelle ne supporte pas le streaming (peut être ajouté ultérieurement)
2. **Pas de function calling** : L'endpoint `/v1/responses` ne supporte pas les tools/functions
3. **Timeout fixe** : 120 secondes (configurable mais pas paramétrable par requête)
4. **Pas de max_tokens** : L'API `/v1/responses` ne permet pas de limiter la longueur de réponse
5. **Pas de temperature** : Les modèles Codex et O-series n'acceptent pas le paramètre `temperature` - ils utilisent leurs propres heuristiques

### 🎉 Conclusion

Cette mise à jour débloque l'accès à 10 modèles supplémentaires (Codex et O-series) tout en maintenant la compatibilité avec l'architecture existante. Les développeurs peuvent désormais bénéficier des capacités avancées de génération de code de GPT-5.1-codex via une API simple et bien documentée.

---

**Version** : 1.0.0
**Status** : ✅ Production ready
**Dernière mise à jour** : 2026-01-06
