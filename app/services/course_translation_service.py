"""
Service de traduction (clonage) d'un cours d'une langue vers une autre.

Stratégie :
- On clone TOUT le graphe rattaché au cours source (Courses.SKU) : Topics (arbre),
  CourseMaterials, CourseMaterialHtmlContents (+ files), Quiz (materials, questions,
  orders, liens), Groups (arbre), HtmlContents (flashcards), Cards, EasterEggContents,
  ainsi que les tables de liaison many-to-many.
- Les FileContents (binaires) sont PARTAGÉS (même SKU réutilisé, pas de duplication).
- Seuls les textes légers user-facing sont TRADUITS via LLM : Courses.Title/Description
  et Topics.Title. Le reste (HTML content, quiz JSON, flashcards) est cloné brut.
- Les appels LLM de traduction sont parallélisés via asyncio.gather ; les écritures DB
  restent synchrones (SQLAlchemy psycopg2).

Modes :
- CLONE : la traduction cible (CourseCode + target_language) n'existe pas encore.
- SYNC  : elle existe déjà -> on compare les LastUpdated source/cible pour ajouter les
  entités manquantes et re-traduire uniquement ce qui a changé.
"""

import asyncio
import datetime
import json
import logging
import uuid
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import insert, select
from sqlalchemy.orm import Session

from app.chains.llm.universal_llm import create_universal_llm
from app.models.db.fmp_models import (
    Cards,
    Courses,
    CourseMaterialHtmlContentFiles,
    CourseMaterialHtmlContents,
    CourseMaterialLinkedQuizzes,
    CourseMaterials,
    EasterEggContents,
    Groups,
    HtmlContents,
    QuizMaterialQuestionOrders,
    QuizMaterials,
    QuizQuestions,
    Topics,
    t_AssemblyCategoryHtmlContent,
    t_FileContentHtmlContent,
)


logger = logging.getLogger(__name__)


def _now() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc)


class CourseTranslationError(Exception):
    """Erreur métier lors de la traduction d'un cours."""


