# CLAUDE.md - AI Assistant Guide for Transl8

## About This Document

This document serves as a comprehensive guide for AI assistants (like Claude) working on the Transl8 project. It provides context about the codebase structure, development workflows, conventions, and best practices to follow when making changes.

**Last Updated:** 2025-11-27
**Project Status:** Initial Setup - Pre-MVP
**Repository:** luanjubica/transl8

---

## Project Overview

### Purpose

**Transl8** is an AI-powered B2B translation platform designed for software localization, product labels, and technical documentation at scale.

**Target Use Cases:**
1. Software/app localization (XML, XLIFF, JSON, .strings files)
2. Product information management (labels, descriptions, catalogs with PIM integrations)
3. Technical documentation (manuals, compliance documents)

**Target Customers:**
- E-commerce companies
- SaaS/software development teams
- Consumer goods/FMCG manufacturers
- Localization agencies

**Key Differentiators:**
- Self-serve with transparent pricing
- Focused on XML/structured content handling
- API-first architecture for PIM integration
- SMB/startup friendly (vs. enterprise-only competitors like TextUnited)

### Tech Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Frontend** | Next.js 14 (App Router) | React framework with server components |
| **UI Components** | Tailwind CSS + shadcn/ui | Styling and component library |
| **Backend** | FastAPI (Python 3.11+) | High-performance async API |
| **Database** | PostgreSQL | Primary data store (Neon or Supabase hosted) |
| **ORM** | SQLAlchemy or SQLModel | Database modeling and queries |
| **Task Queue** | Celery + Redis | Async job processing (file parsing, translation) |
| **Translation APIs** | DeepL (primary) + OpenAI GPT-4 (fallback) | AI translation engines |
| **File Storage** | Cloudflare R2 or AWS S3 | Document storage |
| **Authentication** | Clerk (frontend) + JWT validation (backend) | User auth and session management |
| **Hosting** | Vercel (frontend) + Railway/Render (backend + Redis) | Deployment platforms |

### Python Libraries for File Processing

```python
# XML Handling
lxml              # XML parsing, XPath, schema validation
defusedxml        # Secure XML parsing (prevent XXE attacks)
xmldiff           # Compare original vs translated structure

# Document Processing
python-docx       # DOCX handling
pdfplumber        # PDF text extraction
openpyxl          # XLSX handling

# Translation & NLP
deepl             # DeepL API client
openai            # OpenAI API client
langdetect        # Language detection

# API & Web
fastapi           # Web framework
pydantic          # Data validation
celery[redis]     # Task queue
sqlalchemy        # ORM
alembic           # Database migrations
```

---

## Repository Structure

