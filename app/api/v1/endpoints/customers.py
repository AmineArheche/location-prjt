import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_active_user
from app.models.user import User
from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerResponse

router = APIRouter()


@router.post("/", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
async def create_customer(
    customer_in: CustomerCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Create a new Customer record.
    """
    # Check uniqueness of CIN/Passport or License number
    stmt = select(Customer).where(
        (Customer.cin_or_passport == customer_in.cin_or_passport) |
        (Customer.driver_license_number == customer_in.driver_license_number),
        Customer.deleted_at.is_(None)
    )
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Customer with given CIN/Passport or Driver License already exists."
        )

    db_customer = Customer(
        full_name=customer_in.full_name,
        phone_number=customer_in.phone_number,
        cin_or_passport=customer_in.cin_or_passport,
        driver_license_number=customer_in.driver_license_number,
        document_scans=customer_in.document_scans,
        is_blacklisted=customer_in.is_blacklisted,
    )
    db.add(db_customer)
    await db.flush()
    await db.refresh(db_customer)
    return db_customer


@router.get("/", response_model=List[CustomerResponse])
async def list_customers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Retrieve list of active (non-soft-deleted) customers.
    """
    stmt = select(Customer).where(Customer.deleted_at.is_(None)).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get customer details by UUID.
    """
    stmt = select(Customer).where(Customer.id == customer_id, Customer.deleted_at.is_(None))
    result = await db.execute(stmt)
    customer = result.scalar_one_or_none()
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    return customer


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def soft_delete_customer(
    customer_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Soft-delete customer record by UUID.
    """
    stmt = select(Customer).where(Customer.id == customer_id, Customer.deleted_at.is_(None))
    result = await db.execute(stmt)
    customer = result.scalar_one_or_none()
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    
    customer.soft_delete()
    db.add(customer)
    return None
