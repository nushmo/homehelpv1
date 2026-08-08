from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.event_service import EventService
from app.models.domain import EventType

router = APIRouter(prefix="/events", tags=["Events"])
event_service = EventService()


class CreateEventRequest(BaseModel):
    user_id: str
    worker_name_or_id: str
    event_type: EventType
    date_str: Optional[str] = "today"
    amount: Optional[float] = 0.0
    notes: Optional[str] = None


@router.post("")
def record_event(req: CreateEventRequest):
    """Manually record attendance or money event via REST API."""
    event, msg = event_service.record_event(
        user_id=req.user_id,
        event_type=req.event_type,
        worker_name=req.worker_name_or_id,
        date_str=req.date_str or "today",
        amount=req.amount or 0.0,
        notes=req.notes,
    )
    if not event:
        raise HTTPException(status_code=400, detail=msg)
    return {"status": "success", "message": msg, "event": event}
