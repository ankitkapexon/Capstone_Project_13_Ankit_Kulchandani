from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(slots=True)
class Settings:
    reviewer_provider: str = os.getenv("REVIEWER_PROVIDER", "heuristic")
    anthropic_api_key: str | None = os.getenv("ANTHROPIC_API_KEY")
    anthropic_model: str = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-latest")
    app_name: str = os.getenv("APP_NAME", "Mobile App")


settings = Settings()
