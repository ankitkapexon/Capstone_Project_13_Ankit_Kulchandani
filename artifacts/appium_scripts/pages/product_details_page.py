import os

from appium.webdriver.common.appiumby import AppiumBy

from core.base_page import BasePage


PLATFORM = os.getenv("MOBILE_PLATFORM", "android").lower()


class ProductDetailsPage(BasePage):
    LOCATORS = {
        "android": {
            "productImage": (AppiumBy.ID, "com.saucelabs.mydemoapp.android:id/productIV"),  # LOCATOR_TODO: verify/replace once Locator Enrichment Agent resolves real selectors
            "productTitle": (AppiumBy.ID, "com.saucelabs.mydemoapp.android:id/productTV"),  # LOCATOR_TODO: verify/replace once Locator Enrichment Agent resolves real selectors
            "price": (AppiumBy.ID, "com.saucelabs.mydemoapp.android:id/priceTV"),  # LOCATOR_TODO: verify/replace once Locator Enrichment Agent resolves real selectors
            "addToCart": (AppiumBy.ID, "com.saucelabs.mydemoapp.android:id/cartBt"),  # LOCATOR_TODO: verify/replace once Locator Enrichment Agent resolves real selectors
            "buyNow": (AppiumBy.ACCESSIBILITY_ID, "Buy Now"),  # LOCATOR_TODO: verify/replace once Locator Enrichment Agent resolves real selectors
        },
        "ios": {},
    }

    def _locator(self, key):
        return self.LOCATORS[PLATFORM][key]

    def navigate(self):
        self.click((AppiumBy.ID, "com.saucelabs.mydemoapp.android:id/productIV"))

    def isProductImageVisible(self, timeout=5):
        return self.isVisible(self._locator("productImage"), timeout=timeout)

    def isProductTitleVisible(self, timeout=5):
        return self.isVisible(self._locator("productTitle"), timeout=timeout)

    def getProductTitleText(self):
        self.waitForVisible(self._locator("productTitle"))
        return self.getText(self._locator("productTitle"))

    def isPriceVisible(self, timeout=5):
        return self.isVisible(self._locator("price"), timeout=timeout)

    def getPriceText(self):
        self.waitForVisible(self._locator("price"))
        return self.getText(self._locator("price"))

    def isAddToCartVisible(self, timeout=5):
        return self.isVisible(self._locator("addToCart"), timeout=timeout)

    def getAddToCartText(self):
        self.waitForVisible(self._locator("addToCart"))
        return self.getText(self._locator("addToCart"))

    def tapAddToCart(self):
        self.click(self._locator("addToCart"))

    def isBuyNowVisible(self, timeout=5):
        return self.isVisible(self._locator("buyNow"), timeout=timeout)

    def getBuyNowText(self):
        self.waitForVisible(self._locator("buyNow"))
        return self.getText(self._locator("buyNow"))

    def tapBuyNow(self):
        self.click(self._locator("buyNow"))
