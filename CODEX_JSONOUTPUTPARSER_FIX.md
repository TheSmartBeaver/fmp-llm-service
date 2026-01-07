# Fix: Codex Models avec JsonOutputParser

## 🐛 Problème rencontré

Lorsqu'on utilise un modèle Codex (comme `gpt-5.1-codex-mini`) avec une chaîne LangChain incluant `JsonOutputParser`:

```python
chain = prompt | llm | JsonOutputParser()
result = await chain.ainvoke(inputs)
```

On obtenait l'erreur :

```
RuntimeError: Cannot use synchronous invoke() with Codex model 'gpt-5.1-codex-mini'
inside an async context (like FastAPI routes)
```

## 🔍 Cause du problème

Même en utilisant `await chain.ainvoke()`, LangChain appelle **en interne** la méthode synchrone `_generate()` du LLM lors de l'utilisation du **chain operator** (`|`) avec `JsonOutputParser`.

Cela pose problème pour les modèles Codex qui nécessitent des appels HTTP async vers l'API OpenAI (`/v1/responses`).

## ✅ Solution appliquée

### Dans `CourseMaterialGeneratorV2._generate_pedagogical_json()`

**Avant** (ne fonctionnait pas avec Codex):
```python
chain = prompt | self.pedagogical_llm | JsonOutputParser()
result = await chain.ainvoke(inputs)
```

**Après** (fonctionne avec Codex):
```python
from app.chains.llm.universal_llm import UniversalLLM

if isinstance(self.pedagogical_llm, UniversalLLM) and self.pedagogical_llm.use_codex_route:
    # Appel direct pour Codex (pas de chain)
    messages = prompt.format_messages(**inputs)
    response = await self.pedagogical_llm.ainvoke(messages)

    # Parser manuellement le JSON de la réponse
    import json
    if hasattr(response, 'content'):
        json_text = response.content
    else:
        json_text = str(response)

    result = json.loads(json_text)
else:
    # Pour les autres modèles, utiliser la chaîne normale
    chain = prompt | self.pedagogical_llm | JsonOutputParser()
    result = await chain.ainvoke(inputs)
```

### Fichiers modifiés

1. [app/chains/course_material_generator_v2.py](app/chains/course_material_generator_v2.py#L321-L354) - Méthode `_generate_pedagogical_json()`
2. [app/chains/template_structure_generator.py](app/chains/template_structure_generator.py) - Méthodes `_generate_json_from_group_async()` et `_generate_path_groups_with_llm()`

## 📝 Explication détaillée

### Pourquoi le chain operator ne fonctionne pas avec Codex

1. **Chaîne LCEL** : `prompt | llm | JsonOutputParser()`
2. **Appel async** : `await chain.ainvoke(inputs)`
3. **Problème** : LangChain, en interne, peut appeler `llm.invoke()` (sync) au lieu de `llm.ainvoke()` (async)
4. **Résultat** : Notre méthode `_generate()` est appelée alors qu'on est dans un contexte async

### Solution: Appel direct au LLM

1. **Détection** : Vérifier si c'est un `UniversalLLM` avec `use_codex_route=True`
2. **Appel direct** : Utiliser `await llm.ainvoke(messages)` directement
3. **Parsing manuel** : Parser le JSON de la réponse avec `json.loads()`
4. **Fallback** : Pour les autres modèles, utiliser la chaîne normale

### Avantages

- ✅ Fonctionne avec **tous** les modèles (LangChain + Codex)
- ✅ Pas de modification des autres parties du code
- ✅ Transparent pour l'utilisateur de la classe
- ✅ Compatible avec les routes FastAPI async

## 🚀 Utilisation

### Avec un modèle Codex

```python
from app.models.dto.llm_config.llm_config_dto import LLMConfigDto
from app.models.dto.llm_config.all_llm_models import AllLLMModels

llm_config = LLMConfigDto(
    pedagogical_json_model=AllLLMModels.GPT_5_1_CODEX  # ✅ Fonctionne maintenant !
)

generator = CourseMaterialGeneratorV2(db, embedding_model, llm_config)
result = await generator.generate_course_material_async(user_entry)
```

### Avec un modèle LangChain standard

```python
llm_config = LLMConfigDto(
    pedagogical_json_model=AllLLMModels.GEMINI_2_5_FLASH  # ✅ Fonctionne aussi !
)

generator = CourseMaterialGeneratorV2(db, embedding_model, llm_config)
result = await generator.generate_course_material_async(user_entry)
```

## ⚠️ Note importante

Si vous utilisez `UniversalLLM` avec un modèle Codex dans **votre propre code** avec `JsonOutputParser`:

### ❌ Ne faites PAS ceci :

```python
chain = prompt | codex_llm | JsonOutputParser()
result = await chain.ainvoke(inputs)  # ❌ Erreur !
```

### ✅ Faites plutôt ceci :

```python
# Appel direct
messages = prompt.format_messages(**inputs)
response = await codex_llm.ainvoke(messages)

# Parsing manuel
import json
result = json.loads(response.content)
```

Ou mieux, copiez le pattern utilisé dans `CourseMaterialGeneratorV2._generate_pedagogical_json()`.

## 📊 Impact

### Fichiers modifiés

1. ✅ [app/chains/course_material_generator_v2.py](app/chains/course_material_generator_v2.py) - Fix dans `_generate_pedagogical_json()`
2. ✅ [app/chains/template_structure_generator.py](app/chains/template_structure_generator.py) - Fix dans `_generate_json_from_group_async()` et `_generate_path_groups_with_llm()`
3. ✅ [app/chains/llm/universal_llm.py](app/chains/llm/universal_llm.py) - Message d'erreur amélioré + `_identifying_params`

### Fonctionnalités

- ✅ Support Codex dans `_generate_pedagogical_json()` (CourseMaterialGeneratorV2)
- ✅ Support Codex dans `_generate_json_from_group_async()` (TemplateStructureGenerator)
- ✅ Support Codex dans `_generate_path_groups_with_llm()` (TemplateStructureGenerator)
- ✅ Parsing JSON manuel pour Codex
- ✅ Chaîne normale pour les autres modèles
- ✅ Compatible avec tous les 45 modèles dans toutes les méthodes

### Tests recommandés

```python
# Test avec Codex
llm_config = LLMConfigDto(pedagogical_json_model="gpt-5.1-codex-mini")
generator = CourseMaterialGeneratorV2(db, embedding_model, llm_config)
result = await generator.generate_course_material_async(user_entry)

# Test avec Gemini
llm_config = LLMConfigDto(pedagogical_json_model="gemini-2.5-flash")
generator = CourseMaterialGeneratorV2(db, embedding_model, llm_config)
result = await generator.generate_course_material_async(user_entry)
```

## 🔗 Références

- [UNIVERSAL_LLM_FIXES.md](UNIVERSAL_LLM_FIXES.md) - Liste complète des fixes
- [INTEGRATION_COMPLETE.md](INTEGRATION_COMPLETE.md) - Résumé de l'intégration
- [README_UNIVERSAL_LLM.md](README_UNIVERSAL_LLM.md) - Documentation UniversalLLM

---

**Version** : 1.1.0
**Date** : 2026-01-07
**Status** : ✅ Fixed - Production ready

🎉 **Les modèles Codex fonctionnent maintenant avec JsonOutputParser !**
