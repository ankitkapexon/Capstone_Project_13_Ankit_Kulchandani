from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from services.appium_agent import create_appium_agent, load_locator_data, load_navigation_steps

ROOT = Path(__file__).resolve().parents[2]


class TestGenerationService:
    """Builds an Appium Page Object + pytest test module from structured screen
    analysis, using the same LLM-backed, locator/navigation-aware generator as the
    command-line pipeline (services/appium_agent.py) - no separate template logic."""

    def generate_script(self, analysis: dict[str, Any]) -> str:
        screen_name = analysis.get("screen_name") or "Screen"
        ssm_data = {"screen_name": screen_name, "elements": analysis.get("elements") or []}

        locator_data = load_locator_data(screen_name)
        navigation_steps = load_navigation_steps(screen_name)

        provider = os.getenv("APPIUM_AGENT_PROVIDER") or ("openai" if os.getenv("OPENAI_API_KEY") else "mock")
        prompt_path = ROOT / "prompts" / "appium_script_generation.txt"
        prompt_template = prompt_path.read_text(encoding="utf-8") if prompt_path.exists() else None
        agent = create_appium_agent(provider=provider, prompt_template=prompt_template)

        files = agent.generate(
            ssm_data,
            testcases_text="",
            filename=screen_name,
            locator_data=locator_data,
            navigation_steps=navigation_steps,
        )

        return "\n\n".join(f'# --- {path} ---\n{content}' for path, content in files.items())
