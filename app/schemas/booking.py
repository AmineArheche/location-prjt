from uuid import UUID
from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, Field, model_validator
from app.models.enums import BookingStatus


class BookingBase(BaseModel):
    agency_id: Optional[UUID] = None
    vehicle_id: UUID
    customer_id: UUID
    agent_id: UUID
    start_datetime: datetime
    end_datetime: datetime
    start_mileage: int = Field(..., ge=0)
    end_mileage: Optional[int] = Field(None, ge=0)
    total_price: Decimal = Field(..., gt=0)
    deposit_amount: Decimal = Field(default=Decimal("0.00"), ge=0)
    status: BookingStatus = BookingStatus.PENDING
    damage_report_start: Optional[Dict[str, Any]] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_booking_dates(self):
        if self.start_datetime and self.end_datetime:
            if self.end_datetime <= self.start_datetime:
                raise ValueError("end_datetime must be strictly after start_datetime")
        if self.end_mileage is not None and self.start_mileage is not None:
            if self.end_mileage < self.start_mileage:
                raise ValueError("end_mileage cannot be less than start_mileage")
        return self


class BookingCreate(BookingBase):
    pass


class BookingUpdate(BaseModel):
    agency_id: Optional[UUID] = None
    start_datetime: Optional[datetime] = None
    end_datetime: Optional[datetime] = None
    start_mileage: Optional[int] = None
    end_mileage: Optional[int] = None
    total_price: Optional[Decimal] = None
    deposit_amount: Optional[Decimal] = None
    status: Optional[BookingStatus] = None
    damage_report_start: Optional[Dict[str, Any]] = None


class BookingResponse(BookingBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
