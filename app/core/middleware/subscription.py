import uuid
from datetime import datetime, timezone
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.core.security import decode_access_token
from app.models.user import User
from app.models.enums import UserRole
from app.models.subscription import Subscription


class SubscriptionCheckMiddleware(BaseHTTPMiddleware):
    """
    Middleware intercepting agency user API calls to verify active subscription status.
    Returns HTTP 402 Payment Required if subscription is inactive or end_date < current UTC time.
    """
    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # Bypass non-v1 API routes, health/docs endpoints, and auth endpoints
        exempt_paths = [
            "/docs",
            "/redoc",
            "/openapi.json",
            "/health",
            "/",
            "/api/v1/auth/login",
            "/api/v1/auth/register",
        ]
        
        if any(path.startswith(p) for p in exempt_paths):
            return await call_next(request)

        # Check authorization header
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            payload = decode_access_token(token)
            if payload and "sub" in payload:
                user_id_str = payload["sub"]
                try:
                    user_uuid = uuid.UUID(user_id_str)
                    async with AsyncSessionLocal() as db:
                        stmt = select(User).where(User.id == user_uuid, User.deleted_at.is_(None))
                        result = await db.execute(stmt)
                        user = result.scalar_one_or_none()

                        # Enforce check for non-SuperAdmin agency users
                        if user and user.role != UserRole.SUPERADMIN and user.agency_id is not None:
                            sub_stmt = select(Subscription).where(
                                Subscription.agency_id == user.agency_id,
                                Subscription.deleted_at.is_(None)
                            )
                            sub_res = await db.execute(sub_stmt)
                            subscription = sub_res.scalar_one_or_none()

                            now_utc = datetime.now(timezone.utc)

                            if not subscription or not subscription.is_active:
                                return JSONResponse(
                                    status_code=402,
                                    content={"detail": "Subscription expired. Please contact platform support."}
                                )

                            sub_end = subscription.end_date
                            if sub_end.tzinfo is None:
                                sub_end = sub_end.replace(tzinfo=timezone.utc)

                            if sub_end < now_utc:
                                return JSONResponse(
                                    status_code=402,
                                    content={"detail": "Subscription expired. Please contact platform support."}
                                )

                except Exception:
                    # Token parse or DB exception - allow downsteam FastAPI auth dependency to handle standard 401
                    pass

        return await call_next(request)
