from uuid import UUID
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class AgencyBase(BaseModel):
    name: str
    city: str
    phone: str
    rc_number: str
    patente_number: str
    logo_url: Optional[str] = None


class AgencyCreate(AgencyBase):
    pass


class AgencyUpdate(BaseModel):
    name: Optional[str] = None
    city: Optional[str] = None
    phone: Optional[str] = None
    rc_number: Optional[str] = None
    patente_number: Optional[str] = None
    logo_url: Optional[str] = None


class AgencyResponse(AgencyBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
