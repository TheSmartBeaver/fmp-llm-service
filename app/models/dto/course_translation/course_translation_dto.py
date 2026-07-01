from typing import List, Optional
import uuid

from pydantic import BaseModel, Field


class CourseTranslationRequestDto(BaseModel):
    """
    Requête de traduction (clonage) d'un cours d'une langue vers une autre.

    Le cours est identifié par son CourseCode. On clone tout le graphe rattaché
    au cours source (Topics, CourseMaterials, HTML content, Quiz, Groups, flashcards,
    EasterEggs, ...) vers la langue cible.

    Seuls les textes légers user-facing sont traduits (titres de cours/topics,
    description du cours). Les gros contenus (CourseMaterialHtmlContents, QuizQuestions,
    flashcards HtmlContents/Cards) sont clonés SANS traduction.
    """

    course_code: str = Field(..., description="CourseCode du cours à traduire")
    source_language: str = Field(..., description="LanguageCode source (ex: 'fr')")
    target_language: str = Field(..., description="LanguageCode cible (ex: 'en')")

    class Config:
        json_schema_extra = {
            "example": {
                "course_code": "MON_COURS",
                "source_language": "fr",
                "target_language": "en",
            }
        }


class CourseTranslationResponseDto(BaseModel):
    """Résultat d'une opération de traduction/clonage de cours."""

    success: bool
    mode: str = Field(..., description="'clone' (nouvelle traduction) ou 'sync' (mise à jour)")
    target_course_sku: uuid.UUID
    source_course_sku: uuid.UUID
    course_code: str
    source_language: str
    target_language: str

    topics_created: int = 0
    topics_updated: int = 0
    course_materials_cloned: int = 0
    quizzes_cloned: int = 0
    flashcards_cloned: int = 0
    files_shared: int = 0

    message: Optional[str] = None


class TranslationSqlRequestDto(BaseModel):
    """
    Requête pour obtenir les SELECT SQL extrayant les contenus lourds restant à
    traduire d'un cours dans une langue donnée (CourseMaterialHtmlContents,
    QuizQuestions, flashcards HtmlContents/Cards).
    """

    course_code: str = Field(..., description="CourseCode du cours")
    language: str = Field(..., description="LanguageCode ciblé (ex: 'en')")

    class Config:
        json_schema_extra = {
            "example": {"course_code": "MON_COURS", "language": "en"}
        }


class TranslationSqlQueryDto(BaseModel):
    """Une requête SQL d'extraction pour un type d'entité donné."""

    entity: str = Field(..., description="Table/entité ciblée")
    description: str = Field(..., description="Ce que la requête extrait")
    sql: str = Field(..., description="SELECT prêt à exécuter (course_sku inline)")


class TranslationSqlResponseDto(BaseModel):
    """Ensemble des SELECT d'extraction pour un cours+langue."""

    course_code: str
    language: str
    course_sku: uuid.UUID
    queries: List[TranslationSqlQueryDto]
