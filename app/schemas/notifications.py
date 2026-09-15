from enum import Enum
from uuid import UUID
from datetime import date, datetime

from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from app.models.enums import MaintenanceType


class NotificationChannel(str, Enum):
    SMS = "SMS"
    WHATSAPP = "WHATSAPP"


class MaintenanceItemSummary(BaseModel):
    vehicle_id: UUID
    matriculation: str
    make_model: str
    maintenance_type: MaintenanceType
    next_due_date: date
    days_until_due: int



class NotificationAlertPayload(BaseModel):
    recipient_phone: str = Field(..., json_schema_extra={"example": "+212 661 234567"})
    channel: NotificationChannel = Field(default=NotificationChannel.WHATSAPP)
    agency_id: Optional[UUID] = None
    maintenance_items: List[MaintenanceItemSummary] = Field(default_factory=list)
    custom_message: Optional[str] = Field(None, json_schema_extra={"example": "Urgent vehicle maintenance reminder"})


class NotificationResponse(BaseModel):
    status: str = Field(default="DELIVERED")
    message_id: str
    channel: NotificationChannel
    recipient_phone: str
    items_count: int
    delivered_at: datetime
    gateway_provider: str = Field(default="Twilio / Local Moroccan SMS Gateway")

    model_config = ConfigDict(from_attributes=True)
