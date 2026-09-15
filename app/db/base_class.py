import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID


class Base(DeclarativeBase):
    """
    Abstract Base Model for all SQLAlchemy entities in the application.
    Includes UUID4 primary key, UTC creation & update timestamps, and soft-delete capabilities.
    """
    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )

    def soft_delete(self) -> None:
        """Mark record as soft-deleted by setting deleted_at timestamp."""
        self.deleted_at = datetime.now(timezone.utc)

    def restore(self) -> None:
        """Restore soft-deleted record."""
        self.deleted_at = None

    @property
    def is_deleted(self) -> bool:
        """Check if record has been soft-deleted."""
        return self.deleted_at is not None
