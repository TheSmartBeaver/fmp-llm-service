# Audit de POST /courses/translate — 17 novembre 2026

Le clonage n'est pas complet. Les deux pertes principales sont les cartes des groupes et les blocs HTML des quiz. Le mode `sync` ne répare pas ces pertes sur une traduction déjà créée. Plusieurs chemins peuvent aussi faire échouer toute la transaction.

Audit du code local de `fmp-llm-service`, comparé au modèle et aux téléchargements de `FMP_API`, et au rendu Flutter de `beaver_learning`. Aucune base distante interrogée, aucune donnée métier modifiée, aucune logique applicative corrigée. Le schéma réellement déployé et les quantités manquantes pour un cours précis restent à vérifier.

Les numéros de ligne ci-dessous correspondent au code au moment de l'audit.

**Mise à jour après correction de l'erreur FK (17 novembre 2026) :** les points 2.2, 4.1, 4.3 et 4.4 sont corrigés. `_flush_cloned_graph` insère d'abord les lignes sans les références topic/support et parent/enfant, puis rétablit ces liens et les liaisons fichiers HTML avant un commit unique. La sync enregistre aussi les correspondances entre parents sources et cibles existants. Les autres omissions décrites dans l'audit restent à traiter.

Sept tests de régression dans `tests/test_course_translation_service.py` valident le clonage bidirectionnel topic/support, la hiérarchie chargée enfant avant parent, les trois chemins de rattachement des supports, les médias et quiz existants, la sync sous un parent cible et le rollback complet en cas d'échec. Ils s'exécutent avec les contraintes FK actives en SQLite, sans connexion distante :

```sh
.venv/bin/python -m unittest discover -s tests -p test_course_translation_service.py -v
```

## 1. Contenus omis lors d'un premier clonage

### 1.1. Les flashcards des groupes ne sont pas parcourues — prioritaire

**Source :** `app/services/course_translation_service.py:495`, `:663`, `:421`.

Chemin métier : `Topics.GroupSKU → Groups → Cards → HtmlContents → FileContentHtmlContent → FileContents`.

`_clone_topic` appelle `_clone_group_chain`, qui copie le groupe et ses ancêtres. Elle ne parcourt ni `Groups.Cards`, ni les groupes descendants. `_clone_flashcard_html` est appelée uniquement pour `Topics.HtmlContentSKU` ; ses cartes associées sont alors copiées, mais cela ne couvre pas les cartes du groupe du topic.

Un topic contenant un groupe de 20 cartes et aucun `HtmlContentSKU` direct donne donc un groupe cible vide : les 20 `Cards`, leurs `HtmlContents` et leurs liens fichiers ne sont pas créés.

Ce chemin par les groupes est bien celui des téléchargements : `FMP_API/API-FlashMemPro/Controllers/MarketplaceController.cs:537` et `:697`. Les groupes descendants appartenant effectivement au périmètre du cours doivent également être recensés ; les groupes ancêtres partagés ne doivent pas entraîner la copie de contenus étrangers au cours.

**Reproduction locale :** groupe contenant une carte → groupe cloné, zéro carte et zéro HtmlContent créés.

### 1.2. Les blocs riches des quiz sont entièrement ignorés — prioritaire

**Source :** `app/services/course_translation_service.py:378` ; `app/models/db/fmp_models.py:500`.

`QuizMaterials`, `QuizQuestions` et les ordres sont copiés. En revanche, le modèle Python ne contient même pas `QuizQuestionHtmlContents`, présent dans l'API C#.

Il manque le chemin :

`QuizQuestions → QuizQuestionHtmlContents → HtmlContents → FileContentHtmlContent → FileContents`.

Les slots à conserver sont `question`, `answer_1…N`, `explanation_0` et `explanation_1…N`, avec leurs nouveaux SKU, leurs deux FK remappées et leur `LastUpdated`.

Les JSON ne contiennent pas nécessairement le texte : un énoncé peut être uniquement `{"type":"html","version":1}`. Copier ce marqueur sans son slot laisse un bloc sans contenu. Le problème concerne les énoncés, réponses et explications HTML, ainsi que leurs images et autres fichiers.

**Références :** `FMP_API/API-FlashMemPro/Models/Entities/QuizQuestionHtmlContent.cs:8`, `MarketplaceController.cs:523` ; `beaver_learning/lib/src/widgets/quiz/quiz_rich_content.dart:51`.

