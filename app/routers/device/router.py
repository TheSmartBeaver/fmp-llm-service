import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.models.db.fmp_models import DeviceTokens, AppUsers
from app.models.dto.device.device_token_dto import (
    DeviceTokenRegisterRequest,
    DeviceTokenUpdateRequest,
    DeviceTokenResponse
)
from app.services.fcm_service import FCMService

device_router = APIRouter(prefix="/devices", tags=["devices"])


def get_user_from_auth_uid(db: Session, auth_uid: str) -> AppUsers:
    user = db.query(AppUsers).filter(AppUsers.AuthentUid == auth_uid).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@device_router.post("/register", response_model=DeviceTokenResponse)
async def register_device(
    request: DeviceTokenRegisterRequest,
    auth_uid: str = Header(..., alias="X-Auth-Uid"),
    db: Session = Depends(get_db)
):
    user = get_user_from_auth_uid(db, auth_uid)

    existing_device = db.query(DeviceTokens).filter(
        DeviceTokens.AppUserSKU == user.SKU,
        DeviceTokens.FcmToken == request.fcm_token
    ).first()

    if existing_device:
        existing_device.IsActive = True
        existing_device.UpdatedAt = datetime.utcnow()
        existing_device.LastUsed = datetime.utcnow()
        if request.device_name:
            existing_device.DeviceName = request.device_name
        db.commit()
        db.refresh(existing_device)

        return DeviceTokenResponse(
            sku=existing_device.SKU,
            app_user_sku=existing_device.AppUserSKU,
            fcm_token=existing_device.FcmToken,
            device_type=existing_device.DeviceType,
            device_name=existing_device.DeviceName,
            is_active=existing_device.IsActive,
            created_at=existing_device.CreatedAt,
            updated_at=existing_device.UpdatedAt,
            last_used=existing_device.LastUsed
        )

    new_device = DeviceTokens(
        SKU=uuid.uuid4(),
        AppUserSKU=user.SKU,
        FcmToken=request.fcm_token,
        DeviceType=request.device_type,
        DeviceName=request.device_name,
        IsActive=True,
        CreatedAt=datetime.utcnow(),
        UpdatedAt=datetime.utcnow(),
        LastUsed=datetime.utcnow()
    )

    db.add(new_device)
    db.commit()
    db.refresh(new_device)

    return DeviceTokenResponse(
        sku=new_device.SKU,
        app_user_sku=new_device.AppUserSKU,
        fcm_token=new_device.FcmToken,
        device_type=new_device.DeviceType,
        device_name=new_device.DeviceName,
        is_active=new_device.IsActive,
        created_at=new_device.CreatedAt,
        updated_at=new_device.UpdatedAt,
        last_used=new_device.LastUsed
    )


@device_router.get("/", response_model=List[DeviceTokenResponse])
async def list_devices(
    auth_uid: str = Header(..., alias="X-Auth-Uid"),
    db: Session = Depends(get_db)
):
    user = get_user_from_auth_uid(db, auth_uid)

    devices = db.query(DeviceTokens).filter(
        DeviceTokens.AppUserSKU == user.SKU
    ).all()

    return [
        DeviceTokenResponse(
            sku=device.SKU,
            app_user_sku=device.AppUserSKU,
            fcm_token=device.FcmToken,
            device_type=device.DeviceType,
            device_name=device.DeviceName,
            is_active=device.IsActive,
            created_at=device.CreatedAt,
            updated_at=device.UpdatedAt,
            last_used=device.LastUsed
        )
        for device in devices
    ]


