import os

from appium.webdriver.common.appiumby import AppiumBy

from core.base_page import BasePage


PLATFORM = os.getenv("MOBILE_PLATFORM", "android").lower()


class ProductListingPage(BasePage):
    LOCATORS = {
        "android": {
            "search": (AppiumBy.ACCESSIBILITY_ID, "Search"),  # LOCATOR_TODO: verify/replace once Locator Enrichment Agent resolves real selectors
            "categoryFilter": (AppiumBy.ACCESSIBILITY_ID, "Category filter"),  # LOCATOR_TODO: verify/replace once Locator Enrichment Agent resolves real selectors
            "sort": (AppiumBy.ACCESSIBILITY_ID, "Sort"),  # LOCATOR_TODO: verify/replace once Locator Enrichment Agent resolves real selectors
            "productItem": (AppiumBy.ACCESSIBILITY_ID, "Product item"),  # LOCATOR_TODO: verify/replace once Locator Enrichment Agent resolves real selectors
            "emptyStateMessage": (AppiumBy.ACCESSIBILITY_ID, "No products found"),  # LOCATOR_TODO: verify/replace once Locator Enrichment Agent resolves real selectors
            "categoryOption": (AppiumBy.ACCESSIBILITY_ID, "Category option"),  # LOCATOR_TODO: verify/replace once Locator Enrichment Agent resolves real selectors
            "sortOption": (AppiumBy.ACCESSIBILITY_ID, "Sort option"),  # LOCATOR_TODO: verify/replace once Locator Enrichment Agent resolves real selectors
        },
        "ios": {},
    }

    def _locator(self, key):
        return self.LOCATORS[PLATFORM][key]

    def tapSearch(self):
        self.click(self._locator("search"))

    def enterSearch(self, value):
        self.typeText(self._locator("search"), value)

    def clearSearch(self):
        self.typeText(self._locator("search"), "")

    def tapCategoryFilter(self):
        self.click(self._locator("categoryFilter"))

    def tapSort(self):
        self.click(self._locator("sort"))

    def tapProductItem(self):
        self.click(self._locator("productItem"))

    def tapCategoryOption(self):
        self.click(self._locator("categoryOption"))

    def tapSortOption(self):
        self.click(self._locator("sortOption"))

    def isSearchVisible(self, timeout=5):
        return self.isVisible(self._locator("search"), timeout=timeout)

    def isCategoryFilterVisible(self, timeout=5):
        return self.isVisible(self._locator("categoryFilter"), timeout=timeout)

    def isSortVisible(self, timeout=5):
        return self.isVisible(self._locator("sort"), timeout=timeout)

    def isProductItemVisible(self, timeout=5):
        return self.isVisible(self._locator("productItem"), timeout=timeout)

    def isEmptyStateMessageVisible(self, timeout=5):
        return self.isVisible(self._locator("emptyStateMessage"), timeout=timeout)

    def getSearchText(self):
        return self.getText(self._locator("search"))
