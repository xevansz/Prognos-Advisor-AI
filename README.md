# Prognosis AI
**A Multi-Agent System for Personalized Financial Planning & Robo-Advisory**

## Instructions to run
### 1. set up environment
* clone the repo:  
```bash
git clone https://github.com/xevansz/Prognos-Advisor-AI.git
cd Prognos-Advisor-AI
```

* Iniate the python virtual env
```bash
# Use python3.12 
cd backend
python3 -m venv .venv
source .venv/bin/activate
# or use pdm (install python 3.12)
cd backend
pdm sync
```

* create .env file and set up vars
```
PROGNOSIS_DATABASE_URL=
PROGNOSIS_LLM_PROVIDER=gemini
PROGNOSIS_LLM_API_KEY= dfjaodsifjaidsfjiasdfjdisjf
PROGNOSIS_LLM_MODEL=gemini-2.5-flash
```

### 2. Run Database Migrations
```bash
# Create initial migration
pdm run alembic revision --autogenerate -m "{number} migration"

# Apply migrations
pdm run alembic upgrade head
```

### 3. Start the Server
```bash
pdm run python main.py
```

The API will be available at:
* **API**: http://localhost:8000
* **Interactive Docs**: http://localhost:8000/api/docs
* **Health Check**: http://localhost:8000/api/health

## Project Structure Reference
```
backend/
├── core/              # Configuration, security, logging
├── models/            # Database models (10 files)
├── schemas/           # Pydantic schemas (5 files)
├── services/          # Business logic (5 files)
├── agents/            # AI agents (3 files)
├── integrations/      # External APIs (3 files)
├── api/               # FastAPI routers (6 files)
├── alembic/           # Database migrations
├── main.py            # Application entry point
├── db.py              # Database session management
├── alembic.ini        # alembic file
├── pdm.lock           # pdm
└── pyproject.toml
```

## LICENCE
* Please check the licensing information provided here: [LICENSE](./LICENSE)