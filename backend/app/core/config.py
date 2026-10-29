"""Application settings loaded from environment / .env file."""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: str = "development"
    simulation_mode: bool = True
    log_level: str = "INFO"

    database_url: str = "sqlite:///./sentinel_test.db"
    redis_url: str = "redis://localhost:6379/0"
    opensearch_host: str = "http://localhost:9200"
    opensearch_index_events: str = "security-events"

    jwt_secret: str = "dev-insecure-secret-change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    seed_admin_email: str = "admin@sentinel.local"
    seed_admin_password: str = "ChangeMe123!"

    llm_provider: str = "mock"
    llm_api_key: str = ""
    llm_base_url: str = ""
    llm_model: str = ""

    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
