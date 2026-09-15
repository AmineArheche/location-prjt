import uuid
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base
from app.models.enums import UserRole

if TYPE_CHECKING:
    from app.models.agency import Agency


class User(Base):
    """
    User Model extending the Base entity with multi-tenant agency assignment.
    """
    __tablename__ = "users"

    agency_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("agencies.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    password_hash: Mapped[str] = mapped_column(
        String(255), nullable=False
    )
    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole, name="user_role_enum", native_enum=True),
        default=UserRole.AGENT,
        nullable=False,
        index=True,
    )
    agency_location: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )

    # Relationships
    agency: Mapped[Optional["Agency"]] = relationship("Agency", lazy="selectin")

