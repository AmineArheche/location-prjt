import pytest
import pytest_asyncio
from datetime import date, timedelta, datetime, timezone
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select

from app.main import app
from app.core.database import AsyncSessionLocal, engine
from app.db.base_class import Base
from app.models.enums import VehicleStatus, MaintenanceType
from app.models.agency import Agency
from app.models.vehicle import Vehicle
from app.models.maintenance import MaintenanceLog
from app.services.maintenance_scheduler import run_maintenance_check_and_alerts


@pytest_asyncio.fixture(scope="session", autouse=True, loop_scope="session")
async def prepare_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield


@pytest.mark.asyncio(loop_scope="session")
async def test_notification_webhook_send_alerts_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {
            "recipient_phone": "+212 661 998877",
            "channel": "WHATSAPP",
            "custom_message": "Urgent maintenance alert test",
            "maintenance_items": [
                {
                    "vehicle_id": "00000000-0000-0000-0000-000000000001",
                    "matriculation": "12345 | A | 15",
                    "make_model": "Dacia Logan",
                    "maintenance_type": "VIDANGE",
                    "next_due_date": "2026-08-12",
                    "days_until_due": 2,
                }
            ],
        }

        response = await ac.post("/api/v1/notifications/send-alerts", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "DELIVERED"
        assert data["channel"] == "WHATSAPP"
        assert data["recipient_phone"] == "+212 661 998877"
        assert data["items_count"] == 1
        assert data["message_id"].startswith("MSG-")


@pytest.mark.asyncio(loop_scope="session")
async def test_maintenance_scheduler_job_and_vehicle_flagging():
    today = date.today()
    async with AsyncSessionLocal() as session:
        agency = Agency(
            name="Tangier Express Agency",
            city="Tangier",
            phone="+212 539 887766",
            rc_number="RC-112233",
            patente_number="PAT-445566",
        )
        session.add(agency)
        await session.flush()

        vehicle1 = Vehicle(
            agency_id=agency.id,
            matriculation="55555 | A | 1",
            make_model="Renault Clio 5",
            year=2024,
            current_mileage=12000,
            daily_rate_mad=350.0,
            status=VehicleStatus.AVAILABLE,
        )
        session.add(vehicle1)
        await session.flush()

        # Maintenance due in 2 days (Trigger <= 3 days rule)
        maint1 = MaintenanceLog(
            vehicle_id=vehicle1.id,
            type=MaintenanceType.VIDANGE,
            date_performed=today - timedelta(days=90),
            next_due_date=today + timedelta(days=2),
            cost=500.0,
        )
        session.add(maint1)

        # Maintenance due in 30 days (Not triggered)
        vehicle2 = Vehicle(
            agency_id=agency.id,
            matriculation="66666 | B | 1",
            make_model="Peugeot 208",
            year=2024,
            current_mileage=5000,
            daily_rate_mad=400.0,
            status=VehicleStatus.AVAILABLE,
        )
        session.add(vehicle2)
        await session.flush()

        maint2 = MaintenanceLog(
            vehicle_id=vehicle2.id,
            type=MaintenanceType.VISITE_TECHNIQUE,
            date_performed=today - timedelta(days=330),
            next_due_date=today + timedelta(days=30),
            cost=400.0,
        )
        session.add(maint2)
        await session.commit()

        v1_id = vehicle1.id
        v2_id = vehicle2.id

    # Run maintenance check service
    async with AsyncSessionLocal() as session:
        results = await run_maintenance_check_and_alerts(session)
        assert results["flagged_vehicles"] >= 1
        assert results["dispatched_notifications"] >= 1

    # Verify vehicle1 status was updated to MAINTENANCE
    async with AsyncSessionLocal() as session:
        res1 = await session.execute(select(Vehicle).where(Vehicle.id == v1_id))
        v1_updated = res1.scalar_one()
        assert v1_updated.status == VehicleStatus.MAINTENANCE

        res2 = await session.execute(select(Vehicle).where(Vehicle.id == v2_id))
        v2_updated = res2.scalar_one()
        assert v2_updated.status == VehicleStatus.AVAILABLE