```
transl8/
├── frontend/                      # Next.js 14 application
│   ├── app/
│   │   ├── (auth)/               # Auth pages (login, signup)
│   │   ├── (dashboard)/          # Main app (protected routes)
│   │   │   ├── projects/         # Project management
│   │   │   ├── glossaries/       # Glossary management
│   │   │   ├── settings/         # User/org settings
│   │   │   └── team/             # Team member management
│   │   ├── (marketing)/          # Landing page, pricing
│   │   └── api/                  # Next.js API routes (optional)
│   ├── components/
│   │   ├── ui/                   # shadcn/ui components
│   │   ├── editor/               # Translation editor components
│   │   ├── file-upload/          # File upload components
│   │   └── shared/               # Shared components
│   ├── lib/
│   │   ├── api-client.ts         # Backend API client
│   │   ├── auth.ts               # Clerk auth utilities
│   │   └── utils.ts              # Helper functions
│   ├── public/
│   ├── styles/
│   ├── package.json
│   ├── tsconfig.json
│   └── tailwind.config.js
│
├── backend/                       # FastAPI application
│   ├── app/
│   │   ├── api/
│   │   │   ├── v1/
│   │   │   │   ├── projects.py
│   │   │   │   ├── documents.py
│   │   │   │   ├── segments.py
│   │   │   │   ├── translations.py
│   │   │   │   ├── glossaries.py
│   │   │   │   ├── tm.py         # Translation Memory
│   │   │   │   ├── jobs.py       # Translation jobs
│   │   │   │   └── integrations.py
│   │   │   └── deps.py           # Dependency injection
│   │   ├── core/
│   │   │   ├── config.py         # Settings management
│   │   │   ├── security.py       # JWT validation, auth
│   │   │   ├── celery_app.py     # Celery configuration
│   │   │   └── database.py       # Database connection
│   │   ├── models/               # SQLAlchemy models
│   │   │   ├── user.py
│   │   │   ├── organization.py
│   │   │   ├── project.py
│   │   │   ├── document.py
│   │   │   ├── segment.py
│   │   │   ├── translation.py
│   │   │   ├── glossary.py
│   │   │   └── tm.py
│   │   ├── schemas/              # Pydantic schemas (request/response)
│   │   │   ├── project.py
│   │   │   ├── document.py
│   │   │   ├── segment.py
│   │   │   ├── translation.py
│   │   │   └── glossary.py
│   │   ├── services/             # Business logic
│   │   │   ├── translation_service.py
│   │   │   ├── file_parser.py
│   │   │   ├── xml_handler.py
│   │   │   ├── json_handler.py
│   │   │   ├── csv_handler.py
│   │   │   ├── tm_service.py     # Translation Memory
│   │   │   ├── glossary_service.py
│   │   │   ├── qa_service.py     # Quality assurance checks
│   │   │   └── storage_service.py
│   │   └── workers/              # Celery tasks
│   │       ├── parse_document.py
│   │       ├── translate_document.py
│   │       └── export_document.py
│   ├── alembic/                  # Database migrations
│   │   ├── versions/
│   │   └── env.py
│   ├── tests/
│   │   ├── api/
│   │   ├── services/
│   │   └── conftest.py
│   ├── requirements.txt
│   └── pyproject.toml
│
├── docker-compose.yml             # Local development services
├── .env.example                   # Environment variables template
├── .gitignore
├── CLAUDE.md                      # This file
└── README.md                      # Project overview
```

### Key Directories

| Directory | Purpose | Notes |
|-----------|---------|-------|
| `frontend/app/(dashboard)` | Main application UI | Protected routes, requires auth |
| `frontend/components/editor` | Translation editor | Core feature - segment editing UI |
| `backend/app/api/v1` | REST API endpoints | Versioned API routes |
| `backend/app/services` | Business logic | Keep controllers thin, logic here |
| `backend/app/workers` | Background jobs | Celery tasks for async processing |
| `backend/alembic/versions` | Database migrations | Auto-generated, review before commit |

---

## Development Workflow

### Branch Strategy

- **Main Branch:** `main` (protected)
- **Feature Branches:** `feature/<description>` (e.g., `feature/xml-parser`)
- **Claude Branches:** `claude/claude-md-<session-id>` (auto-generated for Claude Code sessions)
- **Bug Fixes:** `fix/<description>` (e.g., `fix/placeholder-detection`)

**Branch Rules:**
- Never commit directly to `main`
- Create PR for all changes
- Squash commits when merging to keep history clean

### Commit Conventions

Follow these commit message guidelines:

**Format:** `<type>: <description>`

**Types:**
- `feat`: New feature (e.g., `feat: add XLIFF 2.0 parser`)
- `fix`: Bug fix (e.g., `fix: preserve XML namespaces on export`)
- `docs`: Documentation changes
- `refactor`: Code refactoring (no functional changes)
- `test`: Adding or updating tests
- `chore`: Maintenance tasks (dependencies, config)
- `style`: Code style changes (formatting, linting)
- `perf`: Performance improvements

**Examples:**
```
feat: add DeepL API integration for translation
fix: handle placeholder detection in nested JSON
docs: update API endpoint documentation
test: add XML structure validation tests
refactor: extract glossary matching logic to service
chore: upgrade FastAPI to 0.104.0
```

