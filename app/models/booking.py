import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict, Any, TYPE_CHECKING
from sqlalchemy import String, Integer, Numeric, DateTime, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base
from app.models.enums import BookingStatus

if TYPE_CHECKING:
    from app.models.agency import Agency

# Cross-database compatible JSON column type
JSONType = JSONB().with_variant(JSON, "sqlite")


class Booking(Base):
    """
    Booking Model mapping rental transactions between Customers, Vehicles, and Agents.
    """
    __tablename__ = "bookings"

    agency_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("agencies.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    vehicle_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("vehicles.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    customer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("customers.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    agent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True
    )

    start_datetime: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    end_datetime: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )

    start_mileage: Mapped[int] = mapped_column(
        Integer, nullable=False
    )
    end_mileage: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True
    )

    total_price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False
    )
    deposit_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False, default=Decimal("0.00")
    )

    status: Mapped[BookingStatus] = mapped_column(
        SQLEnum(BookingStatus, name="booking_status_enum", native_enum=True),
        default=BookingStatus.PENDING,
        nullable=False,
        index=True,
    )

    damage_report_start: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONType, nullable=True, default=dict
    )

    # Relationships
    agency: Mapped[Optional["Agency"]] = relationship("Agency", lazy="selectin")
    vehicle: Mapped["Vehicle"] = relationship("Vehicle", lazy="selectin")
    customer: Mapped["Customer"] = relationship("Customer", lazy="selectin")
    agent: Mapped["User"] = relationship("User", lazy="selectin")

