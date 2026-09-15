import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_active_user
from app.models.user import User
from app.models.maintenance import MaintenanceLog
from app.models.vehicle import Vehicle
from app.models.enums import MaintenanceType
from app.schemas.maintenance import MaintenanceLogCreate, MaintenanceLogUpdate, MaintenanceLogResponse

router = APIRouter()


@router.post("/", response_model=MaintenanceLogResponse, status_code=status.HTTP_201_CREATED)
async def create_maintenance_log(
    log_in: MaintenanceLogCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Record a new vehicle maintenance log.
    """
    stmt_v = select(Vehicle).where(Vehicle.id == log_in.vehicle_id, Vehicle.deleted_at.is_(None))
    res_v = await db.execute(stmt_v)
    if not res_v.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found")

    db_log = MaintenanceLog(
        vehicle_id=log_in.vehicle_id,
        type=log_in.type,
        date_performed=log_in.date_performed,
        next_due_date=log_in.next_due_date,
        cost=log_in.cost,
    )
    db.add(db_log)
    await db.flush()
    await db.refresh(db_log)
    return db_log


@router.get("/", response_model=List[MaintenanceLogResponse])
async def list_maintenance_logs(
    vehicle_id: Optional[uuid.UUID] = None,
    type_filter: Optional[MaintenanceType] = Query(None, alias="type"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Retrieve list of maintenance logs.
    """
    stmt = select(MaintenanceLog).where(MaintenanceLog.deleted_at.is_(None))
    if vehicle_id:
        stmt = stmt.where(MaintenanceLog.vehicle_id == vehicle_id)
    if type_filter:
        stmt = stmt.where(MaintenanceLog.type == type_filter)

    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{log_id}", response_model=MaintenanceLogResponse)
async def get_maintenance_log(
    log_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get maintenance log by UUID.
    """
    stmt = select(MaintenanceLog).where(MaintenanceLog.id == log_id, MaintenanceLog.deleted_at.is_(None))
    result = await db.execute(stmt)
    log_entry = result.scalar_one_or_none()
    if not log_entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Maintenance log not found")
    return log_entry


@router.delete("/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
async def soft_delete_maintenance_log(
    log_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Soft-delete maintenance log entry.
    """
    stmt = select(MaintenanceLog).where(MaintenanceLog.id == log_id, MaintenanceLog.deleted_at.is_(None))
    result = await db.execute(stmt)
    log_entry = result.scalar_one_or_none()
    if not log_entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Maintenance log not found")

    log_entry.soft_delete()
    db.add(log_entry)
    return None
