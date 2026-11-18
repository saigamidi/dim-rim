"""Health check router."""
from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check():
    """
    Health check endpoint for liveness probe.
    
    Note: This endpoint is intentionally unauthenticated to allow
    infrastructure health monitoring without requiring credentials.
    """
    return {"status": "healthy"}
