import logging
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.controllers import (
    webhook_router,
    workers_router,
    events_router,
    payment_router,
    analytics_router,
    legal_router,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger("homehelp.main")

app = FastAPI(
    title="HomeHelp AI (V1)",
    description="WhatsApp-First AI Assistant for Domestic Worker Salary Management",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(webhook_router)
app.include_router(workers_router)
app.include_router(events_router)
app.include_router(payment_router)
app.include_router(analytics_router)
app.include_router(legal_router)

@app.middleware("http")
async def log_requests(request, call_next):
    print(f"📥 [HTTP REQUEST] {request.method} {request.url.path}", flush=True)
    response = await call_next(request)
    print(f"📤 [HTTP RESPONSE] {request.method} {request.url.path} ──> {response.status_code}", flush=True)
    return response


@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint for Railway and monitoring."""
    return {
        "status": "healthy",
        "service": "HomeHelp AI Backend",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=settings.PORT, reload=True)