@device_router.put("/{device_id}", response_model=DeviceTokenResponse)
async def update_device(
    device_id: str,
    request: DeviceTokenUpdateRequest,
    auth_uid: str = Header(..., alias="X-Auth-Uid"),
    db: Session = Depends(get_db)
):
    user = get_user_from_auth_uid(db, auth_uid)

    try:
        device_uuid = uuid.UUID(device_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid device ID format")

    device = db.query(DeviceTokens).filter(
        DeviceTokens.SKU == device_uuid,
        DeviceTokens.AppUserSKU == user.SKU
    ).first()

    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    if request.fcm_token is not None:
        device.FcmToken = request.fcm_token
    if request.device_name is not None:
        device.DeviceName = request.device_name
    if request.is_active is not None:
        device.IsActive = request.is_active

    device.UpdatedAt = datetime.utcnow()
    db.commit()
    db.refresh(device)

    return DeviceTokenResponse(
        sku=device.SKU,
        app_user_sku=device.AppUserSKU,
        fcm_token=device.FcmToken,
        device_type=device.DeviceType,
        device_name=device.DeviceName,
        is_active=device.IsActive,
        created_at=device.CreatedAt,
        updated_at=device.UpdatedAt,
        last_used=device.LastUsed
    )


@device_router.delete("/{device_id}")
async def delete_device(
    device_id: str,
    auth_uid: str = Header(..., alias="X-Auth-Uid"),
    db: Session = Depends(get_db)
):
    user = get_user_from_auth_uid(db, auth_uid)

    try:
        device_uuid = uuid.UUID(device_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid device ID format")

    device = db.query(DeviceTokens).filter(
        DeviceTokens.SKU == device_uuid,
        DeviceTokens.AppUserSKU == user.SKU
    ).first()

    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    db.delete(device)
    db.commit()

    return {"message": "Device deleted successfully"}


class TestNotificationRequest(BaseModel):
    """Requête pour envoyer une notification de test"""
    title: Optional[str] = "Test Notification"
    body: Optional[str] = "Ceci est une notification de test depuis fmp-llm-service"
    data: Optional[dict] = None

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Test FCM",
                "body": "Votre notification de test",
                "data": {
                    "test_key": "test_value",
                    "action": "test"
                }
            }
        }


class TestNotificationResponse(BaseModel):
    """Réponse après l'envoi d'une notification de test"""
    success: bool
    message: str
    devices_found: int
    active_devices: int
    success_count: int
    failure_count: int
    failed_tokens: List[str]


@device_router.post("/test-notification", response_model=TestNotificationResponse)
async def send_test_notification(
    request: TestNotificationRequest,
    auth_uid: str = Header(..., alias="X-Auth-Uid"),
    db: Session = Depends(get_db)
):
    """
    Envoie une notification FCM de test à tous les appareils actifs de l'utilisateur.

    Cette route permet de tester que:
    - L'utilisateur existe dans la base de données
    - Des tokens FCM sont enregistrés pour l'utilisateur
    - Le service FCM est correctement configuré
    - Les notifications arrivent bien sur l'application Flutter

    Args:
        request: Contenu de la notification (titre, corps, données optionnelles)
        auth_uid: AuthentUid de l'utilisateur (header X-Auth-Uid)
        db: Session de base de données

    Returns:
        TestNotificationResponse avec les détails de l'envoi
    """
    # Récupérer l'utilisateur
    user = db.query(AppUsers).filter(AppUsers.AuthentUid == auth_uid).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail=f"User not found with auth_uid: {auth_uid}"
        )

    # Récupérer tous les appareils de l'utilisateur
    all_devices = db.query(DeviceTokens).filter(
        DeviceTokens.AppUserSKU == user.SKU
    ).all()

    # Filtrer les appareils actifs
    active_devices = [device for device in all_devices if device.IsActive]

    if not active_devices:
        return TestNotificationResponse(
            success=False,
            message="No active devices found for this user",
            devices_found=len(all_devices),
            active_devices=0,
            success_count=0,
            failure_count=0,
            failed_tokens=[]
        )

    # Récupérer les tokens FCM
    tokens = [device.FcmToken for device in active_devices]

    # Préparer les données de la notification
    notification_data = request.data or {}
    notification_data.update({
        "test": "true",
        "timestamp": datetime.utcnow().isoformat(),
        "auth_uid": auth_uid
    })

    # Convertir les valeurs en string pour FCM
    notification_data_str = {k: str(v) for k, v in notification_data.items()}

    # Envoyer la notification via FCM
    fcm_service = FCMService()
    result = fcm_service.send_multicast_notification(
        tokens=tokens,
        title=request.title,
        body=request.body,
        data=notification_data_str,
        notification_id=f"test-{uuid.uuid4()}"
    )

    return TestNotificationResponse(
        success=result["success_count"] > 0,
        message=f"Notification sent to {result['success_count']}/{len(tokens)} devices",
        devices_found=len(all_devices),
        active_devices=len(active_devices),
        success_count=result["success_count"],
        failure_count=result["failure_count"],
        failed_tokens=result["failed_tokens"]
    )