**Reproduction locale :** question HTML clonée, aucun contenu HTML associé créé ; table de liaison absente des métadonnées Python.

### 1.3. Les catégories des assemblages sont perdues

**Source :** `app/services/course_translation_service.py:46`, `:421` ; `app/models/db/fmp_models.py:572`.

`IsAssembly` et le JSON sont copiés, mais pas les lignes de `AssemblyCategoryHtmlContent`. La table est importée par le service sans être utilisée. Un assemblage cloné perd donc son classement. Il faut recréer les liaisons vers les catégories conservées ou remappées selon leur périmètre ; dupliquer toutes les catégories globales n'est pas nécessaire.

## 2. Références incorrectes entre source et cible

### 2.1. Une carte peut rester dans le groupe source

**Source :** `app/services/course_translation_service.py:230`, `:464`, `:641`.

`Cards.GroupSKU` passe par `_map_existing`, qui conserve le SKU source si aucun remplacement n'est encore connu. Les groupes ne sont pas tous réservés avant la copie des cartes. Si le groupe d'une carte est traité plus tard, ou n'est pas porté par un topic parcouru, la carte copiée reste rattachée au groupe source. Le remapping créé ultérieurement ne corrige pas l'objet déjà construit.

**Reproduction locale :** copie d'une carte, puis de son groupe → `Cards.GroupSKU` contient toujours le SKU source malgré l'existence du nouveau SKU.

### 2.2. En sync, un nouveau topic peut avoir un parent dans le cours source

**Source :** `app/services/course_translation_service.py:748`, `:801`, `:687`.

Les topics existants sont rapprochés par `(Order, Path)`, mais leurs correspondances source → cible ne sont jamais ajoutées à `sku_map`. Pour un enfant ajouté sous un parent déjà présent en cible, `ParentCourseSKU` désigne la cible alors que `ParentSKU` conserve le parent source.

Le même défaut de correspondance peut toucher les groupes déjà présents et les supports partagés entre topics existants et nouveaux. Une correspondance connue doit être enregistrée avant de parcourir les nouveaux sous-graphes.

**Reproduction locale :** parent présent dans les deux langues + nouvel enfant → l'enfant cible pointe vers le parent source.

### 2.3. Le rapprochement `(Order, Path)` n'identifie pas sûrement un topic

**Source :** `app/services/course_translation_service.py:748`.

Le parent ne fait pas partie de la clé, `Path` est nullable et `Order` peut se répéter dans des branches différentes. Le dictionnaire écrase les doublons ; plusieurs topics sources peuvent correspondre au même topic cible. Inversement, changer l'ordre ou le chemin d'un topic peut créer une seconde copie au lieu de reconnaître l'existant.

**Reproduction locale :** deux topics sources de clé `(0, None)`, un seul topic cible de même clé → aucun topic manquant détecté.

Il n'existe aucune correspondance persistée entre les SKU source et cible : `sku_map` disparaît à la fin de l'appel. Pour les anciens clones, les rapprochements ambigus devront être identifiés avant réparation.

## 3. Le mode sync ne complète pas les cours existants

**Source :** `app/services/course_translation_service.py:740`.

Sur un topic existant, la seule mise à jour possible est son titre. Le service ne compare pas et ne complète pas :

- les supports et leurs contenus pédagogiques HTML ou liens fichiers ;
- les quiz, leurs questions, ordres, liens au support et slots HTML ;
- les groupes, cartes, contenus HTML et liens fichiers ;
- les EasterEggContents et leurs fichiers ;
- les associations et propriétés structurelles du topic, dont parent, groupe, support, publication et ordre.

Les supports rattachés directement au cours par `CourseSKU`, sans topic nouvellement ajouté, ne sont pas chargés en sync : `_load_course_materials` est appelée uniquement avec les topics manquants, sans SKU du cours.

Conséquences : relancer la route sur un clone incomplet ne le répare pas ; ajouter des cartes ou un quiz à un topic source existant ne les fait pas apparaître en cible. Un changement de `LastUpdated` du topic ne résout pas cela.

**Reproduction locale :** groupe/cartes source absents d'un topic cible déjà reconnu → aucune création.

## 4. Cas pouvant annuler toute la transaction

### 4.1. Insertion des liens fichiers avant celle de leur HtmlContent

