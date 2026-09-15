import secrets
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_superadmin
from app.core.security import hash_password
from app.models.agency import Agency
from app.models.subscription import Subscription
from app.models.user import User
from app.models.enums import UserRole, SubscriptionPlan
from app.schemas.superadmin import (
    AgencyProvisionRequest,
    AgencyProvisionResponse,
    ManagerCredentials,
)

router = APIRouter()

# Default plan max vehicle limits
PLAN_MAX_VEHICLES_MAP = {
    SubscriptionPlan.STARTER: 10,
    SubscriptionPlan.PRO: 30,
    SubscriptionPlan.ENTERPRISE: 9999,
}


@router.post("/agencies/provision", response_model=AgencyProvisionResponse, status_code=status.HTTP_201_CREATED)
async def provision_agency(
    provision_in: AgencyProvisionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin),
):
    """
    SuperAdmin API endpoint to provision a new car rental agency with active subscription plan
    and automatically generated initial AGENCY_MANAGER credentials.
    """
    # 1. Check for duplicate agency by RC Number
    stmt_rc = select(Agency).where(
        Agency.rc_number == provision_in.rc_number,
        Agency.deleted_at.is_(None)
    )
    res_rc = await db.execute(stmt_rc)
    if res_rc.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Agency with RC number '{provision_in.rc_number}' already exists."
        )

    # 2. Check for duplicate agency by Patente Number
    stmt_patente = select(Agency).where(
        Agency.patente_number == provision_in.patente_number,
        Agency.deleted_at.is_(None)
    )
    res_patente = await db.execute(stmt_patente)
    if res_patente.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Agency with Patente number '{provision_in.patente_number}' already exists."
        )

    # 3. Check for existing manager user email
    stmt_user = select(User).where(
        User.email == provision_in.manager_email,
        User.deleted_at.is_(None)
    )
    res_user = await db.execute(stmt_user)
    if res_user.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with email '{provision_in.manager_email}' already exists."
        )

    # 4. Create Agency
    db_agency = Agency(
        name=provision_in.name,
        city=provision_in.city,
        phone=provision_in.phone,
        rc_number=provision_in.rc_number,
        patente_number=provision_in.patente_number,
        logo_url=provision_in.logo_url,
    )
    db.add(db_agency)
    await db.flush()
    await db.refresh(db_agency)

    # 5. Calculate Subscription Dates & Max Vehicle Limit
    now_utc = datetime.now(timezone.utc)
    # Approximate duration in days based on 30 days per month
    end_date = now_utc + timedelta(days=provision_in.duration_months * 30)

    max_vehicles = provision_in.max_vehicles
    if max_vehicles is None:
        max_vehicles = PLAN_MAX_VEHICLES_MAP.get(provision_in.plan_name, 10)

    db_subscription = Subscription(
        agency_id=db_agency.id,
        plan_name=provision_in.plan_name,
        max_vehicles=max_vehicles,
        start_date=now_utc,
        end_date=end_date,
        is_active=True,
        payment_notes=provision_in.payment_notes,
    )
    db.add(db_subscription)
    await db.flush()
    await db.refresh(db_subscription)

    # 6. Generate Temporary Manager Password & Create AGENCY_MANAGER User
    temp_password = f"MgrTemp#{secrets.token_urlsafe(6)}!"
    password_hash = hash_password(temp_password)

    db_manager = User(
        email=provision_in.manager_email,
        password_hash=password_hash,
        role=UserRole.AGENCY_MANAGER,
        agency_id=db_agency.id,
        agency_location=provision_in.manager_agency_location or f"{db_agency.city} Main Office",
        is_active=True,
    )
    db.add(db_manager)
    await db.flush()

    return AgencyProvisionResponse(
        agency=db_agency,
        subscription=db_subscription,
        manager_credentials=ManagerCredentials(
            email=provision_in.manager_email,
            temporary_password=temp_password,
        ),
        login_url="/login",
    )
