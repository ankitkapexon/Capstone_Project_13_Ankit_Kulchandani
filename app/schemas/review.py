from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class ReviewIssue(BaseModel):
    category: str = Field(..., description="Issue category")
    severity: str = Field(..., description="Issue severity: low/medium/high")
    title: str = Field(..., description="Short issue title")
    description: str = Field(..., description="Detailed explanation")
    recommendation: str = Field(..., description="Suggested fix")
    example_fix: str = Field(..., description="Example remediation snippet")


class ReviewResponse(BaseModel):
    overall_score: int = Field(..., ge=0, le=100)
    summary: str = Field(..., description="High-level assessment")
    issues: List[ReviewIssue] = Field(default_factory=list)
    optimized_script: str = Field(..., description="Optimized script suggestion")
