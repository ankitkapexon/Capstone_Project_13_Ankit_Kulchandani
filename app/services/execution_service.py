from __future__ import annotations

import json
import os
from html import escape
from pathlib import Path
from typing import Any
from urllib.error import URLError

from app.core.logging_config import configure_logging

try:
    from appium import webdriver
    from appium.options.android import UiAutomator2Options
except ImportError:  # pragma: no cover - optional dependency path
    webdriver = None  # type: ignore[assignment]
    UiAutomator2Options = None  # type: ignore[assignment]


class ExecutionService:
    """Simple execution/reporting service for generated automation artifacts."""

    def __init__(self, output_dir: str | None = None) -> None:
        self.output_dir = Path(output_dir or "artifacts/reports")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger = configure_logging()

    def run(self, script: str, app_name: str = "Demo App") -> dict[str, Any]:
        base_name = app_name.lower().replace(" ", "_")
        report_path = self.output_dir / f"{base_name}_report.json"
        html_path = self.output_dir / f"{base_name}_report.html"
        payload = {
            "app_name": app_name,
            "status": "completed",
            "summary": "Execution placeholder completed successfully",
            "script_preview": script[:400],
        }

        if webdriver is not None:
            appium_server = os.getenv("APPIUM_SERVER_URL", "http://127.0.0.1:4723")
            options = UiAutomator2Options()
            options.platform_name = "Android"
            options.device_name = os.getenv("ANDROID_DEVICE_NAME", "Android Emulator")
            options.automation_name = "UiAutomator2"
            android_app_path = os.getenv("ANDROID_APP_PATH")
            if android_app_path:
                options.app = android_app_path
            try:
                session = webdriver.Remote(appium_server, options=options)
                try:
                    payload.update({"status": "completed", "summary": f"Opened a live Appium session at {appium_server}"})
                finally:
                    session.quit()
            except URLError as exc:  # pragma: no cover - environment-dependent
                payload.update({"status": "completed", "summary": f"Appium unavailable, saved fallback report: {exc}"})
            except Exception as exc:  # pragma: no cover - environment-dependent
                payload.update({"status": "completed", "summary": f"Appium unavailable, saved fallback report: {exc}"})

        report_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        html_content = f"""<!DOCTYPE html>
<html lang=\"en\">
  <head>
    <meta charset=\"utf-8\" />
    <title>Execution Report</title>
    <style>body {{ font-family: Arial, sans-serif; margin: 2rem; }} .card {{ border: 1px solid #ddd; padding: 1rem; border-radius: 8px; }} pre {{ background: #f7f7f7; padding: 1rem; border-radius: 6px; }}</style>
  </head>
  <body>
    <div class=\"card\">
      <h1>Execution Report</h1>
      <p><strong>App:</strong> {escape(app_name)}</p>
      <p><strong>Status:</strong> {escape(payload['status'])}</p>
      <p><strong>Summary:</strong> {escape(payload['summary'])}</p>
      <pre>{escape(payload['script_preview'])}</pre>
    </div>
  </body>
</html>"""
        html_path.write_text(html_content, encoding="utf-8")
        self.logger.info("Wrote execution report for %s at %s and %s", app_name, report_path, html_path)
        return {
            "status": payload["status"],
            "report_path": str(report_path),
            "html_report_path": str(html_path),
            "summary": payload["summary"],
        }
