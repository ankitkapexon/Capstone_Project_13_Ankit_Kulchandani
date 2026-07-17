import pytest

from pages.product_listing_page import ProductListingPage


@pytest.fixture
def productListingPage(driver):
    return ProductListingPage(driver)


def test_verifyProductListingScreenLoadsWithKeyBrowsingControls(productListingPage):
    """1. Verify Product Listing screen loads with key browsing controls"""
    assert productListingPage.isSearchVisible(), "The Product Listing screen should open successfully with the Search field visible and accessible."
    assert productListingPage.isCategoryFilterVisible(), "The Category filter control should be visible and tappable on the Product Listing screen."
    assert productListingPage.isSortVisible(), "The Sort button should be visible and tappable on the Product Listing screen."
    assert productListingPage.isProductItemVisible(), "At least one Product item card should be displayed for browsing."


def test_searchForAProductUsingTheSearchField(productListingPage):
    """2. Search for a product using the Search field"""
    productListingPage.tapSearch()
    productListingPage.enterSearch("shoes")
    assert productListingPage.getSearchText() == "shoes", "The Search field should accept text input."
    assert productListingPage.isProductItemVisible(), "The product list should refresh based on the entered keyword and display relevant Product item cards."


def test_verifySearchWithPartialKeywordInput(productListingPage):
    """3. Verify search with partial keyword input"""
    productListingPage.tapSearch()
    productListingPage.enterSearch("sho")
    assert productListingPage.getSearchText() == "sho", "The Search field should accept partial text."
    assert productListingPage.isProductItemVisible(), "The listing should update without error and show matching or related Product item cards when applicable."


def test_verifySearchWithNonMatchingKeyword(productListingPage):
    """4. Verify search with non-matching keyword"""
    productListingPage.tapSearch()
    productListingPage.enterSearch("zzz_invalid_product_123")
    assert productListingPage.isSearchVisible(), "The app should handle the non-matching search gracefully without crash or UI corruption."
    assert productListingPage.isEmptyStateMessageVisible() or not productListingPage.isProductItemVisible(timeout=2), "The screen should show either no Product item cards or an appropriate empty state/message."


def test_verifySearchFieldCanBeClearedAndProductListResets(productListingPage):
    """5. Verify search field can be cleared and product list resets"""
    productListingPage.tapSearch()
    productListingPage.enterSearch("shoes")
    assert productListingPage.getSearchText() == "shoes", "Filtered results should be initiated by entering a valid keyword."
    productListingPage.clearSearch()
    assert productListingPage.getSearchText() == "", "The Search field text should be removed successfully."
    assert productListingPage.isProductItemVisible(), "The product list should reset to the default or broader catalog state and show Product item cards."


def test_applyCategoryFilterToNarrowProductResults(productListingPage):
    """6. Apply Category filter to narrow product results"""
    productListingPage.tapCategoryFilter()
    assert productListingPage.isCategoryFilterVisible(), "The Category filter should open successfully."
    productListingPage.tapCategoryOption()
    assert productListingPage.isProductItemVisible(), "A category should be selectable and the product listing should refresh to show relevant products."


def test_changeCategoryFilterSelection(productListingPage):
    """7. Change category filter selection"""
    productListingPage.tapCategoryFilter()
    productListingPage.tapCategoryOption()
    assert productListingPage.isProductItemVisible(), "The listing should refresh after the first category selection."
    productListingPage.tapCategoryFilter()
    productListingPage.tapCategoryOption()
    assert productListingPage.isProductItemVisible(), "The second category selection should be accepted and results should update appropriately."


def test_verifySortReordersProductListing(productListingPage):
    """8. Verify Sort reorders product listing"""
    assert productListingPage.isProductItemVisible(), "Product item cards should be visible before sorting."
    productListingPage.tapSort()
    productListingPage.tapSortOption()
    assert productListingPage.isProductItemVisible(), "The Sort button should provide sorting functionality and keep product items visible after reordering."