**Source :** `app/services/course_translation_service.py:425`, `:449` ; `app/database.py:11`.

Le nouvel `HtmlContents` est ajouté à la session ORM, puis les lignes `FileContentHtmlContent` sont insérées immédiatement avec SQL Core. La session utilise `autoflush=False` et aucun flush n'a eu lieu. La FK du lien vise donc une ligne encore inexistante.

**Reproduction locale avec les méthodes et modèles réels, SQLite en mémoire et FK actives :** `FOREIGN KEY constraint failed` à l'insertion du lien. Il faut organiser les insertions en phases ; un flush global improvisé peut lui-même rencontrer les cycles du graphe.

### 4.2. Le partage de `Topics.FileSKU` contredit sa contrainte unique

**Source :** `app/services/course_translation_service.py:690` ; `app/models/db/fmp_models.py:167`.

La route réutilise le fichier source, alors que `IX_Topics_FileSKU` est unique. Un second topic ne peut pas référencer ce même fichier non nul.

Cette contrainte est également présente dans `FMP_API/API-FlashMemPro/Infrastructure/UnitOfWork.cs` (`Topic.FileContent.WithOne`) et dans le snapshot EF. Il faut soit une copie du fichier pour ce lien précis, soit faire évoluer cette relation pour autoriser le partage. Les liens fichiers many-to-many des HTML n'ont pas cette restriction.

**Vérification locale :** le clone reprend exactement le SKU soumis à l'index unique. L'échec PostgreSQL dépend de la présence de cet index dans la base déployée.

### 4.3. Réserver des UUID ne résout pas le cycle Topic ↔ CourseMaterial

**Source :** `app/services/course_translation_service.py:636`, `:692`, `:715`.

Quand `Topics.CourseMaterialSKU` et `CourseMaterials.TopicSKU` sont tous deux renseignés, les objets sont créés avec leurs FK scalaires sans phase intermédiaire. L'existence d'un UUID dans `sku_map` ne garantit pas l'existence de la ligne référencée.

**Reproduction locale avec les méthodes et modèles réels, FK actives :** échec au flush sur `INSERT INTO CourseMaterials`. Prévoir une insertion avec les liens circulaires temporairement nuls, puis leur mise à jour, ou une autre stratégie explicite compatible avec les contraintes.

### 4.4. L'ordre parent/enfant des topics n'est pas garanti

**Source :** `app/services/course_translation_service.py:248`, `:651`.

La requête des topics n'a ni tri hiérarchique ni `order_by`. Les objets sont ensuite ajoutés dans cet ordre avec `ParentSKU` renseigné. Un enfant peut être inséré avant son parent.

**Reproduction locale avec les méthodes et modèles réels, FK actives :** chargement enfant avant parent → échec au flush sur la FK du parent.

Ces erreurs font échouer le commit ou une insertion ; la route effectue alors un rollback. Elles n'expliquent pas une transaction partiellement validée, mais un clonage entièrement refusé.

## 5. Données présentes mais potentiellement invisibles dans l'application

**Source :** `app/services/course_translation_service.py:359`, `:387`, `:407`, `:434`, `:462`, `:483`, `:517`.

Les nouveaux contenus pédagogiques HTML, liens fichiers pédagogiques, quiz, questions, flashcards, cartes, groupes et EasterEggContents reprennent le `LastUpdated` source. Un nouvel objet créé aujourd'hui peut donc porter une date ancienne.

Les champs `LastUpdated` de `QuizMaterialQuestionOrders` et `CourseMaterialLinkedQuizzes` sont entièrement absents du modèle Python et des insertions. La migration C# `20260718223705_AddLastUpdatedToQuizLinkTables.cs` leur attribue par défaut le 19 juillet 2026, pas la date de l'opération.

Or `FMP_API/API-FlashMemPro/Controllers/SynchronizeController.cs:1090–1210` filtre ces entités avec `LastUpdated > lastMobileUpdate`. Un client déjà synchronisé peut recevoir les nouveaux topics datés du jour sans recevoir leurs dépendances plus anciennes. Le téléchargement intégral marketplace utilise un autre chemin : ce constat concerne la synchronisation incrémentale.

Le service ne gère pas non plus les versions marketplace. En sync, l'ajout de topics ne met pas nécessairement à jour `target_course.LastUpdated`, et aucune version de cours/topic n'est incrémentée. Les mécanismes C# de `CourseVersioningService` ne sont pas exécutés par les écritures SQLAlchemy directes.

