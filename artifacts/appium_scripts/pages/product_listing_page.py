import os

from appium.webdriver.common.appiumby import AppiumBy

from core.base_page import BasePage


class ProductListingPage(BasePage):
    PLATFORM = os.getenv("MOBILE_PLATFORM", "android").lower()
    LOCATORS = {
        "android": {
            "search": (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("search")'),  # LOCATOR_TODO: verify/replace once Locator Enrichment Agent resolves real selectors
            "categoryFilter": (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("category filter")'),  # LOCATOR_TODO: verify/replace once Locator Enrichment Agent resolves real selectors
            "sort": (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("sort")'),  # LOCATOR_TODO: verify/replace once Locator Enrichment Agent resolves real selectors
            "productGrid": (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("product grid")'),  # LOCATOR_TODO: verify/replace once Locator Enrichment Agent resolves real selectors
            "productItem": (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("product item")'),  # LOCATOR_TODO: verify/replace once Locator Enrichment Agent resolves real selectors
            "addToCart": (AppiumBy.ID, 'com.saucelabs.mydemoapp.android:id/cartBt'),  # LOCATOR_TODO: verify/replace once Locator Enrichment Agent resolves real selectors
        },
        "ios": {},
    }

    def _locator(self, key):
        return self.LOCATORS[self.PLATFORM][key]

    def navigate(self):
        pass

    def tapSearch(self):
        self.click(self._locator("search"))

    def enterSearch(self, value):
        self.typeText(self._locator("search"), value)

    def tapCategoryFilter(self):
        self.click(self._locator("categoryFilter"))

    def tapSort(self):
        self.click(self._locator("sort"))

    def tapProductItem(self):
        self.click(self._locator("productItem"))

    def isProductGridVisible(self, timeout=5):
        return self.isVisible(self._locator("productGrid"), timeout=timeout)

    def isSearchVisible(self, timeout=5):
        return self.isVisible(self._locator("search"), timeout=timeout)

    def isCategoryFilterVisible(self, timeout=5):
        return self.isVisible(self._locator("categoryFilter"), timeout=timeout)

    def isSortVisible(self, timeout=5):
        return self.isVisible(self._locator("sort"), timeout=timeout)

    def isProductItemVisible(self, timeout=5):
        return self.isVisible(self._locator("productItem"), timeout=timeout)

    def isAddToCartVisible(self, timeout=5):
        return self.isVisible(self._locator("addToCart"), timeout=timeout)

    def getSearchText(self):
        return self.getText(self._locator("search"))
