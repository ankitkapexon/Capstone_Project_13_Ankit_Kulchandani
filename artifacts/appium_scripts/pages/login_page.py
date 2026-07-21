import os

from appium.webdriver.common.appiumby import AppiumBy

from core.base_page import BasePage


class LoginPage(BasePage):
    PLATFORM = os.getenv("MOBILE_PLATFORM", "android").lower()

    LOCATORS = {
        "android": {
            "menu": (AppiumBy.ID, "com.saucelabs.mydemoapp.android:id/menuIV"),  # LOCATOR_TODO: verify/replace once Locator Enrichment Agent resolves real selectors
            "loginMenuItem": (AppiumBy.ACCESSIBILITY_ID, "Login Menu Item"),  # LOCATOR_TODO: verify/replace once Locator Enrichment Agent resolves real selectors
            "username": (AppiumBy.ID, "com.saucelabs.mydemoapp.android:id/nameET"),  # LOCATOR_TODO: verify/replace once Locator Enrichment Agent resolves real selectors
            "password": (AppiumBy.ID, "com.saucelabs.mydemoapp.android:id/passwordET"),  # LOCATOR_TODO: verify/replace once Locator Enrichment Agent resolves real selectors
            "loginButton": (AppiumBy.ID, "com.saucelabs.mydemoapp.android:id/loginBtn"),  # LOCATOR_TODO: verify/replace once Locator Enrichment Agent resolves real selectors
        },
        "ios": {},
    }

    def _locator(self, key):
        return self.LOCATORS[self.PLATFORM][key]

    def navigate(self):
        self.click(self._locator("menu"))
        self.click(self._locator("loginMenuItem"))

    def enterUsername(self, value):
        self.typeText(self._locator("username"), value)

    def enterPassword(self, value):
        self.typeText(self._locator("password"), value)

    def tapLoginButton(self):
        self.click(self._locator("loginButton"))

    def isUsernameVisible(self, timeout=5):
        return self.isVisible(self._locator("username"), timeout=timeout)

    def isPasswordVisible(self, timeout=5):
        return self.isVisible(self._locator("password"), timeout=timeout)

    def isLoginButtonVisible(self, timeout=5):
        return self.isVisible(self._locator("loginButton"), timeout=timeout)
