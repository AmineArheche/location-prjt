import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from app.services.maintenance_scheduler import run_maintenance_check_and_alerts

logger = logging.getLogger("app.core.scheduler")

scheduler = AsyncIOScheduler()


async def scheduled_maintenance_job():
    """Daily scheduled background job executing maintenance check & alerts."""
    logger.info("Executing daily background maintenance inspection job...")
    try:
        results = await run_maintenance_check_and_alerts()
        logger.info(f"Daily maintenance job finished: {results}")
    except Exception as e:
        logger.error(f"Error executing daily maintenance background job: {e}")


def start_scheduler():
    """Start APScheduler background job manager."""
    if not scheduler.running:
        # Schedule daily job at 08:00 AM (or every 24 hours)
        scheduler.add_job(
            scheduled_maintenance_job,
            trigger=CronTrigger(hour=8, minute=0),
            id="daily_maintenance_inspection",
            name="Daily Vehicle Maintenance Inspection & Alerts",
            replace_existing=True,
        )
        scheduler.start()
        logger.info("APScheduler started successfully for proactive maintenance alerts.")


def stop_scheduler():
    """Stop APScheduler background job manager."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("APScheduler stopped successfully.")
