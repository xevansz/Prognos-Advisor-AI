from typing import Annotated

from fastapi import Depends, FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from sqlalchemy.ext.asyncio import AsyncSession

from api.accounts import router as accounts_router
from api.goals import router as goals_router
from api.profile import router as profile_router
from api.prognosis import router as prognosis_router
from api.transactions import router as transactions_router
from api.user import router as user_router
from core.config import settings
from core.logging import setup_logging
from core.rate_limiter import limiter
from db import get_db
from integrations.fx_client import get_cached_rates

setup_logging()

app = FastAPI(
    title="Prognosis AI API",
    version="0.2.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

# Add rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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


@app.get("/api/fx-rates")
async def get_fx_rates(
    base: Annotated[str, Query(min_length=3, max_length=3)] = "USD",
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Return cached FX rates for the given base currency.
    Reuses the same cache as the prognosis engine.
    """
    rates = await get_cached_rates(db, base.upper())
    return {"base": base.upper(), "rates": rates}


app.include_router(profile_router)
app.include_router(accounts_router)
app.include_router(transactions_router)
app.include_router(goals_router)
app.include_router(prognosis_router)
app.include_router(user_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