### Git Operations

**Push Commands:**
```bash
git push -u origin <branch-name>
```
- Branch names for Claude must start with `claude/` and end with session ID
- Retry up to 4 times with exponential backoff (2s, 4s, 8s, 16s) on network failures

**Fetch/Pull Commands:**
```bash
git fetch origin <branch-name>
git pull origin <branch-name>
```
- Retry logic same as push operations

---

## Code Conventions

### General Principles

1. **Keep It Simple:** Avoid over-engineering. Only make changes that are directly requested or clearly necessary.
2. **Security First:** Always consider security implications (XSS, SQL injection, XXE, command injection)
3. **No Premature Optimization:** Don't add abstractions or helper functions for one-time operations
4. **Clean Deletions:** Remove unused code completely—no `// removed` comments or unused parameters
5. **Type Safety:** Use TypeScript in frontend, type hints in Python backend
6. **Error Handling:** Always handle errors gracefully, return meaningful error messages

### Python (Backend) Style

- **PEP 8 Compliance:** Follow Python style guide
- **Type Hints:** Use type annotations for all function signatures
- **Naming Conventions:**
  - Functions/variables: `snake_case`
  - Classes: `PascalCase`
  - Constants: `UPPER_SNAKE_CASE`
  - Private methods: `_leading_underscore`
- **Indentation:** 4 spaces
- **Line Length:** 100 characters (not strict, use judgment)
- **Imports:** Group in order: stdlib, third-party, local
- **Docstrings:** Use for public APIs, not required for private methods

**Example:**
```python
from typing import Optional, List
from app.models.segment import Segment
from app.schemas.translation import TranslationCreate

def translate_segments(
    segments: List[Segment],
    target_lang: str,
    glossary_id: Optional[str] = None
) -> List[Translation]:
    """
    Translate a list of segments to target language.

    Args:
        segments: List of source segments to translate
        target_lang: ISO 639-1 language code (e.g., 'de', 'fr')
        glossary_id: Optional glossary to enforce terminology

    Returns:
        List of Translation objects with translated text
    """
    # Implementation
```

### TypeScript/JavaScript (Frontend) Style

- **TypeScript Required:** All new code must be TypeScript
- **Naming Conventions:**
  - Functions/variables: `camelCase`
  - Components: `PascalCase`
  - Constants: `UPPER_SNAKE_CASE`
  - Types/Interfaces: `PascalCase`
- **Indentation:** 2 spaces
- **Semicolons:** Required
- **Quotes:** Single quotes for strings
- **React:** Use functional components with hooks (no class components)

**Example:**
```typescript
interface TranslationEditorProps {
  documentId: string;
  targetLanguage: string;
  onSave: (segmentId: string, text: string) => void;
}

export function TranslationEditor({
  documentId,
  targetLanguage,
  onSave
}: TranslationEditorProps) {
  // Implementation
}
```

### File Naming Conventions

**Python:**
- Modules: `snake_case.py` (e.g., `xml_handler.py`)
- Test files: `test_<module>.py` (e.g., `test_xml_handler.py`)

**TypeScript/React:**
- Components: `PascalCase.tsx` (e.g., `TranslationEditor.tsx`)
- Utilities: `kebab-case.ts` (e.g., `api-client.ts`)
- Test files: `<name>.test.tsx`

### Comments and Documentation

- Only add comments where logic isn't self-evident
- Don't add docstrings to code you didn't change
- Focus on "why" rather than "what" in comments
- Document business rules and edge cases
- Add JSDoc for complex TypeScript functions
- Add docstrings for all Python service methods

---

## Database Schema Overview

### Core Entities

**Organizations & Users:**
- `organizations` - Multi-tenant org structure
- `users` - User accounts (synced with Clerk)
- `org_members` - Many-to-many with roles (owner, admin, translator, reviewer)

