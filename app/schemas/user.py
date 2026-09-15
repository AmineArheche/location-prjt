from uuid import UUID
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict
from app.models.enums import UserRole


class UserBase(BaseModel):
    email: EmailStr
    agency_id: Optional[UUID] = None
    role: UserRole = UserRole.AGENT
    agency_location: Optional[str] = None
    is_active: bool = True


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    agency_id: Optional[UUID] = None
    role: Optional[UserRole] = None
    agency_location: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

