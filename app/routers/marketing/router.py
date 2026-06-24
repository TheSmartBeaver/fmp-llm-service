import uuid
from collections import defaultdict
from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.db.fmp_models import AppUsers, DeviceTokens
from app.models.dto.marketing.marketing_dto import (
    PromotionalNotificationRequest,
    PromotionalNotificationResponse
)
from app.services.fcm_service import FCMService

marketing_router = APIRouter(prefix="/marketing", tags=["marketing"])

DEFAULT_LANGUAGE_CODE = "en"
SUPPORTED_LANGUAGE_CODES = ["en", "fr"]
PROMOTIONAL_EVENT_NAME = "promotional_notification"


def resolve_language_code(language_code: Optional[str]) -> str:
    if not language_code or language_code not in SUPPORTED_LANGUAGE_CODES:
        return DEFAULT_LANGUAGE_CODE
    return language_code


@marketing_router.post("/notifications/promotional", response_model=PromotionalNotificationResponse)
async def send_promotional_notification(
    request: PromotionalNotificationRequest,
    db: Session = Depends(get_db)
):
    """
    Envoie une notification promotionnelle à une liste d'utilisateurs choisis.

    Pour chaque utilisateur, le contenu de la notification est sélectionné selon sa
    langue préférée (AppUsers.LanguageCode). Si l'utilisateur n'a pas de langue
    définie, ou que sa langue n'est pas supportée, l'anglais ("en") est utilisé.
    """
    if DEFAULT_LANGUAGE_CODE not in request.content_by_language:
        raise HTTPException(
            status_code=400,
            detail="content_by_language must include a fallback 'en' entry"
        )

    users = db.query(AppUsers).filter(AppUsers.SKU.in_(request.user_skus)).all()
    found_skus = {user.SKU for user in users}
    users_not_found = [sku for sku in request.user_skus if sku not in found_skus]

    user_skus_by_language: Dict[str, List[uuid.UUID]] = defaultdict(list)
    for user in users:
        language_code = resolve_language_code(user.LanguageCode)
        if language_code not in request.content_by_language:
            language_code = DEFAULT_LANGUAGE_CODE
        user_skus_by_language[language_code].append(user.SKU)

    notification_data = {"event": PROMOTIONAL_EVENT_NAME, **request.data}

    fcm_service = FCMService()
    devices_found = 0
    success_count = 0
    failure_count = 0
    failed_tokens: List[str] = []

    for language_code, language_user_skus in user_skus_by_language.items():
        devices = db.query(DeviceTokens).filter(
            DeviceTokens.AppUserSKU.in_(language_user_skus),
            DeviceTokens.IsActive.is_(True)
        ).all()
        devices_found += len(devices)

        tokens = [device.FcmToken for device in devices]
        if not tokens:
            continue

        content = request.content_by_language[language_code]
        result = fcm_service.send_multicast_notification(
            tokens=tokens,
            title=content.title,
            body=content.body,
            data=notification_data,
            notification_id=f"promo-{uuid.uuid4()}"
        )
        success_count += result["success_count"]
        failure_count += result["failure_count"]
        failed_tokens.extend(result["failed_tokens"])

    return PromotionalNotificationResponse(
        users_targeted=len(users),
        users_not_found=users_not_found,
        devices_found=devices_found,
        success_count=success_count,
        failure_count=failure_count,
        failed_tokens=failed_tokens
    )
