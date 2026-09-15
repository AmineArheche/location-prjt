import asyncio
from decimal import Decimal
from datetime import datetime, date, timedelta, timezone
from sqlalchemy import select

from app.core.database import AsyncSessionLocal, engine
from app.db.base_class import Base
from app.core.security import hash_password
from app.models.enums import UserRole, VehicleStatus, BookingStatus, MaintenanceType
from app.models.user import User
from app.models.customer import Customer
from app.models.vehicle import Vehicle
from app.models.booking import Booking
from app.models.maintenance import MaintenanceLog


async def seed_data():
    print("Initializing Database tables if needed...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        # 1. Create Demo Users
        print("Seeding Demo Users...")
        users_data = [
            {
                "email": "superadmin@agency.ma",
                "password_hash": hash_password("adminpassword123"),
                "role": UserRole.SUPERADMIN,
                "agency_location": "Casablanca Headquarters",
                "is_active": True,
            },
            {
                "email": "manager@agency.ma",
                "password_hash": hash_password("managerpassword123"),
                "role": UserRole.AGENCY_MANAGER,
                "agency_location": "Marrakech City Center",
                "is_active": True,
            },
            {
                "email": "agent@agency.ma",
                "password_hash": hash_password("agentpassword123"),
                "role": UserRole.AGENT,
                "agency_location": "Fès Airport Hub",
                "is_active": True,
            },
        ]

        created_users = []
        for u in users_data:
            stmt = select(User).where(User.email == u["email"])
            res = await session.execute(stmt)
            existing = res.scalar_one_or_none()
            if not existing:
                user_obj = User(**u)
                session.add(user_obj)
                await session.flush()
                created_users.append(user_obj)
            else:
                created_users.append(existing)

        # 2. Create Demo Customers
        print("Seeding Demo Customers...")
        customers_data = [
            {
                "full_name": "Youssef El Amrani",
                "phone_number": "+212 661 112 233",
                "cin_or_passport": "AB123456",
                "driver_license_number": "DL-998877",
                "is_blacklisted": False,
            },
            {
                "full_name": "Fatima Zohra Benali",
                "phone_number": "+212 662 334 455",
                "cin_or_passport": "CD987654",
                "driver_license_number": "DL-554433",
                "is_blacklisted": False,
            },
            {
                "full_name": "Karim Alami",
                "phone_number": "+212 663 778 899",
                "cin_or_passport": "EF456789",
                "driver_license_number": "DL-112233",
                "is_blacklisted": True,  # Blacklisted for testing
            },
        ]

        created_customers = []
        for c in customers_data:
            stmt = select(Customer).where(Customer.cin_or_passport == c["cin_or_passport"])
            res = await session.execute(stmt)
            existing = res.scalar_one_or_none()
            if not existing:
                cust_obj = Customer(**c)
                session.add(cust_obj)
                await session.flush()
                created_customers.append(cust_obj)
            else:
                created_customers.append(existing)

        # 3. Create Demo Vehicles
        print("Seeding Demo Vehicles...")
        vehicles_data = [
            {
                "matriculation": "12345 | A | 15",
                "make_model": "Dacia Logan 1.5 dCi",
                "year": 2023,
                "current_mileage": 24500,
                "daily_rate_mad": Decimal("300.00"),
                "status": VehicleStatus.AVAILABLE,
            },
            {
                "matriculation": "67890 | B | 6",
                "make_model": "Renault Clio V Diesel",
                "year": 2024,
                "current_mileage": 12800,
                "daily_rate_mad": Decimal("350.00"),
                "status": VehicleStatus.AVAILABLE,
            },
            {
                "matriculation": "54321 | H | 26",
                "make_model": "Peugeot 208 GT Line",
                "year": 2023,
                "current_mileage": 31000,
                "daily_rate_mad": Decimal("400.00"),
                "status": VehicleStatus.RENTED,
            },
            {
                "matriculation": "99887 | D | 1",
                "make_model": "Hyundai Tucson 2.0 CRDi",
                "year": 2024,
                "current_mileage": 8500,
                "daily_rate_mad": Decimal("750.00"),
                "status": VehicleStatus.MAINTENANCE,
            },
            {
                "matriculation": "WW-123456",
                "make_model": "Volkswagen Golf 8 TDI",
                "year": 2025,
                "current_mileage": 1200,
                "daily_rate_mad": Decimal("600.00"),
                "status": VehicleStatus.RESERVED,
            },
        ]

        created_vehicles = []
        for v in vehicles_data:
            stmt = select(Vehicle).where(Vehicle.matriculation == v["matriculation"])
            res = await session.execute(stmt)
            existing = res.scalar_one_or_none()
            if not existing:
                veh_obj = Vehicle(**v)
                session.add(veh_obj)
                await session.flush()
                created_vehicles.append(veh_obj)
            else:
                created_vehicles.append(existing)

        # 4. Create Demo Maintenance Logs (Triggering 7-day alert)
        print("Seeding Maintenance Logs...")
        today = date.today()
        maint_data = [
            {
                "vehicle_id": created_vehicles[0].id,
                "type": MaintenanceType.VIDANGE,
                "date_performed": today - timedelta(days=90),
                "next_due_date": today + timedelta(days=3),  # Urgent warning in 3 days!
                "cost": Decimal("450.00"),
            },
            {
                "vehicle_id": created_vehicles[3].id,
                "type": MaintenanceType.VISITE_TECHNIQUE,
                "date_performed": today - timedelta(days=360),
                "next_due_date": today - timedelta(days=2),  # OVERDUE warning!
                "cost": Decimal("350.00"),
            },
        ]

        for m in maint_data:
            stmt = select(MaintenanceLog).where(
                MaintenanceLog.vehicle_id == m["vehicle_id"],
                MaintenanceLog.next_due_date == m["next_due_date"]
            )
            res = await session.execute(stmt)
            if not res.scalar_one_or_none():
                session.add(MaintenanceLog(**m))

        await session.commit()
        print("Database Seed Completed Successfully!")


if __name__ == "__main__":
    asyncio.run(seed_data())
