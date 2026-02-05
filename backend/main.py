from fastapi import FastAPI

from api.accounts import router as accounts_router
from api.goals import router as goals_router
from api.profile import router as profile_router
from api.prognosis import router as prognosis_router
from api.transactions import router as transactions_router
from core.config import settings
from core.logging import setup_logging

setup_logging()

app = FastAPI(
    title="Prognosis AI API",
    version="0.1.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)


@app.get("/api/health")
async def health_check() -> dict:
    """
    Simple health endpoint for uptime monitoring.
    """
    return {
        "status": "ok",
        "environment": settings.environment,
        "app_version": app.version,
    }


app.include_router(profile_router)
app.include_router(accounts_router)
app.include_router(transactions_router)
app.include_router(goals_router)
app.include_router(prognosis_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
