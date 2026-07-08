import json
import os
from pathlib import Path
from typing import Any, Dict, List

from openai import OpenAI

from agents.core.testcase_agent import TestCaseAgent


class OpenAITestCaseAgent(TestCaseAgent):
    def __init__(self, prompt_template: str = None):
        self.prompt_template = prompt_template
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.api_base = os.getenv("OPENAI_API_BASE")
        self._client = None

    def _get_client(self) -> OpenAI:
        if self._client is None:
            self._client = OpenAI(api_key=self.api_key, base_url=self.api_base or None)
        return self._client

    def _create_chat_completion(self, client: OpenAI, prompt: str):
        request_kwargs = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1024,
        }

        if self.model.lower().startswith("gpt-5"):
            request_kwargs["temperature"] = 1
        else:
            request_kwargs["temperature"] = 0

        try:
            return client.chat.completions.create(**request_kwargs)
        except Exception as exc:
            message = str(exc)
            if "temperature" in message and "UnsupportedParamsError" in message:
                request_kwargs.pop("temperature", None)
                return client.chat.completions.create(**request_kwargs)
            raise

    def _build_prompt(self, ssm_json: str, filename: str = None) -> str:
        if self.prompt_template:
            return self.prompt_template.replace("{{ssm_json}}", ssm_json).replace("{{filename}}", filename or "ssm")
        return (
            "You are a test case generation assistant. Given the Screen Semantic Model JSON, generate a plain-text manual test case specification."
            " Do not output JSON, code, or Appium locators. Use numbered test cases and numbered steps.\n\nSSM_JSON:\n" + ssm_json
        )

    def generate_from_ssm(self, ssm_data: Dict[str, Any], **kwargs) -> str:
        try:
            client = self._get_client()
        except Exception as exc:
            raise RuntimeError("openai package is required for OpenAITestCaseAgent") from exc

        ssm_json = json.dumps(ssm_data, indent=2)
        prompt = self._build_prompt(ssm_json, filename=kwargs.get("filename"))

        try:
            resp = self._create_chat_completion(client, prompt)
            return resp.choices[0].message.content.strip()
        except Exception as exc:
            raise RuntimeError(f"Test case generation failed: {exc}")