À prévoir : date de modification cible courante pour les nouvelles lignes, versionnement approprié et suivi distinct de la révision source pour préserver les traductions déjà réalisées.

## 6. Autres contenus et champs du cours non repris

Le modèle Python est en retard sur le modèle C#. Les éléments suivants sont absents du modèle utilisé par cette route, donc absents du clonage et de la sync.

| Élément | Données concernées | Effet |
| --- | --- | --- |
| Course | `ShortDescription` | Description courte non reprise, ni disponible pour une traduction ultérieure en cible |
| Course | `IsPreSell`, `IsFounderExclusive`, `CommitmentMinScore` | Paramétrage de prévente, accès fondateur et seuil d'engagement non repris |
| Topic | `UnlockLevel` | Progression de déblocage non reprise |
| Course et Topic | `Version` | Pas de politique de versionnement explicite ; une nouvelle variante peut commencer à 1, mais une variante complétée doit signaler le changement |
| Contrat d'engagement | `CommitmentObjectives`, `CommitmentAnswerOptions` | Objectifs, explications, réponses, ordre, scores et pondérations absents dans la langue cible |
| Dictionnaire | `DictionaryEntries` | Termes, définitions, alias, sections, propriétés et autres champs absents |
| Dictionnaire | `DictionaryEntryOccurrences` | Associations aux topics et aux supports/cartes/questions absentes ; `SourceSKU` devra aussi être remappé selon `SourceType` |
| Dictionnaire | `DictionaryEntryHtmlContents`, `DictionaryEntryFileContents` | Sections HTML, slots, références de fichiers et leurs liens HTML/fichiers absents |
| Dictionnaire | `DictionaryEntryCategories`, `DictionaryEntryRelations` | Classement et relations entre entrées absents ; catégories par langue à résoudre/créer, relations internes à remapper |

**Références :** `FMP_API/API-FlashMemPro/Models/Entities/Course.cs`, `Topic.cs`, `CommitmentObjective.cs`, `CommitmentAnswerOption.cs`, `DictionaryEntry.cs` ; `MarketplaceController.cs:537` inclut déjà les HTML du dictionnaire dans le périmètre téléchargé.

La définition globale des propriétés du dictionnaire (`DictionaryPropertyDefinitions`) doit rester utilisable, mais n'a pas à être dupliquée pour chaque cours. Les libellés manquant dans la langue cible relèvent d'un travail de traduction du registre global.

## 7. L'extraction pour traduction ultérieure est elle aussi incomplète

**Source :** `app/services/course_translation_service.py:62–185` ; route `/courses/translation-sql`.

Les SELECT pour `HtmlContents` et `Cards` ne couvrent que `Topics.HtmlContentSKU`. Ils ignorent les cartes des groupes et les HTML attachés aux questions. Ils ne livrent pas les correspondances question/slot/HTML, ni les éléments du dictionnaire et du contrat d'engagement.

Même après un clonage corrigé, ces requêtes resteraient donc insuffisantes pour préparer tous les contenus à traduire. Le périmètre de l'extraction doit être aligné sur celui du clonage, avec les identifiants et associations nécessaires pour réinjecter les traductions.

## 8. Ce qui est déjà repris ou partagé à bon escient

- Au premier clone, les supports sont recherchés par les trois chemins `CourseMaterials.CourseSKU`, `CourseMaterials.TopicSKU` et `Topics.CourseMaterialSKU` : ce chargement est déjà prévu.
- Les JSON textuels des quiz, `CorrectAnswerOrder` et l'ordre des questions sont copiés. Le manque majeur porte sur leurs dépendances HTML, pas sur ces colonnes.
- Pour un HtmlContent effectivement atteint, les champs HTML/recto/verso/JSON sont repris. Les liens fichiers sont prévus, mais leur ordre d'insertion est défectueux.
- Les contenus pédagogiques `MaterialsJson`, leur type, les liens fichiers pédagogiques et les EasterEggContents sont prévus au premier clone.
- Les binaires peuvent rester partagés pour les liens many-to-many et les fichiers des EasterEggContents ; l'exception bloquante est le lien unique `Topics.FileSKU`.
- Les `CardTemplates` restent accessibles via l'auteur conservé (`AppUserSKU`) ; le téléchargement les sélectionne par auteur. Leur absence de duplication n'est donc pas, à elle seule, une perte de contenu.
- Les catégories de cours sont reliées par `CourseCode`, conservé entre langues. Les appartenances aux packs sont également résolues par `CourseCode` dans le marketplace : les dupliquer n'est pas nécessaire. Les libellés localisés sont un sujet distinct.
- Les tentatives de quiz, historiques de révision, téléchargements, avis, abonnements, alertes de sortie et photos contribuées sont des données d'usage, pas des contenus pédagogiques à cloner automatiquement. Les champs FSRS absents du modèle Python relèvent aussi de l'état d'apprentissage. Les dates de révision anciennes déjà copiées par le service méritent une politique explicite de réinitialisation.

