"""FastAPI application main entry point."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.middleware.correlation_middleware import CorrelationMiddleware
from app.middleware.error_handling_middleware import register_error_handlers
from app.middleware.request_logging_middleware import RequestLoggingMiddleware
from app.routers import audit, auth, classification, health, intake, parsing, vins
from app.seed import seed_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup/shutdown tasks."""
    # Seed database if configured
    if settings.seed_data:
        seed_database()
    yield


app = FastAPI(
    title="TMNA Disruption Manager RIM API",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom middleware
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(CorrelationMiddleware)

# Global error handlers
register_error_handlers(app)

# Include routers
app.include_router(auth.router)
app.include_router(intake.router)
app.include_router(parsing.router)
app.include_router(classification.router)
app.include_router(vins.router)
app.include_router(audit.router)
app.include_router(health.router)
