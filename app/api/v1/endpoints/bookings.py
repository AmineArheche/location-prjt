import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_active_user
from app.models.user import User
from app.models.booking import Booking
from app.models.vehicle import Vehicle
from app.models.customer import Customer
from app.models.enums import BookingStatus, VehicleStatus
from app.schemas.booking import BookingCreate, BookingUpdate, BookingResponse
from app.services.booking_service import check_vehicle_date_overlap
from app.services.pdf_service import generate_contract_pdf


router = APIRouter()


@router.post("/", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def create_booking(
    booking_in: BookingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Create a new Booking transaction.
    Wraps operations in a database transaction, verifies customer blacklist status,
    checks vehicle availability, checks for date overlaps, and updates vehicle status to RESERVED or RENTED.
    """
    # 1. Verify customer exists and is not blacklisted
    stmt_c = select(Customer).where(Customer.id == booking_in.customer_id, Customer.deleted_at.is_(None))
    res_c = await db.execute(stmt_c)
    customer = res_c.scalar_one_or_none()
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    if customer.is_blacklisted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Customer is blacklisted and cannot create vehicle bookings."
        )

    # 2. Verify vehicle exists and is currently AVAILABLE
    stmt_v = select(Vehicle).where(Vehicle.id == booking_in.vehicle_id, Vehicle.deleted_at.is_(None))
    res_v = await db.execute(stmt_v)
    vehicle = res_v.scalar_one_or_none()
    if not vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found")
    if vehicle.status != VehicleStatus.AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Vehicle is not available for booking (Current status: '{vehicle.status.value}')."
        )

    # 3. Check for overlapping bookings
    is_overlapping = await check_vehicle_date_overlap(
        db=db,
        vehicle_id=booking_in.vehicle_id,
        start_datetime=booking_in.start_datetime,
        end_datetime=booking_in.end_datetime,
    )
    if is_overlapping:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Vehicle is already booked during the requested date/time interval."
        )

    # 4. Update vehicle status to RENTED or RESERVED
    new_vehicle_status = VehicleStatus.RENTED if booking_in.status == BookingStatus.ACTIVE else VehicleStatus.RESERVED
    vehicle.status = new_vehicle_status
    db.add(vehicle)

    # 5. Create booking record
    db_booking = Booking(
        vehicle_id=booking_in.vehicle_id,
        customer_id=booking_in.customer_id,
        agent_id=current_user.id,
        start_datetime=booking_in.start_datetime,
        end_datetime=booking_in.end_datetime,
        start_mileage=booking_in.start_mileage,
        end_mileage=booking_in.end_mileage,
        total_price=booking_in.total_price,
        deposit_amount=booking_in.deposit_amount,
        status=booking_in.status,
        damage_report_start=booking_in.damage_report_start,
    )
    db.add(db_booking)
    await db.flush()
    await db.refresh(db_booking)
    return db_booking


@router.get("/", response_model=List[BookingResponse])
async def list_bookings(
    vehicle_id: Optional[uuid.UUID] = None,
    customer_id: Optional[uuid.UUID] = None,
    status_filter: Optional[BookingStatus] = Query(None, alias="status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Retrieve list of active (non-soft-deleted) bookings with optional filtering. Accessible by AGENTs.
    """
    stmt = select(Booking).where(Booking.deleted_at.is_(None))
    if vehicle_id:
        stmt = stmt.where(Booking.vehicle_id == vehicle_id)
    if customer_id:
        stmt = stmt.where(Booking.customer_id == customer_id)
    if status_filter:
        stmt = stmt.where(Booking.status == status_filter)
    
    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{booking_id}", response_model=BookingResponse)
async def get_booking(
    booking_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get booking details by UUID. Accessible by AGENTs.
    """
    stmt = select(Booking).where(Booking.id == booking_id, Booking.deleted_at.is_(None))
    result = await db.execute(stmt)
    booking = result.scalar_one_or_none()
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    return booking


@router.get("/{booking_id}/pdf")
async def generate_booking_contract_pdf(
    booking_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Generate and stream 2-page Moroccan Rental Contract PDF for a given booking.
    Returns inline media stream with filename=contract_{booking_id}.pdf.
    """
    stmt = select(Booking).where(Booking.id == booking_id, Booking.deleted_at.is_(None))
    result = await db.execute(stmt)
    booking = result.scalar_one_or_none()
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking contract not found")

    pdf_bytes = generate_contract_pdf(booking)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"inline; filename=contract_{booking_id}.pdf"
        },
    )


@router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
async def soft_delete_booking(
    booking_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Soft-delete booking record.
    """
    stmt = select(Booking).where(Booking.id == booking_id, Booking.deleted_at.is_(None))
    result = await db.execute(stmt)
    booking = result.scalar_one_or_none()
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")

    booking.soft_delete()
    db.add(booking)
    return None

