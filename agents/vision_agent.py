import base64
import json
import os
from pathlib import Path
from typing import Any, Dict

from openai import OpenAI
from pydantic import ValidationError

from agents.core.vision_agent import VisionAgent
from models.ssm import ScreenSemanticModel


class OpenAIVisionAgent(VisionAgent):
    """Adapter for OpenAI-style multimodal models."""

    def __init__(self, prompt_template: str | None = None, model_name: str | None = None):
        super().__init__(model_name=model_name or os.getenv("OPENAI_MODEL", "gpt-4o-mini"))
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.api_base = os.getenv("OPENAI_API_BASE")
        self.prompt_template = prompt_template
        self._client = None

    def validate_configuration(self) -> None:
        if not self.api_key:
            raise EnvironmentError("OPENAI_API_KEY is required for OpenAIVisionAgent.")

    def _get_client(self) -> OpenAI:
        if self._client is None:
            self._client = OpenAI(api_key=self.api_key, base_url=self.api_base or None)
        return self._client

    def _create_chat_completion(self, client: OpenAI, prompt: str):
        request_kwargs = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1024,
        }

        if "gpt-5" in str(self.model_name).lower():
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

    def _infer_screen_name(self, raw_name: str | None, image_path: str | None = None, screen_purpose: str | None = None) -> str | None:
        if raw_name:
            normalized = str(raw_name).strip()
            if normalized.lower() not in {"unknown", "unspecified", "n/a", "none", "screen", ""}:
                return normalized

        stem = Path(image_path).stem if image_path else ""
        normalized_stem = stem.lower().replace(" ", "_").replace("-", "_")

        if "login" in normalized_stem:
            return "Login"
        if "cart" in normalized_stem:
            return "Cart"
        if "detail" in normalized_stem or "product_detail" in normalized_stem or "productdetails" in normalized_stem:
            return "Product Details"
        if "listing" in normalized_stem or "product_listing" in normalized_stem or "productlist" in normalized_stem or "products" in normalized_stem or "search" in normalized_stem:
            return "Product Listing"
        if "checkout" in normalized_stem:
            return "Checkout"
        if "home" in normalized_stem:
            return "Home"
        if "profile" in normalized_stem:
            return "Profile"
        if "settings" in normalized_stem:
            return "Settings"

        if screen_purpose:
            purpose = screen_purpose.lower()
            if "login" in purpose or "authenticate" in purpose:
                return "Login"
            if "cart" in purpose or "checkout" in purpose:
                return "Cart"
            if "detail" in purpose:
                return "Product Details"
            if "listing" in purpose or "search" in purpose or "product" in purpose:
                return "Product Listing"

        return raw_name or None

    def _build_prompt(self, image_b64: str, filename: str | None = None) -> str:
        if self.prompt_template:
            return self.prompt_template.replace("{{image_b64}}", image_b64).replace("{{filename}}", filename or "image")
    
        return f"""
                You are an expert Mobile UI Understanding Assistant.

                Analyze the mobile app screenshot and return ONLY valid JSON matching the ScreenSemanticModel schema.

                Rules:

                1. Detect every visible UI element.

                2. IMPORTANT:
                If a label is immediately followed by an editable text box, treat them as TWO separate elements.

                Example:

                Username
                [ empty input box ]

                Generate:

                {
                "label": "Username",
                "type": "label"
                }

                {
                "label": "Username Input",
                "type": "textfield"
                }

                Similarly:

                Password
                [ empty input box ]

                Generate:

                {
                "label": "Password",
                "type": "label"
                }

                {
                "label": "Password Input",
                "type": "password_field"
                }

                Buttons remain buttons.

                Never classify a label as a text field.

                Respond ONLY with valid JSON.

                IMAGE_BASE64:
                {image_b64}
                """

    def analyze_image(self, image_path: str, **kwargs) -> Dict[str, Any]:
        self.validate_configuration()
        with open(image_path, "rb") as f:
            img_bytes = f.read()
        image_b64 = base64.b64encode(img_bytes).decode("utf-8")

        prompt = self._build_prompt(image_b64, filename=os.path.basename(image_path))

        try:
            client = self._get_client()
            resp = self._create_chat_completion(client, prompt)
            text = resp.choices[0].message.content.strip()
        except Exception as exc:
            raise RuntimeError(f"Vision model call failed: {exc}")

        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            import re

            match = re.search(r"\{.*\}", text, re.S)
            if not match:
                raise ValueError("Model response did not contain valid JSON")
            parsed = json.loads(match.group(0))

        try:
            ssm = ScreenSemanticModel.model_validate(parsed)
        except ValidationError as ve:
            raise ValueError(f"Response validation failed: {ve}")

        inferred_name = self._infer_screen_name(ssm.screen_name, image_path=image_path, screen_purpose=ssm.screen_purpose)
        if inferred_name:
            ssm.screen_name = inferred_name

        return ssm.model_dump()


class MockVisionAgent(VisionAgent):
    """Mock agent for local pipeline testing without a real model provider."""

    def analyze_image(self, image_path: str, **kwargs) -> Dict[str, Any]:
        stem = Path(image_path).stem
        return {
            "screen_name": stem.replace("_", " ").title(),
            "screen_purpose": "Understand the primary action for this screen.",
            "source": image_path,
            "elements": [
                {
                    "id": "action_1",
                    "label": "Primary button",
                    "type": "button",
                    "actions": ["tap"],
                    "confidence": 0.75,
                },
                {
                    "id": "field_1",
                    "label": "Input field",
                    "type": "textfield",
                    "actions": ["enter_text"],
                    "confidence": 0.65,
                },
            ],
            "metadata": {
                "note": "Mock output; replace with real vision provider for production.",
            },
        }


def create_vision_agent(provider: str = "openai", prompt_template: str = None) -> VisionAgent:
    provider = provider.lower().strip()
    if provider == "openai":
        return OpenAIVisionAgent(prompt_template=prompt_template)
    if provider == "mock":
        return MockVisionAgent()
    raise ValueError(f"Unsupported vision provider: {provider}")
