from fastapi import APIRouter
from pydantic import BaseModel
import uuid

from app.models.dto.user_entry.user_entry_dto import UserEntryDto
from app.workers.tasks import generate_course_material_task


course_material_router = APIRouter(prefix="/course_material")


class CourseMaterialTaskResponse(BaseModel):
    """Réponse contenant l'ID de la tâche Celery"""
    task_id: str
    status: str

    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "pending"
            }
        }


@course_material_router.post("/generate_CELERY", response_model=CourseMaterialTaskResponse)
async def generate_course_material(
    request: UserEntryDto
):
    """
    Lance une génération asynchrone de support de cours via Celery.

    Args:
        request: UserEntryDto contenant le contexte, le contenu textuel et les médias

    Returns:
        CourseMaterialTaskResponse avec l'ID de la tâche Celery

    Note:
        Le résultat sera publié sur Redis (canal 'course_material_events') une fois la génération terminée.
    """
    # Générer un ID unique pour cette tâche
    task_id = str(uuid.uuid4())

    # Lancer la tâche Celery de manière asynchrone
    generate_course_material_task.apply_async(
        args=[task_id, request.model_dump()],
        task_id=task_id
    )

    return CourseMaterialTaskResponse(
        task_id=task_id,
        status="pending"
    )


@course_material_router.get("/health")
async def health_check():
    """
    Endpoint de santé pour vérifier que le service est opérationnel.
    """
    return {
        "status": "ok",
        "service": "course_material_generator",
        "llm_model": "gpt-5-mini"
    }
