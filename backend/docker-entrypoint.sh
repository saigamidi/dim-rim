#!/bin/sh
# docker-entrypoint.sh — Run migrations and seed before starting backend
set -e

echo "Running database migrations..."
alembic upgrade head

# Run seed data if SEED_DATA=true
if [ "$SEED_DATA" = "true" ]; then
    echo "Seeding database..."
    python -c "from app.seed import seed_database; seed_database()" || true
fi

echo "Starting backend..."
exec "$@"
