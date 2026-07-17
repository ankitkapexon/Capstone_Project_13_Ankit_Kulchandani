import os
from appium.webdriver.common.appiumby import AppiumBy
from core.base_page import BasePage


class ProductDetailsPage(BasePage):
    PLATFORM = os.getenv("MOBILE_PLATFORM", "android").lower()
    LOCATORS = {
        "android": {
            "productImage": (AppiumBy.ACCESSIBILITY_ID, "Product image"),  # LOCATOR_TODO: verify/replace once Locator Enrichment Agent resolves real selectors
            "productTitle": (AppiumBy.ACCESSIBILITY_ID, "Product title"),  # LOCATOR_TODO: verify/replace once Locator Enrichment Agent resolves real selectors
            "price": (AppiumBy.ACCESSIBILITY_ID, "Price"),  # LOCATOR_TODO: verify/replace once Locator Enrichment Agent resolves real selectors
            "rating": (AppiumBy.ACCESSIBILITY_ID, "Rating"),  # LOCATOR_TODO: verify/replace once Locator Enrichment Agent resolves real selectors
            "quantitySelector": (AppiumBy.ACCESSIBILITY_ID, "Quantity selector"),  # LOCATOR_TODO: verify/replace once Locator Enrichment Agent resolves real selectors
            "quantityIncrement": (AppiumBy.ACCESSIBILITY_ID, "Quantity increment"),  # LOCATOR_TODO: verify/replace once Locator Enrichment Agent resolves real selectors
            "quantityDecrement": (AppiumBy.ACCESSIBILITY_ID, "Quantity decrement"),  # LOCATOR_TODO: verify/replace once Locator Enrichment Agent resolves real selectors
            "addToCart": (AppiumBy.ACCESSIBILITY_ID, "Add to Cart"),  # LOCATOR_TODO: verify/replace once Locator Enrichment Agent resolves real selectors
            "buyNow": (AppiumBy.ACCESSIBILITY_ID, "Buy Now"),  # LOCATOR_TODO: verify/replace once Locator Enrichment Agent resolves real selectors
            "back": (AppiumBy.ACCESSIBILITY_ID, "Back"),  # LOCATOR_TODO: verify/replace once Locator Enrichment Agent resolves real selectors
            "favorite": (AppiumBy.ACCESSIBILITY_ID, "Favorite"),  # LOCATOR_TODO: verify/replace once Locator Enrichment Agent resolves real selectors
            "favoriteSelected": (AppiumBy.ACCESSIBILITY_ID, "Favorite selected"),  # LOCATOR_TODO: verify/replace once Locator Enrichment Agent resolves real selectors
            "favoriteUnselected": (AppiumBy.ACCESSIBILITY_ID, "Favorite unselected"),  # LOCATOR_TODO: verify/replace once Locator Enrichment Agent resolves real selectors
            "cartSuccessMessage": (AppiumBy.ACCESSIBILITY_ID, "Added to cart"),  # LOCATOR_TODO: verify/replace once Locator Enrichment Agent resolves real selectors
            "checkoutScreen": (AppiumBy.ACCESSIBILITY_ID, "Checkout"),  # LOCATOR_TODO: verify/replace once Locator Enrichment Agent resolves real selectors
            "previousScreen": (AppiumBy.ACCESSIBILITY_ID, "Previous screen"),  # LOCATOR_TODO: verify/replace once Locator Enrichment Agent resolves real selectors
        },
        "ios": {},
    }

    def _locator(self, key):
        return self.LOCATORS[self.PLATFORM][key]

    def isProductImageVisible(self, timeout=5):
        return self.isVisible(self._locator("productImage"), timeout=timeout)

    def isProductTitleVisible(self, timeout=5):
        return self.isVisible(self._locator("productTitle"), timeout=timeout)

    def getProductTitleText(self):
        return self.getText(self._locator("productTitle"))

    def isPriceVisible(self, timeout=5):
        return self.isVisible(self._locator("price"), timeout=timeout)

    def getPriceText(self):
        return self.getText(self._locator("price"))

    def isRatingVisible(self, timeout=5):
        return self.isVisible(self._locator("rating"), timeout=timeout)

    def getRatingText(self):
        return self.getText(self._locator("rating"))

    def isQuantitySelectorVisible(self, timeout=5):
        return self.isVisible(self._locator("quantitySelector"), timeout=timeout)

    def tapQuantitySelector(self):
        self.click(self._locator("quantitySelector"))

    def tapQuantityIncrement(self):
        self.click(self._locator("quantityIncrement"))

    def tapQuantityDecrement(self):
        self.click(self._locator("quantityDecrement"))

    def getQuantitySelectorText(self):
        return self.getText(self._locator("quantitySelector"))

    def tapAddToCart(self):
        self.click(self._locator("addToCart"))

    def isAddToCartVisible(self, timeout=5):
        return self.isVisible(self._locator("addToCart"), timeout=timeout)

    def tapBuyNow(self):
        self.click(self._locator("buyNow"))

    def isBuyNowVisible(self, timeout=5):
        return self.isVisible(self._locator("buyNow"), timeout=timeout)

    def tapBack(self):
        self.click(self._locator("back"))

    def isBackVisible(self, timeout=5):
        return self.isVisible(self._locator("back"), timeout=timeout)

    def tapFavorite(self):
        self.click(self._locator("favorite"))

    def isFavoriteVisible(self, timeout=5):
        return self.isVisible(self._locator("favorite"), timeout=timeout)

    def isFavoriteSelectedVisible(self, timeout=5):
        return self.isVisible(self._locator("favoriteSelected"), timeout=timeout)

    def isFavoriteUnselectedVisible(self, timeout=5):
        return self.isVisible(self._locator("favoriteUnselected"), timeout=timeout)

    def isCartSuccessMessageVisible(self, timeout=5):
        return self.isVisible(self._locator("cartSuccessMessage"), timeout=timeout)

    def isCheckoutScreenVisible(self, timeout=5):
        return self.isVisible(self._locator("checkoutScreen"), timeout=timeout)

    def isPreviousScreenVisible(self, timeout=5):
        return self.isVisible(self._locator("previousScreen"), timeout=timeout)
