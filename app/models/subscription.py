import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base
from app.models.enums import SubscriptionPlan

if TYPE_CHECKING:
    from app.models.agency import Agency


class Subscription(Base):
    """
    Subscription Model for multi-tenant Agency SaaS plan management.
    """
    __tablename__ = "subscriptions"

    agency_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("agencies.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    plan_name: Mapped[SubscriptionPlan] = mapped_column(
        SQLEnum(SubscriptionPlan, name="subscription_plan_enum", native_enum=True),
        default=SubscriptionPlan.STARTER,
        nullable=False,
        index=True,
    )
    max_vehicles: Mapped[int] = mapped_column(
        Integer, nullable=False, default=10
    )
    start_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    end_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )
    payment_notes: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True
    )

    # Relationships
    agency: Mapped["Agency"] = relationship("Agency", back_populates="subscription", lazy="selectin")
