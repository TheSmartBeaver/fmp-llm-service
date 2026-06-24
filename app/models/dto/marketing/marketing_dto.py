import uuid
from typing import Dict, List
from pydantic import BaseModel, Field, field_validator

RESERVED_DATA_KEYS = {"event", "route", "title", "body"}


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
    route: str = Field(
        ...,
        description="Nom de route Flutter cible (doit correspondre exactement à un routeName "
                     "existant côté client, ex: '/MarketplaceCourseDetail'). Sans ce champ, le "
                     "clic sur la notification ne déclenche aucune navigation."
    )
    extra_data: Dict[str, str] = Field(
        default_factory=dict,
        description="Champs additionnels transmis tels quels au widget Flutter cible en argument "
                     "de navigation (ex: 'course_code'). Toutes les valeurs doivent être des "
                     "strings (contrainte FCM). Ne pas y mettre 'event', 'route', 'title' ou 'body'."
    )

    @field_validator("extra_data")
    @classmethod
    def validate_extra_data_keys(cls, value: Dict[str, str]) -> Dict[str, str]:
        reserved_keys_used = RESERVED_DATA_KEYS.intersection(value.keys())
        if reserved_keys_used:
            raise ValueError(
                f"extra_data must not contain reserved keys: {sorted(reserved_keys_used)}"
            )
        return value

    class Config:
        json_schema_extra = {
            "example": {
                "user_skus": [
                    "123e4567-e89b-12d3-a456-426614174000",
                    "223e4567-e89b-12d3-a456-426614174001"
                ],
                "content_by_language": {
                    "en": {"title": "New course available!", "body": "Check out \"Course Title\" now."},
                    "fr": {"title": "Nouveau cours disponible !", "body": "Découvrez \"Titre du cours\" dès maintenant."}
                },
                "route": "/MarketplaceCourseDetail",
                "extra_data": {
                    "course_code": "ABC123"
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
