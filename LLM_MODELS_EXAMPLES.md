# Exemples d'utilisation des modèles LLM

Ce document présente des exemples concrets d'utilisation de différentes combinaisons de modèles LLM pour optimiser coût/performance selon vos besoins.

## Scénarios d'utilisation

### 1. Configuration économique (Budget limité)

Utilisation de modèles rapides et peu coûteux pour toutes les étapes.

```json
{
  "llm_config": {
    "pedagogical_json_model": "gemini-2.5-flash-lite",
    "group_json_model": "gemini-2.0-flash-lite",
    "path_groups_model": "gpt-4o-mini"
  }
}
```

**Avantages :**
- Coût très faible
- Rapidité d'exécution
- Bon pour le prototypage

**Cas d'usage :** Tests, développement, volumes importants

---

### 2. Configuration équilibrée (Recommandée)

Bon équilibre entre qualité et coût.

```json
{
  "llm_config": {
    "pedagogical_json_model": "gemini-2.5-flash",
    "group_json_model": "claude-3-5-haiku-20241022",
    "path_groups_model": "gpt-5-mini"
  }
}
```

**Avantages :**
- Excellente qualité de sortie
- Coût raisonnable
- Bonne vitesse

**Cas d'usage :** Production standard, la plupart des cas

---

### 3. Configuration haute qualité (Qualité maximale)

Utilisation des meilleurs modèles pour chaque tâche.

```json
{
  "llm_config": {
    "pedagogical_json_model": "claude-sonnet-4-5-20250929",
    "group_json_model": "gpt-5.2",
    "path_groups_model": "claude-opus-4-5"
  }
}
```

**Avantages :**
- Qualité exceptionnelle
- Compréhension approfondie
- Résultats les plus précis

**Cas d'usage :** Contenus critiques, formations premium

---

### 4. Configuration spécialisée Codex (Contenu de programmation)

Optimisée pour les cours de programmation et documentation technique.

```json
{
  "llm_config": {
    "pedagogical_json_model": "gpt-5.1-codex",
    "group_json_model": "gpt-5-codex",
    "path_groups_model": "gpt-5.1-codex-mini"
  }
}
```

**Avantages :**
- Excellente compréhension du code
- Explications techniques précises
- Exemples de code de qualité

**Cas d'usage :** Cours de programmation, tutoriels techniques

---

### 5. Configuration raisonnement profond (O-Series)

⚠️ **Note importante** : Les modèles O-series utilisent une configuration spéciale et peuvent être plus lents (timeout augmenté à 5 minutes).

Utilisation de modèles de raisonnement pour des sujets complexes.

```json
{
  "llm_config": {
    "pedagogical_json_model": "o3-mini",
    "group_json_model": "o1-mini",
    "path_groups_model": "o3-mini"
  }
}
```

**Avantages :**
- Raisonnement approfondi
- Analyse en profondeur
- Connexions conceptuelles avancées
- Excellent pour les problèmes complexes

**Inconvénients :**
- Plus lents que les modèles standards
- Plus coûteux
- Pas de contrôle de température

**Cas d'usage :** Mathématiques avancées, physique théorique, philosophie, problèmes de logique

---

### 6. Configuration Claude pure (Cohérence maximale)

Tous les modèles Anthropic pour une cohérence de style.

```json
{
  "llm_config": {
    "pedagogical_json_model": "claude-sonnet-4-5-20250929",
    "group_json_model": "claude-3-7-sonnet-20250219",
    "path_groups_model": "claude-haiku-4-5-20251001"
  }
}
```

**Avantages :**
- Style d'écriture cohérent
- Excellente qualité narrative
- Sécurité et éthique renforcées

**Cas d'usage :** Contenus sensibles, formations professionnelles

---

### 7. Configuration Gemini pure (Multimodal)

Utilisation exclusive de modèles Google pour l'intégration multimodale.

```json
{
  "llm_config": {
    "pedagogical_json_model": "gemini-3-flash-preview",
    "group_json_model": "gemini-2.5-flash",
    "path_groups_model": "gemini-2.0-flash"
  }
}
```

**Avantages :**
- Excellente gestion des images/vidéos
- Bonne intégration Google Workspace
- Rapidité

