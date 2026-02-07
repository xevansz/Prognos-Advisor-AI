# Prognosis AI Backend

FastAPI backend for Prognosis AI - A multi-agent financial planning and robo-advisory system.

## Architecture

The backend follows a layered architecture:

```
backend/
├── core/           # Configuration, security, logging
├── models/         # SQLAlchemy ORM models
├── schemas/        # Pydantic schemas for API
├── services/       # Business logic layer
├── agents/         # AI agents (Risk, Goal, Investment)
├── integrations/   # External API clients (FX, Market, LLM)
├── api/            # FastAPI routers
├── alembic/        # Database migrations
├── db.py           # Database session management
└── main.py         # Application entry point
```

## Setup

### Prerequisites

- Python 3.12
- PostgreSQL database (Supabase recommended)
- PDM for dependency management

### Installation

1. Install dependencies:
```bash
pdm install
```

2. Copy `.env.example` to `.env` and configure:
```bash
cp .env.example .env
```

3. Set required environment variables in `.env`:
   - `PROGNOSIS_DATABASE_URL`: PostgreSQL connection string
   - `PROGNOSIS_LLM_API_KEY`: API key for LLM provider (optional for MVP)
   - Other optional configurations

4. Run database migrations:
```bash
pdm run alembic upgrade head
```

5. Start the development server:
```bash
pdm run python main.py
```

The API will be available at `http://localhost:8000`
API documentation at `http://localhost:8000/api/docs`

## Database Migrations

Create a new migration:
```bash
pdm run alembic revision --autogenerate -m "description"
```

Apply migrations:
```bash
pdm run alembic upgrade head
```

Rollback:
```bash
pdm run alembic downgrade -1
```

## API Endpoints

### Health
- `GET /api/health` - Health check

### Profile
- `GET /api/profile` - Get user profile
- `PUT /api/profile` - Create/update profile

### Accounts
- `GET /api/accounts` - List accounts
- `POST /api/accounts` - Create account
- `GET /api/accounts/{id}` - Get account
- `PUT /api/accounts/{id}` - Update account
- `DELETE /api/accounts/{id}` - Delete account

### Transactions
- `GET /api/transactions` - List transactions (with filters)
- `POST /api/transactions` - Create transaction
- `GET /api/transactions/{id}` - Get transaction
- `PUT /api/transactions/{id}` - Update transaction
- `DELETE /api/transactions/{id}` - Delete transaction

### Goals
- `GET /api/goals` - List goals
- `POST /api/goals` - Create goal
- `GET /api/goals/{id}` - Get goal
- `PUT /api/goals/{id}` - Update goal
- `DELETE /api/goals/{id}` - Delete goal

### Prognosis
- `POST /api/prognosis/refresh` - Generate new prognosis report
- `GET /api/prognosis/current` - Get cached report

## Multi-Agent System

### Risk Agent
Computes burn rate, runway, and risk capacity score based on recent transactions and liquid assets.

### Goal Feasibility Agent
Evaluates whether financial goals are on track, at risk, or unrealistic based on current savings rate.

### Investment Agent
Recommends asset allocation (cash, debt, equity) based on risk capacity, appetite, and goals.

### Narrator (LLM)
Synthesizes agent outputs into human-readable financial prognosis reports.

## Development

### Project Structure

- **core/**: Application configuration, security (JWT), and logging
- **models/**: Database models (User, Profile, Account, Transaction, Goal, etc.)
- **schemas/**: Pydantic models for request/response validation
- **services/**: Business logic separated from API routes
- **agents/**: Financial planning agents with pure Python logic
- **integrations/**: External API clients (FX rates, market data, LLM)
- **api/**: FastAPI routers organized by resource

### Key Features

- **Layered Architecture**: Clear separation of concerns
- **Async/Await**: Full async support with SQLAlchemy async
- **Type Safety**: Pydantic schemas and Python type hints
- **Database Migrations**: Alembic for schema versioning
- **Multi-Currency**: FX rate caching and conversion
- **Rate Limiting**: Configurable prognosis generation limits
- **Atomic Transactions**: Balance updates are atomic with transaction creation

## Testing

**TODO: Add tests**

## literature survey

current existing financial managers and how they are faring... how will your product compete and who will it compete with? dataset source, and llm model training method and its technology and science

## License

Apache License 2.0
