from __future__ import annotations

from app.schemas.review import ReviewResponse
from app.services.reviewer_service import ReviewerService


class ReviewService:
    """Facade for reviewing generated Appium scripts."""

    def __init__(self, reviewer: ReviewerService | None = None) -> None:
        self.reviewer = reviewer or ReviewerService()

    def review_script(self, script: str, app_name: str = "Demo App") -> ReviewResponse:
        return self.reviewer.analyze_script(script, app_name=app_name)
