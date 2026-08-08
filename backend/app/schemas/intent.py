from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class IntentType(str, Enum):
    REGISTER_WORKER = "REGISTER_WORKER"
    REMOVE_WORKER = "REMOVE_WORKER"
    UPDATE_WORKER = "UPDATE_WORKER"
    ABSENT = "ABSENT"
    HALF_DAY = "HALF_DAY"
    PLANNED_LEAVE = "PLANNED_LEAVE"
    ADVANCE = "ADVANCE"
    BONUS = "BONUS"
    PAYMENT = "PAYMENT"
    GENERATE_PAYMENT = "GENERATE_PAYMENT"
    HELP = "HELP"
    UNKNOWN = "UNKNOWN"


class ParsedIntent(BaseModel):
    intent: IntentType = IntentType.UNKNOWN
    worker_name: Optional[str] = Field(
        default=None, description="Name of domestic worker, e.g., Sunita"
    )
    role: Optional[str] = Field(
        default=None, description="Role of worker, e.g., maid, cook, driver"
    )
    monthly_salary: Optional[float] = Field(
        default=None, description="Monthly fixed salary amount in numeric form"
    )
    weekly_off: Optional[str] = Field(
        default=None, description="Day of weekly off, e.g., Sunday"
    )
    working_days_per_month: Optional[int] = Field(
        default=26, description="Total expected working days per month"
    )
    amount: Optional[float] = Field(
        default=None, description="Monetary amount for advance, bonus, or payment"
    )
    date: Optional[str] = Field(
        default="today",
        description="Date of event: 'today', 'yesterday', 'tomorrow', or 'YYYY-MM-DD'",
    )
    notes: Optional[str] = Field(
        default=None, description="Any additional context or notes"
    )
    clarification_needed: Optional[str] = Field(
        default=None,
        description="Prompt to send back if essential information is missing",
    )