**Projects & Documents:**
- `projects` - Translation projects with source/target languages
- `documents` - Uploaded files with metadata
- `segments` - Extracted translatable units from documents
- `translations` - Translated text for each segment + language

**Glossary & TM:**
- `glossaries` - Term databases per language pair
- `glossary_terms` - Individual source/target term pairs
- `translation_memory` - Previously translated segments for reuse

**Jobs & Integrations:**
- `translation_jobs` - Async translation task tracking
- `integrations` - API keys, PIM connections, webhooks

**Key Constraints:**
- All IDs are UUIDs
- Cascade deletes on organization/project removal
- Unique constraints on (segment_id, target_language) for translations
- Hash-based indexing for TM lookups

For complete schema DDL, see project spec or migration files in `backend/alembic/versions/`.

---

## File Format Handling

### Priority Levels

**🥇 Core (MVP):**
- XML (generic)
- XLIFF 1.2 / 2.0
- Android XML (strings.xml)
- iOS .strings
- JSON (nested)
- CSV
- XLSX

**🥈 Secondary (Post-MVP):**
- DOCX
- PDF

**🥉 Later:**
- InDesign (IDML)
- HTML

### File Processing Pipeline

1. **Upload** → S3/R2 storage
2. **Parse** → Celery job extracts segments
3. **Detect** → Identify placeholders, tags, context
4. **Translate** → AI translation with TM/glossary
5. **Review** → Manual editing in UI
6. **Export** → Reconstruct original format with translations

### XML Handling Rules

- **Preserve Structure:** All tags, attributes, namespaces must remain intact
- **Extract Text Nodes:** Only text content becomes segments
- **Detect Placeholders:** `{variable}`, `%s`, `%(name)s`, `%1$s`, etc.
- **Lock Placeholders:** Users cannot delete or modify them
- **Context Preservation:** XML comments and attributes provide context
- **Schema Validation:** Validate against XSD if provided

---

## Testing Strategy

### Running Tests

**Backend (Python/FastAPI):**
```bash
cd backend
pytest                          # Run all tests
pytest tests/api                # Run API tests
pytest tests/services           # Run service tests
pytest -v --cov=app            # Run with coverage report
```

**Frontend (Next.js/React):**
```bash
cd frontend
npm test                        # Run Jest tests
npm run test:watch              # Watch mode
npm run test:coverage           # Coverage report
```

### Test Coverage Goals

- **Backend:** Aim for 80%+ coverage
- **Frontend:** Aim for 70%+ coverage
- **Critical Paths:** 100% coverage required:
  - XML/JSON parsing and export
  - Placeholder detection
  - Glossary matching
  - TM scoring
  - Auth middleware

### Testing Conventions

**Backend:**
- Use `pytest` fixtures for database setup
- Mock external APIs (DeepL, OpenAI, S3)
- Test both success and error paths
- Use `conftest.py` for shared fixtures

**Frontend:**
- Use Jest + React Testing Library
- Test user interactions, not implementation details
- Mock API calls with MSW (Mock Service Worker)
- Snapshot tests for complex UI components

**Example Test Structure:**
```python
# backend/tests/services/test_xml_handler.py
def test_parse_android_xml():
    """Test parsing Android strings.xml file."""
    xml_content = """
    <resources>
        <string name="app_name">MyApp</string>
        <string name="welcome">Hello {name}!</string>
    </resources>
    """
    segments = parse_xml(xml_content, file_type="android_xml")
    assert len(segments) == 2
    assert segments[1].placeholders == ["{name}"]
```

---

## Build and Deployment

### Local Development Setup

**Prerequisites:**
- Node.js 18+
- Python 3.11+
- Docker & Docker Compose
- PostgreSQL 14+ (or use Docker)
- Redis (or use Docker)

