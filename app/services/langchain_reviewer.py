from __future__ import annotations

import json
from typing import Optional

from pydantic import BaseModel, Field

from app.core.config import settings
from app.schemas.review import ReviewIssue, ReviewResponse

try:
    from anthropic import Anthropic
except ImportError:  # pragma: no cover - optional dependency path
    Anthropic = None  # type: ignore[assignment]


class ReviewAgentSchema(BaseModel):
    overall_score: int = Field(..., ge=0, le=100)
    summary: str
    issues: list[dict]
    optimized_script: str


class LangChainReviewer:
    """Claude-backed reviewer that can produce structured review output."""

    def __init__(self, model_name: Optional[str] = None) -> None:
        self.model_name = model_name or settings.anthropic_model
        self._client = Anthropic(api_key=settings.anthropic_api_key) if Anthropic is not None and settings.anthropic_api_key else None

    def review(self, script: str, app_name: str = "Unknown App") -> ReviewResponse:
        if settings.reviewer_provider != "langchain":
            raise RuntimeError("LangChain reviewer is not enabled")

        if not settings.anthropic_api_key or self._client is None:
            raise RuntimeError("ANTHROPIC_API_KEY is not configured")

        prompt = (
            "You are a Principal AI Engineer reviewing an Appium Python script. "
            "Analyze the script for XPath locators, hardcoded waits, missing explicit waits, weak assertions, "
            "duplicate code, code smells, poor naming, missing exception handling, missing logging, PEP8 issues, "
            "Page Object Model violations, and Appium best practices. "
            "Return JSON only with keys: overall_score, summary, issues, optimized_script. "
            f"App Name: {app_name}\n\nScript:\n{script}"
        )

        response = self._client.messages.create(
            model=self.model_name,
            max_tokens=1200,
            temperature=0,
            messages=[{"role": "user", "content": prompt}],
        )

        content = response.content[0].text if response.content else "{}"
        payload = json.loads(content)
        issues = [ReviewIssue(**issue) for issue in payload.get("issues", [])]
        return ReviewResponse(
            overall_score=int(payload.get("overall_score", 70)),
            summary=str(payload.get("summary", "Reviewed with Claude")),
            issues=issues,
            optimized_script=str(payload.get("optimized_script", "")),
        )
