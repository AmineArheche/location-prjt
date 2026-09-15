from datetime import datetime
from uuid import UUID
from typing import Optional
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.booking import Booking
from app.models.enums import BookingStatus


async def check_vehicle_date_overlap(
    db: AsyncSession,
    vehicle_id: UUID,
    start_datetime: datetime,
    end_datetime: datetime,
    exclude_booking_id: Optional[UUID] = None,
) -> bool:
    """
    SQLAlchemy query method that checks for overlapping dates to prevent double-booking a vehicle.
    
    A target interval [start_datetime, end_datetime] overlaps with an existing booking [b.start, b.end] if:
        (b.start_datetime < end_datetime) AND (b.end_datetime > start_datetime)
    
    Only non-cancelled, active/pending, non-soft-deleted bookings are checked.
    
    Returns:
        bool: True if an overlapping booking exists (double-booking risk), False if vehicle is available.
    """
    stmt = select(Booking).where(
        Booking.vehicle_id == vehicle_id,
        Booking.deleted_at.is_(None),
        Booking.status.in_([BookingStatus.PENDING, BookingStatus.ACTIVE]),
        and_(
            Booking.start_datetime < end_datetime,
            Booking.end_datetime > start_datetime,
        ),
    )

    if exclude_booking_id:
        stmt = stmt.where(Booking.id != exclude_booking_id)

    result = await db.execute(stmt)
    overlapping_booking = result.scalar_one_or_none()
    return overlapping_booking is not None
