from datetime import date
from app.models.domain import Worker, Event, EventType
from app.salary.engine import SalaryEngine


def test_daily_rate_calculation():
    # 9000 salary / 26 days = 346.15
    rate = SalaryEngine.calculate_daily_rate(9000, 26)
    assert rate == 346.15

    # 12000 salary / 30 days = 400.00
    rate30 = SalaryEngine.calculate_daily_rate(12000, 30)
    assert rate30 == 400.00


def test_salary_summary_calculation():
    worker = Worker(
        id="w-101",
        user_id="u-202",
        name="Sunita",
        role="Domestic Worker",
        monthly_salary=9000.0,
        working_days_per_month=26,
        weekly_off="Sunday",
    )

    daily_rate = 346.15

    events = [
        Event(id="e-1", worker_id="w-101", event_type=EventType.ABSENT, event_date=date(2026, 8, 5)),
        Event(id="e-2", worker_id="w-101", event_type=EventType.HALF_DAY, event_date=date(2026, 8, 10)),
        Event(id="e-3", worker_id="w-101", event_type=EventType.ADVANCE, event_date=date(2026, 8, 15), amount=500.0),
        Event(id="e-4", worker_id="w-101", event_type=EventType.BONUS, event_date=date(2026, 8, 20), amount=1000.0),
    ]

    summary = SalaryEngine.generate_summary(worker, events, 2026, 8)

    assert summary.absent_days == 1
    assert summary.half_days == 1
    # Total deductions: 1 * 346.15 + 1 * 173.07 = 519.22
    assert summary.total_deductions == 519.22
    assert summary.total_advances == 500.0
    assert summary.total_bonuses == 1000.0
    # Net payable: 9000 - 519.22 - 500 + 1000 = 8980.78
    assert summary.net_payable == 8980.78
    assert summary.payment_status == "PENDING"
