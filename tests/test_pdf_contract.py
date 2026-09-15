import pytest
import pytest_asyncio
import uuid
from datetime import datetime, timedelta, timezone
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select

from app.main import app
from app.core.database import AsyncSessionLocal, engine
from app.db.base_class import Base
from app.core.security import hash_password, create_access_token
from app.models.enums import UserRole, VehicleStatus, BookingStatus
from app.models.agency import Agency
from app.models.subscription import Subscription
from app.models.user import User
from app.models.customer import Customer
from app.models.vehicle import Vehicle
from app.models.booking import Booking


@pytest_asyncio.fixture(scope="session", autouse=True, loop_scope="session")
async def prepare_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield


@pytest.mark.asyncio(loop_scope="session")
async def test_generate_booking_contract_pdf_stream():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        async with AsyncSessionLocal() as session:
            # 1. Create Agency & Active Subscription
            agency = Agency(
                name="Casablanca Premium Rentals",
                city="Casablanca",
                phone="+212 522 112233",
                rc_number="RC-778899",
                patente_number="PAT-665544",
                logo_url="https://example.com/logo.png",
            )
            session.add(agency)
            await session.flush()

            sub = Subscription(
                agency_id=agency.id,
                plan_name="PRO",
                max_vehicles=30,
                start_date=datetime.now(timezone.utc),
                end_date=datetime.now(timezone.utc) + timedelta(days=365),
                is_active=True,
            )
            session.add(sub)

            # 2. Create User (Agent)
            user = User(
                email="pdf_agent@agency.ma",
                password_hash=hash_password("password123"),
                role=UserRole.AGENT,
                agency_id=agency.id,
                is_active=True,
            )
            session.add(user)
            await session.flush()

            # 3. Create Customer
            customer = Customer(
                agency_id=agency.id,
                full_name="Mehdi Benjelloun",
                phone_number="+212 661 998877",
                cin_or_passport="BK654321",
                driver_license_number="DL-776655",
                is_blacklisted=False,
            )
            session.add(customer)
            await session.flush()

            # 4. Create Vehicle
            vehicle = Vehicle(
                agency_id=agency.id,
                matriculation="98765 | A | 1",
                make_model="Peugeot 308 GT",
                year=2024,
                current_mileage=15200,
                daily_rate_mad=450.0,
                status=VehicleStatus.RENTED,
            )
            session.add(vehicle)
            await session.flush()

            # 5. Create Booking
            now = datetime.now(timezone.utc)
            booking = Booking(
                agency_id=agency.id,
                vehicle_id=vehicle.id,
                customer_id=customer.id,
                agent_id=user.id,
                start_datetime=now,
                end_datetime=now + timedelta(days=4),
                start_mileage=15200,
                total_price=1800.0,
                deposit_amount=3000.0,
                status=BookingStatus.ACTIVE,
            )
            session.add(booking)
            await session.commit()
            await session.refresh(booking)

            booking_id = booking.id
            user_id = user.id

        token = create_access_token(subject=user_id)
        headers = {"Authorization": f"Bearer {token}"}

        # Execute PDF request
        response = await ac.get(f"/api/v1/bookings/{booking_id}/pdf", headers=headers)

        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/pdf"
        assert f"contract_{booking_id}.pdf" in response.headers["Content-Disposition"]
        assert response.headers["Content-Disposition"].startswith("inline;")
        
        pdf_bytes = response.content
        assert len(pdf_bytes) > 5000  # Multi-page PDF binary payload size
        assert pdf_bytes.startswith(b"%PDF-")  # Valid PDF header magic bytes
