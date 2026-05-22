from twilio.rest import Client
from app.config import settings
from sqlalchemy import text
from app.database import get_db
from datetime import datetime, timedelta
import uuid

def send_whatsapp_reminder(to_phone: str, message: str) -> bool:
    try:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        client.messages.create(
            from_=settings.TWILIO_WHATSAPP_FROM,
            to=f"whatsapp:{to_phone}",
            body=message
        )
        print(f"✅ WhatsApp sent to {to_phone}")
        return True
    except Exception as e:
        print(f"❌ WhatsApp failed: {e}")
        return False

def schedule_reminders(document_id: str, doc_type: str, deadlines: list, user_phone: str):
    db = next(get_db())
    try:
        for deadline in deadlines:
            date_str = deadline.get("date")
            description = deadline.get("description", "")
            if not date_str:
                continue
            try:
                deadline_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except:
                continue
            for days_before in [7, 3, 1]:
                send_at = datetime.combine(
                    deadline_date - timedelta(days=days_before),
                    datetime.min.time().replace(hour=9)
                )
                if send_at < datetime.now():
                    continue
                db.execute(text("""
                    INSERT INTO reminders (
                        id, document_id, deadline_date,
                        reminder_type, delivery_channel,
                        send_at, sent
                    ) VALUES (
                        :id, :doc_id, :deadline_date,
                        :reminder_type, :channel,
                        :send_at, false
                    )
                """), {
                    "id": str(uuid.uuid4()),
                    "doc_id": document_id,
                    "deadline_date": deadline_date,
                    "reminder_type": f"{days_before}_days_before",
                    "channel": "whatsapp",
                    "send_at": send_at
                })
        db.commit()
        print(f"📅 Reminders scheduled for {len(deadlines)} deadlines")
    except Exception as e:
        print(f"❌ Schedule failed: {e}")
        db.rollback()

def process_due_reminders():
    db = next(get_db())
    try:
        due = db.execute(text("""
            SELECT r.id, r.document_id, r.deadline_date,
                   r.reminder_type, d.doc_type
            FROM reminders r
            JOIN documents d ON d.id = r.document_id
            WHERE r.sent = false
            AND r.send_at <= NOW()
            AND r.delivery_channel = 'whatsapp'
        """)).fetchall()

        print(f"📬 Found {len(due)} due reminders")

        for reminder in due:
            days = reminder.reminder_type.replace("_days_before", "").replace("_", " ")
            message = (
                f"🇮🇪 Bureaucracy Destroyer Reminder\n\n"
                f"You have a deadline coming up in {days}!\n\n"
                f"Document: {reminder.doc_type.replace('_', ' ').title()}\n"
                f"Deadline: {reminder.deadline_date.strftime('%d %B %Y')}\n\n"
                f"Visit bureaucracy-destroyer.vercel.app to review your action steps."
            )
            sent = send_whatsapp_reminder("+353870305924", message)
            if sent:
                db.execute(text("""
                    UPDATE reminders SET sent = true, sent_at = NOW()
                    WHERE id = :id
                """), {"id": str(reminder.id)})
                db.commit()
    except Exception as e:
        print(f"❌ Process reminders failed: {e}")
        db.rollback()