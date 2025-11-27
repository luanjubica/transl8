# Transl8

> AI-powered translation platform for software localization, product labels, and catalogs at scale.

## Overview

Transl8 is a B2B translation platform focused on:
- **Software/app localization** — XML, XLIFF, JSON, strings files
- **Product information** — labels, descriptions, catalogs (PIM integrations)
- **Technical docs** — manuals, compliance documents

### Key Features

- 🤖 **AI-Powered Translation** - DeepL and OpenAI GPT-4 integration
- 📁 **Structured File Support** - XML, XLIFF, JSON, CSV, XLSX, DOCX, PDF
- 🔒 **Placeholder Protection** - Automatically detect and lock variables
- 📏 **Length Constraints** - Set character limits for product labels
- 📚 **Glossary Enforcement** - Consistent terminology across translations
- 💾 **Translation Memory** - Never translate the same sentence twice
- 🔌 **API-First Design** - Full REST API for integrations

## Tech Stack

### Backend (API)
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL 15
- **ORM**: SQLAlchemy
- **Task Queue**: Celery + Redis
- **Translation**: DeepL + OpenAI
- **Storage**: Cloudflare R2 / AWS S3
- **Auth**: Clerk JWT validation

### Frontend (Coming Soon)
- **Framework**: Next.js 14 (App Router)
- **UI**: Tailwind CSS + shadcn/ui
- **Auth**: Clerk

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+ (for frontend)
- Docker & Docker Compose
- PostgreSQL 14+
- Redis 6+

### Quick Start (Backend)

1. **Start services**:
```bash
docker-compose up -d postgres redis
```

2. **Set up backend**:
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your settings
```

3. **Run migrations**:
```bash
alembic upgrade head
```

4. **Start API server**:
```bash
uvicorn app.main:app --reload
```

Visit http://localhost:8000/docs for API documentation.

## API Documentation

The API is fully documented using OpenAPI/Swagger. Once the server is running:

- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/api/v1/openapi.json

### Key Endpoints

#### Projects
- `GET /api/v1/projects` - List projects
- `POST /api/v1/projects` - Create project
- `GET /api/v1/projects/{id}` - Get project
- `PATCH /api/v1/projects/{id}` - Update project
- `DELETE /api/v1/projects/{id}` - Delete project

#### Documents
- `GET /api/v1/documents` - List documents
- `POST /api/v1/documents` - Upload document
- `GET /api/v1/documents/{id}` - Get document
- `PATCH /api/v1/documents/{id}` - Update document
- `DELETE /api/v1/documents/{id}` - Delete document

More endpoints coming soon for segments, translations, glossaries, and translation memory.

## Project Structure

```
transl8/
├── backend/                  # FastAPI backend
│   ├── app/
│   │   ├── api/v1/          # API endpoints
│   │   ├── core/            # Config & utilities
│   │   ├── models/          # Database models
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── services/        # Business logic
│   │   └── workers/         # Celery tasks
│   ├── alembic/             # Database migrations
│   └── tests/               # Test suite
├── frontend/                 # Next.js frontend (coming soon)
├── docker-compose.yml        # Local development
├── CLAUDE.md                 # AI assistant guide
└── README.md                 # This file
```

## Development

### Running Tests

```bash
cd backend
pytest
pytest -v --cov=app  # With coverage
```

### Code Quality

```bash
# Linting
ruff check .

# Type checking
mypy app

# Formatting
black .
```

### Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## API-First Design

Transl8 is designed as an API-first platform, meaning:

- ✅ All functionality accessible via REST API
- ✅ Comprehensive OpenAPI documentation
- ✅ JWT authentication (Clerk)
- ✅ Versioned API (`/api/v1`)
- ✅ Suitable for both UI and direct API consumption
- ✅ PIM integrations and webhooks

This design allows you to:
- Build custom integrations
- Automate translation workflows
- Connect to PIM systems (Akeneo, Salsify)
- Trigger translations via CI/CD pipelines

## Roadmap

### Phase 1: Foundation ✅
- [x] Database schema
- [x] FastAPI structure
- [x] Authentication middleware
- [x] Basic API endpoints (projects, documents)

### Phase 2: Core Features (In Progress)
- [ ] File upload + S3 integration
- [ ] XML/JSON parsers
- [ ] Segment extraction
- [ ] Translation editor API

### Phase 3: Translation
- [ ] DeepL integration
- [ ] Celery job queue
- [ ] Glossary management
- [ ] Translation Memory
- [ ] Placeholder detection

### Phase 4: Polish
- [ ] Export to original format
- [ ] QA checks
- [ ] Team management
- [ ] Frontend UI

## Contributing

See [CLAUDE.md](./CLAUDE.md) for comprehensive development guidelines.

## License

Proprietary

## Support

For issues and questions, please contact the development team.
