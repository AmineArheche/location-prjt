import pytest
import pytest_asyncio
import asyncio
from datetime import datetime, timedelta, timezone
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select

from app.main import app
from app.core.database import AsyncSessionLocal, engine
from app.db.base_class import Base
from app.core.security import hash_password, create_access_token
from app.models.enums import UserRole, SubscriptionPlan, VehicleStatus
from app.models.agency import Agency
from app.models.subscription import Subscription
from app.models.user import User
from app.models.vehicle import Vehicle


@pytest_asyncio.fixture(scope="session", autouse=True, loop_scope="session")
async def prepare_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield



@pytest.mark.asyncio(loop_scope="session")
async def test_superadmin_provision_agency_success():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        async with AsyncSessionLocal() as session:
            # Create SuperAdmin
            sa_user = User(
                email="test_superadmin@platform.com",
                password_hash=hash_password("supersecret123"),
                role=UserRole.SUPERADMIN,
                is_active=True,
            )
            session.add(sa_user)
            await session.commit()
            await session.refresh(sa_user)
            sa_id = sa_user.id

        sa_token = create_access_token(subject=sa_id)
        headers = {"Authorization": f"Bearer {sa_token}"}

        provision_payload = {
            "name": "Marrakech Royal Cars",
            "city": "Marrakech",
            "phone": "+212 524 998877",
            "rc_number": "RC-990011",
            "patente_number": "PAT-887766",
            "logo_url": "https://example.com/royal.png",
            "plan_name": "STARTER",
            "duration_months": 6,
            "max_vehicles": 2,  # Custom max limit for testing quota
            "payment_notes": "Paid 1200 MAD via CIH Bank Transfer",
            "manager_email": "manager@royalcar.ma",
            "manager_agency_location": "Marrakech Airport Terminal",
        }

        response = await ac.post(
            "/api/v1/superadmin/agencies/provision",
            json=provision_payload,
            headers=headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert "agency" in data
        assert data["agency"]["name"] == "Marrakech Royal Cars"
        assert data["agency"]["rc_number"] == "RC-990011"
        assert "subscription" in data
        assert data["subscription"]["plan_name"] == "STARTER"
        assert data["subscription"]["max_vehicles"] == 2
        assert data["subscription"]["is_active"] is True
        assert data["subscription"]["payment_notes"] == "Paid 1200 MAD via CIH Bank Transfer"
        assert "manager_credentials" in data
        assert data["manager_credentials"]["email"] == "manager@royalcar.ma"
        assert len(data["manager_credentials"]["temporary_password"]) > 0
        assert data["login_url"] == "/login"

        # Verify manager user can login with returned credentials
        login_res = await ac.post(
            "/api/v1/auth/login",
            data={
                "username": data["manager_credentials"]["email"],
                "password": data["manager_credentials"]["temporary_password"],
            },
        )
        assert login_res.status_code == 200
        assert "access_token" in login_res.json()


@pytest.mark.asyncio(loop_scope="session")
async def test_vehicle_creation_quota_limit():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Get manager created in previous step
        async with AsyncSessionLocal() as session:
            stmt = select(User).where(User.email == "manager@royalcar.ma")
            res = await session.execute(stmt)
            manager = res.scalar_one()
            manager_id = manager.id

        mgr_token = create_access_token(subject=manager_id)
        headers = {"Authorization": f"Bearer {mgr_token}"}

        # Create Vehicle 1 (Allowed)
        v1_payload = {
            "matriculation": "11111 | A | 26",
            "make_model": "Dacia Sandero",
            "year": 2024,
            "current_mileage": 10000,
            "daily_rate_mad": 250.0,
            "status": "AVAILABLE",
        }
        res1 = await ac.post("/api/v1/vehicles/", json=v1_payload, headers=headers)
        assert res1.status_code == 201

        # Create Vehicle 2 (Allowed, reaching max_vehicles=2 limit)
        v2_payload = {
            "matriculation": "22222 | B | 26",
            "make_model": "Renault Clio",
            "year": 2024,
            "current_mileage": 5000,
            "daily_rate_mad": 300.0,
            "status": "AVAILABLE",
        }
        res2 = await ac.post("/api/v1/vehicles/", json=v2_payload, headers=headers)
        assert res2.status_code == 201

        # Create Vehicle 3 (Blocked - Limit Reached)
        v3_payload = {
            "matriculation": "33333 | C | 26",
            "make_model": "Peugeot 208",
            "year": 2025,
            "current_mileage": 1000,
            "daily_rate_mad": 350.0,
            "status": "AVAILABLE",
        }
        res3 = await ac.post("/api/v1/vehicles/", json=v3_payload, headers=headers)
        assert res3.status_code == 403
        assert "Vehicle limit reached for subscription plan" in res3.json()["detail"]


@pytest.mark.asyncio(loop_scope="session")
async def test_subscription_expiration_returns_402():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Expire subscription for Marrakech Royal Cars
        async with AsyncSessionLocal() as session:
            stmt = select(User).where(User.email == "manager@royalcar.ma")
            res = await session.execute(stmt)
            manager = res.scalar_one()
            manager_id = manager.id

            sub_stmt = select(Subscription).where(Subscription.agency_id == manager.agency_id)
            sub_res = await session.execute(sub_stmt)
            subscription = sub_res.scalar_one()

            # Set end_date to yesterday in UTC
            subscription.end_date = datetime.now(timezone.utc) - timedelta(days=1)
            await session.commit()

        mgr_token = create_access_token(subject=manager_id)
        headers = {"Authorization": f"Bearer {mgr_token}"}

        # Attempt API call on vehicles list
        res = await ac.get("/api/v1/vehicles/", headers=headers)
        assert res.status_code == 402
        assert res.json()["detail"] == "Subscription expired. Please contact platform support."

        # SuperAdmin calling should NOT be blocked
        stmt_sa = select(User).where(User.role == UserRole.SUPERADMIN)
        async with AsyncSessionLocal() as session:
            sa_res = await session.execute(stmt_sa)
            sa_user = sa_res.scalars().first()

        sa_token = create_access_token(subject=sa_user.id)
        sa_headers = {"Authorization": f"Bearer {sa_token}"}

        sa_res_veh = await ac.get("/api/v1/vehicles/", headers=sa_headers)
        assert sa_res_veh.status_code == 200
