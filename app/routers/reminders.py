from fastapi import APIRouter
from app.services.reminder import process_due_reminders, schedule_reminders
from pydantic import BaseModel

router = APIRouter()

class ScheduleRequest(BaseModel):
    document_id: str
    doc_type: str
    deadlines: list
    user_phone: str

@router.post("/reminders/schedule")
def schedule(request: ScheduleRequest):
    schedule_reminders(
        document_id=request.document_id,
        doc_type=request.doc_type,
        deadlines=request.deadlines,
        user_phone=request.user_phone
    )
    return {"status": "reminders scheduled"}

@router.post("/reminders/process")
def process():
    process_due_reminders()
    return {"status": "processed"}