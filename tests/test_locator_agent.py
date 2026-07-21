import json
import os
import tempfile
import unittest

from agents.locator_agent import LocatorAgent


class LocatorAgentTests(unittest.TestCase):
    def test_generate_locators_uses_ssm_labels_and_preferred_strategies(self) -> None:
        agent = LocatorAgent()
        ssm_payload = {
            "screen_name": "Cart",
            "elements": [
                {
                    "label": "Checkout",
                    "type": "button",
                    "actions": ["tap"],
                    "confidence": 0.78,
                    "accessibility_id": "checkout_button",
                    "resource_id": "com.example:id/checkout",
                },
                {
                    "label": "Username",
                    "type": "textfield",
                    "actions": ["enter_text"],
                    "confidence": 0.82,
                },
            ],
        }
        test_case_text = "Verify Checkout button is displayed\nTap Checkout button"

        result = agent.generate_locators(ssm_payload, test_case_text)

        self.assertEqual(result["screen"], "Cart")
        self.assertEqual(len(result["elements"]), 1)
        locator = result["elements"][0]
        self.assertEqual(locator["element"], "Checkout")
        self.assertEqual(locator["action"], "tap")
        self.assertEqual(locator["locator_strategy"], "accessibility_id")
        self.assertEqual(locator["locator_value"], "checkout_button")

    def test_generate_locators_falls_back_to_text_when_no_real_locator_exists(self) -> None:
        # "Widget Zeta" is deliberately not one of the app-specific fallback labels
        # (login/username/cart/etc.) so this exercises the generic text fallback,
        # not the hardcoded MyDemoApp shortcut.
        agent = LocatorAgent()
        ssm_payload = {
            "screen_name": "Login",
            "elements": [
                {
                    "label": "Widget Zeta",
                    "type": "button",
                    "actions": ["tap"],
                    "confidence": 0.68,
                }
            ],
        }
        test_case_text = "Tap the Widget Zeta button"

        result = agent.generate_locators(ssm_payload, test_case_text)

        locator = result["elements"][0]
        self.assertEqual(locator["locator_strategy"], "text")
        self.assertEqual(locator["locator_value"], "widget zeta")

    def test_generate_locators_rejects_empty_test_cases(self) -> None:
        agent = LocatorAgent()
        with self.assertRaises(ValueError):
            agent.generate_locators({"screen_name": "Cart", "elements": [{"label": "Checkout"}]}, "   ")

    def test_generate_locators_rejects_invalid_json(self) -> None:
        agent = LocatorAgent()
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as handle:
            handle.write("{ invalid json }")
            temp_path = handle.name

        try:
            with self.assertRaises(ValueError):
                agent.generate_locators(temp_path, "Tap Checkout")
        finally:
            os.remove(temp_path)


if __name__ == "__main__":
    unittest.main()