Le chargement des topics suppose que tous les descendants portent `ParentCourseSKU`. C'est cohérent avec les chemins d'import et de téléchargement consultés. Si des données historiques ne respectent pas cette convention, les descendants liés seulement par `ParentSKU` sont également exclus ; ce point exige une vérification des données réelles.

## 9. Travail à prévoir pour la correction

1. Aligner les modèles Python sur les tables/champs utiles du schéma C#, en particulier les slots HTML des quiz, les dates de liaison et `UnlockLevel`.
2. Définir un parcours complet des dépendances du cours, commun au premier clonage, à la réparation et à l'extraction SQL.
3. Enregistrer les correspondances source/cible pour chaque entité et réutiliser celles déjà existantes ; réserver tout le graphe avant de construire les références internes.
4. Insérer par phases : lignes de base, hiérarchie, liens circulaires, puis tables de liaison. Traiter explicitement le fichier à relation unique.
5. Ajouter un mode de réparation des cours existants qui crée les entités/liaisons manquantes et préserve les textes déjà traduits. Résoudre séparément les anciens rapprochements ambigus et les mises à jour de contenu.
6. Mettre à jour les dates de sync et versions cibles ; suivre la révision source séparément des dates d'édition des traductions.
7. Compléter `/courses/translation-sql` avec exactement le même périmètre.
8. Vérifier la complétude par entité et par relation, et retourner des compteurs de cartes, questions, slots et liens. Le compteur actuel `flashcards_cloned` compte des HtmlContents atteints, même sans Card, et ne prouve pas que les cartes d'un groupe ont été copiées.

Cas de validation attendus : groupe multi-cartes, quiz entièrement HTML avec médias, HtmlContent partagé entre plusieurs slots, supports atteints par les trois chemins, parent/enfant dans un ordre de chargement quelconque, cycle topic/support, fichier directement porté par un topic, ajout sous parent cible existant, clés `(Order, Path)` en doublon, réparation répétée sans doublons, préservation d'une traduction déjà éditée et visibilité en synchronisation incrémentale. Compléter avec dictionnaire et contrat d'engagement si le périmètre retenu est le cours entier.

## 10. Vérifications exécutées

Le script compagnon [course_translation_audit_repro.py](course_translation_audit_repro.py) appelle les méthodes et modèles réels, avec LLM remplacé par un stub, sessions d'enregistrement pour les parcours, et SQLite en mémoire pour les erreurs de FK. Il n'appelle aucune API et n'ouvre aucune connexion distante.

Commande depuis la racine de `fmp-llm-service` :

```sh
.venv/bin/python docs/course_translation_audit_repro.py
```

Au moment de l'audit initial, treize constats étaient confirmés : groupe sans ses cartes, question HTML sans ses slots/contenus, absence de deux champs `LastUpdated`, carte restant dans le groupe source, catégories d'assemblage ignorées, sync sans réparation, parent source conservé en sync, collision de clé de topic, FK du lien fichier avant insertion HTML, partage incompatible avec l'index unique du fichier de topic, cycle topic/support, enfant inséré avant parent. Le script affiche désormais `FIXED` pour les quatre défauts corrigés et `CONFIRMED` pour les neuf autres constats.

Ce script vérifie les défauts restants et les relations corrigées ; il sert de reproduction d'audit et devra évoluer avec les corrections suivantes. Les fixtures SQLite retirent les valeurs par défaut spécifiques à PostgreSQL et remplacent le champ de recherche calculé pour les seuls essais d'insertion. Ces essais ne remplacent pas un test d'intégration PostgreSQL du schéma déployé. Les autres éléments de l'inventaire ont été vérifiés par lecture croisée des sources.
