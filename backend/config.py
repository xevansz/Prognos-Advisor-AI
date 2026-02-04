from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application configuration.

    Values are loaded from environment variables by default.
    """

    environment: str = "local"  # local | dev | prod

    # Supabase
    database_url: str

    # Supabase Auth / JWT
    supabase_jwt_audience: str | None = None
    supabase_jwt_issuer: str | None = None
    supabase_jwks_url: str | None = None

    model_config = {
        "env_file": ".env",
        "env_prefix": "PROGNOSIS_",
        "extra": "ignore",
    }


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

