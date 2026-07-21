"""Runtime helpers for driving a live Appium session - as opposed to
services/appium_agent.py, which only ever emits Python source code and never
touches a real driver. Used by the live locator agent to open a session,
navigate to a screen using the same navigation_map.json steps the generated
tests use, and read the live UI hierarchy.
"""

from __future__ import annotations

import os
import time
from typing import Any, Dict, List

from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy

_STRATEGY_TO_APPIUMBY = {
    "resource_id": AppiumBy.ID,
    "id": AppiumBy.ID,
    "accessibility_id": AppiumBy.ACCESSIBILITY_ID,
    "android_uiautomator": AppiumBy.ANDROID_UIAUTOMATOR,
}


def to_appium_locator(strategy: str, value: str) -> tuple[str, str]:
    """Convert a logical (strategy, value) pair - the same shape used in
    navigation_map.json and locator_output/*.json - into a real Appium locator."""
    strategy = (strategy or "").lower()
    if strategy == "text":
        return AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{value}")'
    by = _STRATEGY_TO_APPIUMBY.get(strategy, AppiumBy.ACCESSIBILITY_ID)
    return by, value


def build_driver_options() -> UiAutomator2Options:
    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.device_name = os.getenv("ANDROID_DEVICE_NAME", "Android Emulator")
    options.automation_name = "UiAutomator2"
    android_app_path = os.getenv("ANDROID_APP_PATH")
    if android_app_path:
        options.app = android_app_path
    return options


def open_session():
    server_url = os.getenv("APPIUM_SERVER_URL", "http://127.0.0.1:4723")
    return webdriver.Remote(server_url, options=build_driver_options())


def navigate(driver, steps: List[Dict[str, Any]]) -> None:
    """Perform the steps recorded in navigation_map.json for one screen. Most steps
    are "tap" (locator_strategy/locator_value); a "back" step presses the Android
    back button instead - used e.g. to return to the product list after adding an
    item to cart, before opening the cart itself. A short settle pause follows each
    step since this emulator's software rendering is slow enough for the next tap to
    otherwise race the current screen transition."""
    for step in steps or []:
        action = step.get("action", "tap")
        if action == "back":
            driver.back()
        else:
            strategy = step.get("locator_strategy")
            value = step.get("locator_value")
            if not strategy or not value:
                continue
            locator = to_appium_locator(strategy, value)
            driver.find_element(*locator).click()
        time.sleep(1.5)


def reset_to_home(driver, home_anchor: tuple[str, str] = (AppiumBy.ID, "com.saucelabs.mydemoapp.android:id/menuIV")) -> None:
    """Force the app back to its freshly-launched home screen before navigating to
    the next screen - navigation_map.json's steps are all relative to app launch,
    not to whatever screen the previous iteration left the driver on. Waits for a
    known home-screen element rather than a fixed sleep, since this emulator's
    software-rendered relaunch time is inconsistent."""
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    package = driver.current_package
    driver.terminate_app(package)
    driver.activate_app(package)
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(home_anchor))
