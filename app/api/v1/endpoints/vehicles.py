import uuid
from datetime import date, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_active_user, require_admin_or_manager
from app.models.user import User
from app.models.vehicle import Vehicle
from app.models.subscription import Subscription
from app.models.maintenance import MaintenanceLog
from app.models.enums import VehicleStatus, UserRole
from app.schemas.vehicle import (
    VehicleCreate,
    VehicleUpdate,
    VehicleResponse,
    VehicleDashboardResponse,
    VehicleStatusAggregate,
    VehicleMaintenanceNearDue,
)

router = APIRouter()


@router.get("/dashboard", response_model=VehicleDashboardResponse)
async def get_vehicle_dashboard(
    days_ahead: int = Query(30, ge=1, le=180, description="Days threshold to check for upcoming maintenance"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get real-time vehicle fleet status aggregate and list vehicles nearing maintenance next_due_date.
    """
    # 1. Real-time aggregate count of vehicle statuses
    stmt_counts = (
        select(Vehicle.status, func.count(Vehicle.id))
        .where(Vehicle.deleted_at.is_(None))
    )
    if current_user.role != UserRole.SUPERADMIN and current_user.agency_id is not None:
        stmt_counts = stmt_counts.where(Vehicle.agency_id == current_user.agency_id)

    stmt_counts = stmt_counts.group_by(Vehicle.status)
    res_counts = await db.execute(stmt_counts)
    counts_dict = dict(res_counts.all())

    available_c = counts_dict.get(VehicleStatus.AVAILABLE, 0)
    rented_c = counts_dict.get(VehicleStatus.RENTED, 0)
    maint_c = counts_dict.get(VehicleStatus.MAINTENANCE, 0)
    res_c = counts_dict.get(VehicleStatus.RESERVED, 0)
    total_c = available_c + rented_c + maint_c + res_c

    status_summary = VehicleStatusAggregate(
        total_vehicles=total_c,
        available_count=available_c,
        rented_count=rented_c,
        maintenance_count=maint_c,
        reserved_count=res_c,
    )

    # 2. Query vehicles nearing next_due_date in maintenance logs
    today = date.today()
    cutoff_date = today + timedelta(days=days_ahead)

    stmt_maint = (
        select(MaintenanceLog, Vehicle)
        .join(Vehicle, MaintenanceLog.vehicle_id == Vehicle.id)
        .where(
            MaintenanceLog.deleted_at.is_(None),
            Vehicle.deleted_at.is_(None),
            MaintenanceLog.next_due_date <= cutoff_date,
        )
    )
    if current_user.role != UserRole.SUPERADMIN and current_user.agency_id is not None:
        stmt_maint = stmt_maint.where(Vehicle.agency_id == current_user.agency_id)

    stmt_maint = stmt_maint.order_by(MaintenanceLog.next_due_date.asc())
    res_maint = await db.execute(stmt_maint)
    maint_rows = res_maint.all()

    vehicles_nearing = []
    for log_item, veh in maint_rows:
        days_until = (log_item.next_due_date - today).days
        vehicles_nearing.append(
            VehicleMaintenanceNearDue(
                vehicle_id=veh.id,
                matriculation=veh.matriculation,
                make_model=veh.make_model,
                maintenance_type=log_item.type,
                next_due_date=log_item.next_due_date,
                days_until_due=days_until,
            )
        )

    return VehicleDashboardResponse(
        status_summary=status_summary,
        vehicles_nearing_maintenance=vehicles_nearing,
    )


@router.post("/", response_model=VehicleResponse, status_code=status.HTTP_201_CREATED)
async def create_vehicle(
    vehicle_in: VehicleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin_or_manager),
):
    """
    Create a new Vehicle entry in fleet inventory (Requires SUPERADMIN or AGENCY_MANAGER).
    Enforces maximum vehicle subscription limits for agency users.
    """
    # 1. Check duplicate matriculation
    stmt = select(Vehicle).where(
        Vehicle.matriculation == vehicle_in.matriculation,
        Vehicle.deleted_at.is_(None)
    )
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Vehicle with matriculation '{vehicle_in.matriculation}' already exists."
        )

    # 2. Subscription limit vehicle guard
    if current_user.role != UserRole.SUPERADMIN and current_user.agency_id is not None:
        sub_stmt = select(Subscription).where(
            Subscription.agency_id == current_user.agency_id,
            Subscription.deleted_at.is_(None)
        )
        sub_res = await db.execute(sub_stmt)
        subscription = sub_res.scalar_one_or_none()

        if subscription:
            count_stmt = select(func.count(Vehicle.id)).where(
                Vehicle.agency_id == current_user.agency_id,
                Vehicle.deleted_at.is_(None)
            )
            count_res = await db.execute(count_stmt)
            active_vehicles_count = count_res.scalar() or 0

            if active_vehicles_count >= subscription.max_vehicles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Vehicle limit reached for subscription plan '{subscription.plan_name.value}'. Maximum allowed: {subscription.max_vehicles}."
                )

    db_vehicle = Vehicle(
        agency_id=current_user.agency_id,
        matriculation=vehicle_in.matriculation,
        make_model=vehicle_in.make_model,
        year=vehicle_in.year,
        current_mileage=vehicle_in.current_mileage,
        daily_rate_mad=vehicle_in.daily_rate_mad,
        status=vehicle_in.status,
    )
    db.add(db_vehicle)
    await db.flush()
    await db.refresh(db_vehicle)
    return db_vehicle



@router.get("/", response_model=List[VehicleResponse])
async def list_vehicles(
    status_filter: Optional[VehicleStatus] = Query(None, alias="status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Retrieve list of vehicles with optional status filtering. Accessible by AGENTs.
    """
    stmt = select(Vehicle).where(Vehicle.deleted_at.is_(None))
    if current_user.role != UserRole.SUPERADMIN and current_user.agency_id is not None:
        stmt = stmt.where(Vehicle.agency_id == current_user.agency_id)
    if status_filter:
        stmt = stmt.where(Vehicle.status == status_filter)
    
    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()



@router.get("/{vehicle_id}", response_model=VehicleResponse)
async def get_vehicle(
    vehicle_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get vehicle by UUID. Accessible by AGENTs.
    """
    stmt = select(Vehicle).where(Vehicle.id == vehicle_id, Vehicle.deleted_at.is_(None))
    result = await db.execute(stmt)
    vehicle = result.scalar_one_or_none()
    if not vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found")
    return vehicle


@router.delete("/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT)
async def soft_delete_vehicle(
    vehicle_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin_or_manager),
):
    """
    Soft-delete vehicle entry by UUID. Restricted to SUPERADMIN and AGENCY_MANAGER.
    """
    stmt = select(Vehicle).where(Vehicle.id == vehicle_id, Vehicle.deleted_at.is_(None))
    result = await db.execute(stmt)
    vehicle = result.scalar_one_or_none()
    if not vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found")
    
    vehicle.soft_delete()
    db.add(vehicle)
    return None
