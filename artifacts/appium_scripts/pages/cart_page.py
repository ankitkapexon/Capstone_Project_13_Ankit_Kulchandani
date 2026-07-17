import os
from appium.webdriver.common.appiumby import AppiumBy
from core.base_page import BasePage


class CartPage(BasePage):
    PLATFORM = os.getenv("MOBILE_PLATFORM", "android").lower()
    LOCATORS = {
        "android": {
            "back": (AppiumBy.ACCESSIBILITY_ID, "Back"),  # LOCATOR_TODO: verify/replace once Locator Enrichment Agent resolves real selectors
            "cartTitle": (AppiumBy.ACCESSIBILITY_ID, "Cart title"),  # LOCATOR_TODO: verify/replace once Locator Enrichment Agent resolves real selectors
            "cartItemsList": (AppiumBy.ACCESSIBILITY_ID, "Cart items list"),  # LOCATOR_TODO: verify/replace once Locator Enrichment Agent resolves real selectors
            "productImage": (AppiumBy.ACCESSIBILITY_ID, "Product image"),  # LOCATOR_TODO: verify/replace once Locator Enrichment Agent resolves real selectors
            "productName": (AppiumBy.ACCESSIBILITY_ID, "Product name"),  # LOCATOR_TODO: verify/replace once Locator Enrichment Agent resolves real selectors
            "productPrice": (AppiumBy.ACCESSIBILITY_ID, "Product price"),  # LOCATOR_TODO: verify/replace once Locator Enrichment Agent resolves real selectors
            "quantityStepper": (AppiumBy.ACCESSIBILITY_ID, "Quantity stepper"),  # LOCATOR_TODO: verify/replace once Locator Enrichment Agent resolves real selectors
            "removeItem": (AppiumBy.ACCESSIBILITY_ID, "Remove item"),  # LOCATOR_TODO: verify/replace once Locator Enrichment Agent resolves real selectors
            "subtotal": (AppiumBy.ACCESSIBILITY_ID, "Subtotal"),  # LOCATOR_TODO: verify/replace once Locator Enrichment Agent resolves real selectors
            "checkout": (AppiumBy.ACCESSIBILITY_ID, "Checkout"),  # LOCATOR_TODO: verify/replace once Locator Enrichment Agent resolves real selectors
        },
        "ios": {},
    }

    def _locator(self, key):
        return self.LOCATORS[self.PLATFORM][key]

    def tapBack(self):
        self.click(self._locator("back"))

    def isCartTitleVisible(self, timeout=5):
        return self.isVisible(self._locator("cartTitle"), timeout=timeout)

    def isCartItemsListVisible(self, timeout=5):
        return self.isVisible(self._locator("cartItemsList"), timeout=timeout)

    def tapProductImage(self):
        self.click(self._locator("productImage"))

    def tapProductName(self):
        self.click(self._locator("productName"))

    def isProductPriceVisible(self, timeout=5):
        return self.isVisible(self._locator("productPrice"), timeout=timeout)

    def tapQuantityStepper(self):
        self.click(self._locator("quantityStepper"))

    def tapRemoveItem(self):
        self.click(self._locator("removeItem"))

    def isSubtotalVisible(self, timeout=5):
        return self.isVisible(self._locator("subtotal"), timeout=timeout)

    def tapCheckout(self):
        self.click(self._locator("checkout"))

    def isBackVisible(self, timeout=5):
        return self.isVisible(self._locator("back"), timeout=timeout)

    def isProductImageVisible(self, timeout=5):
        return self.isVisible(self._locator("productImage"), timeout=timeout)

    def isProductNameVisible(self, timeout=5):
        return self.isVisible(self._locator("productName"), timeout=timeout)

    def isQuantityStepperVisible(self, timeout=5):
        return self.isVisible(self._locator("quantityStepper"), timeout=timeout)

    def isRemoveItemVisible(self, timeout=5):
        return self.isVisible(self._locator("removeItem"), timeout=timeout)

    def isCheckoutVisible(self, timeout=5):
        return self.isVisible(self._locator("checkout"), timeout=timeout)

    def getProductNameText(self):
        return self.getText(self._locator("productName"))

    def getProductPriceText(self):
        return self.getText(self._locator("productPrice"))

    def getQuantityStepperText(self):
        return self.getText(self._locator("quantityStepper"))

    def getSubtotalText(self):
        return self.getText(self._locator("subtotal"))
