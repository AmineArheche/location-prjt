from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, customers, vehicles, bookings, maintenance, superadmin, notifications

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(customers.router, prefix="/customers", tags=["Customers"])
api_router.include_router(vehicles.router, prefix="/vehicles", tags=["Vehicles"])
api_router.include_router(bookings.router, prefix="/bookings", tags=["Bookings"])
api_router.include_router(maintenance.router, prefix="/maintenance", tags=["Maintenance"])
api_router.include_router(superadmin.router, prefix="/superadmin", tags=["SuperAdmin"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])


