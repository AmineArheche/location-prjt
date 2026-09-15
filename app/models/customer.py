import uuid
from typing import Optional, Any, Dict, TYPE_CHECKING
from sqlalchemy import String, Boolean, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base

if TYPE_CHECKING:
    from app.models.agency import Agency

# Cross-database compatible JSON column type
JSONType = JSONB().with_variant(JSON, "sqlite")


class Customer(Base):
    """
    Customer Model for rental clients with multi-tenant agency assignment.
    """
    __tablename__ = "customers"

    agency_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("agencies.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    full_name: Mapped[str] = mapped_column(
        String(255), nullable=False
    )
    phone_number: Mapped[str] = mapped_column(
        String(50), index=True, nullable=False
    )
    cin_or_passport: Mapped[str] = mapped_column(
        String(50), index=True, nullable=False
    )
    driver_license_number: Mapped[str] = mapped_column(
        String(50), index=True, nullable=False
    )
    document_scans: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONType, nullable=True, default=dict
    )
    is_blacklisted: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, index=True
    )

    # Relationships
    agency: Mapped[Optional["Agency"]] = relationship("Agency", lazy="selectin")