class CourseTranslationService:
    def __init__(self, db: Session, translation_model: Optional[str] = None):
        self.db = db
        self.llm = create_universal_llm(translation_model or "gpt-5-mini")
        # Remapping global old_sku -> new_sku pour toute la durée du clonage.
        self.sku_map: Dict[uuid.UUID, uuid.UUID] = {}
        # FileContents partagés (SKU réutilisés tels quels, pas dupliqués).
        self.shared_file_skus: set[uuid.UUID] = set()
        # Stats
        self.stats = {
            "topics_created": 0,
            "topics_updated": 0,
            "course_materials_cloned": 0,
            "quizzes_cloned": 0,
            "flashcards_cloned": 0,
            "files_shared": 0,
        }

    # ------------------------------------------------------------------ #
    # SKU remapping helpers
    # ------------------------------------------------------------------ #
    def _new_sku(self, old: Optional[uuid.UUID]) -> Optional[uuid.UUID]:
        """Retourne le nouveau SKU associé à `old`, en le créant si besoin."""
        if old is None:
            return None
        if old not in self.sku_map:
            self.sku_map[old] = uuid.uuid4()
        return self.sku_map[old]

    def _map_existing(self, old: Optional[uuid.UUID]) -> Optional[uuid.UUID]:
        """Retourne le SKU remappé s'il existe, sinon l'original (FK partagée)."""
        if old is None:
            return None
        return self.sku_map.get(old, old)

    def _share_file(self, file_sku: Optional[uuid.UUID]) -> Optional[uuid.UUID]:
        """Marque un FileContents comme partagé (non dupliqué) et retourne son SKU."""
        if file_sku is not None:
            self.shared_file_skus.add(file_sku)
        return file_sku

    # ------------------------------------------------------------------ #
    # Chargement du graphe source
    # ------------------------------------------------------------------ #
    def _load_source_course(self, course_code: str, language: str) -> Courses:
        course = (
            self.db.query(Courses)
            .filter(Courses.CourseCode == course_code, Courses.LanguageCode == language)
            .first()
        )
        if not course:
            raise CourseTranslationError(
                f"Cours source introuvable (CourseCode={course_code}, LanguageCode={language})"
            )
        return course

    def _find_target_course(self, course_code: str, language: str) -> Optional[Courses]:
        return (
            self.db.query(Courses)
            .filter(Courses.CourseCode == course_code, Courses.LanguageCode == language)
            .first()
        )

    def _load_topics(self, course_sku: uuid.UUID) -> List[Topics]:
        """Tous les topics du cours (rattachés via ParentCourseSKU)."""
        return (
            self.db.query(Topics)
            .filter(Topics.ParentCourseSKU == course_sku)
            .all()
        )

    def _load_course_materials(self, topic_skus: List[uuid.UUID]) -> List[CourseMaterials]:
        if not topic_skus:
            return []
        return (
            self.db.query(CourseMaterials)
            .filter(CourseMaterials.TopicSKU.in_(topic_skus))
            .all()
        )

    # ------------------------------------------------------------------ #
    # Traduction batchée (LLM parallèle)
    # ------------------------------------------------------------------ #
    async def _translate_batch(
        self, texts: List[str], source_language: str, target_language: str
    ) -> List[str]:
        """
        Traduit une liste de textes courts. Retourne une liste alignée sur l'entrée.
        Les appels sont découpés en chunks parallélisés via asyncio.gather.
        """
        if not texts:
            return []

        CHUNK = 40  # nombre de textes par appel LLM

        async def translate_chunk(chunk: List[str]) -> List[str]:
            payload = json.dumps(
                [{"id": i, "text": t} for i, t in enumerate(chunk)],
                ensure_ascii=False,
            )
            prompt = (
                f"Tu es un traducteur professionnel. Traduis chaque 'text' de la langue "
                f"'{source_language}' vers la langue '{target_language}'. "
                "Conserve strictement le sens, le ton et la mise en forme. "
                "Ne traduis PAS les noms propres ni le code technique. "
                "Réponds UNIQUEMENT avec un tableau JSON valide de la forme "
                '[{"id": 0, "text": "TRADUCTION"}, ...], un objet par entrée, '
                "en conservant les mêmes 'id'.\n\n"
                f"Entrées :\n{payload}"
            )
            try:
                raw = await self.llm.ainvoke(prompt)
                content = raw.content if hasattr(raw, "content") else str(raw)
                content = content.strip()
                if content.startswith("```"):
                    content = content.split("```")[1]
                    if content.startswith("json"):
                        content = content[4:]
                    content = content.strip()
                if content.endswith("```"):
                    content = content[:-3].strip()
                parsed = json.loads(content)
                # Réaligner sur l'ordre d'entrée via les id.
                by_id = {item["id"]: item["text"] for item in parsed}
                return [by_id.get(i, chunk[i]) for i in range(len(chunk))]
            except Exception:
                # En cas d'échec (LLM ou parsing), on dégrade en gardant le texte
                # source plutôt que de faire échouer tout le clonage.
                logger.error(
                    "Échec de la traduction d'un chunk (%s -> %s), fallback sur le "
                    "texte source pour %d entrée(s)",
                    source_language,
                    target_language,
                    len(chunk),
                    exc_info=True,
                )
                return list(chunk)

        chunks = [texts[i : i + CHUNK] for i in range(0, len(texts), CHUNK)]
        results = await asyncio.gather(*(translate_chunk(c) for c in chunks))

        translated: List[str] = []
        for r in results:
            translated.extend(r)
        return translated

    # ------------------------------------------------------------------ #
    # Clonage brut d'entités (sans traduction)
    # ------------------------------------------------------------------ #
    def _clone_html_content(self, hc: CourseMaterialHtmlContents) -> None:
        new = CourseMaterialHtmlContents(
            SKU=self._new_sku(hc.SKU),
            AppUserSKU=hc.AppUserSKU,
            LastUpdated=hc.LastUpdated,
            MaterialsJson=hc.MaterialsJson,
            MaterialsJsonType=hc.MaterialsJsonType,
        )
        self.db.add(new)
        # Fichiers liés (FileContents partagés -> on ne remappe pas FileSKU)
        for f in hc.CourseMaterialHtmlContentFiles:
            self.db.add(
                CourseMaterialHtmlContentFiles(
                    SKU=self._new_sku(f.SKU),
                    LastUpdated=f.LastUpdated,
                    FileSKU=self._share_file(f.FileSKU),  # partagé
                    CourseMaterialHtmlContentSKU=self._new_sku(hc.SKU),
                )
            )

    def _clone_quiz_material(self, qm: QuizMaterials) -> None:
        self.db.add(
            QuizMaterials(
                SKU=self._new_sku(qm.SKU),
                AppUserSKU=qm.AppUserSKU,
                LastUpdated=qm.LastUpdated,
            )
        )
        for order in qm.QuizMaterialQuestionOrders:
            # Clone la question (sans traduction) si pas déjà clonée.
            question = order.QuizQuestions_
            if question is not None and question.SKU not in self.sku_map:
                self.db.add(
                    QuizQuestions(
                        SKU=self._new_sku(question.SKU),
                        AppUserSKU=question.AppUserSKU,
                        QuestionJson=question.QuestionJson,
                        AnswersJson=question.AnswersJson,
                        ExplanationJson=question.ExplanationJson,
                        CorrectAnswerOrder=question.CorrectAnswerOrder,
                        LastUpdated=question.LastUpdated,
                    )
                )
            self.db.add(
                QuizMaterialQuestionOrders(
                    SKU=self._new_sku(order.SKU),
                    Order=order.Order,
                    QuizMaterialSKU=self._new_sku(qm.SKU),
                    QuizQuestionSKU=self._map_existing(order.QuizQuestionSKU),
                )
            )
        self.stats["quizzes_cloned"] += 1

    def _clone_flashcard_html(self, hc: HtmlContents) -> None:
        """Clone une flashcard HtmlContents (sans traduction) + ses liaisons + sa Card."""
        if hc.SKU in self.sku_map:
            return
        self.db.add(
            HtmlContents(
                SKU=self._new_sku(hc.SKU),
                AppUserSKU=hc.AppUserSKU,
                IsTemplated=hc.IsTemplated,
                CardTemplatedJson=hc.CardTemplatedJson,
                IsAssembly=hc.IsAssembly,
                LastUpdated=hc.LastUpdated,
                FullHtmlContent=hc.FullHtmlContent,
                IsFullHtml=hc.IsFullHtml,
                Path=hc.Path,
                Recto=hc.Recto,
                Verso=hc.Verso,
            )
        )
        # Liaison FileContentHtmlContent (FileContents partagés)
        rows = self.db.execute(
            select(t_FileContentHtmlContent).where(
                t_FileContentHtmlContent.c.HtmlContentSKU == hc.SKU
            )
        ).all()
        for row in rows:
            self.db.execute(
                insert(t_FileContentHtmlContent).values(
                    FileContentsSKU=self._share_file(row.FileContentsSKU),  # partagé
                    HtmlContentSKU=self._new_sku(hc.SKU),
                )
            )
        # Card associée (relation 1-1 via IX unique HtmlContentSKU)
        for card in hc.Cards:
            self.db.add(
                Cards(
                    SKU=self._new_sku(card.SKU),
                    AppUserSKU=card.AppUserSKU,
                    Tags=card.Tags,
                    NextRevisionDateMultiplicator=card.NextRevisionDateMultiplicator,
                    LastUpdated=card.LastUpdated,
                    GroupSKU=self._map_existing(card.GroupSKU),
                    HtmlContentSKU=self._new_sku(hc.SKU),
                    MnemotechnicHint=card.MnemotechnicHint,
                    NextRevisionDate=card.NextRevisionDate,
                    Path=card.Path,
                )
            )
        self.stats["flashcards_cloned"] += 1

    def _clone_easter_egg(self, egg: EasterEggContents) -> None:
        if egg.SKU in self.sku_map:
            return
        self.db.add(
            EasterEggContents(
                SKU=self._new_sku(egg.SKU),
                AppUserSKU=egg.AppUserSKU,
                LastUpdated=egg.LastUpdated,
                Title=egg.Title,
                BodyText=egg.BodyText,
                FileSKU=self._share_file(egg.FileSKU),  # FileContents partagé
            )
        )

    def _clone_group_chain(self, group: Groups) -> None:
        """Clone un Group et sa chaîne de parents (arbre via ParentSKU)."""
        chain: List[Groups] = []
        current: Optional[Groups] = group
        while current is not None and current.SKU not in self.sku_map:
            chain.append(current)
            current = current.Groups  # parent
        # Cloner depuis la racine vers la feuille pour que les parents existent d'abord.
        for g in reversed(chain):
            self.db.add(
                Groups(
                    SKU=self._new_sku(g.SKU),
                    AppUserSKU=g.AppUserSKU,
                    Title=g.Title,
                    Tags=g.Tags,
                    LastUpdated=g.LastUpdated,
                    Path=g.Path,
                    ParentSKU=self._map_existing(g.ParentSKU),
                )
            )

    # ------------------------------------------------------------------ #
    # Point d'entrée
    # ------------------------------------------------------------------ #
    async def translate_course(
        self, course_code: str, source_language: str, target_language: str
    ) -> Dict[str, Any]:
        if source_language == target_language:
            raise CourseTranslationError(
                "La langue source et la langue cible doivent être différentes."
            )

        logger.info(
            "Début de traduction du cours CourseCode=%s (%s -> %s)",
            course_code,
            source_language,
            target_language,
        )

        try:
            source_course = self._load_source_course(course_code, source_language)
            target_course = self._find_target_course(course_code, target_language)

            if target_course is None:
                result = await self._clone_course(source_course, target_language)
                mode = "clone"
            else:
                result = await self._sync_course(
                    source_course, target_course, target_language
                )
                mode = "sync"

            self.db.commit()
        except CourseTranslationError:
            # Erreur métier attendue : loggée en warning, gérée par le router (400).
            logger.warning(
                "Traduction refusée pour CourseCode=%s (%s -> %s)",
                course_code,
                source_language,
                target_language,
                exc_info=True,
            )
            raise
        except Exception:
            logger.error(
                "Échec de la traduction du cours CourseCode=%s (%s -> %s)",
                course_code,
                source_language,
                target_language,
                exc_info=True,
            )
            raise

        logger.info(
            "Traduction terminée (mode=%s) pour CourseCode=%s (%s -> %s) : %s",
            mode,
            course_code,
            source_language,
            target_language,
            self.stats,
        )

        return {
            "success": True,
            "mode": mode,
            "source_course_sku": source_course.SKU,
            "target_course_sku": result["target_course_sku"],
            "course_code": course_code,
            "source_language": source_language,
            "target_language": target_language,
            **self.stats,
        }

    # ------------------------------------------------------------------ #
    # CLONE : la traduction n'existe pas encore
    # ------------------------------------------------------------------ #
    async def _clone_course(
        self, source_course: Courses, target_language: str
    ) -> Dict[str, Any]:
        source_language = source_course.LanguageCode
        topics = self._load_topics(source_course.SKU)
        topic_skus = [t.SKU for t in topics]
        materials = self._load_course_materials(topic_skus)

        # --- 1. Collecte des textes à traduire (course + topics) ---
        texts_to_translate = [source_course.Title, source_course.Description]
        texts_to_translate += [t.Title for t in topics]

        translated = await self._translate_batch(
            texts_to_translate, source_language, target_language
        )
        new_title, new_description = translated[0], translated[1]
        translated_topic_titles = translated[2:]

        # --- 2. Cloner le cours ---
        new_course_sku = self._new_sku(source_course.SKU)
        self.db.add(
            Courses(
                SKU=new_course_sku,
                AppUserSKU=source_course.AppUserSKU,
                ImageUrl=source_course.ImageUrl,
                Title=new_title,
                Description=new_description,
                LastUpdated=_now(),
                CourseCode=source_course.CourseCode,
                FreePercent=source_course.FreePercent,
                LanguageCode=target_language,
                IsPublished=source_course.IsPublished,
                ImageRaw=source_course.ImageRaw,
            )
        )

        # --- 3. Cloner l'arbre des Topics (parents d'abord) ---
        # On pré-réserve les nouveaux SKU pour pouvoir remapper ParentSKU peu importe l'ordre.
        for t in topics:
            self._new_sku(t.SKU)

        title_by_sku = {t.SKU: translated_topic_titles[i] for i, t in enumerate(topics)}

        for t in topics:
            self._clone_topic(t, new_course_sku, title_by_sku[t.SKU])
            self.stats["topics_created"] += 1

        # --- 4. Cloner les CourseMaterials + HTML + Quiz ---
        for m in materials:
            self._clone_course_material(m, new_course_sku)

        self.stats["files_shared"] = len(self.shared_file_skus)

        return {"target_course_sku": new_course_sku}

    def _clone_topic(
        self, topic: Topics, new_course_sku: uuid.UUID, translated_title: str
    ) -> None:
        # Cloner les entités satellites référencées par le topic.
        if topic.Groups is not None:
            self._clone_group_chain(topic.Groups)
        if topic.HtmlContents is not None:
            self._clone_flashcard_html(topic.HtmlContents)
        if topic.EasterEggContents is not None:
            self._clone_easter_egg(topic.EasterEggContents)

        self.db.add(
            Topics(
                SKU=self._new_sku(topic.SKU),
                Title=translated_title,
                AppUserSKU=topic.AppUserSKU,
                LastUpdated=_now(),
                IsPremium=topic.IsPremium,
                IsUnpublished=topic.IsUnpublished,
                Order=topic.Order,
                Path=topic.Path,
                ParentSKU=self._map_existing(topic.ParentSKU),
                ParentCourseSKU=new_course_sku,
                GroupSKU=self._map_existing(topic.GroupSKU),
                FileSKU=self._share_file(topic.FileSKU),  # FileContents partagé
                HtmlContentSKU=self._map_existing(topic.HtmlContentSKU),
                CourseMaterialSKU=self._map_existing(topic.CourseMaterialSKU),
                RedditUrl=topic.RedditUrl,
                EasterEggContentSKU=self._map_existing(topic.EasterEggContentSKU),
            )
        )

    def _clone_course_material(
        self, material: CourseMaterials, new_course_sku: uuid.UUID
    ) -> None:
        # Cloner le HTML content (sans traduction) s'il existe et pas déjà cloné.
        if material.CourseMaterialHtmlContents is not None:
            if material.HtmlContentSKU not in self.sku_map:
                self._clone_html_content(material.CourseMaterialHtmlContents)

        self.db.add(
            CourseMaterials(
                SKU=self._new_sku(material.SKU),
                AppUserSKU=material.AppUserSKU,
                LastUpdated=_now(),
                TaskId=material.TaskId,
                HtmlContentSKU=self._map_existing(material.HtmlContentSKU),
                TopicSKU=self._map_existing(material.TopicSKU),
                CourseSKU=new_course_sku,
                TemplatesUsed=material.TemplatesUsed,
                Prompt=material.Prompt,
                DebugDataJson=material.DebugDataJson,
                CreatedAt=material.CreatedAt,
            )
        )
        self.stats["course_materials_cloned"] += 1

        # Quiz liés
        for link in material.CourseMaterialLinkedQuizzes:
            if link.QuizMaterials_ is not None and link.QuizMaterialSKU not in self.sku_map:
                self._clone_quiz_material(link.QuizMaterials_)
            self.db.add(
                CourseMaterialLinkedQuizzes(
                    SKU=self._new_sku(link.SKU),
                    QuizMaterialSKU=self._map_existing(link.QuizMaterialSKU),
                    CourseMaterialSKU=self._new_sku(material.SKU),
                )
            )

    # ------------------------------------------------------------------ #
    # SYNC : la traduction existe déjà -> on met à jour le delta
    # ------------------------------------------------------------------ #
    async def _sync_course(
        self, source_course: Courses, target_course: Courses, target_language: str
    ) -> Dict[str, Any]:
        source_language = source_course.LanguageCode

        source_topics = self._load_topics(source_course.SKU)
        target_topics = self._load_topics(target_course.SKU)

        # On associe source <-> cible par Order + Path (heuristique stable sans lien de traçabilité).
        target_by_key = {(t.Order, t.Path): t for t in target_topics}

        # 1. Mettre à jour le cours si la source est plus récente.
        to_translate: List[str] = []
        translate_targets: List[Tuple[str, Any]] = []  # (kind, ref)

        if source_course.LastUpdated > target_course.LastUpdated:
            to_translate.append(source_course.Title)
            translate_targets.append(("course_title", target_course))
            to_translate.append(source_course.Description)
            translate_targets.append(("course_description", target_course))

        # 2. Topics : ajouter les manquants, re-traduire les modifiés.
        missing_source_topics: List[Topics] = []
        for st in source_topics:
            match = target_by_key.get((st.Order, st.Path))
            if match is None:
                missing_source_topics.append(st)
            elif st.LastUpdated > match.LastUpdated:
                to_translate.append(st.Title)
                translate_targets.append(("topic_title", match))

        # Les titres des topics manquants sont aussi à traduire.
        missing_start = len(to_translate)
        to_translate += [st.Title for st in missing_source_topics]

        translated = await self._translate_batch(
            to_translate, source_language, target_language
        )

        # Appliquer les updates.
        for (kind, ref), value in zip(translate_targets, translated[:missing_start]):
            if kind == "course_title":
                ref.Title = value
                ref.LastUpdated = _now()
            elif kind == "course_description":
                ref.Description = value
                ref.LastUpdated = _now()
            elif kind == "topic_title":
                ref.Title = value
                ref.LastUpdated = _now()
                self.stats["topics_updated"] += 1

        # Ajouter les topics manquants (clone complet de leur sous-graphe).
        for st in missing_source_topics:
            self._new_sku(st.SKU)
        translated_missing = translated[missing_start:]
        for i, st in enumerate(missing_source_topics):
            self._clone_topic(st, target_course.SKU, translated_missing[i])
            self.stats["topics_created"] += 1

        # Cloner les CourseMaterials des topics nouvellement ajoutés.
        if missing_source_topics:
            new_topic_skus = [st.SKU for st in missing_source_topics]
            for m in self._load_course_materials(new_topic_skus):
                self._clone_course_material(m, target_course.SKU)

        self.stats["files_shared"] = len(self.shared_file_skus)

        return {"target_course_sku": target_course.SKU}
