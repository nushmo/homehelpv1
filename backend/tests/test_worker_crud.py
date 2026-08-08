from app.services.worker_service import WorkerService
from app.repositories.user_repo import UserRepository
from app.database.client import db_store


def test_worker_crud_flow():
    db_store.clear()
    user_repo = UserRepository()
    worker_service = WorkerService()

    user = user_repo.create("+919876543210", display_name="Vikas")

    # 1. Register worker
    w1, msg1 = worker_service.register_worker(
        user_id=user.id,
        name="Sunita",
        monthly_salary=9000.0,
        role="Maid",
        weekly_off="Sunday",
    )
    assert w1 is not None
    assert w1.name == "Sunita"
    assert "Registered worker" in msg1

    # 2. Prevent Duplicate worker
    w_dup, msg_dup = worker_service.register_worker(
        user_id=user.id,
        name="Sunita",
        monthly_salary=9000.0,
    )
    assert w_dup is None
    assert "already registered" in msg_dup

    # 3. Update worker salary
    updated, msg_up = worker_service.update_salary(user.id, "Sunita", 9500.0)
    assert updated is not None
    assert updated.monthly_salary == 9500.0

    # 4. List workers
    workers = worker_service.list_workers(user.id)
    assert len(workers) == 1
    assert workers[0].monthly_salary == 9500.0

    # 5. Remove worker
    success, msg_rem = worker_service.remove_worker(user.id, "Sunita")
    assert success is True

    # 6. List workers should now be empty
    active_workers = worker_service.list_workers(user.id)
    assert len(active_workers) == 0
