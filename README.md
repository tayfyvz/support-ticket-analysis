# Support Ticket Analyst

An AI-powered support ticket management system that automatically analyzes, categorizes, and prioritizes support tickets using LangGraph and OpenAI's GPT models.

## Quickstart

### Prerequisites

- **Docker** (version 20.10 or later)
- **Docker Compose** (version 2.0 or later)
- **OpenAI API Key** (for ticket analysis)

### Running the Project

1. **Clone the repository** (if you haven't already):
   ```bash
   git clone <repository-url>
   cd support-ticket-analysis
   ```

2. **Set up environment variables**:
   
   Create a `.env` file in the **project root** directory (same level as `docker-compose.yml`):
   ```env
   OPENAI_API_KEY=sk-your-openai-api-key-here
   ```
   
   > **Note:** The database URL is automatically configured in `docker-compose.yml` and doesn't need to be set in `.env`. Docker Compose will automatically load the `.env` file from the project root.

3. **Start all services**:
   ```bash
   docker compose up --build
   ```

4. **Access the application**:
   - **Frontend**: http://localhost:8080
   - **Backend API**: http://localhost:8000
   - **API Documentation**: http://localhost:8000/docs
   - **Database**: localhost:5432

### Default Ports

- **Frontend**: `8080`
- **Backend API**: `8000`
- **PostgreSQL**: `5432`

### Stopping the Services

```bash
docker compose down
```

To also remove volumes (database data):
```bash
docker compose down -v
```

## Configuration

### Environment Variables

The application uses environment variables for configuration. 

**For Docker (recommended):**
- Create a `.env` file in the **project root** directory (same level as `docker-compose.yml`)
- Docker Compose automatically loads variables from this file
- The `OPENAI_API_KEY` from `.env` will be passed to the backend service

**For local development (without Docker):**
- Create a `.env` file in the project root
- The application will automatically load it via `python-dotenv` and `pydantic-settings`

#### Required Variables

- `OPENAI_API_KEY`: Your OpenAI API key for ticket analysis
  - **Required for the LLM analysis to work**
  - **Getting your API key:**
    1. Go to https://platform.openai.com/api-keys
    2. Sign in or create an account
    3. Click "Create new secret key"
    4. Copy the key and paste it in your `.env` file
  - **Important:** Never commit your `.env` file to version control. It should already be in `.gitignore`.

#### Optional Variables

- `DATABASE_URL`: PostgreSQL connection string (defaults to Docker service URL)
  - Format: `postgresql+asyncpg://user:password@host:port/database`
  - Default in Docker: `postgresql+asyncpg://postgres:postgres@db:5432/support_tickets`

### Database Connection

The backend uses **SQLAlchemy** with **asyncpg** for async PostgreSQL operations. The connection is configured in:
- `backend/app/core/config.py` - Settings and configuration
- `backend/app/db/session.py` - Database session management

The database tables are automatically created on startup via SQLAlchemy's `Base.metadata.create_all()` in the FastAPI lifespan event.

### LLM Configuration

The application uses **LangGraph** with **OpenAI's GPT-4o-mini** model for ticket analysis:

- **Model**: `gpt-4o-mini` (configured in `backend/app/services/llm_service.py`)
- **Temperature**: `0` (deterministic output)
- **API Key**: Set via `OPENAI_API_KEY` environment variable

The LangGraph agent implements a **Map-Reduce** pattern:
1. **Map Step**: Classifies each ticket individually (category, priority, notes)
2. **Reduce Step**: Generates an executive summary of all analyzed tickets

Prompts are defined in `backend/app/prompts/ticket_analysis.py` with clear priority guidelines to ensure accurate classification.

## API Overview

### Base URL

- **Local**: `http://localhost:8000`
- **Docker**: `http://backend:8000` (internal)

### Endpoints

#### Tickets

**POST `/api/tickets`**
- Create one or more tickets
- **Request Body**: `[{ "title": string, "description": string }]`
- **Response**: `[{ "id": int, "title": string, "description": string, "created_at": datetime, "status": string }]`
- **Status Code**: `201`

**GET `/api/tickets`**
- List tickets with pagination (defaults to PENDING status)
- **Query Parameters**:
  - `page` (int, default: 1): Page number
  - `page_size` (int, default: 10, max: 1000): Items per page
  - `status` (string, optional): Filter by status (`pending`, `processing`, `analyzed`, `failed`)
- **Response**: `{ "items": [...], "page": int, "page_size": int }`

**GET `/api/tickets/analyzed`**
- List analyzed tickets with analysis details
- **Query Parameters**: Same as above
- **Response**: `{ "items": [{ "id": int, "analysis_id": int, "title": string, "description": string, "category": string, "priority": string, "notes": string | null }], "page": int, "page_size": int }`

#### Analysis

**POST `/api/analyze`**
- Start analysis of tickets (returns immediately, processes in background)
- **Request Body**: `{ "ticketIds": [int] | null }` (null = analyze all pending tickets)
- **Response**: `{ "id": int, "created_at": datetime, "summary": string, "ticket_analyses": [...] }`
- **Status Code**: `201`
- **Note**: Analysis runs asynchronously. Use status endpoint to check progress.

**GET `/api/analyze/runs`**
- List all analysis runs with pagination
- **Query Parameters**: `page` (int), `page_size` (int, max: 100)
- **Response**: `{ "items": [{ "id": int, "created_at": datetime, "summary": string, "ticket_count": int, "status": string }], "page": int, "page_size": int, "total": int }`

**GET `/api/analyze/{analysis_run_id}`**
- Get detailed information about a specific analysis run
- **Response**: `{ "id": int, "created_at": datetime, "summary": string, "ticket_analyses": [...] }`

**GET `/api/analyze/{analysis_run_id}/status`**
- Get current status of an analysis run
- **Response**: `{ "analysis_run_id": int, "status": string, "ticket_ids": [int] }`
- **Status values**: `pending`, `processing`, `completed`, `failed`

**GET `/api/analyze/active`**
- Get all active analysis runs (with processing or pending tickets)
- **Response**: `[{ "analysis_run_id": int, "status": string, "ticket_ids": [int] }]`

### Health Check

**GET `/healthz`**
- Health check endpoint
- **Response**: `{ "status": "ok" }`

### API Documentation

Interactive API documentation is available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Architecture Notes

### Tech Stack

**Backend:**
- **Python 3.12+**: Programming language
- **FastAPI**: Modern, fast Python web framework
- **SQLAlchemy**: ORM with async support
- **PostgreSQL**: Relational database
- **LangGraph**: Agent framework for LLM orchestration
- **LangChain OpenAI**: LLM integration
- **Pydantic**: Data validation and settings management
- **pydantic-settings**: Settings management from environment variables
- **python-dotenv**: Environment variable loading from .env files
- **uvicorn**: ASGI server
- **asyncpg**: Async PostgreSQL driver
- **uv**: Python package manager (used in Dockerfile)

**Frontend:**
- **React 19**: UI framework
- **TypeScript**: Type safety
- **Vite**: Build tool and dev server
- **Zustand**: State management
- **ESLint**: Code linting
- **CSS**: Custom styling (no UI framework)

### Directory Structure

```
support-ticket-analysis/
├── backend/
│   ├── app/
│   │   ├── api/              # FastAPI route handlers
│   │   │   ├── tickets.py    # Ticket endpoints
│   │   │   └── analysis.py   # Analysis endpoints
│   │   ├── core/             # Configuration
│   │   ├── db/               # Database session management
│   │   ├── models/           # SQLAlchemy ORM models
│   │   ├── schemas/          # Pydantic request/response models
│   │   ├── services/         # Business logic
│   │   │   ├── ticket_service.py
│   │   │   ├── analysis_service.py
│   │   │   └── llm_service.py  # LangGraph agent
│   │   ├── prompts/          # LLM prompt templates
│   │   └── main.py           # FastAPI app entry point
│   ├── tests/                # Test suite
│   ├── Dockerfile
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── api/              # API client
│   │   ├── components/       # React components
│   │   ├── store/            # Zustand stores
│   │   ├── types/            # TypeScript types
│   │   └── App.tsx
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml
└── README.md
```

### LangGraph Agent Integration

The LangGraph agent is integrated as follows:

1. **Service Layer** (`analysis_service.py`):
   - Creates analysis run and marks tickets as `PROCESSING`
   - Spawns background task for LLM processing
   - Returns immediately with analysis run ID

2. **Background Processing**:
   - Uses FastAPI's `BackgroundTasks` to run async processing
   - Creates new database session for background work
   - Calls `LLMService.analyze_tickets()` with ticket data

3. **LLM Service** (`llm_service.py`):
   - Implements Map-Reduce pattern with LangGraph
   - **Map**: Classifies each ticket in parallel (max 5 concurrent)
   - **Reduce**: Generates executive summary
   - Returns structured data (category, priority, notes)

4. **Database Updates**:
   - Creates `TicketAnalysis` records for each ticket
   - Updates ticket status to `ANALYZED` or `FAILED`
   - Updates analysis run summary

### Tradeoffs and Shortcuts

Due to time constraints, the following shortcuts were taken:

1. **Database Migrations**: Using `Base.metadata.create_all()` for automatic table creation on startup. No migration system is implemented - schema changes require manual database updates or recreation.

2. **Error Handling**: Basic error handling in place. More comprehensive error handling, retry logic, and error recovery would be added in production.

3. **Background Tasks**: Using FastAPI's built-in `BackgroundTasks` instead of a proper task queue (Celery, RQ). This works for development but doesn't scale well and tasks are lost on server restart.

4. **Authentication/Authorization**: Not implemented. All endpoints are publicly accessible.

5. **Rate Limiting**: No rate limiting on API endpoints.

6. **Caching**: No caching layer. All database queries are direct.

7. **Monitoring/Logging**: Basic logging only. No metrics, tracing, or structured logging.

8. **Testing**: Unit tests for API endpoints exist, but integration tests and E2E tests are not included.

9. **Frontend Error Handling**: Basic error states, but no retry logic or offline support.

## Development

### Running Tests

```bash
cd backend
# Install test dependencies using uv (recommended)
uv sync --extra test
# or using pip
pip install -e ".[test]"

# Run all tests
uv run pytest tests/ -v
# or
pytest tests/ -v

# Run specific test file
pytest tests/test_tickets_api.py -v
```

### Local Development (without Docker)

**Backend:**
```bash
cd backend
# Install dependencies using uv (recommended)
uv sync
# or using pip
pip install -e .

# Create .env file at project root with:
# OPENAI_API_KEY=your-key-here
# DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/support_tickets

# Run server
uv run uvicorn app.main:app --reload --port 8000
# or
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

**Database:**
```bash
# Start PostgreSQL (or use Docker)
docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=support_tickets postgres:16-alpine
```

## Future Improvements

With more time, the following improvements would be prioritized:

### Backend

- [ ] **Proper Task Queue**: Replace `BackgroundTasks` with Celery or RQ for reliable background processing
- [ ] **Database Migrations**: Implement a migration system (Alembic or similar) for schema versioning
- [ ] **Rate Limiting**: Implement rate limiting on API endpoints
- [ ] **Caching**: Add Redis for caching frequently accessed data
- [ ] **Error Handling**: Comprehensive error handling with retry logic and dead letter queues
- [ ] **Monitoring**: Add Prometheus metrics, structured logging, and distributed tracing
- [ ] **Testing**: Expand test coverage with integration tests and E2E tests
- [ ] **API Versioning**: Implement API versioning strategy
- [ ] **Webhooks**: Add webhook support for analysis completion events
- [ ] **Batch Processing**: Optimize LLM calls with better batching strategies
- [ ] **Concurrent Analysis Limits**: Implement maximum number of concurrent analyses to prevent resource exhaustion
- [ ] **Analysis Locking Mechanism**: Add locking mechanism to prevent analyzing the same tickets simultaneously and handle concurrent analysis requests gracefully
- [ ] **Cost Optimization**: Add token usage tracking and cost monitoring

### Frontend

- [ ] **Error Recovery**: Add retry logic and better error boundaries
- [ ] **Offline Support**: Implement service worker for offline functionality
- [ ] **Real-time Updates**: Add WebSocket support for live analysis status updates
- [ ] **Performance**: Implement virtual scrolling for large ticket lists
- [ ] **Testing**: Add unit tests for components and E2E tests with Playwright
- [ ] **State Management**: Consider adding optimistic updates
- [ ] **UI/UX**: Add loading skeletons, better animations, and improved mobile responsiveness

### Infrastructure

- [ ] **CI/CD**: Set up GitHub Actions for automated testing and deployment
- [ ] **Containerization**: Optimize Docker images (multi-stage builds, smaller base images)
- [ ] **Database**: Add read replicas for scaling, connection pooling optimization
- [ ] **Backup Strategy**: Implement automated database backups
- [ ] **Environment Management**: Separate dev/staging/prod environments

### Features

- [ ] **Ticket Search**: Full-text search across tickets
- [ ] **Filters**: Advanced filtering and sorting options
- [ ] **Custom Categories**: Allow users to define custom ticket categories
- [ ] **Assignments**: Assign tickets to team members
- [ ] **Integration**: Integrate with external ticketing systems (Jira, Zendesk, etc.)

## License

[Add your license here]

## Contributing

[Add contributing guidelines here]

