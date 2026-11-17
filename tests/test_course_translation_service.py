"""Regression tests for cloning with immediate foreign-key constraints."""

import datetime
import unittest
import uuid
from unittest.mock import AsyncMock, patch

from sqlalchemy import MetaData, Text, create_engine, event, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.db import fmp_models as models
from app.services.course_translation_service import CourseTranslationService


class CourseTranslationPersistenceTest(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")

        @event.listens_for(self.engine, "connect")
        def enable_foreign_keys(connection, _):
            connection.execute("PRAGMA foreign_keys=ON")

        # Keep real FK/index definitions. Only adapt PostgreSQL-specific defaults
        # and the computed search vector to the local SQLite test database.
        schema = MetaData()
        for name in (
            "AppUsers", "Courses", "Topics", "CourseMaterials", "Groups",
            "HtmlContents", "Cards", "FileContents", "EasterEggContents",
            "CourseMaterialHtmlContents", "CourseMaterialHtmlContentFiles",
            "QuizMaterials", "QuizQuestions", "QuizMaterialQuestionOrders",
            "CourseMaterialLinkedQuizzes", "FileContentHtmlContent",
        ):
            table = models.Base.metadata.tables[name].to_metadata(schema)
            for column in table.columns:
                column.server_default = None
            if name == "Courses":
                column = table.c.SearchVector
                column.type = Text()
                column.computed = None
                column.server_onupdate = None
                column.nullable = True
        schema.create_all(self.engine)
        self.db = Session(self.engine, autoflush=False)
        self.addCleanup(self.engine.dispose)
        self.addCleanup(self.db.close)
        self.now = datetime.datetime(2026, 11, 17, 12)
        self.owner = self.insert(models.AppUsers, AuthentUid="translation-test")
        self.source = self.course("fr")
        self.db.commit()

    def insert(self, model, **values):
        values.setdefault("SKU", uuid.uuid4())
        if "AppUserSKU" in model.__table__.c:
            values.setdefault("AppUserSKU", self.owner)
        if "LastUpdated" in model.__table__.c:
            values.setdefault("LastUpdated", self.now)
        self.db.execute(model.__table__.insert().values(**values))
        return values["SKU"]

    def course(self, language):
        return self.insert(
            models.Courses, Title="Cours", Description="Description",
            CourseCode="translation-test", LanguageCode=language,
            ImageUrl="", FreePercent=0, IsPublished=False,
        )

    def topic(self, course, *, parent=None, path="root", order=0):
        return self.insert(
            models.Topics, Title=path, ParentCourseSKU=course,
            ParentSKU=parent, Path=path, Order=order,
            IsPremium=False, IsUnpublished=False,
        )

    def graph(self, *, inverse_only=False, topic_only=False, media=False):
        self.root = self.topic(self.source)
        self.child = self.topic(
            self.source, parent=self.root, path="root/child", order=1,
        )
        self.material_html = self.insert(
            models.CourseMaterialHtmlContents,
            MaterialsJson='{"content":"Source lesson"}', MaterialsJsonType=1,
        )
        self.material = self.insert(
            models.CourseMaterials,
            CourseSKU=None if inverse_only else self.source,
            TopicSKU=None if inverse_only else self.child,
            HtmlContentSKU=self.material_html,
        )
        if not topic_only:
            self.db.execute(models.Topics.__table__.update().where(
                models.Topics.SKU == self.child,
            ).values(CourseMaterialSKU=self.material))
        if media:
            self.file = self.insert(
                models.FileContents, Name="image", Format="png", Content=b"image",
            )
            self.flashcard_html = self.insert(
                models.HtmlContents, IsTemplated=False, CardTemplatedJson="",
                IsAssembly=False, IsFullHtml=True,
                FullHtmlContent="<p>Source flashcard</p>",
            )
            self.db.execute(models.Topics.__table__.update().where(
                models.Topics.SKU == self.child,
            ).values(HtmlContentSKU=self.flashcard_html))
            self.db.execute(models.t_FileContentHtmlContent.insert().values(
                HtmlContentSKU=self.flashcard_html, FileContentsSKU=self.file,
            ))
            self.insert(
                models.CourseMaterialHtmlContentFiles,
                CourseMaterialHtmlContentSKU=self.material_html, FileSKU=self.file,
            )
            self.quiz = self.insert(models.QuizMaterials)
            self.question = self.insert(
                models.QuizQuestions, QuestionJson='{"content":"Question"}',
                AnswersJson="[]", ExplanationJson="[]", CorrectAnswerOrder=1,
            )
            self.insert(
                models.QuizMaterialQuestionOrders, QuizMaterialSKU=self.quiz,
                QuizQuestionSKU=self.question, Order=1,
            )
            self.insert(
                models.CourseMaterialLinkedQuizzes,
                CourseMaterialSKU=self.material, QuizMaterialSKU=self.quiz,
            )
        self.db.commit()

    def service(self):
        with patch(
            "app.services.course_translation_service.create_universal_llm",
            return_value=None,
        ):
            service = CourseTranslationService(self.db)

        async def translate(texts, *_):
            return ["EN: " + text for text in texts]

        service._translate_batch = AsyncMock(side_effect=translate)
        load_topics = service._load_topics
        # Deliberately load children first, as the database makes no ordering
        # guarantee. The final graph must not depend on this query order.
        service._load_topics = lambda sku: sorted(
            load_topics(sku), key=lambda topic: topic.ParentSKU is None,
        )
        return service

    async def translate(self, service=None):
        return await (service or self.service()).translate_course(
            "translation-test", "fr", "en",
        )

    def target_topics(self, course_sku):
        return {
            topic.Path: topic
            for topic in self.db.query(models.Topics).filter_by(
                ParentCourseSKU=course_sku,
            ).all()
        }

    def assert_source_unchanged(self):
        self.db.expire_all()
        source_child = self.db.get(models.Topics, self.child)
        self.assertEqual(source_child.ParentSKU, self.root)
        self.assertEqual(source_child.CourseMaterialSKU, self.material)
        source_material = self.db.get(models.CourseMaterials, self.material)
        self.assertEqual(source_material.HtmlContentSKU, self.material_html)

    async def test_clone_preserves_circular_links_and_child_first_hierarchy(self):
        self.graph()
        result = await self.translate()
        topics = self.target_topics(result["target_course_sku"])
        root, child = topics["root"], topics["root/child"]
        material = self.db.get(models.CourseMaterials, child.CourseMaterialSKU)
        self.assertEqual(result["mode"], "clone")
        self.assertEqual(result["topics_created"], 2)
        self.assertEqual(child.ParentSKU, root.SKU)
        self.assertEqual(material.TopicSKU, child.SKU)
        self.assertEqual(material.CourseSKU, result["target_course_sku"])
        self.assertNotEqual(material.SKU, self.material)
        self.assertNotEqual(material.HtmlContentSKU, self.material_html)
        self.assertEqual(self.db.get(
            models.CourseMaterialHtmlContents, material.HtmlContentSKU,
        ).MaterialsJson, '{"content":"Source lesson"}')
        self.assert_source_unchanged()

    async def test_clone_loads_material_referenced_only_by_topic(self):
        self.graph(inverse_only=True)
        result = await self.translate()
        child = self.target_topics(result["target_course_sku"])["root/child"]
        material = self.db.get(models.CourseMaterials, child.CourseMaterialSKU)
        self.assertIsNone(material.TopicSKU)
        self.assertEqual(material.CourseSKU, result["target_course_sku"])
        self.assertNotEqual(material.SKU, self.material)
        self.assert_source_unchanged()

    async def test_clone_preserves_material_to_topic_only_link(self):
        self.graph(topic_only=True)
        result = await self.translate()
        child = self.target_topics(result["target_course_sku"])["root/child"]
        material = self.db.query(models.CourseMaterials).filter_by(
            CourseSKU=result["target_course_sku"],
        ).one()
        self.assertIsNone(child.CourseMaterialSKU)
        self.assertEqual(material.TopicSKU, child.SKU)

    async def test_clone_material_attached_directly_to_course(self):
        self.material = self.insert(models.CourseMaterials, CourseSKU=self.source)
        self.db.commit()
        result = await self.translate()
        material = self.db.query(models.CourseMaterials).filter_by(
            CourseSKU=result["target_course_sku"],
        ).one()
        self.assertIsNone(material.TopicSKU)
        self.assertEqual(result["course_materials_cloned"], 1)

    async def test_clone_preserves_media_and_quiz_dependencies(self):
        self.graph(media=True)
        result = await self.translate()
        child = self.target_topics(result["target_course_sku"])["root/child"]
        files = self.db.execute(select(models.t_FileContentHtmlContent).where(
            models.t_FileContentHtmlContent.c.HtmlContentSKU == child.HtmlContentSKU,
        )).all()
        self.assertEqual([row.FileContentsSKU for row in files], [self.file])
        material = self.db.get(models.CourseMaterials, child.CourseMaterialSKU)
        self.assertEqual(material.CourseMaterialHtmlContents.MaterialsJson,
                         '{"content":"Source lesson"}')
        self.assertEqual(
            material.CourseMaterialHtmlContents.CourseMaterialHtmlContentFiles[0].FileSKU,
            self.file,
        )
        link = material.CourseMaterialLinkedQuizzes[0]
        self.assertNotEqual(link.QuizMaterialSKU, self.quiz)
        order = link.QuizMaterials_.QuizMaterialQuestionOrders[0]
        self.assertNotEqual(order.QuizQuestionSKU, self.question)
        self.assertEqual(order.QuizQuestions_.QuestionJson, '{"content":"Question"}')
        self.assertEqual(result["files_shared"], 1)
        self.assert_source_unchanged()

    async def test_sync_links_new_child_to_existing_target_parent(self):
        self.graph()
        target = self.course("en")
        target_root = self.topic(target)
        self.db.commit()
        result = await self.translate()
        topics = self.target_topics(target)
        child = topics["root/child"]
        material = self.db.get(models.CourseMaterials, child.CourseMaterialSKU)
        self.assertEqual(result["mode"], "sync")
        self.assertEqual(child.ParentSKU, target_root)
        self.assertEqual(material.TopicSKU, child.SKU)
        self.assert_source_unchanged()
        repeat = await self.translate()
        self.assertEqual(repeat["topics_created"], 0)
        self.assertEqual(repeat["course_materials_cloned"], 0)
        self.assertEqual(len(self.target_topics(target)), 2)

    async def test_link_failure_rolls_back_all_clone_phases(self):
        self.graph(media=True)
        service = self.service()
        map_existing = service._map_existing
        missing_parent = uuid.uuid4()
        service._map_existing = lambda sku: (
            missing_parent if sku == self.root else map_existing(sku)
        )
        with self.assertLogs(
            "app.services.course_translation_service", level="ERROR",
        ), self.assertRaises(IntegrityError):
            await self.translate(service)
        # The router rolls back the failed request; intermediate flushes must
        # not commit any of the cloned entities or file junctions.
        self.db.rollback()
        self.assertEqual(self.db.query(models.Courses).count(), 1)
        self.assertEqual(self.db.query(models.Topics).count(), 2)
        self.assertEqual(self.db.query(models.CourseMaterials).count(), 1)
        self.assertEqual(len(self.db.execute(select(
            models.t_FileContentHtmlContent,
        )).all()), 1)
        self.assert_source_unchanged()


if __name__ == "__main__":
    unittest.main()
