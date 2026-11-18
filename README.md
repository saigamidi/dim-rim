# TMNA Disruption Manager RIM MVP

TMNA Disruption Manager RIM is an AI-assisted disruption-management workflow system that validates and loads affected VIN lists into disruption event drafts.

## Tech Stack

- **Backend:** Python 3.11+, FastAPI, SQLAlchemy, Alembic
- **Frontend:** React 18, TypeScript, Vite 6, Tailwind CSS 3
- **Database:** SQLite (local development), PostgreSQL (production)

## Project Structure

```
dim-rim/
├── backend/             # FastAPI backend application
│   ├── app/            # Application source code
│   │   ├── models/     # SQLAlchemy ORM models
│   │   ├── schemas/    # Pydantic request/response schemas
│   │   ├── repositories/  # Data access layer
│   │   ├── services/   # Business logic layer
│   │   ├── routers/    # API route handlers
│   │   ├── middleware/ # Auth, CORS, error handling
│   │   ├── core/       # Security utilities
│   │   └── adapters/   # External system integration seams
│   ├── alembic/        # Database migrations
│   ├── tests/          # Backend tests
│   ├── Dockerfile      # Backend container image
│   ├── docker-entrypoint.sh  # Container startup script
│   └── pyproject.toml  # Python dependencies
├── frontend/           # React frontend application
│   ├── src/
│   │   ├── components/ # React components (intake, classification, VIN, audit, layout)
│   │   ├── pages/      # Page components
│   │   ├── lib/        # API client, auth context, utilities
│   │   └── types/      # TypeScript types
│   ├── e2e/            # Playwright end-to-end tests
│   ├── Dockerfile      # Frontend container image
│   ├── nginx.conf.template  # Nginx configuration for production
│   └── package.json    # Node dependencies
├── .github/
│   └── workflows/
│       └── ci.yml      # CI workflow for GitHub Actions
├── docker-compose.yml  # Container orchestration
├── start.sh            # Local development startup script
├── stop.sh             # Local development stop script
└── shared_config.json  # Shared application configuration
```

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Node.js 20.19+/22.12+ or higher
- npm (included with Node.js)

### Quick Start

1. Clone the repository
2. Run the startup script:

```bash
./start.sh
```

The script will:
- Check prerequisites (Python 3.11+, Node.js 20.19+/22.12+)
- Install Python dependencies in a virtual environment
- Copy `dev.env` to `.env` if missing
- Run database migrations
- Seed demo data with sample cases and users
- Start the backend API server (default port: 9000)
- Install frontend dependencies
- Start the frontend development server (default port: 5173)

Access the application at the URL displayed (typically `http://localhost:5173`)

### Stopping the Application

```bash
./stop.sh
```

### Demo Seed Credentials

The application includes three demo users with different roles:

**Disruption Manager** (can create intake cases, view all data):
```
Email:    disruption.mgr@tmna.com
Password: Manager123!
```

**Event Approval Reviewer** (can review and approve classifications - required for BR-06 AMBER gate):
```
Email:    event.reviewer@tmna.com
Password: Reviewer123!
```

**VIP Communication Reviewer** (for VIP/special-order vehicle communications):
```
Email:    vip.comms@tmna.com
Password: Comms123!
```

## API Documentation

Once the backend is running, interactive API documentation is available at:
- **Swagger UI**: `http://localhost:9000/docs`
- **ReDoc**: `http://localhost:9000/redoc`

All API endpoints are mounted under `/api/v1/`:
- `/api/v1/intake/` - Intake case management
- `/api/v1/parsing/` - Attachment parsing
- `/api/v1/classification/` - Classification recommendations and decisions
- `/api/v1/vins/` - VIN extraction and validation
- `/api/v1/audit/` - Audit trail
- `/api/v1/auth/` - Authentication

## Development

### Backend Development

```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install .

# Install development dependencies
pip install .[dev]

# Run migrations
alembic upgrade head

# Run seed data
python app/seed.py

# Start development server
uvicorn app.main:app --reload --port 9000

# Run tests
pytest -v

# Run linter
ruff check app

# Run type checker
mypy app --ignore-missing-imports

# Generate migration
alembic revision --autogenerate -m "description"
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Start development server (backend must be running)
npm run dev

# Run unit tests
npm test

# Run end-to-end tests (backend and frontend must be running)
npx playwright test

# Run linter
npm run lint

# Type check
npm run type-check

# Build for production
npm run build

# Preview production build
npm run preview
```

## Docker Deployment

### Build and Run with Docker Compose

```bash
# Build images
docker compose build

# Start services
docker compose up -d

# View logs
docker compose logs -f

# Stop services
docker compose down

# Stop and remove volumes
docker compose down -v
```

The frontend will be available at `http://localhost:5173` and the backend at `http://localhost:8000`.

### Build Individual Images

```bash
# Build backend
docker build -t dim-rim-backend ./backend

# Build frontend
docker build -t dim-rim-frontend -f frontend/Dockerfile .
```

## Database Migrations

