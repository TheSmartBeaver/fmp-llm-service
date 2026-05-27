from pydantic import BaseModel
from typing import Optional, List


class QuizItemDto(BaseModel):
    """Représente un item de quiz existant à modifier."""
    questionJson: Optional[dict] = None
    answersJson: Optional[dict] = None
    explanationJson: Optional[dict] = None
    correctAnswerOrder: Optional[int] = None


class QuizGenerationRequestDto(BaseModel):
    """Corps de la requête de génération de quiz."""
    pedagogical_json: dict
    quiz_items: Optional[List[QuizItemDto]] = None
    additional_instructions: Optional[str] = None
    courseName: Optional[str] = None
    topicPath: Optional[str] = None


class QuizOutputItemDto(BaseModel):
    """Représente un item de quiz généré."""
    questionJson: dict
    answersJson: dict
    explanationJson: dict
    correctAnswerOrder: int


class QuizTaskResponse(BaseModel):
    """Réponse immédiate après lancement de la tâche Celery."""
    task_id: str
    status: str = "pending"


class QuizResultResponse(BaseModel):
    """Réponse finale contenant les items de quiz générés."""
    success: bool
    quiz_items: List[QuizOutputItemDto]
