from datetime import datetime, date
from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class UserStatus(str, Enum):
    NEW = "NEW"
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class ActivationStep(str, Enum):
    STARTED_CHAT = "STARTED_CHAT"
    REGISTERED_FIRST_WORKER = "REGISTERED_FIRST_WORKER"
    LOGGED_FIRST_EVENT = "LOGGED_FIRST_EVENT"
    GENERATED_FIRST_PAYMENT = "GENERATED_FIRST_PAYMENT"
    RETURNING_USER = "RETURNING_USER"


class EventType(str, Enum):
    ABSENT = "ABSENT"
    HALF_DAY = "HALF_DAY"
    PLANNED_LEAVE = "PLANNED_LEAVE"
    ADVANCE = "ADVANCE"
    BONUS = "BONUS"
    PAYMENT = "PAYMENT"


class AnalyticsEventType(str, Enum):
    USER_STARTED_CHAT = "USER_STARTED_CHAT"
    USER_ACTIVATED = "USER_ACTIVATED"
    WORKER_REGISTERED = "WORKER_REGISTERED"
    WORKER_REMOVED = "WORKER_REMOVED"
    EVENT_LOGGED = "EVENT_LOGGED"
    VOICE_MESSAGE_RECEIVED = "VOICE_MESSAGE_RECEIVED"
    TEXT_MESSAGE_RECEIVED = "TEXT_MESSAGE_RECEIVED"
    PAYMENT_GENERATED = "PAYMENT_GENERATED"
    UNKNOWN_INTENT = "UNKNOWN_INTENT"
    ERROR_OCCURRED = "ERROR_OCCURRED"


class User(BaseModel):
    id: str
    phone_number: str
    display_name: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    last_seen: datetime = Field(default_factory=datetime.now)
    status: UserStatus = UserStatus.NEW
    source: str = "WHATSAPP"
    activation_step: ActivationStep = ActivationStep.STARTED_CHAT


class Worker(BaseModel):
    id: str
    user_id: str
    name: str
    role: str = "Domestic Worker"
    monthly_salary: float
    working_days_per_month: int = 26
    weekly_off: str = "Sunday"
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)


class Event(BaseModel):
    id: str
    worker_id: str
    event_type: EventType
    event_date: date = Field(default_factory=date.today)
    amount: float = 0.0
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)


class AnalyticsEvent(BaseModel):
    id: str
    user_id: Optional[str] = None
    event_name: AnalyticsEventType
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
