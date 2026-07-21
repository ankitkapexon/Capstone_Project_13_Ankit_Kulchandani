import os
import sys
from pathlib import Path

import pytest
from appium import webdriver
from appium.options.android import UiAutomator2Options

ROOT = Path(__file__).resolve().parents[2]
APPIUM_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(APPIUM_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(APPIUM_SCRIPTS_DIR))

DEMO_APPS_DIR = ROOT / "demo_mobile_apps"
DEFAULT_ANDROID_APP = DEMO_APPS_DIR / "mda-2.2.0-25.apk"


def _build_options():
    platform = os.getenv("MOBILE_PLATFORM", "android").lower()

    if platform == "ios":
        # iOS is intentionally not implemented yet - Android is the current focus.
        # Every generated Page Object already reserves an "ios" key in its LOCATORS
        # dict, so wiring this up later is additive here and doesn't require touching
        # any generated page object or test.
        raise NotImplementedError(
            "iOS is not supported yet. Set MOBILE_PLATFORM=android, or implement "
            "XCUITestOptions here and populate the 'ios' locator entries in pages/."
        )

    if platform != "android":
        raise ValueError(f"Unsupported MOBILE_PLATFORM: {platform!r}. Only 'android' is supported today.")

    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.device_name = os.getenv("ANDROID_DEVICE_NAME", "Android Emulator")
    options.app = os.getenv("ANDROID_APP_PATH", str(DEFAULT_ANDROID_APP))
    options.automation_name = "UiAutomator2"
    return options


@pytest.fixture
def driver():
    """Yields a live Appium session for MOBILE_PLATFORM (android only for now).

    Requires an Appium server reachable at APPIUM_SERVER_URL (default http://127.0.0.1:4723).
    Defaults to the demo app checked into demo_mobile_apps/ unless ANDROID_APP_PATH overrides it.
    """
    server_url = os.getenv("APPIUM_SERVER_URL", "http://127.0.0.1:4723")
    options = _build_options()

    session = webdriver.Remote(server_url, options=options)
    try:
        yield session
    finally:
        session.quit()
