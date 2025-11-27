#!/bin/bash
# Entrypoint script for Celery worker

set -e

echo "Waiting for PostgreSQL..."
while ! pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER"; do
    sleep 1
done
echo "PostgreSQL is ready!"

echo "Waiting for Redis..."
while ! redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" ping > /dev/null 2>&1; do
    sleep 1
done
echo "Redis is ready!"

echo "Starting Celery worker..."
exec celery -A app.core.celery_app worker \
    --loglevel=info \
    --concurrency=4 \
    --max-tasks-per-child=50 \
    --queues=${CELERY_QUEUES:-parsing,translation,export}
