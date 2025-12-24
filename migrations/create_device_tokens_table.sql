-- Migration: Create DeviceTokens table
-- Description: Table pour stocker les tokens FCM (Firebase Cloud Messaging) des appareils utilisateurs
-- Date: 2025-01-23

CREATE TABLE IF NOT EXISTS "DeviceTokens" (
    "SKU" UUID PRIMARY KEY,
    "AppUserSKU" UUID NOT NULL,
    "FcmToken" TEXT NOT NULL,
    "DeviceType" TEXT NOT NULL,
    "DeviceName" TEXT,
    "IsActive" BOOLEAN NOT NULL DEFAULT true,
    "CreatedAt" TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    "UpdatedAt" TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    "LastUsed" TIMESTAMP WITH TIME ZONE,

    CONSTRAINT "FK_DeviceTokens_AppUsers_AppUserSKU"
        FOREIGN KEY ("AppUserSKU")
        REFERENCES "AppUsers"("SKU")
        ON DELETE CASCADE
);

-- Create indexes for better query performance
CREATE INDEX "IX_DeviceTokens_AppUserSKU" ON "DeviceTokens"("AppUserSKU");
CREATE INDEX "IX_DeviceTokens_FcmToken" ON "DeviceTokens"("FcmToken");

-- Comments
COMMENT ON TABLE "DeviceTokens" IS 'Stores FCM (Firebase Cloud Messaging) tokens for user devices';
COMMENT ON COLUMN "DeviceTokens"."SKU" IS 'Unique identifier for the device token record';
COMMENT ON COLUMN "DeviceTokens"."AppUserSKU" IS 'Foreign key to AppUsers table';
COMMENT ON COLUMN "DeviceTokens"."FcmToken" IS 'Firebase Cloud Messaging token for push notifications';
COMMENT ON COLUMN "DeviceTokens"."DeviceType" IS 'Type of device: android, ios, or web';
COMMENT ON COLUMN "DeviceTokens"."DeviceName" IS 'User-friendly name for the device';
COMMENT ON COLUMN "DeviceTokens"."IsActive" IS 'Whether the device is currently active for notifications';
COMMENT ON COLUMN "DeviceTokens"."CreatedAt" IS 'Timestamp when the device was first registered';
COMMENT ON COLUMN "DeviceTokens"."UpdatedAt" IS 'Timestamp of last update to the device record';
COMMENT ON COLUMN "DeviceTokens"."LastUsed" IS 'Timestamp when the device last received a notification';
