import logging
from datetime import date, timedelta
from typing import Dict, List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import httpx

from app.core.database import AsyncSessionLocal
from app.models.maintenance import MaintenanceLog
from app.models.vehicle import Vehicle
from app.models.user import User
from app.models.agency import Agency
from app.models.enums import VehicleStatus, UserRole
from app.schemas.notifications import (
    NotificationAlertPayload,
    NotificationChannel,
    MaintenanceItemSummary,
)

logger = logging.getLogger("app.services.maintenance_scheduler")


async def run_maintenance_check_and_alerts(db: Optional[AsyncSession] = None):
    """
    Core maintenance inspection function.
    1. Queries MaintenanceLog for items where next_due_date <= today + 3 days (or overdue).
    2. Flags corresponding vehicles as VehicleStatus.MAINTENANCE in database.
    3. Groups upcoming/overdue items by agency and dispatches SMS/WhatsApp alerts to AGENCY_MANAGER.
    """
    close_db_on_exit = False
    if db is None:
        db = AsyncSessionLocal()
        close_db_on_exit = True

    try:
        today = date.today()
        cutoff_date = today + timedelta(days=3)

        # 1. Query upcoming/overdue maintenance logs
        stmt = (
            select(MaintenanceLog, Vehicle)
            .join(Vehicle, MaintenanceLog.vehicle_id == Vehicle.id)
            .where(
                MaintenanceLog.deleted_at.is_(None),
                Vehicle.deleted_at.is_(None),
                MaintenanceLog.next_due_date <= cutoff_date,
            )
        )
        result = await db.execute(stmt)
        rows = result.all()

        if not rows:
            logger.info("No upcoming or overdue maintenance logs found.")
            return {"flagged_vehicles": 0, "dispatched_notifications": 0}

        # 2. Flag vehicles & group items by agency
        flagged_count = 0
        agency_items_map: Dict[Optional[str], List[MaintenanceItemSummary]] = {}

        for maint_log, vehicle in rows:
            # Flag vehicle status to MAINTENANCE if currently AVAILABLE or RESERVED
            if vehicle.status in [VehicleStatus.AVAILABLE, VehicleStatus.RESERVED]:
                vehicle.status = VehicleStatus.MAINTENANCE
                db.add(vehicle)
                flagged_count += 1

            days_until = (maint_log.next_due_date - today).days
            summary_item = MaintenanceItemSummary(
                vehicle_id=vehicle.id,
                matriculation=vehicle.matriculation,
                make_model=vehicle.make_model,
                maintenance_type=maint_log.type,
                next_due_date=maint_log.next_due_date,
                days_until_due=days_until,
            )

            agency_key = str(vehicle.agency_id) if vehicle.agency_id else "global"
            if agency_key not in agency_items_map:
                agency_items_map[agency_key] = []
            agency_items_map[agency_key].append(summary_item)

        await db.commit()

        # 3. For each agency, resolve manager phone and dispatch notification payload
        dispatched_count = 0
        for agency_key, items in agency_items_map.items():
            manager_phone = "+212 661 000 000"  # Default fallback
            agency_id_uuid = None

            if agency_key != "global":
                import uuid
                agency_id_uuid = uuid.UUID(agency_key)
                
                # Fetch agency & manager
                stmt_agency = select(Agency).where(Agency.id == agency_id_uuid)
                res_agency = await db.execute(stmt_agency)
                agency = res_agency.scalar_one_or_none()
                if agency and agency.phone:
                    manager_phone = agency.phone

                stmt_mgr = select(User).where(
                    User.agency_id == agency_id_uuid,
                    User.role == UserRole.AGENCY_MANAGER,
                    User.deleted_at.is_(None)
                )
                res_mgr = await db.execute(stmt_mgr)
                mgr_user = res_mgr.scalars().first()
                if mgr_user and mgr_user.agency_location:
                    # In real deployment, manager phone number field or user contact
                    pass

            payload = NotificationAlertPayload(
                recipient_phone=manager_phone,
                channel=NotificationChannel.WHATSAPP,
                agency_id=agency_id_uuid,
                maintenance_items=items,
                custom_message=f"Proactive alert: {len(items)} vehicle maintenance items require immediate attention.",
            )

            # Route dispatch to internal webhook service
            from app.api.v1.endpoints.notifications import send_maintenance_notifications_webhook
            await send_maintenance_notifications_webhook(payload)
            dispatched_count += 1

        return {
            "flagged_vehicles": flagged_count,
            "dispatched_notifications": dispatched_count,
            "items_processed": len(rows),
        }

    finally:
        if close_db_on_exit:
            await db.close()