**Cas d'usage :** Contenus avec médias, intégration Google

---

### 8. Configuration mixte optimisée (Meilleur de chaque provider)

Chaque modèle est choisi pour ses forces spécifiques.

```json
{
  "llm_config": {
    "pedagogical_json_model": "claude-sonnet-4-5-20250929",
    "group_json_model": "gemini-2.5-flash",
    "path_groups_model": "gpt-5.2"
  }
}
```

**Pourquoi cette configuration :**
- **Claude Sonnet 4.5** : Excellence en structuration pédagogique, compréhension contextuelle
- **Gemini 2.5 Flash** : Rapidité et efficacité pour la génération de groupes JSON
- **GPT-5.2** : Précision dans l'analyse et le regroupement de chemins

**Cas d'usage :** Production de haute qualité avec contraintes de temps

---

## Comparaison par tâche

### Pour `pedagogical_json_model` (Génération du JSON pédagogique)

**Meilleurs choix :**
1. `claude-sonnet-4-5-20250929` - Structure narrative excellente
2. `claude-opus-4-5` - Compréhension contextuelle supérieure
3. `gpt-5.2` - Qualité et cohérence
4. `o3-deep-research` - Pour sujets complexes

**Choix économiques :**
- `gemini-2.5-flash` - Bon rapport qualité/prix
- `gpt-5-mini` - Rapide et efficace

### Pour `group_json_model` (Génération des JSONs de groupe)

**Meilleurs choix :**
1. `gpt-5.2` - Excellente précision structurelle
2. `claude-3-7-sonnet-20250219` - Bonne analyse sémantique
3. `gemini-2.5-flash` - Rapide et fiable

**Choix économiques :**
- `gpt-4o-mini` - Très bon rapport qualité/prix
- `claude-3-5-haiku-20241022` - Rapide et précis

### Pour `path_groups_model` (Regroupement de chemins)

**Meilleurs choix :**
1. `o4-mini` - Excellent raisonnement logique
2. `gpt-5.2` - Analyse de patterns précise
3. `claude-haiku-4-5-20251001` - Rapide et fiable

**Choix économiques :**
- `gpt-4o-mini` - Performant et économique
- `gemini-2.0-flash` - Très rapide

---

## Recommandations par type de contenu

### Cours de sciences (Mathématiques, Physique, Chimie)
```json
{
  "pedagogical_json_model": "o3-mini",
  "group_json_model": "gpt-5.2",
  "path_groups_model": "o1-mini"
}
```
⚠️ **Note**: Les modèles O-series sont plus lents mais excellent pour le raisonnement mathématique.

### Cours de langues
```json
{
  "pedagogical_json_model": "claude-sonnet-4-5-20250929",
  "group_json_model": "gemini-2.5-flash",
  "path_groups_model": "gpt-5-mini"
}
```

### Cours de programmation
```json
{
  "pedagogical_json_model": "gpt-5.1-codex",
  "group_json_model": "gpt-5-codex",
  "path_groups_model": "gpt-5.1-codex-mini"
}
```

### Cours d'histoire / Sciences humaines
```json
{
  "pedagogical_json_model": "claude-opus-4-5",
  "group_json_model": "claude-sonnet-4-20250514",
  "path_groups_model": "gpt-5.1"
}
```

### Cours avec beaucoup de médias (images/vidéos)
```json
{
  "pedagogical_json_model": "gemini-3-flash-preview",
  "group_json_model": "gemini-2.5-flash",
  "path_groups_model": "gemini-2.0-flash"
}
```

---

## Tests A/B suggérés

Pour trouver la meilleure configuration pour votre cas d'usage :

1. **Test de base :**
   - Configuration par défaut (gemini-2.5-flash partout)
   - vs Configuration équilibrée

2. **Test qualité :**
   - Configuration économique
   - vs Configuration haute qualité
   - Mesurer : satisfaction utilisateur, taux d'erreur

3. **Test provider :**
   - Configuration Claude pure
   - vs Configuration Gemini pure
   - vs Configuration OpenAI pure
   - Mesurer : cohérence, style, pertinence

4. **Test par domaine :**
   - Tester les configurations spécialisées pour votre domaine
   - Comparer avec la configuration équilibrée
