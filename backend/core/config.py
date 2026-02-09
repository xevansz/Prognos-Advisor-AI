from functools import lru_cache
from os import path
from pathlib import Path
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parents[1]

class Settings(BaseSettings):
    """
    Application configuration.

    Values are loaded from environment variables by default.
    """

    environment: str = "local"

    database_url: str

    supabase_jwt_audience: str | None = None
    supabase_jwt_issuer: str | None = None
    supabase_jwks_url: str | None = None

    prognosis_rate_limit_enabled: bool = False
    prognosis_max_requests_per_day: int = 5

    fx_api_key: str | None = None
    fx_api_url: str = "https://api.exchangerate-api.com/v4/latest"

    market_api_key: str | None = None
    market_api_url: str | None = None

    llm_provider: str = "gemini"
    llm_api_key: str | None = None
    llm_model: str = "gemini-1.5-flash"

    model_config = {
        "env_file": BASE_DIR / ".env",
        "env_prefix": "PROGNOSIS_",
        "extra": "ignore",
    }


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
