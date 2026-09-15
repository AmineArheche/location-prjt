import uuid
from typing import AsyncGenerator, List
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.core.config import settings
from app.core.security import decode_access_token
from app.models.user import User
from app.models.enums import UserRole

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Reusable database session dependency for FastAPI routes.
    Provides an async SQLAlchemy session and handles commit/rollback lifecycle.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> User:
    """
    Dependency for extracting, decoding, and verifying the current user from JWT token.
    Checks that the user exists in database and has not been soft-deleted.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    user_id_str: str = payload.get("sub")
    if user_id_str is None:
        raise credentials_exception
    
    try:
        user_uuid = uuid.UUID(user_id_str)
    except ValueError:
        raise credentials_exception

    stmt = select(User).where(User.id == user_uuid, User.deleted_at.is_(None))
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception
    
    return user


from datetime import datetime, timezone
from app.models.subscription import Subscription


async def get_current_active_user(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> User:
    """Dependency verifying that authenticated user is active and agency subscription is valid."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account"
        )

    # Subscription expiration check for non-SuperAdmin agency users
    if current_user.role != UserRole.SUPERADMIN and current_user.agency_id is not None:
        stmt = select(Subscription).where(
            Subscription.agency_id == current_user.agency_id,
            Subscription.deleted_at.is_(None)
        )
        res = await db.execute(stmt)
        subscription = res.scalar_one_or_none()

        now_utc = datetime.now(timezone.utc)
        if not subscription or not subscription.is_active:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="Subscription expired. Please contact platform support."
            )

        sub_end = subscription.end_date
        if sub_end.tzinfo is None:
            sub_end = sub_end.replace(tzinfo=timezone.utc)

        if sub_end < now_utc:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="Subscription expired. Please contact platform support."
            )


    return current_user



class RoleChecker:
    """
    RBAC Dependency enforcing role-based access control.
    """
    def __init__(self, allowed_roles: List[UserRole]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"User with role '{current_user.role.value}' does not have permission to perform this action. "
                    f"Required roles: {[r.value for r in self.allowed_roles]}"
                ),
            )
        return current_user


# Preset RBAC Dependencies
require_admin_or_manager = RoleChecker([UserRole.SUPERADMIN, UserRole.AGENCY_MANAGER])
require_superadmin = RoleChecker([UserRole.SUPERADMIN])
