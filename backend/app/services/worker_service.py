import logging
from typing import Optional, List, Tuple
from app.models.domain import Worker, ActivationStep
from app.repositories.worker_repo import WorkerRepository
from app.repositories.user_repo import UserRepository
from app.repositories.analytics_repo import AnalyticsRepository
from app.models.domain import AnalyticsEventType

logger = logging.getLogger("homehelp.service.worker")


class WorkerService:
    def __init__(self):
        self.worker_repo = WorkerRepository()
        self.user_repo = UserRepository()
        self.analytics_repo = AnalyticsRepository()

    def register_worker(
        self,
        user_id: str,
        name: str,
        monthly_salary: float,
        role: str = "Domestic Worker",
        working_days_per_month: int = 26,
        weekly_off: str = "Sunday",
    ) -> Tuple[Optional[Worker], str]:
        # Check duplicate
        existing = self.worker_repo.find_by_name(user_id, name)
        if existing:
            return None, f"Worker '{existing.name}' is already registered with salary ₹{existing.monthly_salary:,.0f}."

        worker = self.worker_repo.create(
            user_id=user_id,
            name=name,
            role=role,
            monthly_salary=monthly_salary,
            working_days_per_month=working_days_per_month,
            weekly_off=weekly_off,
        )

        # Update activation step if user registered their first worker
        user = self.user_repo.get_by_id(user_id)
        if user and user.activation_step == ActivationStep.STARTED_CHAT.value:
            self.user_repo.update_activation(user_id, ActivationStep.REGISTERED_FIRST_WORKER)
            self.analytics_repo.log(
                AnalyticsEventType.USER_ACTIVATED, user_id=user_id, metadata={"worker_id": worker.id}
            )

        self.analytics_repo.log(
            AnalyticsEventType.WORKER_REGISTERED, user_id=user_id, metadata={"worker_name": name, "salary": monthly_salary}
        )

        msg = (
            f"✅ Registered worker *{worker.name}* ({worker.role})\n"
            f"💰 Monthly Salary: ₹{worker.monthly_salary:,.0f}\n"
            f"📅 Working Days: {worker.working_days_per_month} days/month\n"
            f"🏖️ Weekly Off: {worker.weekly_off}"
        )
        return worker, msg

    def remove_worker(self, user_id: str, name_or_id: str) -> Tuple[bool, str]:
        worker = self.worker_repo.find_by_name(user_id, name_or_id)
        if not worker:
            worker = self.worker_repo.get_by_id(name_or_id)

        if not worker:
            return False, f"⚠️ Worker '{name_or_id}' not found in your registered list."

        self.worker_repo.deactivate(worker.id)
        self.analytics_repo.log(
            AnalyticsEventType.WORKER_REMOVED, user_id=user_id, metadata={"worker_id": worker.id, "worker_name": worker.name}
        )

        return True, f"🗑️ Worker *{worker.name}* has been removed from active tracking."

    def update_salary(self, user_id: str, name_or_id: str, new_salary: float) -> Tuple[Optional[Worker], str]:
        worker = self.worker_repo.find_by_name(user_id, name_or_id)
        if not worker:
            worker = self.worker_repo.get_by_id(name_or_id)

        if not worker:
            return None, f"⚠️ Worker '{name_or_id}' not found."

        updated = self.worker_repo.update(worker.id, {"monthly_salary": float(new_salary)})
        return updated, f"✅ Updated salary for *{worker.name}* to ₹{new_salary:,.0f} per month."

    def get_worker(self, user_id: str, name_or_id: str) -> Optional[Worker]:
        worker = self.worker_repo.find_by_name(user_id, name_or_id)
        if not worker:
            worker = self.worker_repo.get_by_id(name_or_id)
        return worker

    def list_workers(self, user_id: str) -> List[Worker]:
        return self.worker_repo.get_all_by_user(user_id, active_only=True)
