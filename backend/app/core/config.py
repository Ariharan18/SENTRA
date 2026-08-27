"""Environment-backed application settings."""

from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parents[3]
ROOT_ENV_FILE = PROJECT_ROOT / ".env"
load_dotenv(ROOT_ENV_FILE, override=False)


class Settings(BaseSettings):
    """Runtime configuration loaded from the project-root environment file."""

    app_env: str = Field(default="development", validation_alias="APP_ENV")
    database_url: str = Field(
        default="mysql+pymysql://traffic_user@localhost:3306/traffic_db",
        validation_alias="DATABASE_URL",
    )
    jwt_secret_key: str = Field(
        default="replace-with-a-long-random-secret",
        validation_alias="JWT_SECRET_KEY",
    )
    jwt_algorithm: str = Field(default="HS256", validation_alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(
        default=60, validation_alias="ACCESS_TOKEN_EXPIRE_MINUTES"
    )
    cors_origins: str = Field(
        default="http://localhost:8501", validation_alias="CORS_ORIGINS"
    )
    mysql_database: str = Field(default="traffic_db", validation_alias="MYSQL_DATABASE")
    mysql_user: str = Field(default="traffic_user", validation_alias="MYSQL_USER")
    mysql_password: str = Field(
        default="change-this-password", validation_alias="MYSQL_PASSWORD"
    )
    congestion_high_threshold: int = Field(
        default=51, validation_alias="CONGESTION_HIGH_THRESHOLD"
    )
    congestion_severe_threshold: int = Field(
        default=76, validation_alias="CONGESTION_SEVERE_THRESHOLD"
    )

    model_config = SettingsConfigDict(
        env_file=ROOT_ENV_FILE,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def cors_origins_list(self) -> list[str]:
        """Return configured CORS origins in the form expected by FastAPI."""

        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """Return the process-wide settings instance."""

    return Settings()
