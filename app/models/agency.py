from typing import Optional, TYPE_CHECKING
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base

if TYPE_CHECKING:
    from app.models.subscription import Subscription


class Agency(Base):
    """
    Agency (Tenant) Model representing distinct car rental agencies.
    """
    __tablename__ = "agencies"

    name: Mapped[str] = mapped_column(
        String(255), nullable=False
    )
    city: Mapped[str] = mapped_column(
        String(100), index=True, nullable=False
    )
    phone: Mapped[str] = mapped_column(
        String(50), nullable=False
    )
    rc_number: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, nullable=False
    )
    patente_number: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, nullable=False
    )
    logo_url: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True
    )

    # Relationships
    subscription: Mapped[Optional["Subscription"]] = relationship(
        "Subscription", back_populates="agency", uselist=False, lazy="selectin"
    )

