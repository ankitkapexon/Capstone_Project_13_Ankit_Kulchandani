import os

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

DEFAULT_TIMEOUT = int(os.getenv("APPIUM_WAIT_TIMEOUT", "10"))


class BasePage:
    """Shared Appium interactions every generated Page Object builds on.

    Generated Page Objects should never call WebDriverWait directly - they
    delegate to these helpers so wait/retry behaviour stays consistent and
    isn't reinvented (or gotten wrong) per screen.
    """

    def __init__(self, driver):
        self.driver = driver

    def waitForVisible(self, locator, timeout: int = DEFAULT_TIMEOUT):
        return WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located(locator))

    def waitForClickable(self, locator, timeout: int = DEFAULT_TIMEOUT):
        return WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable(locator))

    def click(self, locator, timeout: int = DEFAULT_TIMEOUT):
        self.waitForClickable(locator, timeout=timeout).click()

    def typeText(self, locator, text: str, timeout: int = DEFAULT_TIMEOUT):
        element = self.waitForVisible(locator, timeout=timeout)
        element.click()
        element.clear()
        if text:
            element.send_keys(text)

    def isVisible(self, locator, timeout: int = 3) -> bool:
        try:
            self.waitForVisible(locator, timeout=timeout)
            return True
        except TimeoutException:
            return False

    def getText(self, locator, timeout: int = DEFAULT_TIMEOUT) -> str:
        return self.waitForVisible(locator, timeout=timeout).text