**Initial Setup:**
```bash
# Clone repository
git clone <repo-url> transl8
cd transl8

# Copy environment variables
cp .env.example .env
# Edit .env with your keys (Clerk, DeepL, etc.)

# Start database and Redis
docker-compose up -d postgres redis

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head          # Run migrations
uvicorn app.main:app --reload # Start API server

# Frontend setup (in new terminal)
cd frontend
npm install
npm run dev                   # Start Next.js dev server
```

**Access:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Build Process

**Backend:**
```bash
cd backend
pytest                        # Run tests
ruff check .                  # Lint
mypy app                      # Type check
```

**Frontend:**
```bash
cd frontend
npm run lint                  # ESLint
npm run type-check            # TypeScript check
npm run build                 # Production build
```

### Environment Variables

**Backend (.env):**
```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/transl8

# Redis
REDIS_URL=redis://localhost:6379/0

# Authentication
CLERK_JWT_PUBLIC_KEY=<your-clerk-jwt-public-key>

# Translation APIs
DEEPL_API_KEY=<your-deepl-api-key>
OPENAI_API_KEY=<your-openai-api-key>

# File Storage
S3_BUCKET_NAME=transl8-documents
S3_ACCESS_KEY_ID=<your-access-key>
S3_SECRET_ACCESS_KEY=<your-secret-key>
S3_REGION=auto  # For Cloudflare R2

# App Config
ENVIRONMENT=development
DEBUG=true
```

**Frontend (.env.local):**
```bash
# Clerk Auth
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=<your-clerk-publishable-key>
CLERK_SECRET_KEY=<your-clerk-secret-key>

# API
NEXT_PUBLIC_API_URL=http://localhost:8000

# App
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

### Deployment

**Frontend (Vercel):**
- Connect GitHub repo
- Auto-deploy on push to `main`
- Set environment variables in Vercel dashboard

**Backend (Railway/Render):**
- Deploy FastAPI app
- Set environment variables
- Enable auto-deploy from `main`
- Configure Redis add-on

---

## API Structure

### REST API Endpoints (FastAPI)

**Base URL:** `/api/v1`

**Projects:**
- `GET /projects` - List projects
- `POST /projects` - Create project
- `GET /projects/{id}` - Get project details
- `PATCH /projects/{id}` - Update project
- `DELETE /projects/{id}` - Delete project

**Documents:**
- `POST /projects/{id}/documents` - Upload document
- `GET /documents/{id}` - Get document details
- `GET /documents/{id}/segments` - List segments
- `POST /documents/{id}/export` - Export translated document

**Translations:**
- `GET /documents/{id}/translations/{lang}` - Get translations for language
- `PATCH /translations/{id}` - Update translation
- `POST /documents/{id}/translate` - Trigger AI translation job

**Glossaries:**
- `GET /glossaries` - List glossaries
- `POST /glossaries` - Create glossary
- `POST /glossaries/{id}/terms` - Add terms
- `POST /glossaries/{id}/import` - Import from CSV

**Translation Memory:**
- `GET /tm/matches` - Find TM matches for segment
- `POST /tm/entries` - Add TM entry

**Jobs:**
- `GET /jobs/{id}` - Get job status
- `POST /jobs/{id}/cancel` - Cancel job

### Authentication

All API endpoints (except health checks) require JWT authentication:
- Frontend obtains JWT from Clerk
- Included in `Authorization: Bearer <token>` header
- Backend validates JWT signature and extracts user ID
- User permissions checked via org membership

---

## Common Tasks

### Adding a New Feature

1. **Read existing related code first** - Understand current patterns
2. **Create a todo list** - Use TodoWrite tool for tracking
3. **Write tests first** - TDD approach when possible
4. **Implement changes** - Follow conventions
5. **Run tests** - Ensure nothing breaks
6. **Update documentation** - If needed
7. **Commit with clear message** - Follow commit conventions
8. **Push to feature branch** - Create PR

**Example Workflow:**
```bash
# Create feature branch
git checkout -b feature/glossary-import

# Make changes, commit frequently
git add .
git commit -m "feat: add CSV glossary import endpoint"

