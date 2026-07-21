import os

from appium.webdriver.common.appiumby import AppiumBy

from core.base_page import BasePage


class CartPage(BasePage):
    PLATFORM = os.getenv("MOBILE_PLATFORM", "android").lower()

    LOCATORS = {
        "android": {
            "cartTitle": (AppiumBy.ID, "com.saucelabs.mydemoapp.android:id/titleTV"),  # LOCATOR_TODO: verify/replace once Locator Enrichment Agent resolves real selectors
            "checkout": (AppiumBy.ID, "com.saucelabs.mydemoapp.android:id/cartBt"),  # LOCATOR_TODO: verify/replace once Locator Enrichment Agent resolves real selectors
            "cartItems": (AppiumBy.ACCESSIBILITY_ID, "cart items"),  # LOCATOR_TODO: verify/replace once Locator Enrichment Agent resolves real selectors
            "quantityControls": (AppiumBy.ID, "com.saucelabs.mydemoapp.android:id/plusIV"),  # LOCATOR_TODO: verify/replace once Locator Enrichment Agent resolves real selectors
            "subtotal": (AppiumBy.ID, "com.saucelabs.mydemoapp.android:id/totalPriceTV"),  # LOCATOR_TODO: verify/replace once Locator Enrichment Agent resolves real selectors
            "removeItem": (AppiumBy.ID, "com.saucelabs.mydemoapp.android:id/removeBt"),  # LOCATOR_TODO: verify/replace once Locator Enrichment Agent resolves real selectors
            "cartIcon": (AppiumBy.ID, "com.saucelabs.mydemoapp.android:id/cartIV"),  # LOCATOR_TODO: verify/replace once Locator Enrichment Agent resolves real selectors
        },
        "ios": {},
    }

    def _locator(self, key):
        return self.LOCATORS[self.PLATFORM][key]

    def navigate(self):
        self.click(self._locator("cartIcon"))

    def isCartTitleVisible(self, timeout=5):
        return self.isVisible(self._locator("cartTitle"), timeout=timeout)

    def tapCartItems(self):
        self.click(self._locator("cartItems"))

    def tapQuantityControls(self):
        self.click(self._locator("quantityControls"))

    def tapRemoveItem(self):
        self.click(self._locator("removeItem"))

    def isSubtotalVisible(self, timeout=5):
        return self.isVisible(self._locator("subtotal"), timeout=timeout)

    def tapCheckout(self):
        self.click(self._locator("checkout"))

    def isCartItemsVisible(self, timeout=5):
        return self.isVisible(self._locator("cartItems"), timeout=timeout)

    def isQuantityControlsVisible(self, timeout=5):
        return self.isVisible(self._locator("quantityControls"), timeout=timeout)

    def isRemoveItemVisible(self, timeout=5):
        return self.isVisible(self._locator("removeItem"), timeout=timeout)

    def isCheckoutVisible(self, timeout=5):
        return self.isVisible(self._locator("checkout"), timeout=timeout)

    def getSubtotalText(self):
        return self.getText(self._locator("subtotal"))
