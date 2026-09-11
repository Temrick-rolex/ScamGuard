from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "ScamGuard API"
    environment: str = "development"
    api_prefix: str = "/api/v1"

    database_url: str = "sqlite:///./scamguard.db"

    jwt_secret: str = "change-me-in-env"
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 15
    refresh_token_days: int = 14

    login_max_attempts: int = 5
    login_window_minutes: int = 15

    admin_email: str = "admin@scamguard.cm"
    admin_password: str = "ChangeMe#2026"

    allowed_origins: str = "*"

    @property
    def origins(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",")]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
