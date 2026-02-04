from fastapi import FastAPI

from config import settings

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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