# Push and create PR
git push -u origin feature/glossary-import
```

### Fixing a Bug

1. **Reproduce the bug** - Write a failing test if possible
2. **Read relevant code** - Understand the issue
3. **Implement minimal fix** - Don't refactor unrelated code
4. **Add regression test** - Prevent bug from returning
5. **Commit and push** - Use `fix:` commit type

### Adding a New File Format Parser

1. **Create parser in `backend/app/services/`** - e.g., `xliff_handler.py`
2. **Implement parse and export functions** - Match interface of existing parsers
3. **Add placeholder detection** - Use regex patterns
4. **Write comprehensive tests** - Cover edge cases
5. **Register parser** - Add to file type mapping in `file_parser.py`
6. **Update frontend** - Add file type to upload component

### Adding Database Migration

```bash
cd backend

# Auto-generate migration from model changes
alembic revision --autogenerate -m "add placeholder_pattern to documents"

# Review generated migration file in alembic/versions/
# Make manual edits if needed

# Apply migration
alembic upgrade head

# Commit migration file
git add alembic/versions/*.py
git commit -m "chore: add migration for placeholder_pattern field"
```

### Updating Dependencies

**Backend:**
```bash
cd backend
pip install --upgrade <package>
pip freeze > requirements.txt  # Update lockfile
pytest                          # Verify tests still pass
```

**Frontend:**
```bash
cd frontend
npm update <package>
npm test                        # Verify tests still pass
```

---

## Architecture Decisions

### Monorepo Structure

- **Why:** Frontend and backend are tightly coupled, share types/schemas
- **Tools:** Simple directory structure, no complex monorepo tools needed
- **Trade-off:** Separate deployments, but shared development

### Async Task Processing

- **Why:** File parsing and translation can take minutes
- **Solution:** Celery + Redis for background jobs
- **Pattern:** Create job record, queue task, poll for status

### Multi-Tenancy

- **Design:** Organization-based with membership roles
- **Isolation:** All queries filtered by org_id
- **Sharing:** Translation Memory shared within org, not across orgs

### API-First Design

- **Why:** Support both web UI and external integrations
- **Pattern:** OpenAPI spec auto-generated from FastAPI
- **Versioning:** `/api/v1` prefix, maintain backwards compatibility

### File Storage

- **Why:** Don't store files in database
- **Solution:** S3-compatible storage (Cloudflare R2)
- **Pattern:** Store URL + metadata in DB, actual file in object storage

---

## Security Guidelines

### Security Checklist

- [x] Input validation at API boundaries (Pydantic schemas)
- [x] No hardcoded credentials (use environment variables)
- [x] JWT authentication and authorization
- [x] SQL injection prevention (use ORM, parameterized queries)
- [x] XSS prevention (React auto-escapes, sanitize user input)
- [x] CSRF protection (SameSite cookies, CORS config)
- [x] XXE attack prevention (use `defusedxml` for XML parsing)
- [x] Secure file uploads (validate file types, scan for malware)
- [x] Rate limiting on API endpoints
- [x] HTTPS only in production

### XML Security

**Critical:** XML files can contain malicious payloads (XXE attacks)

**Prevention:**
```python
# Use defusedxml instead of standard library
from defusedxml import ElementTree as ET

# Parse XML safely
tree = ET.parse(file)  # Safe against XXE
```

### Sensitive Files

**Never commit:**
- `.env` files (commit `.env.example` instead)
- `credentials.json` or similar
- Private keys, certificates
- API tokens, secrets
- Database dumps with real data

**Use `.gitignore`:**
```
.env
.env.local
*.key
*.pem
credentials.json
secrets/
```

### API Security

- Validate JWT on every request
- Check org membership before allowing access
- Rate limit public endpoints (10 req/min for uploads)
- Validate file sizes (max 100MB)
- Sanitize user-provided regex patterns

---

## AI Assistant Specific Guidelines

### Before Making Changes

1. **Always read files first** - Never propose changes to code you haven't read
2. **Understand the full context** - Read related files (models, schemas, services)
3. **Check existing patterns** - Follow established conventions in the codebase
4. **Review database schema** - Understand relationships before modifying models
5. **Check migration history** - Know current database state

### During Implementation

1. **Use TodoWrite tool** - Track tasks for complex multi-step work
2. **Make focused changes** - One logical change per commit
3. **Test as you go** - Run tests after each change
4. **Parallel tool calls** - Use multiple independent tool calls in one message when possible
5. **Follow file format priorities** - Focus on core formats first (XML, XLIFF, JSON)
6. **Preserve XML structure** - Never modify tags, only text content
7. **Validate placeholders** - Ensure variables are detected and preserved

### After Changes

1. **Mark todos complete** - Update todo status immediately after finishing tasks
2. **Run test suite** - Verify nothing broke (`pytest` for backend, `npm test` for frontend)
3. **Check linting** - Fix any style issues
4. **Review your changes** - Do a final check before pushing
5. **Update CLAUDE.md** - If you made architectural changes

### Common Pitfalls to Avoid

- **Don't modify XML tags** - Only extract/replace text content
- **Don't lose placeholders** - They must survive parse → translate → export
- **Don't skip org_id filtering** - All queries must be scoped to organization
- **Don't commit migrations without review** - Auto-generated migrations can be wrong
- **Don't add features beyond MVP scope** - Focus on core use cases first

### Communication Style

- Be concise and technical
- Focus on facts over validation
- Use markdown for formatting
- Avoid emojis unless requested
- No time estimates in plans
- Reference file paths with line numbers (e.g., `backend/app/services/xml_handler.py:42`)

---

## MVP Milestones

### Phase 1: Foundation (Weeks 1-2)

- [ ] Monorepo setup (frontend + backend directories)
- [ ] Database schema implementation (PostgreSQL + migrations)
- [ ] Auth flow with Clerk (frontend) + JWT validation (backend)
- [ ] Basic API structure (FastAPI routes, Pydantic schemas)
- [ ] Docker Compose for local development
- [ ] CI/CD pipeline (GitHub Actions)

### Phase 2: Core Flow (Weeks 3-4)

- [ ] File upload + S3 storage integration
- [ ] XML parser (generic + Android strings.xml)
- [ ] JSON parser (nested structure support)
- [ ] Segment extraction and storage
- [ ] Basic translation editor UI (Next.js + shadcn/ui)
- [ ] Project CRUD operations

### Phase 3: Translation (Weeks 5-6)

- [ ] DeepL API integration
- [ ] Celery + Redis setup for async jobs
- [ ] Translation job queue and status tracking
- [ ] Glossary CRUD + term matching
- [ ] Translation Memory matching (fuzzy search)
- [ ] Placeholder detection (regex patterns for common formats)

### Phase 4: Polish (Weeks 7-8)

- [ ] Export to original format (XML, JSON)
- [ ] XLIFF 1.2 export
- [ ] QA checks (length constraints, placeholder validation)
- [ ] Team invite flow
- [ ] Landing page with pricing
- [ ] Documentation and API reference

### Post-MVP

- [ ] XLIFF 2.0 support
- [ ] iOS .strings parser
- [ ] CSV/XLSX import
- [ ] DOCX handling
- [ ] PDF text extraction
- [ ] Webhook integrations
- [ ] PIM connectors (Akeneo, Salsify)

---

## Resources

### Documentation

**Framework Docs:**
- [Next.js 14](https://nextjs.org/docs)
- [FastAPI](https://fastapi.tiangolo.com/)
- [shadcn/ui](https://ui.shadcn.com/)
- [SQLAlchemy](https://docs.sqlalchemy.org/)
- [Celery](https://docs.celeryproject.org/)

**Translation APIs:**
- [DeepL API](https://www.deepl.com/docs-api)
- [OpenAI API](https://platform.openai.com/docs)

**File Formats:**
- [XLIFF 1.2 Spec](http://docs.oasis-open.org/xliff/v1.2/os/xliff-core.html)
- [XLIFF 2.0 Spec](http://docs.oasis-open.org/xliff/xliff-core/v2.0/xliff-core-v2.0.html)

### Related Projects

**Competitors (for reference):**
- TextUnited (enterprise TMS)
- Crowdin (developer-focused)
- Lokalise (SaaS localization)

**Key Differentiator:** Transl8 focuses on structured file handling (XML, JSON) with API-first design for PIM integration, targeting SMBs with transparent pricing.

---

## Troubleshooting

### Common Issues

**Database Connection Errors:**
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Verify connection string in .env
echo $DATABASE_URL
```

**Celery Tasks Not Running:**
```bash
# Start Celery worker
cd backend
celery -A app.core.celery_app worker --loglevel=info

# Check Redis connection
redis-cli ping  # Should return PONG
```

**Frontend API Calls Failing:**
- Verify `NEXT_PUBLIC_API_URL` is set correctly
- Check CORS configuration in FastAPI
- Ensure JWT token is included in request headers

**File Upload Failures:**
- Check S3 credentials and bucket permissions
- Verify file size limits (default 100MB)
- Check network connectivity to S3 endpoint

### Debug Strategies

1. **Check logs first** - FastAPI logs, Next.js console, Celery worker logs
2. **Verify environment configuration** - Print env vars, check .env file
3. **Ensure dependencies are installed** - `pip list`, `npm list`
4. **Check git branch and status** - Make sure you're on the right branch
5. **Run tests in isolation** - Use `pytest -k <test_name>` to debug specific tests
6. **Use debugger** - `breakpoint()` in Python, `debugger;` in JavaScript
7. **Check database state** - Query tables directly to verify data

---

## Performance Considerations

### Database Optimization

- **Indexes:** Add indexes on frequently queried fields (org_id, source_hash)
- **Pagination:** Use limit/offset for large result sets
- **Eager Loading:** Use `joinedload()` to avoid N+1 queries
- **Connection Pooling:** Configure SQLAlchemy pool size

### File Processing

- **Stream Large Files:** Don't load entire file into memory
- **Batch Segments:** Process segments in batches of 100
- **Cache Glossaries:** Load once per job, not per segment
- **Async Processing:** Use Celery for files >1MB or >100 segments

### API Response Times

- **Target:** <200ms for CRUD operations
- **Caching:** Use Redis for frequently accessed data (glossaries, TM matches)
- **Background Jobs:** Queue heavy operations (translation, export)

---

## Change Log

### 2025-11-27
- Initial CLAUDE.md creation
- Added comprehensive project specification
- Defined tech stack and repository structure
- Documented database schema overview
- Added development workflows and conventions
- Defined MVP milestones and feature priorities

---

## Notes for Future Updates

This document should be updated whenever:
- New architectural decisions are made
- Development workflows change
- New file format parsers are added
- Testing strategies evolve
- Security vulnerabilities are discovered
- New features are added to the MVP scope
- API endpoints are added or changed
- Database schema is modified

**Keep this document current to ensure AI assistants have accurate context!**

---

## Quick Reference

**Start Development:**
```bash
docker-compose up -d              # Start DB + Redis
cd backend && uvicorn app.main:app --reload  # Start API
cd frontend && npm run dev        # Start UI
```

**Run Tests:**
```bash
cd backend && pytest              # Backend tests
cd frontend && npm test           # Frontend tests
```

**Create Migration:**
```bash
cd backend
alembic revision --autogenerate -m "description"
alembic upgrade head
```

**Common Commands:**
```bash
# Backend
pip install -r requirements.txt
pytest -v --cov=app
ruff check .
mypy app

# Frontend
npm install
npm run dev
npm run build
npm run lint
npm run type-check
```
