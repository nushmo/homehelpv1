from fastapi import APIRouter
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])
analytics_service = AnalyticsService()


@router.get("/overview")
def get_overview_analytics():
    """Get high-level product analytics and operational metrics."""
    return analytics_service.get_overview_metrics()


@router.get("/funnel")
def get_product_funnel():
    """Get product adoption lifecycle funnel and conversion rates."""
    return analytics_service.get_funnel_metrics()
