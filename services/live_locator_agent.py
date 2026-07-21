from __future__ import annotations

import json
import os
import re
import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Optional

from openai import OpenAI

from agents.core.live_locator_agent import LiveLocatorAgent


def extract_candidates(page_source_xml: str) -> List[Dict[str, Any]]:
    """Parse a live Appium page_source dump into a compact list of real, addressable
    UI nodes. This is the ground truth the LLM is allowed to choose from - it is
    never shown the raw XML, only this list, and every value it returns is checked
    against this same list afterwards so an invented locator cannot slip through."""
    candidates: List[Dict[str, Any]] = []
    try:
        root = ET.fromstring(page_source_xml)
    except ET.ParseError:
        return candidates

    for node in root.iter():
        resource_id = node.get("resource-id") or ""
        content_desc = node.get("content-desc") or ""
        text = node.get("text") or ""
        clickable = node.get("clickable") == "true"
        if not (resource_id or content_desc or text):
            continue
        candidates.append({
            "resource_id": resource_id,
            "content_desc": content_desc,
            "text": text,
            "class": node.get("class") or "",
            "clickable": clickable,
        })
    return candidates


def _candidate_matches(candidate: Dict[str, Any], strategy: str, value: str) -> bool:
    if strategy == "resource_id":
        return candidate["resource_id"] == value
    if strategy == "accessibility_id":
        return candidate["content_desc"] == value
    if strategy == "text":
        return candidate["text"] == value
    return False


def _validate_against_candidates(
    elements: List[Dict[str, Any]], candidates: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Drop any element whose locator_strategy/locator_value the model invented
    instead of copying verbatim from the candidate list."""
    verified: List[Dict[str, Any]] = []
    for element in elements:
        strategy = str(element.get("locator_strategy") or "")
        value = str(element.get("locator_value") or "")
        if any(_candidate_matches(c, strategy, value) for c in candidates):
            verified.append(element)
    return verified


class OpenAILiveLocatorAgent(LiveLocatorAgent):
    """Grounds each SSM element in the real, live UI hierarchy of the screen
    currently on-device, via a single JSON-mode LLM call, then deterministically
    verifies every returned locator against the candidate list before accepting it."""

    def __init__(self, model_name: str | None = None):
        self.model_name = model_name or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.api_base = os.getenv("OPENAI_API_BASE")
        self._client: Optional[OpenAI] = None

    def _get_client(self) -> OpenAI:
        if self._client is None:
            if not self.api_key:
                raise EnvironmentError("OPENAI_API_KEY is required for OpenAILiveLocatorAgent.")
            self._client = OpenAI(api_key=self.api_key, base_url=self.api_base or None)
        return self._client

    def _build_prompt(self, screen_name: str, ssm_elements: List[Dict[str, Any]], candidates: List[Dict[str, Any]]) -> str:
        return f"""You are grounding a screen's SSM (Screen Semantic Model) elements in
the REAL, live UI hierarchy captured from the device right now. You must never invent
a locator - every locator_value you return must be copied EXACTLY (character for
character) from one of the REAL_UI_ELEMENTS below.

SCREEN: {screen_name}

SSM_ELEMENTS (what the vision agent believes is on this screen):
{json.dumps(ssm_elements, indent=2)}

REAL_UI_ELEMENTS (ground truth, from a live uiautomator dump of this exact screen):
{json.dumps(candidates, indent=2)}

For each SSM element, find the REAL_UI_ELEMENT that best corresponds to it and return
a locator built from that node:
- Prefer resource_id (from "resource_id") when non-empty.
- Otherwise prefer accessibility_id (from "content_desc") when non-empty.
- Otherwise use text (from "text") when non-empty.
If no REAL_UI_ELEMENT reasonably corresponds to an SSM element (it may not actually be
on this screen, or the vision agent hallucinated it), OMIT that element entirely rather
than guessing.

Respond ONLY with JSON: {{"elements": [{{"element": <ssm label>, "element_type": <ssm type>,
"action": "tap"|"type"|"verify"|"scroll", "locator_strategy": "resource_id"|"accessibility_id"|"text",
"locator_value": <copied exactly from a REAL_UI_ELEMENT field>, "input_value": <only if action is "type">}}]}}"""

    def resolve(self, ssm_data: Dict[str, Any], page_source_xml: str) -> Dict[str, Any]:
        screen_name = ssm_data.get("screen_name") or "Screen"
        ssm_elements = ssm_data.get("elements") or []
        candidates = extract_candidates(page_source_xml)

        if not candidates:
            return {"screen": screen_name, "elements": []}

        client = self._get_client()
        # ChatOpenAI/OpenAI both default gpt-5 models to reject temperature=0 (they
        # only support the default of 1) - same quirk services/appium_agent.py
        # already works around for the script-generation LLM call.
        temperature = 1 if "gpt-5" in self.model_name.lower() else 0
        response = client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": self._build_prompt(screen_name, ssm_elements, candidates)}],
            temperature=temperature,
            response_format={"type": "json_object"},
        )
        text = response.choices[0].message.content or "{}"
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", text, re.S)
            parsed = json.loads(match.group(0)) if match else {"elements": []}

        elements = _validate_against_candidates(parsed.get("elements") or [], candidates)
        return {"screen": screen_name, "elements": elements}


class MockLiveLocatorAgent(LiveLocatorAgent):
    """Offline, deterministic grounding for tests/demos: matches SSM elements to real
    candidates by label token overlap instead of an LLM call - still refuses to invent
    a locator that isn't in the live page_source."""

    def _score(self, label: str, candidate: Dict[str, Any]) -> int:
        label_tokens = set(re.findall(r"[a-z0-9]+", label.lower()))
        candidate_text = " ".join([candidate["resource_id"], candidate["content_desc"], candidate["text"]]).lower()
        candidate_tokens = set(re.findall(r"[a-z0-9]+", candidate_text))
        return len(label_tokens & candidate_tokens)

    def resolve(self, ssm_data: Dict[str, Any], page_source_xml: str) -> Dict[str, Any]:
        screen_name = ssm_data.get("screen_name") or "Screen"
        candidates = extract_candidates(page_source_xml)
        elements: List[Dict[str, Any]] = []

        for ssm_element in ssm_data.get("elements") or []:
            label = str(ssm_element.get("label") or "")
            best = max(candidates, key=lambda c: self._score(label, c), default=None)
            if best is None or self._score(label, best) == 0:
                continue

            if best["resource_id"]:
                strategy, value = "resource_id", best["resource_id"]
            elif best["content_desc"]:
                strategy, value = "accessibility_id", best["content_desc"]
            else:
                strategy, value = "text", best["text"]

            actions = [str(a).lower() for a in ssm_element.get("actions") or []]
            action = "type" if "enter_text" in actions else "tap" if "tap" in actions else "verify"

            elements.append({
                "element": label,
                "element_type": ssm_element.get("type"),
                "action": action,
                "locator_strategy": strategy,
                "locator_value": value,
            })

        return {"screen": screen_name, "elements": _validate_against_candidates(elements, candidates)}


def create_live_locator_agent(provider: str | None = None) -> LiveLocatorAgent:
    provider = (provider or os.getenv("LOCATOR_AGENT_PROVIDER") or "").lower().strip()
    if not provider:
        provider = "openai" if os.getenv("OPENAI_API_KEY") else "mock"
    if provider == "openai":
        return OpenAILiveLocatorAgent()
    if provider == "mock":
        return MockLiveLocatorAgent()
    raise ValueError(f"Unsupported locator agent provider: {provider}")
