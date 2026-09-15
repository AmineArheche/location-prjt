import uuid
from decimal import Decimal
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Integer, Numeric, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base
from app.models.enums import VehicleStatus

if TYPE_CHECKING:
    from app.models.agency import Agency


class Vehicle(Base):
    """
    Vehicle Model for rental fleet inventory with multi-tenant agency assignment.
    """
    __tablename__ = "vehicles"

    agency_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("agencies.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    matriculation: Mapped[str] = mapped_column(
        String(50), index=True, nullable=False
    )
    make_model: Mapped[str] = mapped_column(
        String(255), nullable=False
    )
    year: Mapped[int] = mapped_column(
        Integer, nullable=False
    )
    current_mileage: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )
    daily_rate_mad: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False
    )
    status: Mapped[VehicleStatus] = mapped_column(
        SQLEnum(VehicleStatus, name="vehicle_status_enum", native_enum=True),
        default=VehicleStatus.AVAILABLE,
        nullable=False,
        index=True,
    )

    # Relationships
    agency: Mapped[Optional["Agency"]] = relationship("Agency", lazy="selectin")

