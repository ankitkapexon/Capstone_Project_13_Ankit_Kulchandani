from __future__ import annotations

from typing import Protocol


class ReviewRepository(Protocol):
    def save_review(self, review_payload: dict) -> dict:
        ...


class InMemoryReviewRepository:
    """Simple repository implementation for demo and testing purposes."""

    def __init__(self) -> None:
        self._reviews: list[dict] = []

    def save_review(self, review_payload: dict) -> dict:
        self._reviews.append(review_payload)
        return review_payload