class MockTestCaseAgent(TestCaseAgent):
    def _element_label(self, element: Dict[str, Any]) -> str:
        return element.get("label") or element.get("id") or "UI element"

    def _build_cases_from_elements(self, screen_name: str, screen_purpose: str, elements: List[Dict[str, Any]]) -> List[str]:
        lines: List[str] = []
        text_fields = [el for el in elements if str(el.get("type") or "").lower() in {"textfield", "searchbar", "input"}]
        buttons = [el for el in elements if str(el.get("type") or "").lower() in {"button", "link", "icon_button"}]
        selectable = [el for el in elements if str(el.get("type") or "").lower() in {"product_card", "list_item", "checkbox", "switch"}]

        if text_fields:
            first_field = text_fields[0]
            lines.append(f"Test Case 1: Validate input handling on {screen_name}")
            lines.append("Test ID: TC-001")
            lines.append("Priority: High")
            lines.append("Type: Functional")
            lines.append(f"Description: Verify the user can enter data into the {self._element_label(first_field)} field and that the screen validates or updates correctly.")
            lines.append("Preconditions:")
            lines.append(f"  - The {screen_name} screen is available and reachable.")
            lines.append("Steps:")
            lines.append(f"  1. Open the {screen_name} screen.")
            lines.append(f"  2. Enter sample text into the {self._element_label(first_field)} field.")
            if buttons:
                lines.append(f"  3. Tap the {self._element_label(buttons[0])} control.")
            lines.append("Expected Result:")
            lines.append("  - The entered data is accepted and the screen reacts appropriately.")
            lines.append("")

        if buttons:
            primary_button = buttons[0]
            lines.append(f"Test Case 2: Verify primary action on {screen_name}")
            lines.append("Test ID: TC-002")
            lines.append("Priority: High")
            lines.append("Type: Functional")
            lines.append(f"Description: Validate the main action exposed by the {self._element_label(primary_button)} control.")
            lines.append("Preconditions:")
            lines.append(f"  - The {screen_name} screen is displayed.")
            lines.append("Steps:")
            lines.append(f"  1. Open the {screen_name} screen.")
            lines.append(f"  2. Review the visible UI elements.")
            lines.append(f"  3. Tap the {self._element_label(primary_button)} control.")
            lines.append("Expected Result:")
            lines.append("  - The expected action is triggered or the appropriate feedback is shown.")
            lines.append("")

        if selectable:
            first_selectable = selectable[0]
            lines.append(f"Test Case 3: Verify selection interaction on {screen_name}")
            lines.append("Test ID: TC-003")
            lines.append("Priority: Medium")
            lines.append("Type: Functional")
            lines.append(f"Description: Ensure the user can select or open the {self._element_label(first_selectable)} item.")
            lines.append("Preconditions:")
            lines.append(f"  - The {screen_name} screen contains at least one selectable item.")
            lines.append("Steps:")
            lines.append(f"  1. Open the {screen_name} screen.")
            lines.append(f"  2. Locate the {self._element_label(first_selectable)} item.")
            lines.append(f"  3. Tap the {self._element_label(first_selectable)} item.")
            lines.append("Expected Result:")
            lines.append("  - The item is opened, highlighted, or transitions to the next relevant state.")
            lines.append("")

        if not lines:
            lines.append(f"Test Case 1: Validate the main screen experience for {screen_name}")
            lines.append("Test ID: TC-001")
            lines.append("Priority: Medium")
            lines.append("Type: Functional")
            lines.append(f"Description: Confirm the {screen_name} screen is displayed correctly for its purpose: {screen_purpose or 'primary user flow'}.")
            lines.append("Preconditions:")
            lines.append(f"  - The {screen_name} screen is available.")
            lines.append("Steps:")
            lines.append(f"  1. Open the {screen_name} screen.")
            lines.append("  2. Verify that the screen loads without errors.")
            lines.append("Expected Result:")
            lines.append("  - The screen appears correctly and is ready for interaction.")

        return lines

    def _build_flow_cases(self, screens: List[Dict[str, Any]]) -> List[str]:
        lines: List[str] = []
        if len(screens) < 2:
            return lines

        lines.append("End-to-End Flow 1: User journey across the main screens")
        lines.append("Test ID: E2E-001")
        lines.append("Priority: High")
        lines.append("Type: End-to-End")
        lines.append("Description: Verify the user can move through the primary application flow across the discovered screens.")
        lines.append("Preconditions:")
        lines.append("  - The app is installed and launched.")
        lines.append("Steps:")
        for index, screen in enumerate(screens, start=1):
            name = screen.get("screen_name") or f"Screen {index}"
            purpose = screen.get("screen_purpose") or ""
            lines.append(f"  {index}. Open the {name} screen{(' for ' + purpose) if purpose else ''}.")
        lines.append("Expected Result:")
        lines.append("  - The user can navigate through the screens in a logical and successful sequence without blocking errors.")
        lines.append("")
        return lines

    def generate_from_ssm(self, ssm_data: Dict[str, Any], **kwargs) -> str:
        if isinstance(ssm_data, dict) and isinstance(ssm_data.get("screens"), list):
            screens = ssm_data["screens"]
            lines = ["Manual test cases generated from the vision SSM JSON:", ""]
            for screen in screens:
                screen_name = screen.get("screen_name") or "Unnamed Screen"
                screen_purpose = screen.get("screen_purpose", "")
                elements = screen.get("elements", [])
                lines.extend([f"Screen: {screen_name}", ""])
                lines.extend(self._build_cases_from_elements(screen_name, screen_purpose, elements))
                lines.append("")
            lines.extend(self._build_flow_cases(screens))
            return "\n".join(lines)

        screen_name = ssm_data.get("screen_name") or "Unnamed Screen"
        screen_purpose = ssm_data.get("screen_purpose", "")
        elements = ssm_data.get("elements", [])

        lines = [f"Manual test cases for {screen_name} screen:", ""]
        lines.extend(self._build_cases_from_elements(screen_name, screen_purpose, elements))
        return "\n".join(lines)


def create_testcase_agent(provider: str = None, prompt_template: str = None) -> TestCaseAgent:
    provider = (provider or os.getenv("TESTCASE_AGENT_PROVIDER") or "").lower().strip()
    if not provider:
        provider = "openai" if os.getenv("OPENAI_API_KEY") else "mock"
    if provider == "openai":
        return OpenAITestCaseAgent(prompt_template=prompt_template)
    if provider == "mock":
        return MockTestCaseAgent()
    raise ValueError(f"Unsupported testcase provider: {provider}")
