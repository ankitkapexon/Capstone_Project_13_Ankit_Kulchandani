from __future__ import annotations

import os
import tempfile
from typing import Any

from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel, Field

from agents.vision_agent import create_vision_agent
from app.repositories.report_repository import JsonReportRepository
from app.schemas.review import ReviewResponse
from app.services.execution_service import ExecutionService
from app.services.generation_service import TestGenerationService
from app.services.review_service import ReviewService

app = FastAPI(title="AI Powered Mobile Test Automation Generator", version="1.0.0")
review_service = ReviewService()
generation_service = TestGenerationService()
execution_service = ExecutionService()
report_repository = JsonReportRepository()


def _get_vision_agent():
    """Constructed per-call (not at import time) so VISION_AGENT_PROVIDER can be
    overridden per-environment/test without needing to reload this module."""
    provider = os.getenv("VISION_AGENT_PROVIDER") or ("openai" if os.getenv("OPENAI_API_KEY") else "mock")
    return create_vision_agent(provider=provider)


class GenerateRequest(BaseModel):
    screen_name: str | None = Field(default=None)
    analysis: dict[str, Any] | None = Field(default=None)


class ReviewRequest(BaseModel):
    script: str = Field(..., min_length=1)
    app_name: str = Field(default="Demo App")


class GenerateBatchRequest(BaseModel):
    analyses: list[dict[str, Any]] = Field(default_factory=list)


class UploadResponse(BaseModel):
    screen_name: str
    elements_detected: int
    analysis: dict[str, Any]


class UploadBatchResponse(BaseModel):
    analyses: list[dict[str, Any]]
    count: int


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/upload", response_model=UploadResponse)
async def upload_image(file: UploadFile = File(...), screen_name: str | None = None) -> UploadResponse:
    if file.content_type not in {"image/png", "image/jpeg", "image/webp"}:
        raise HTTPException(status_code=400, detail="Unsupported image format")

    contents = await file.read()
    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File exceeds maximum size")

    temp_dir = tempfile.gettempdir()
    os.makedirs(temp_dir, exist_ok=True)
    temp_path = os.path.join(temp_dir, file.filename or "upload.png")
    with open(temp_path, "wb") as handle:
        handle.write(contents)

    analysis = _get_vision_agent().analyze_image(temp_path)
    if screen_name:
        analysis["screen_name"] = screen_name
    return UploadResponse(screen_name=analysis["screen_name"], elements_detected=len(analysis.get("elements", [])), analysis=analysis)


@app.post("/upload_batch", response_model=UploadBatchResponse)
async def upload_batch(files: list[UploadFile] = File(...)) -> UploadBatchResponse:
    if not files:
        raise HTTPException(status_code=400, detail="At least one image is required")

    analyses: list[dict[str, Any]] = []
    for file in files:
        if file.content_type not in {"image/png", "image/jpeg", "image/webp"}:
            continue

        contents = await file.read()
        if len(contents) > 5 * 1024 * 1024:
            continue

        temp_dir = tempfile.gettempdir()
        os.makedirs(temp_dir, exist_ok=True)
        temp_path = os.path.join(temp_dir, file.filename or "upload.png")
        with open(temp_path, "wb") as handle:
            handle.write(contents)

        analysis = _get_vision_agent().analyze_image(temp_path)
        analyses.append(analysis)

    return UploadBatchResponse(analyses=analyses, count=len(analyses))


@app.post("/generate")
def generate_script(payload: GenerateRequest) -> dict[str, Any]:
    analysis = payload.analysis or {
        "screen_name": payload.screen_name or "Generated Screen",
        "elements": [{"id": "primary_button", "label": "Primary action", "type": "button", "actions": ["tap"]}],
    }
    if not analysis.get("elements"):
        analysis["elements"] = [{"id": "primary_button", "label": "Primary action", "type": "button", "actions": ["tap"]}]
    if not analysis.get("screen_name"):
        analysis["screen_name"] = payload.screen_name or "Generated Screen"
    script = generation_service.generate_script(analysis)
    return {"script": script, "screen_name": analysis["screen_name"]}


@app.post("/generate_batch")
def generate_batch(payload: GenerateBatchRequest) -> dict[str, Any]:
    scripts: list[dict[str, Any]] = []
    for analysis in payload.analyses:
        normalized = dict(analysis or {})
        if not normalized.get("elements"):
            normalized["elements"] = [{"id": "primary_button", "label": "Primary action", "type": "button", "actions": ["tap"]}]
        if not normalized.get("screen_name"):
            normalized["screen_name"] = "Generated Screen"
        scripts.append({
            "screen_name": normalized["screen_name"],
            "script": generation_service.generate_script(normalized),
        })
    return {"scripts": scripts, "count": len(scripts)}


@app.post("/review", response_model=ReviewResponse)
def review_script(payload: ReviewRequest) -> ReviewResponse:
    return review_service.review_script(payload.script, app_name=payload.app_name)


@app.get("/history")
def history() -> list[dict[str, Any]]:
    return report_repository.list_reports()


@app.get("/report/{report_id}")
def report(report_id: str) -> dict[str, Any]:
    return report_repository.load(report_id)


@app.post("/execute")
def execute(payload: ReviewRequest) -> dict[str, Any]:
    report_id = f"report_{len(report_repository.list_reports()) + 1}"
    result = execution_service.run(payload.script, app_name=payload.app_name)
    report_repository.save(report_id, {"id": report_id, **result})
    return {"id": report_id, **result}
