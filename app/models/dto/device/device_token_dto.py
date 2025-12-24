from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid


class DeviceTokenRegisterRequest(BaseModel):
    fcm_token: str = Field(..., description="Firebase Cloud Messaging token")
    device_type: str = Field(..., description="Device type: android, ios, or web")
    device_name: Optional[str] = Field(None, description="User-friendly device name")

    class Config:
        json_schema_extra = {
            "example": {
                "fcm_token": "fGHj8kL3R...token_example",
                "device_type": "android",
                "device_name": "Samsung Galaxy S21"
            }
        }


class DeviceTokenUpdateRequest(BaseModel):
    fcm_token: Optional[str] = Field(None, description="New FCM token")
    device_name: Optional[str] = Field(None, description="New device name")
    is_active: Optional[bool] = Field(None, description="Device active status")

    class Config:
        json_schema_extra = {
            "example": {
                "fcm_token": "new_token_example",
                "device_name": "My New Phone",
                "is_active": True
            }
        }


class DeviceTokenResponse(BaseModel):
    sku: uuid.UUID
    app_user_sku: uuid.UUID
    fcm_token: str
    device_type: str
    device_name: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_used: Optional[datetime]

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "sku": "123e4567-e89b-12d3-a456-426614174000",
                "app_user_sku": "223e4567-e89b-12d3-a456-426614174001",
                "fcm_token": "fGHj8kL3R...token_example",
                "device_type": "android",
                "device_name": "Samsung Galaxy S21",
                "is_active": True,
                "created_at": "2025-01-15T10:30:00Z",
                "updated_at": "2025-01-15T10:30:00Z",
                "last_used": "2025-01-15T12:45:00Z"
            }
        }
