import re
from decimal import Decimal
from typing import Optional, List
from uuid import UUID
from datetime import datetime, date
from pydantic import BaseModel, ConfigDict, Field, field_validator
from app.models.enums import VehicleStatus, MaintenanceType

MOROCCAN_PLATE_REGEX = re.compile(
    r"^(?P<num>\d{1,6})\s*[\s\|\/\-]\s*(?P<series>[A-Za-z\u0600-\u06FF]{1,10})\s*[\s\|\/\-]\s*(?P<region>\d{1,2})$"
)
WW_PLATE_REGEX = re.compile(r"^(WW)\s*[\s\|\/\-]?\s*(\d{1,6})$", re.IGNORECASE)
SPECIAL_PLATE_REGEX = re.compile(r"^([A-Z]{1,3})\s*[\s\|\/\-]?\s*(\d{1,6})$", re.IGNORECASE)


class VehicleBase(BaseModel):
    agency_id: Optional[UUID] = None
    matriculation: str
    make_model: str = Field(..., min_length=2, max_length=255)
    year: int = Field(..., ge=1900, le=2100)
    current_mileage: int = Field(default=0, ge=0)
    daily_rate_mad: Decimal = Field(..., gt=0)
    status: VehicleStatus = VehicleStatus.AVAILABLE

    @field_validator("matriculation")
    @classmethod
    def validate_and_normalize_matriculation(cls, v: str) -> str:
        """
        Validates and normalizes Moroccan vehicle matriculation formats.
        Supports standard 3-part formats ('12345 | A | 15', '12345-A-15', '12345 | أ | 15'),
        WW temporary series ('WW-12345'), and official series.
        """
        if not v or not isinstance(v, str):
            raise ValueError("Matriculation number is required")
        
        cleaned = v.strip()

        # Check standard 3-part format (e.g. "12345 | A | 15" or "12345-A-15")
        match = MOROCCAN_PLATE_REGEX.match(cleaned)
        if match:
            num = match.group("num")
            series = match.group("series").upper()
            region = match.group("region")
            return f"{num} | {series} | {region}"
        
        # Check WW temporary plate format (e.g. "WW-12345")
        ww_match = WW_PLATE_REGEX.match(cleaned)
        if ww_match:
            return f"WW-{ww_match.group(2)}"
        
        # Check special plate format (e.g. "MA-12345")
        spec_match = SPECIAL_PLATE_REGEX.match(cleaned)
        if spec_match:
            return f"{spec_match.group(1).upper()}-{spec_match.group(2)}"

        raise ValueError(
            f"Invalid Moroccan matriculation format: '{v}'. "
            f"Expected format like '12345 | A | 15', '12345-A-15', or 'WW-12345'."
        )


class VehicleCreate(VehicleBase):
    pass


class VehicleUpdate(BaseModel):
    agency_id: Optional[UUID] = None
    matriculation: Optional[str] = None
    make_model: Optional[str] = None
    year: Optional[int] = None
    current_mileage: Optional[int] = None
    daily_rate_mad: Optional[Decimal] = None
    status: Optional[VehicleStatus] = None

    @field_validator("matriculation")
    @classmethod
    def validate_optional_matriculation(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        return VehicleBase.validate_and_normalize_matriculation(v)


class VehicleResponse(VehicleBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class VehicleStatusAggregate(BaseModel):
    total_vehicles: int
    available_count: int
    rented_count: int
    maintenance_count: int
    reserved_count: int


class VehicleMaintenanceNearDue(BaseModel):
    vehicle_id: UUID
    matriculation: str
    make_model: str
    maintenance_type: MaintenanceType
    next_due_date: date
    days_until_due: int


class VehicleDashboardResponse(BaseModel):
    status_summary: VehicleStatusAggregate
    vehicles_nearing_maintenance: List[VehicleMaintenanceNearDue]
