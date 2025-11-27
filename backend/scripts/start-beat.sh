#!/bin/bash
# Entrypoint script for Celery beat (scheduler)

set -e

echo "Waiting for Redis..."
while ! redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" ping > /dev/null 2>&1; do
    sleep 1
done
echo "Redis is ready!"

echo "Starting Celery beat..."
exec celery -A app.core.celery_app beat --loglevel=info
