import re
from uuid import UUID
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import field_validator, BaseModel, ConfigDict, Field


class CustomerBase(BaseModel):
    agency_id: Optional[UUID] = None
    full_name: str = Field(..., min_length=2, max_length=255)
    phone_number: str = Field(..., min_length=8, max_length=50)
    cin_or_passport: str = Field(..., min_length=4, max_length=50)
    driver_license_number: str = Field(..., min_length=4, max_length=50)
    document_scans: Optional[Dict[str, Any]] = Field(default_factory=dict)
    is_blacklisted: bool = False


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    agency_id: Optional[UUID] = None
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    cin_or_passport: Optional[str] = None
    driver_license_number: Optional[str] = None
    document_scans: Optional[Dict[str, Any]] = None
    is_blacklisted: Optional[bool] = None


class CustomerResponse(CustomerBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

    # Code Review: Validation stricte du téléphone marocain
    @field_validator('phone_number')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        clean = re.sub(r'[\s\.\-\(\)]', '', v)
        if not re.match(r'^(?:\+212|0)[5-7][0-9]{8}$', clean):
            raise ValueError('Numéro de téléphone marocain invalide')
        return clean

    # Code Review: Normalisation de la CIN en majuscules
    @field_validator('cin_or_passport')
    @classmethod
    def normalize_cin(cls, v: str) -> str:
        return v.strip().upper()
