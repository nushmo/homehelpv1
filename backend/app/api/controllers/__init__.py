from app.api.controllers.webhook import router as webhook_router
from app.api.controllers.workers import router as workers_router
from app.api.controllers.events import router as events_router
from app.api.controllers.payment import router as payment_router
from app.api.controllers.analytics import router as analytics_router
from app.api.controllers.legal import router as legal_router

__all__ = [
    "webhook_router",
    "workers_router",
    "events_router",
    "payment_router",
    "analytics_router",
    "legal_router",
]
