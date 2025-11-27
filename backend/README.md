# Transl8 Backend

FastAPI-based backend for the Transl8 translation platform.

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Redis 6+
- Docker & Docker Compose (optional)

### Local Development

1. **Start database and Redis**:
```bash
docker-compose up -d postgres redis
```

2. **Set up Python environment**:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Configure environment**:
```bash
cp .env.example .env
# Edit .env with your settings
```

4. **Run database migrations**:
```bash
alembic upgrade head
```

5. **Start development server**:
```bash
uvicorn app.main:app --reload
```

The API will be available at:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API-First Design

This backend is designed as an API-first service, meaning:

- All functionality is accessible via RESTful API endpoints
- Authentication via JWT (Clerk)
- Comprehensive OpenAPI documentation
- Versioned API (`/api/v1`)
- Suitable for both web UI and direct API consumption

### API Endpoints

#### Projects
- `GET /api/v1/projects` - List projects
- `POST /api/v1/projects` - Create project
- `GET /api/v1/projects/{id}` - Get project details
- `PATCH /api/v1/projects/{id}` - Update project
- `DELETE /api/v1/projects/{id}` - Delete project

#### Documents
- `GET /api/v1/documents` - List documents
- `POST /api/v1/documents` - Create document
- `GET /api/v1/documents/{id}` - Get document details
- `PATCH /api/v1/documents/{id}` - Update document
- `DELETE /api/v1/documents/{id}` - Delete document

More endpoints to be added for segments, translations, glossaries, etc.

## Database Migrations

### Create a new migration
```bash
alembic revision --autogenerate -m "description of changes"
```

### Apply migrations
```bash
alembic upgrade head
```

### Rollback migration
```bash
alembic downgrade -1
```

## Testing

Run tests with pytest:
```bash
pytest
pytest -v                    # Verbose output
pytest --cov=app            # With coverage
pytest tests/api            # Specific directory
```

## Code Quality

### Linting
```bash
ruff check .
ruff check --fix .          # Auto-fix issues
```

### Type Checking
```bash
mypy app
```

### Formatting
```bash
black .
```

## Project Structure

```
backend/
├── alembic/              # Database migrations
├── app/
│   ├── api/              # API endpoints
│   │   └── v1/           # API version 1
│   ├── core/             # Core config and utilities
│   ├── models/           # SQLAlchemy models
│   ├── schemas/          # Pydantic schemas
│   ├── services/         # Business logic
│   └── workers/          # Celery tasks
├── tests/                # Test suite
└── requirements.txt      # Python dependencies
```

## Environment Variables

See `.env.example` for all available configuration options.

Key variables:
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `CLERK_JWT_PUBLIC_KEY` - Clerk authentication public key
- `DEEPL_API_KEY` - DeepL translation API key
- `S3_BUCKET_NAME` - File storage bucket

## License

Proprietary
