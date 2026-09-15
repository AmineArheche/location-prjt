from uuid import UUID
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from app.models.enums import SubscriptionPlan


class SubscriptionBase(BaseModel):
    plan_name: SubscriptionPlan = SubscriptionPlan.STARTER
    max_vehicles: int = Field(default=10, ge=1)
    start_date: datetime
    end_date: datetime
    is_active: bool = True
    payment_notes: Optional[str] = None


class SubscriptionCreate(SubscriptionBase):
    agency_id: UUID


class SubscriptionUpdate(BaseModel):
    plan_name: Optional[SubscriptionPlan] = None
    max_vehicles: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_active: Optional[bool] = None
    payment_notes: Optional[str] = None


class SubscriptionResponse(SubscriptionBase):
    id: UUID
    agency_id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
