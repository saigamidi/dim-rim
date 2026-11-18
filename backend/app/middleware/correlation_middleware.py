"""Correlation ID middleware for request tracing."""
import uuid
from contextvars import ContextVar

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

# Context variable for storing correlation ID per request
correlation_id_var: ContextVar[str] = ContextVar("correlation_id", default="")


class CorrelationMiddleware(BaseHTTPMiddleware):
    """Middleware to generate or reuse correlation ID for request tracing."""

    async def dispatch(self, request: Request, call_next):
        """Generate or reuse X-Correlation-ID header."""
        correlation_id = request.headers.get("X-Correlation-ID")
        if not correlation_id:
            correlation_id = str(uuid.uuid4())
        
        # Store in context variable
        correlation_id_var.set(correlation_id)
        
        # Add to request state
        request.state.correlation_id = correlation_id
        
        response = await call_next(request)
        
        # Include in response headers
        response.headers["X-Correlation-ID"] = correlation_id
        
        return response


def get_correlation_id() -> str:
    """Get correlation ID from context variable."""
    return correlation_id_var.get()
