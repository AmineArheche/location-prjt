from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from app.models.enums import SubscriptionPlan
from app.schemas.agency import AgencyResponse
from app.schemas.subscription import SubscriptionResponse


class ManagerCredentials(BaseModel):
    email: EmailStr
    temporary_password: str


class AgencyProvisionRequest(BaseModel):
    # Agency details
    name: str = Field(..., json_schema_extra={"example": "Atlas Car Rental"})
    city: str = Field(..., json_schema_extra={"example": "Casablanca"})
    phone: str = Field(..., json_schema_extra={"example": "+212 522 123456"})
    rc_number: str = Field(..., json_schema_extra={"example": "RC-123456"})
    patente_number: str = Field(..., json_schema_extra={"example": "PAT-987654"})
    logo_url: Optional[str] = Field(None, json_schema_extra={"example": "https://example.com/logo.png"})

    # Subscription details
    plan_name: SubscriptionPlan = Field(default=SubscriptionPlan.STARTER)
    duration_months: int = Field(default=12, ge=1, description="Subscription duration in months")
    max_vehicles: Optional[int] = Field(None, description="Optional custom vehicle limit override")
    payment_notes: Optional[str] = Field(None, json_schema_extra={"example": "Paid 1200 MAD via CIH Bank Transfer"})

    # Initial Manager details
    manager_email: EmailStr = Field(..., json_schema_extra={"example": "manager@atlascar.ma"})
    manager_agency_location: Optional[str] = Field(None, json_schema_extra={"example": "Casablanca Downtown"})



class AgencyProvisionResponse(BaseModel):
    agency: AgencyResponse
    subscription: SubscriptionResponse
    manager_credentials: ManagerCredentials
    login_url: str = "/login"

    model_config = ConfigDict(from_attributes=True)
