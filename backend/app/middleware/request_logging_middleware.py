"""Request logging middleware for structured logging."""
import logging
import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log request/response with structured data."""

    async def dispatch(self, request: Request, call_next):
        """Log request and response with timing."""
        start_time = time.time()
        
        # Get correlation ID from request state
        correlation_id = getattr(request.state, "correlation_id", "unknown")
        
        # Log request
        logger.info(
            "Request started",
            extra={
                "method": request.method,
                "path": request.url.path,
                "correlation_id": correlation_id,
            },
        )
        
        response = await call_next(request)
        
        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000
        
        # Log response
        logger.info(
            "Request completed",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
                "correlation_id": correlation_id,
            },
        )
        
        return response
