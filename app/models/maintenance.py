import uuid
from datetime import date
from decimal import Decimal
from typing import Optional, TYPE_CHECKING
from sqlalchemy import Date, Numeric, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base
from app.models.enums import MaintenanceType

if TYPE_CHECKING:
    from app.models.agency import Agency


class MaintenanceLog(Base):
    """
    Maintenance Log Model tracking vehicle service and inspection records with multi-tenant agency assignment.
    """
    __tablename__ = "maintenance_logs"

    agency_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("agencies.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    vehicle_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    type: Mapped[MaintenanceType] = mapped_column(
        SQLEnum(MaintenanceType, name="maintenance_type_enum", native_enum=True),
        nullable=False,
        index=True,
    )
    date_performed: Mapped[date] = mapped_column(
        Date, nullable=False
    )
    next_due_date: Mapped[date] = mapped_column(
        Date, nullable=False, index=True
    )
    cost: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False
    )

    # Relationships
    agency: Mapped[Optional["Agency"]] = relationship("Agency", lazy="selectin")
    vehicle: Mapped["Vehicle"] = relationship("Vehicle", lazy="selectin")

