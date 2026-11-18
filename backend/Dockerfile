# Multi-stage build for TMNA Disruption Manager RIM Backend
FROM python:3.11-slim as base

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency manifests and package directory
COPY pyproject.toml ./
COPY app/ ./app/

# Install dependencies
ARG INSTALL_SPEC=.
RUN pip install --no-cache-dir "$INSTALL_SPEC"

# Copy migrations
COPY alembic/ ./alembic/
COPY alembic.ini ./

# Copy entrypoint script
COPY docker-entrypoint.sh ./
RUN chmod +x docker-entrypoint.sh

# Expose backend port
EXPOSE 8000

# Set entrypoint and command
ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
