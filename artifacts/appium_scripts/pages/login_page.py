import os

from appium.webdriver.common.appiumby import AppiumBy

from core.base_page import BasePage


class LoginPage(BasePage):
    PLATFORM = os.getenv("MOBILE_PLATFORM", "android").lower()
    LOCATORS = {
        "android": {
            "username": (AppiumBy.ACCESSIBILITY_ID, "Username"),  # LOCATOR_TODO: verify/replace once Locator Enrichment Agent resolves real selectors
            "password": (AppiumBy.ACCESSIBILITY_ID, "Password"),  # LOCATOR_TODO: verify/replace once Locator Enrichment Agent resolves real selectors
            "login": (AppiumBy.ACCESSIBILITY_ID, "Login"),  # LOCATOR_TODO: verify/replace once Locator Enrichment Agent resolves real selectors
            "loginScreen": (AppiumBy.ACCESSIBILITY_ID, "Login"),  # LOCATOR_TODO: verify/replace once Locator Enrichment Agent resolves real selectors
            "errorMessage": (AppiumBy.ACCESSIBILITY_ID, "Authentication failed"),  # LOCATOR_TODO: verify/replace once Locator Enrichment Agent resolves real selectors
            "usernameRequiredMessage": (AppiumBy.ACCESSIBILITY_ID, "Username is required"),  # LOCATOR_TODO: verify/replace once Locator Enrichment Agent resolves real selectors
            "passwordRequiredMessage": (AppiumBy.ACCESSIBILITY_ID, "Password is required"),  # LOCATOR_TODO: verify/replace once Locator Enrichment Agent resolves real selectors
            "authorizedArea": (AppiumBy.ACCESSIBILITY_ID, "Home"),  # LOCATOR_TODO: verify/replace once Locator Enrichment Agent resolves real selectors
        },
        "ios": {},
    }

    def _locator(self, key):
        return self.LOCATORS[self.PLATFORM][key]

    def enterUsername(self, value):
        self.typeText(self._locator("username"), value)

    def enterPassword(self, value):
        self.typeText(self._locator("password"), value)

    def tapLogin(self):
        self.click(self._locator("login"))

    def isLoginScreenVisible(self, timeout=5):
        return self.isVisible(self._locator("loginScreen"), timeout=timeout)

    def isErrorMessageVisible(self, timeout=5):
        return self.isVisible(self._locator("errorMessage"), timeout=timeout)

    def isUsernameRequiredMessageVisible(self, timeout=5):
        return self.isVisible(self._locator("usernameRequiredMessage"), timeout=timeout)

    def isPasswordRequiredMessageVisible(self, timeout=5):
        return self.isVisible(self._locator("passwordRequiredMessage"), timeout=timeout)

    def isAuthorizedAreaVisible(self, timeout=5):
        return self.isVisible(self._locator("authorizedArea"), timeout=timeout)

    def getUsernameText(self):
        return self.getText(self._locator("username"))

    def getPasswordText(self):
        return self.getText(self._locator("password"))
