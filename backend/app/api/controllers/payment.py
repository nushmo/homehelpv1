from datetime import date
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.worker_service import WorkerService
from app.services.reply_service import ReplyService
from app.repositories.event_repo import EventRepository
from app.salary.engine import SalaryEngine

router = APIRouter(tags=["Payment Summary"])

worker_service = WorkerService()
event_repo = EventRepository()


class GeneratePaymentRequest(BaseModel):
    user_id: str
    worker_name_or_id: Optional[str] = None
    year: Optional[int] = None
    month: Optional[int] = None


@router.post("/generate-payment")
def generate_payment_summary(req: GeneratePaymentRequest):
    """Generate salary summary for a worker."""
    workers = worker_service.list_workers(req.user_id)
    if not workers:
        raise HTTPException(status_code=400, detail="User has no registered workers")

    target_worker = None
    if req.worker_name_or_id:
        target_worker = worker_service.get_worker(req.user_id, req.worker_name_or_id)

    if not target_worker:
        if len(workers) == 1:
            target_worker = workers[0]
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Multiple workers found. Please specify worker_name_or_id: {[w.name for w in workers]}"
            )

    today = date.today()
    target_year = req.year or today.year
    target_month = req.month or today.month

    events = event_repo.get_events_for_month(target_worker.id, target_year, target_month)
    summary = SalaryEngine.generate_summary(target_worker, events, target_year, target_month)
    formatted_reply = ReplyService.format_payment_summary(summary)

    return {
        "status": "success",
        "summary": summary,
        "whatsapp_formatted_text": formatted_reply,
    }
