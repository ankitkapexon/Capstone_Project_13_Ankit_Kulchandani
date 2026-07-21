from __future__ import annotations

from fastapi.testclient import TestClient

import app.services.execution_service as execution_module
from app.api.main import app


def test_execute_endpoint_persists_report() -> None:
    client = TestClient(app)
    response = client.post(
        "/execute",
        json={"script": "def test_example():\n    assert True", "app_name": "Demo App"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "completed"
    assert payload["id"].startswith("report_")


def test_execution_service_uses_appium_options(monkeypatch, tmp_path) -> None:
    observed: dict[str, object] = {}

    class FakeDriver:
        def quit(self) -> None:
            return None

    def fake_remote(command_executor, extensions=None, options=None, client_config=None):
        observed["command_executor"] = command_executor
        observed["options"] = options
        return FakeDriver()

    monkeypatch.setattr(execution_module, "webdriver", type("FakeWebdriver", (), {"Remote": staticmethod(fake_remote)}))

    service = execution_module.ExecutionService(str(tmp_path))
    result = service.run("def test_example():\n    assert True", app_name="Demo App")

    assert result["status"] == "completed"
    assert observed["options"] is not None
