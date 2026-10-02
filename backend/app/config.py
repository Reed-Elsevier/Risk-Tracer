"""Environment-backed application settings."""

from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


REPO_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-sonnet-4-5"
    data_dir: Path = REPO_ROOT / "center_data"
    db_path: Path = REPO_ROOT / "var" / "risktracer.duckdb"
    cors_origins: str = "http://localhost:3000"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]