The application uses Alembic for database schema versioning.

### Create a new migration

```bash
cd backend
alembic revision --autogenerate -m "description of change"
```

### Apply migrations

```bash
alembic upgrade head
```

### Rollback one migration

```bash
alembic downgrade -1
```

### View migration history

```bash
alembic history
```

## Testing

### Backend Tests

```bash
cd backend

# Run all tests
pytest -v

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_intake_acceptance.py -v

# Run specific test
pytest tests/test_intake_acceptance.py::test_submit_inbox_email_endpoint -v
```

### Frontend Tests

```bash
cd frontend

# Run unit tests
npm test -- --run

# Run unit tests in watch mode
npm test

# Run end-to-end tests (requires backend and frontend running)
npx playwright test

# Run specific E2E test
npx playwright test e2e/wireframe_01_intake_case_workspace.spec.ts

# View E2E test report
npx playwright show-report
```

## Environment Configuration

Backend configuration is managed through environment variables. The `dev.env` file contains development defaults that are automatically copied to `.env` by `start.sh`.

### Backend Environment Variables

- `DATABASE_URL`: Database connection string (default: `sqlite:///./app.db`)
- `SECRET_KEY`: Application secret key for sessions
- `JWT_SECRET_KEY`: JWT signing key for authentication tokens
- `JWT_ALGORITHM`: JWT algorithm (default: `HS256`)
- `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time (default: 1440 = 24 hours)
- `DEBUG`: Debug mode flag (default: `true`)
- `CORS_ORIGINS`: Allowed CORS origins, comma-separated (default: `http://localhost:5173,http://localhost:3000`)
- `SEED_DATA`: Whether to seed database on startup (default: `true`)
- `RATE_LIMIT_ENABLED`: Enable/disable rate limiting (default: `false`)

### Frontend Environment Variables

Frontend uses Vite environment variables (prefixed with `VITE_`):

- `VITE_API_URL`: API base URL (default: `/api` for same-origin requests)

## Continuous Integration

The project includes a GitHub Actions CI workflow (`.github/workflows/ci.yml`) that runs on every push and pull request:

1. **Backend Tests**: Linting (ruff), type checking (mypy), migrations, unit/integration tests
2. **Frontend Tests**: Linting (eslint), type checking (tsc), unit tests (vitest), production build
3. **Docker Build**: Validates both backend and frontend Docker images build successfully

## Architecture Overview

### Backend Architecture

The backend follows a layered architecture:
- **Models**: SQLAlchemy ORM models defining database schema
- **Schemas**: Pydantic models for request/response validation
- **Repositories**: Data access layer abstracting database operations
- **Services**: Business logic orchestrating repositories and external adapters
- **Routers**: FastAPI route handlers exposing HTTP endpoints
- **Middleware**: Cross-cutting concerns (auth, CORS, error handling, logging)
- **Adapters**: Integration seams for external systems (mocked in MVP)

### Frontend Architecture

The frontend follows component-based architecture:
- **Pages**: Top-level route components (Intake, Classification, VIN Review, Audit)
- **Components**: Reusable UI components organized by domain
- **Layout**: Shared layout components (Header, Sidebar, Breadcrumbs, Stepper)
- **Lib**: API client, authentication context, utilities
- **Types**: TypeScript type definitions

### Authentication Flow

1. User submits credentials via login page
2. Backend validates credentials and returns JWT token
3. Frontend stores token in localStorage
4. All subsequent API requests include `Authorization: Bearer <token>` header
5. Backend middleware validates token on protected routes
6. On 401 response, frontend clears token and redirects to login

### Data Flow Example (Intake to Validation)

1. **Intake** (FR-001): Email received → create intake case → parse attachments
2. **Parsing** (FR-002): Extract candidate rows from Excel/CSV with lineage
3. **Classification** (FR-003): AI-assisted recommendation → human review (BR-06 AMBER gate)
4. **Extraction** (FR-004): Extract VINs → normalize → deduplicate
5. **Validation** (FR-005): Validate VIN structure → check digit verification (BR-01)
6. **Audit Trail**: All actions recorded with correlation IDs and requirement tags

## Troubleshooting

### Backend won't start

- Check Python version: `python --version` (must be 3.11+)
- Ensure virtual environment is activated
- Check database file permissions
- Review logs for migration errors

### Frontend won't start

- Check Node.js version: `node --version` (must be 20.19+/22.12+)
- Clear node_modules: `rm -rf node_modules && npm install`
- Check backend is running and accessible
- Review browser console for errors

### Tests failing

- Ensure database is clean: delete `backend/app.db` and rerun migrations
- Check all dependencies are installed
- For E2E tests, ensure both backend and frontend are running
- Review test logs for specific errors

### Docker build fails

- Check Dockerfile syntax
- Ensure all COPY paths exist
- Review build logs for missing dependencies
- Check .dockerignore isn't excluding required files

## License

Internal TMNA project - All rights reserved.

## Support

For issues or questions, please contact the development team or file an issue in the project repository.
