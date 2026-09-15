from uuid import UUID
from datetime import datetime, date
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, model_validator
from app.models.enums import MaintenanceType


class MaintenanceLogBase(BaseModel):
    vehicle_id: UUID
    type: MaintenanceType
    date_performed: date
    next_due_date: date
    cost: Decimal = Field(..., ge=0)

    @model_validator(mode="after")
    def validate_maintenance_dates(self):
        if self.date_performed and self.next_due_date:
            if self.next_due_date < self.date_performed:
                raise ValueError("next_due_date cannot be earlier than date_performed")
        return self


class MaintenanceLogCreate(MaintenanceLogBase):
    pass


class MaintenanceLogUpdate(BaseModel):
    type: Optional[MaintenanceType] = None
    date_performed: Optional[date] = None
    next_due_date: Optional[date] = None
    cost: Optional[Decimal] = None


class MaintenanceLogResponse(MaintenanceLogBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
