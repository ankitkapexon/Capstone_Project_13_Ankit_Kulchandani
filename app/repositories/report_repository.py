from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class JsonReportRepository:
    """Simple JSON-backed repository for reports and execution history."""

    def __init__(self, storage_dir: str | None = None) -> None:
        self.storage_dir = Path(storage_dir or "artifacts/reports")
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def save(self, report_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        path = self.storage_dir / f"{report_id}.json"
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return payload

    def load(self, report_id: str) -> dict[str, Any]:
        path = self.storage_dir / f"{report_id}.json"
        return json.loads(path.read_text(encoding="utf-8"))

    def list_reports(self) -> list[dict[str, Any]]:
        return [json.loads(path.read_text(encoding="utf-8")) for path in sorted(self.storage_dir.glob("*.json"))]
