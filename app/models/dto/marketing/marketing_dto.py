import uuid
from typing import Dict, List
from pydantic import BaseModel, Field


class NotificationContentDto(BaseModel):
    """Contenu traduit d'une notification pour une langue donnée."""
    title: str = Field(..., description="Titre de la notification")
    body: str = Field(..., description="Corps de la notification")


class PromotionalNotificationRequest(BaseModel):
    """Requête d'envoi d'une notification promotionnelle à une liste d'utilisateurs."""
    user_skus: List[uuid.UUID] = Field(..., description="Liste des SKU (UUID) des utilisateurs ciblés")
    content_by_language: Dict[str, NotificationContentDto] = Field(
        ...,
        description="Contenu de la notification par code de langue (ex: 'en', 'fr'). "
                     "La langue 'en' doit être fournie en tant que fallback."
    )
    data: Dict[str, str] = Field(default_factory=dict, description="Données additionnelles envoyées avec la notification")

    class Config:
        json_schema_extra = {
            "example": {
                "user_skus": [
                    "123e4567-e89b-12d3-a456-426614174000",
                    "223e4567-e89b-12d3-a456-426614174001"
                ],
                "content_by_language": {
                    "en": {"title": "New feature!", "body": "Check out what's new in the app."},
                    "fr": {"title": "Nouveauté !", "body": "Découvrez les nouveautés de l'application."}
                },
                "data": {
                    "event": "promotional_notification"
                }
            }
        }


class PromotionalNotificationResponse(BaseModel):
    """Réponse après l'envoi d'une notification promotionnelle."""
    users_targeted: int
    users_not_found: List[uuid.UUID]
    devices_found: int
    success_count: int
    failure_count: int
    failed_tokens: List[str]
