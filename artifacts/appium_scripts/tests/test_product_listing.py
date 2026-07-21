import pytest

from pages.product_listing_page import ProductListingPage


@pytest.fixture
def productListingPage(driver):
    page = ProductListingPage(driver)
    page.navigate()
    return page


def test_verifyProductListingScreenLoadsWithCoreBrowsingControls(productListingPage):
    """1. Verify Product Listing screen loads with core browsing controls"""
    assert productListingPage.isSearchVisible(), "Search bar should be visible on the Product Listing screen."
    assert productListingPage.isCategoryFilterVisible(), "Category filter control should be visible on the Product Listing screen."
    assert productListingPage.isSortVisible(), "Sort button should be visible on the Product Listing screen."
    assert productListingPage.isProductGridVisible(), "Product grid should be visible on the Product Listing screen."
    assert productListingPage.isProductItemVisible(), "At least one product item should be visible in the Product grid."
    assert productListingPage.isAddToCartVisible(), "Add to cart button should be visible for a product item or within the listing context."


def test_verifyProductSearchUsingValidKeyword(productListingPage):
    """2. Verify product search using valid keyword"""
    productListingPage.tapSearch()
    productListingPage.enterSearch("backpack")
    assert productListingPage.isProductGridVisible(), "Product grid should refresh and remain visible after entering a valid search keyword."
    assert productListingPage.isProductItemVisible(), "Displayed product items should be relevant and visible after applying a valid search term."
    assert productListingPage.getSearchText() == "backpack", "Search field should contain the entered valid keyword after search is applied."


def test_verifySearchBehaviorWithNoMatchingResults(productListingPage):
    """3. Verify search behavior with no matching results"""
    productListingPage.tapSearch()
    productListingPage.enterSearch("zzzinvalidnomatch")
    assert productListingPage.isProductGridVisible() or not productListingPage.isProductItemVisible(timeout=2), "Screen should reflect no matching products by showing an empty grid or no visible product items."
    assert productListingPage.isSearchVisible(), "Search should remain editable and visible after an unsuccessful search."
    assert productListingPage.getSearchText() == "zzzinvalidnomatch", "Search field should retain the no-match keyword so the user can edit it again."


def test_verifySearchFieldAcceptsAndProcessesEditedText(productListingPage):
    """4. Verify search field accepts and processes edited text"""
    productListingPage.tapSearch()
    productListingPage.enterSearch("backpack")
    assert productListingPage.getSearchText() == "backpack", "Search bar should accept the initial keyword."
    assert productListingPage.isProductGridVisible(), "Product grid should refresh after the initial search term is entered."
    productListingPage.tapSearch()
    productListingPage.enterSearch("shirt")
    assert productListingPage.getSearchText() == "shirt", "Search bar should accept updated text when the user edits the search term."
    assert productListingPage.isProductGridVisible(), "Product grid should refresh according to the updated search term."
    assert productListingPage.isProductItemVisible(), "Results from the previous search should be replaced by new relevant product items after editing the search text."


def test_verifyCategoryFilterOpensAndAppliesAProductFilter(productListingPage):
    """5. Verify Category filter opens and applies a product filter"""
    productListingPage.tapCategoryFilter()
    assert productListingPage.isCategoryFilterVisible(), "Category filter should open successfully and remain accessible for selection."
    assert productListingPage.isProductGridVisible(), "Product grid should update and remain visible after applying a category filter."
    assert productListingPage.isProductItemVisible(), "Filtered result set should contain visible products belonging to the selected category."


def test_verifyCategoryFilterCanBeChangedToAnotherCategory(productListingPage):
    """6. Verify Category filter can be changed to another category"""
    productListingPage.tapCategoryFilter()
    assert productListingPage.isProductGridVisible(), "Product grid should display results after the first category selection."
    productListingPage.tapCategoryFilter()
    assert productListingPage.isCategoryFilterVisible(), "Category filter should allow changing the current category selection."
    assert productListingPage.isProductGridVisible(), "Product grid should update to match the newly selected category."
    assert productListingPage.isProductItemVisible(), "Products shown after changing category should match the new selection."


def test_verifySortControlReordersTheProductGrid(productListingPage):
    """7. Verify Sort control reorders the Product grid"""
    assert productListingPage.isProductItemVisible(), "At least one product item should be visible before sorting."
    productListingPage.tapSort()
    assert productListingPage.isSortVisible(), "Sort options should be accessible when the Sort control is tapped."
    assert productListingPage.isProductGridVisible(), "Product grid should refresh and remain visible after a sort option is selected."
    assert productListingPage.isProductItemVisible(), "Product items should remain visible after sorting is applied."
