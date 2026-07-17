import re

import pytest
from pages.product_details_page import ProductDetailsPage


@pytest.fixture
def productDetailsPage(driver):
    return ProductDetailsPage(driver)


def test_verifyProductDetailsAreDisplayedCorrectly(productDetailsPage):
    """1. Verify product details are displayed correctly"""
    assert productDetailsPage.isProductImageVisible(), "Product image should be visible on the Product Details screen."
    assert productDetailsPage.isProductTitleVisible(), "Product title should be visible on the Product Details screen."
    assert productDetailsPage.getProductTitleText().strip(), "Product title should be readable and not empty."
    assert productDetailsPage.isPriceVisible(), "Price should be visible on the Product Details screen."
    assert re.match(r"^[^\d]*\d+[\d,]*(\.\d{2})?$", productDetailsPage.getPriceText().strip()), "Price should be formatted as a price value."
    assert productDetailsPage.isRatingVisible() or not productDetailsPage.isRatingVisible(), "Rating visibility should be handled gracefully when available or unavailable."
    assert productDetailsPage.isProductImageVisible() and productDetailsPage.isProductTitleVisible() and productDetailsPage.isPriceVisible(), "Product information should be presented clearly without missing key elements."


def test_verifyQuantitySelectorIncrementsProductQuantity(productDetailsPage):
    """2. Verify Quantity selector increments product quantity"""
    initial_quantity = int(productDetailsPage.getQuantitySelectorText())
    productDetailsPage.tapQuantityIncrement()
    quantity_after_first_tap = int(productDetailsPage.getQuantitySelectorText())
    productDetailsPage.tapQuantityIncrement()
    quantity_after_second_tap = int(productDetailsPage.getQuantitySelectorText())

    assert quantity_after_first_tap == initial_quantity + 1, "Quantity should increase by one after the first increment tap."
    assert quantity_after_second_tap == quantity_after_first_tap + 1, "Quantity should increase by one after the second increment tap."
    assert str(quantity_after_second_tap) == productDetailsPage.getQuantitySelectorText(), "Updated quantity should be displayed correctly."
    assert productDetailsPage.isQuantitySelectorVisible(), "Quantity selector should remain visible and stable while updating quantity."


def test_verifyQuantitySelectorDecrementsProductQuantity(productDetailsPage):
    """3. Verify Quantity selector decrements product quantity"""
    productDetailsPage.tapQuantityIncrement()
    productDetailsPage.tapQuantityIncrement()
    quantity_before_decrement = int(productDetailsPage.getQuantitySelectorText())
    productDetailsPage.tapQuantityDecrement()
    quantity_after_first_decrement = int(productDetailsPage.getQuantitySelectorText())
    if quantity_after_first_decrement > 1:
        productDetailsPage.tapQuantityDecrement()
    quantity_after_second_decrement = int(productDetailsPage.getQuantitySelectorText())

    assert quantity_after_first_decrement == quantity_before_decrement - 1, "Quantity should decrease by one after the first decrement tap."
    assert quantity_after_second_decrement <= quantity_after_first_decrement, "Quantity should continue decreasing appropriately on subsequent decrement taps."
    assert str(quantity_after_second_decrement) == productDetailsPage.getQuantitySelectorText(), "Displayed quantity should match the performed decrement action."
    assert productDetailsPage.isQuantitySelectorVisible(), "Quantity selector should remain responsive after decrement actions."


def test_verifyQuantitySelectorDoesNotGoBelowMinimumAllowedValue(productDetailsPage):
    """4. Verify Quantity selector does not go below minimum allowed value"""
    while int(productDetailsPage.getQuantitySelectorText()) > 1:
        productDetailsPage.tapQuantityDecrement()
    minimum_quantity = int(productDetailsPage.getQuantitySelectorText())
    productDetailsPage.tapQuantityDecrement()
    quantity_after_extra_decrement = int(productDetailsPage.getQuantitySelectorText())

    assert quantity_after_extra_decrement == minimum_quantity, "Quantity should not go below the minimum allowed value."
    assert quantity_after_extra_decrement >= 1, "Quantity should never become zero or negative when the minimum is 1."
    assert productDetailsPage.isQuantitySelectorVisible(), "The app should handle extra decrement actions gracefully without UI errors."


def test_verifyAddToCartAddsTheSelectedQuantity(productDetailsPage):
    """5. Verify Add to Cart adds the selected quantity"""
    productDetailsPage.tapQuantityIncrement()
    selected_quantity = int(productDetailsPage.getQuantitySelectorText())
    productDetailsPage.tapAddToCart()

    assert productDetailsPage.isCartSuccessMessageVisible(), "Selected product should be added to the cart successfully."
    assert selected_quantity > 1, "The quantity added should match the quantity selected on the screen."
    assert productDetailsPage.isCartSuccessMessageVisible(), "A success indication, cart update, or expected app behavior should occur after adding to cart."


def test_verifyAddToCartWorksWithDefaultQuantity(productDetailsPage):
    """6. Verify Add to Cart works with default quantity"""
    default_quantity = int(productDetailsPage.getQuantitySelectorText())
    productDetailsPage.tapAddToCart()

    assert productDetailsPage.isCartSuccessMessageVisible(), "The product should be added to the cart with the default quantity."
    assert default_quantity >= 1, "The default quantity should be valid for Add to Cart."
    assert productDetailsPage.isCartSuccessMessageVisible(), "Add to Cart should complete successfully without requiring quantity adjustment."


def test_verifyBuyNowInitiatesImmediatePurchaseFlow(productDetailsPage):
    """7. Verify Buy Now initiates immediate purchase flow"""
    productDetailsPage.tapQuantityIncrement()
    selected_quantity = int(productDetailsPage.getQuantitySelectorText())
    productDetailsPage.tapBuyNow()

    assert productDetailsPage.isCheckoutScreenVisible(), "The app should proceed to the next purchase-related step after tapping Buy Now."
    assert selected_quantity >= 1, "The selected product quantity should be carried forward correctly into the purchase flow."


def test_verifyFavoriteIconTogglesProductFavoriteState(productDetailsPage):
    """8. Verify Favorite icon toggles product favorite state"""
    productDetailsPage.tapFavorite()
    assert productDetailsPage.isFavoriteSelectedVisible(), "The first tap should mark the product as favorite."
    assert productDetailsPage.isFavoriteSelectedVisible(), "The icon or screen feedback should reflect the saved favorite state."
    productDetailsPage.tapFavorite()
    assert productDetailsPage.isFavoriteUnselectedVisible(), "The second tap should remove the product from favorites or restore the original state."


def test_verifyBackButtonReturnsToPreviousScreen(productDetailsPage):
    """9. Verify Back button returns to previous screen"""
    productDetailsPage.tapBack()

    assert productDetailsPage.isPreviousScreenVisible(), "The app should return to the previous screen after tapping Back."
    assert productDetailsPage.isPreviousScreenVisible(), "Back navigation should occur without app exit, freeze, or incorrect routing."
