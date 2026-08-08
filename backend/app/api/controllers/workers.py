from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from app.services.worker_service import WorkerService
from app.repositories.user_repo import UserRepository

router = APIRouter(prefix="/workers", tags=["Workers"])

worker_service = WorkerService()
user_repo = UserRepository()


class CreateWorkerRequest(BaseModel):
    user_id: str
    name: str
    monthly_salary: float = Field(gt=0)
    role: str = "Domestic Worker"
    working_days_per_month: int = 26
    weekly_off: str = "Sunday"


class UpdateWorkerRequest(BaseModel):
    monthly_salary: Optional[float] = None
    role: Optional[str] = None
    working_days_per_month: Optional[int] = None
    weekly_off: Optional[str] = None


@router.get("")
def list_workers(
    user_id: Optional[str] = Query(None),
    phone_number: Optional[str] = Query(None),
):
    """List active workers for a user."""
    target_user_id = user_id
    if not target_user_id and phone_number:
        user = user_repo.get_by_phone(phone_number)
        if user:
            target_user_id = user.id

    if not target_user_id:
        raise HTTPException(status_code=400, detail="Must provide user_id or phone_number parameter")

    workers = worker_service.list_workers(target_user_id)
    return {"status": "success", "count": len(workers), "workers": workers}


@router.post("")
def create_worker(req: CreateWorkerRequest):
    """Register a new domestic worker."""
    worker, msg = worker_service.register_worker(
        user_id=req.user_id,
        name=req.name,
        monthly_salary=req.monthly_salary,
        role=req.role,
        working_days_per_month=req.working_days_per_month,
        weekly_off=req.weekly_off,
    )
    if not worker:
        raise HTTPException(status_code=400, detail=msg)
    return {"status": "success", "message": msg, "worker": worker}


@router.put("/{worker_id}")
def update_worker(worker_id: str, req: UpdateWorkerRequest):
    """Update worker salary or properties."""
    updates = {k: v for k, v in req.model_dump().items() if v is not None}
    if not updates:
        raise HTTPException(status_code=400, detail="No fields provided for update")

    updated = worker_service.worker_repo.update(worker_id, updates)
    if not updated:
        raise HTTPException(status_code=404, detail="Worker not found")
    return {"status": "success", "worker": updated}


@router.delete("/{worker_id}")
def delete_worker(worker_id: str, user_id: str = Query(...)):
    """Deactivate a worker."""
    success, msg = worker_service.remove_worker(user_id, worker_id)
    if not success:
        raise HTTPException(status_code=404, detail=msg)
    return {"status": "success", "message": msg}
