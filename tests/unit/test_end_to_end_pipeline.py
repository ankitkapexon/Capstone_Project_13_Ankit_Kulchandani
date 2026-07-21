from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from agents.vision_agent import MockVisionAgent
from app.api.main import app
from app.services.generation_service import TestGenerationService
from app.services.review_service import ReviewService


@pytest.fixture(autouse=True)
def _use_mock_providers(monkeypatch: pytest.MonkeyPatch) -> None:
    """Force the deterministic mock agents so this suite never depends on a real
    OpenAI call - both agents read their provider from the environment per-call,
    so this override takes effect for every request made in this file."""
    monkeypatch.setenv("VISION_AGENT_PROVIDER", "mock")
    monkeypatch.setenv("APPIUM_AGENT_PROVIDER", "mock")


def test_upload_and_review_pipeline(tmp_path: Path) -> None:
    image_path = tmp_path / "login.png"
    image_path.write_bytes(b"fake image bytes")

    analysis = MockVisionAgent().analyze_image(str(image_path))
    assert analysis["screen_name"]
    assert analysis["elements"]

    generator = TestGenerationService()
    generated_script = generator.generate_script(analysis)
    assert "pages/" in generated_script
    assert "tests/" in generated_script
    assert "BasePage" in generated_script

    reviewer = ReviewService()
    review = reviewer.review_script(generated_script, app_name="Demo App")
    assert 0 <= review.overall_score <= 100
    assert review.optimized_script


def test_upload_analysis_is_used_for_generation() -> None:
    client = TestClient(app)

    upload_response = client.post(
        "/upload",
        files={"file": ("login.png", b"fake image bytes", "image/png")},
        data={"screen_name": "Login Screen"},
    )
    assert upload_response.status_code == 200
    analysis = upload_response.json()["analysis"]

    generate_response = client.post(
        "/generate",
        json={"screen_name": "Login Screen", "analysis": analysis},
    )
    assert generate_response.status_code == 200
    script = generate_response.json()["script"]
    assert "AppiumBy" in script


def test_batch_upload_returns_multiple_analyses() -> None:
    client = TestClient(app)

    response = client.post(
        "/upload_batch",
        files=[
            ("files", ("login.png", b"fake image bytes", "image/png")),
            ("files", ("cart.png", b"fake image bytes", "image/png")),
        ],
    )

    assert response.status_code == 200
    payload = response.json()
    assert len(payload["analyses"]) == 2
    assert payload["analyses"][0]["screen_name"]
    assert payload["analyses"][1]["screen_name"]


def test_health_and_review_endpoints() -> None:
    client = TestClient(app)

    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["status"] == "ok"

    review_payload = {"script": "def test_example():\n    assert True", "app_name": "Demo App"}
    response = client.post("/review", json=review_payload)
    assert response.status_code == 200
    assert response.json()["overall_score"] >= 0
