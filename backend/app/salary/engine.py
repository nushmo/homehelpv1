import math
from datetime import date
from typing import List, Optional
from pydantic import BaseModel, Field
from app.models.domain import Worker, Event, EventType


class SalarySummary(BaseModel):
    month_name: str
    year: int
    worker_name: str
    role: str
    monthly_salary: float
    working_days: int
    daily_rate: float
    absent_days: int = 0
    half_days: int = 0
    planned_leave_days: int = 0
    total_deductions: float = 0.0
    total_advances: float = 0.0
    total_bonuses: float = 0.0
    total_paid: float = 0.0
    net_payable: float = 0.0
    events_count: int = 0
    recent_events_summary: List[str] = Field(default_factory=list)
    payment_status: str = "PENDING"  # PENDING, PARTIALLY_PAID, PAID


class SalaryEngine:
    """100% Deterministic Salary Engine. Never uses AI for calculations."""

    @staticmethod
    def calculate_daily_rate(monthly_salary: float, working_days: int) -> float:
        if working_days <= 0:
            working_days = 26
        return round(monthly_salary / working_days, 2)

    @classmethod
    def generate_summary(
        cls,
        worker: Worker,
        events: List[Event],
        year: int,
        month: int,
    ) -> SalarySummary:
        daily_rate = cls.calculate_daily_rate(
            worker.monthly_salary, worker.working_days_per_month
        )

        absent_days = 0
        half_days = 0
        planned_leave_days = 0
        total_advances = 0.0
        total_bonuses = 0.0
        total_paid = 0.0
        recent_events = []

        # Process each event
        for ev in events:
            ev_type = (
                ev.event_type.value
                if isinstance(ev.event_type, EventType)
                else str(ev.event_type)
            )

            if ev_type == EventType.ABSENT.value:
                absent_days += 1
                recent_events.append(f"• {ev.event_date}: Absent (-₹{daily_rate:.2f})")
            elif ev_type == EventType.HALF_DAY.value:
                half_days += 1
                half_deduction = round(0.5 * daily_rate, 2)
                recent_events.append(
                    f"• {ev.event_date}: Half Day (-₹{half_deduction:.2f})"
                )
            elif ev_type == EventType.PLANNED_LEAVE.value:
                planned_leave_days += 1
                recent_events.append(
                    f"• {ev.event_date}: Planned Leave (-₹{daily_rate:.2f})"
                )
            elif ev_type == EventType.ADVANCE.value:
                total_advances += ev.amount
                recent_events.append(f"• {ev.event_date}: Advance ₹{ev.amount:.2f}")
            elif ev_type == EventType.BONUS.value:
                total_bonuses += ev.amount
                recent_events.append(f"• {ev.event_date}: Bonus +₹{ev.amount:.2f}")
            elif ev_type == EventType.PAYMENT.value:
                total_paid += ev.amount
                recent_events.append(f"• {ev.event_date}: Paid ₹{ev.amount:.2f}")

        # Deductions calculation
        # Absent = 1 * daily rate, Planned Leave = 1 * daily rate, Half Day = round(0.5 * daily rate, 2)
        half_day_rate = round(0.5 * daily_rate, 2)
        total_deductions = round(
            (absent_days + planned_leave_days) * daily_rate
            + (half_days * half_day_rate),
            2,
        )

        net_payable = round(
            worker.monthly_salary - total_deductions - total_advances + total_bonuses - total_paid,
            2,
        )

        if net_payable <= 0 and (worker.monthly_salary > 0 or total_paid > 0):
            payment_status = "SETTLED / PAID"
        elif total_paid > 0:
            payment_status = "PARTIALLY PAID"
        else:
            payment_status = "PENDING"

        month_date = date(year, month, 1)
        month_name = month_date.strftime("%B %Y")

        return SalarySummary(
            month_name=month_name,
            year=year,
            worker_name=worker.name,
            role=worker.role,
            monthly_salary=round(worker.monthly_salary, 2),
            working_days=worker.working_days_per_month,
            daily_rate=daily_rate,
            absent_days=absent_days,
            half_days=half_days,
            planned_leave_days=planned_leave_days,
            total_deductions=total_deductions,
            total_advances=round(total_advances, 2),
            total_bonuses=round(total_bonuses, 2),
            total_paid=round(total_paid, 2),
            net_payable=net_payable,
            events_count=len(events),
            recent_events_summary=recent_events[:10],
            payment_status=payment_status,
        )
