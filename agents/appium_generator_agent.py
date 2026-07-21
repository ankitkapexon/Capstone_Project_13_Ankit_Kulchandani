import json
import os
from typing import Any, Dict
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from navigation_agent import NavigationAgent

try:
    from appium.webdriver.common.appiumby import AppiumBy  # type: ignore
except ImportError:  # pragma: no cover - environment dependent
    AppiumBy = None  # type: ignore

try:
    from selenium.webdriver.support import expected_conditions as EC  # type: ignore
    from selenium.webdriver.support.ui import WebDriverWait  # type: ignore
except ImportError:  # pragma: no cover - environment dependent
    EC = None  # type: ignore
    WebDriverWait = None  # type: ignore


class AppiumGeneratorAgent:
    """Generate Android Appium pytest scripts from locator JSON artifacts."""

    def __init__(self, project_root: Optional[Path | str] = None) -> None:
        self.project_root = Path(project_root or Path(__file__).resolve().parents[1])
        self.input_dir = self.project_root / "artifacts" / "locator_output"
        self.output_dir = self.project_root / "artifacts" / "generated_appium_scripts"
        self.navigation_agent = NavigationAgent()

    def generate_script_for_locator(self, locator_payload: Dict[str, Any]) -> str:
        """Create one pytest-style Appium script from a locator payload."""
        screen_name = self._screen_name_from_payload(locator_payload)
        class_name = self._to_class_name(screen_name)
        test_name = self._to_test_name(screen_name)
        script_name = self._to_script_name(screen_name)

        elements = locator_payload.get("elements") or []
        if not elements:
            raise ValueError("Locator payload does not contain any elements.")

        step_lines = self._build_step_lines(screen_name, elements)

        return f'''"""Generated Appium pytest script for {screen_name}."""

import os

from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class {class_name}:
    """Example Appium test class for the {screen_name} screen."""

    def setup_method(self) -> None:
        """Create the Appium driver and explicit wait before each test."""
        desired_caps = {{
            "platformName": "Android",
    "automationName": "UiAutomator2",
    "deviceName": "Android Emulator",
    "app": "C:/Users/Reshma.R/MobileAppTesting/capstone-cross-platform-mobile-test-script-generator/demo_mobile_apps/mda-2.2.0-25.apk",
    "appPackage": "com.saucelabs.mydemoapp.android",
    "appActivity": "com.saucelabs.mydemoapp.android.view.activities.SplashActivity",
    "noReset": True,
        }}
        self.driver = self._create_driver(desired_caps)
        self.wait = WebDriverWait(self.driver, 10) if WebDriverWait is not None else None

    def teardown_method(self) -> None:
        """Quit the Appium session after the test finishes."""
        if getattr(self, "driver", None):
            self.driver.quit()

    def tap(self, locator_strategy: str, locator_value: str) -> None:
        """Tap an element using a UiAutomator2 locator and an explicit wait."""
        locator = self._build_locator(locator_strategy, locator_value)
        if self.wait is not None and EC is not None:
            element = self.wait.until(EC.element_to_be_clickable(locator))
        else:
            element = self.driver.find_element(*locator)
        element.click()

    def type(self, locator_strategy: str, locator_value: str, text: str) -> None:
        """Type text into an editable field using a UiAutomator2 locator."""
        locator = self._build_locator(locator_strategy, locator_value)
        if self.wait is not None and EC is not None:
            element = self.wait.until(EC.element_to_be_clickable(locator))
        else:
            element = self.driver.find_element(*locator)
        element.clear()
        element.send_keys(text)

    def scroll(self, locator_strategy: str, locator_value: str) -> None:
        """Scroll until a target element is visible using UiAutomator2."""
        selector = self._build_uiautomator_selector(locator_strategy, locator_value)
        scroll_command = (
            f"new UiScrollable(new UiSelector().scrollable(true)).scrollIntoView({{self._build_uiautomator_selector(locator_strategy, locator_value)}})"
        )
        self.driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, scroll_command)
        if self.wait is not None and EC is not None:
            self.wait.until(EC.visibility_of_element_located(self._build_locator(locator_strategy, locator_value)))

    def _create_driver(self, desired_caps: Dict[str, Any]) -> Any:
        """Create the Appium driver."""
        from appium import webdriver
        from appium.options.android import UiAutomator2Options

        options = UiAutomator2Options().load_capabilities(desired_caps)

        return webdriver.Remote(
            "http://127.0.0.1:4723",
            options=options,
        )

    def _build_locator(self, locator_strategy: str, locator_value: str) -> Tuple[str, str]:
        """Convert a logical locator into an Appium locator tuple."""

        if locator_strategy == "resource_id":
            return (AppiumBy.ID, locator_value)

        if locator_strategy == "accessibility_id":
            return (AppiumBy.ACCESSIBILITY_ID, locator_value)

        return (
            AppiumBy.ANDROID_UIAUTOMATOR,
            self._build_uiautomator_selector(locator_strategy, locator_value),
    )

    def _build_uiautomator_selector(self, locator_strategy: str, locator_value: str) -> str:
        """Create a UiAutomator2 selector string without using fragile XPath."""
        strategy = (locator_strategy or "text").strip().lower()
        if strategy == "accessibility_id":
            return f'new UiSelector().description("{{locator_value}}")'
        if strategy == "resource_id":
            return f'new UiSelector().resourceId("{{locator_value}}")'
        return f'new UiSelector().text("{{locator_value}}")'

    def {test_name}(self) -> None:
        """Exercise the screen actions discovered by the locator agent."""
{step_lines}
'''

    def generate_scripts_from_directory(
        self,
        input_dir: Optional[Path | str] = None,
        output_dir: Optional[Path | str] = None,
    ) -> List[Path]:
        """Generate one script for every locator JSON file in the input directory."""
        source_dir = Path(input_dir or self.input_dir)
        destination_dir = Path(output_dir or self.output_dir)
        destination_dir.mkdir(parents=True, exist_ok=True)

        generated_files: List[Path] = []
        for locator_path in sorted(source_dir.glob("*.json")):
            with locator_path.open("r", encoding="utf-8") as handle:
                locator_payload = json.load(handle)

            script_content = self.generate_script_for_locator(locator_payload)
            output_path = destination_dir / f"{self._to_script_name(self._screen_name_from_payload(locator_payload))}"
            with output_path.open("w", encoding="utf-8") as handle:
                handle.write(script_content)
            generated_files.append(output_path)

        return generated_files

    def _build_step_lines(self, screen_name: str, elements: List[Dict[str, Any]]) -> str:
        """Create readable Python comments and action calls for each discovered element."""

        lines: List[str] = []

    # Navigation
        navigation_steps = self.navigation_agent.get_navigation_steps(screen_name)

        for nav_action, strategy, value in navigation_steps:
            if nav_action == "tap":
                lines.append(f"        self.tap('{strategy}', '{value}')")
            elif nav_action == "scroll":
                lines.append(f"        self.scroll('{strategy}', '{value}')")

        if navigation_steps:
            lines.append("")

        # Screen actions
        for index, element in enumerate(elements, start=1):

            label = str(element.get("element") or f"Element {index}")
            action = str(element.get("action") or "verify").strip().lower()
            locator_strategy = str(element.get("locator_strategy") or "text")
            locator_value = str(element.get("locator_value") or label)

            # Skip navigation Login tap
            if (
                screen_name.lower() == "login"
                and action == "tap"
                and label.lower() == "login"
            ):
                continue

            lines.append(
                f"        # Step {index}: {action.replace('_', ' ')} the {label} element."
            )

            if action == "tap":
                lines.append(
                    f"        self.tap('{locator_strategy}', '{locator_value}')"
                )

            elif action == "type":
                input_value = element.get("input_value", "")
                lines.append(
                    f"        self.type('{locator_strategy}', '{locator_value}', '{input_value}')"
                )

            elif action == "scroll":
                lines.append(
                    f"        self.scroll('{locator_strategy}', '{locator_value}')"
                )

            else:
                lines.append(
                    f"        self.wait.until(EC.visibility_of_element_located(self._build_locator('{locator_strategy}', '{locator_value}')))"
                )

            lines.append("")

        # Submit Login AFTER all fields
        if screen_name.lower() == "login":
            lines.append("        # Submit login")
            lines.append(
                "        self.tap('resource_id', 'com.saucelabs.mydemoapp.android:id/loginBtn')"
            )
            lines.append("")

        if not lines:
            return "        pass\n"

        return "\n".join(lines).rstrip() + "\n"

    def _screen_name_from_payload(self, locator_payload: Dict[str, Any]) -> str:
        """Extract a readable screen name from the locator payload."""
        screen_name = locator_payload.get("screen") or "Screen"
        return str(screen_name)

    def _to_class_name(self, screen_name: str) -> str:
        """Turn a screen name into a Python class name."""
        parts = re.split(r"[^0-9A-Za-z]+", screen_name)
        cleaned = [part.capitalize() for part in parts if part]
        return "Test" + "".join(cleaned) if cleaned else "TestScreen"

    def _to_test_name(self, screen_name: str) -> str:
        """Turn a screen name into a pytest test method name."""
        return "test_" + self._slugify(screen_name)

    def _to_script_name(self, screen_name: str) -> str:
        """Turn a screen name into a Python script file name."""
        return f"test_{self._slugify(screen_name)}_screen.py"

    def _slugify(self, value: str) -> str:
        """Create a lowercase slug from a screen name."""
        slug = re.sub(r"[^a-z0-9]+", "_", str(value).strip().lower()).strip("_")
        return slug or "screen"


def main() -> List[Path]:
    """Automatically process every locator JSON file and create Appium scripts."""
    agent = AppiumGeneratorAgent()
    agent.output_dir.mkdir(parents=True, exist_ok=True)
    generated_files = agent.generate_scripts_from_directory(input_dir=agent.input_dir, output_dir=agent.output_dir)

    for path in generated_files:
        print(f"Generated {path}")
    return generated_files


if __name__ == "__main__":
    main()
