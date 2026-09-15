import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, status
from app.schemas.notifications import NotificationAlertPayload, NotificationResponse

router = APIRouter()


@router.post("/send-alerts", response_model=NotificationResponse, status_code=status.HTTP_200_OK)
async def send_maintenance_notifications_webhook(payload: NotificationAlertPayload):
    """
    Webhook endpoint to route SMS or WhatsApp proactive maintenance notifications
    (via Twilio or local gateway) directly to AGENCY_MANAGER phone numbers.
    """
    msg_id = f"MSG-{uuid.uuid4().hex[:10].upper()}"
    now_utc = datetime.now(timezone.utc)

    # Log dispatch details (Simulation of Twilio / WhatsApp Business API / Local Gateway API call)
    channel_name = payload.channel.value
    recipient = payload.recipient_phone
    count = len(payload.maintenance_items)
    
    print(f"[{now_utc.isoformat()}] DISPATCHING {channel_name} NOTIFICATION via Gateway to {recipient} (MsgID: {msg_id})")
    print(f"  Summary: {count} vehicle maintenance item(s) due or overdue.")
    for item in payload.maintenance_items:
        print(f"  - Vehicle {item.matriculation} ({item.make_model}): {item.maintenance_type.value} due on {item.next_due_date} (in {item.days_until_due} days)")

    return NotificationResponse(
        status="DELIVERED",
        message_id=msg_id,
        channel=payload.channel,
        recipient_phone=recipient,
        items_count=count,
        delivered_at=now_utc,
        gateway_provider="Twilio / Local Moroccan Gateway",
    )
