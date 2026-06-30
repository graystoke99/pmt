from dataclasses import dataclass
from pathlib import Path
import os


def _default_database_path() -> str:
    base_dir = Path(__file__).resolve().parents[1]
    return str(base_dir / "data" / "app.db")


@dataclass(frozen=True)
class Settings:
    app_name: str = "Project Management MVP Backend"
    database_path: str = _default_database_path()
    allowed_origins: tuple[str, ...] = (
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    )


def get_settings() -> Settings:
    configured_path = os.getenv("PM_DATABASE_PATH", _default_database_path())
    return Settings(database_path=configured_path)