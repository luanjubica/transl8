# Transl8 Makefile - Microservices Management

.PHONY: help build up down restart logs clean test migrate shell

# Default target
help:
	@echo "Transl8 - Microservices Commands"
	@echo ""
	@echo "Development:"
	@echo "  make build          - Build all Docker images"
	@echo "  make up             - Start all services"
	@echo "  make down           - Stop all services"
	@echo "  make restart        - Restart all services"
	@echo "  make logs           - View logs from all services"
	@echo "  make logs-api       - View API logs"
	@echo "  make logs-worker    - View worker logs"
	@echo "  make logs-frontend  - View frontend logs"
	@echo ""
	@echo "Database:"
	@echo "  make migrate        - Run database migrations"
	@echo "  make migrate-create - Create new migration"
	@echo "  make db-shell       - Open PostgreSQL shell"
	@echo ""
	@echo "Utilities:"
	@echo "  make shell          - Open Python shell in API container"
	@echo "  make test           - Run tests"
	@echo "  make clean          - Remove containers and volumes"
	@echo "  make ps             - List running services"
	@echo ""
	@echo "Production:"
	@echo "  make prod-build     - Build production images"
	@echo "  make prod-up        - Start production stack"
	@echo "  make prod-down      - Stop production stack"

# Development commands
build:
	docker-compose build

up:
	docker-compose up -d
	@echo "Services starting..."
	@echo "Frontend: http://localhost:3000"
	@echo "API: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"
	@echo "Flower (Celery monitoring): http://localhost:5555"

down:
	docker-compose down

restart:
	docker-compose restart

logs:
	docker-compose logs -f

logs-api:
	docker-compose logs -f api

logs-worker:
	docker-compose logs -f worker-parsing worker-translation worker-export

logs-flower:
	docker-compose logs -f flower

logs-frontend:
	docker-compose logs -f frontend

# Frontend commands
frontend-shell:
	docker-compose exec frontend /bin/sh

frontend-build:
	docker-compose build frontend

restart-frontend:
	docker-compose restart frontend

# Database commands
migrate:
	docker-compose exec api alembic upgrade head

migrate-create:
	@read -p "Enter migration message: " msg; \
	docker-compose exec api alembic revision --autogenerate -m "$$msg"

migrate-downgrade:
	docker-compose exec api alembic downgrade -1

db-shell:
	docker-compose exec postgres psql -U transl8 -d transl8

# Utility commands
shell:
	docker-compose exec api python

shell-bash:
	docker-compose exec api /bin/bash

test:
	docker-compose exec api pytest

test-cov:
	docker-compose exec api pytest --cov=app --cov-report=html

ps:
	docker-compose ps

# Cleanup
clean:
	docker-compose down -v
	docker system prune -f

clean-all:
	docker-compose down -v --rmi all
	docker system prune -af

# Production commands
prod-build:
	docker-compose -f docker-compose.prod.yml build

prod-up:
	docker-compose -f docker-compose.prod.yml up -d

prod-down:
	docker-compose -f docker-compose.prod.yml down

prod-logs:
	docker-compose -f docker-compose.prod.yml logs -f

prod-ps:
	docker-compose -f docker-compose.prod.yml ps

# Health checks
health:
	@echo "Checking service health..."
	@echo "Frontend:"
	@curl -s http://localhost:3000/api/health | python -m json.tool || echo "Frontend not responding"
	@echo "\nAPI:"
	@curl -s http://localhost:8000/health | python -m json.tool || echo "API not responding"

# Quick restart specific services
restart-api:
	docker-compose restart api

restart-workers:
	docker-compose restart worker-parsing worker-translation worker-export

restart-db:
	docker-compose restart postgres

restart-redis:
	docker-compose restart redis
