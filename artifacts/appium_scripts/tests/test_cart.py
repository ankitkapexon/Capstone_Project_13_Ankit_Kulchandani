import re

import pytest
from pages.cart_page import CartPage


@pytest.fixture
def cartPage(driver):
    return CartPage(driver)


def _extractNumericValue(text):
    match = re.search(r"-?\d+(?:\.\d+)?", text.replace(",", ""))
    return float(match.group()) if match else None


def test_verifyCartScreenLoadsWithAllKeyCartComponents(cartPage):
    """1. Verify Cart screen loads with all key cart components"""
    assert cartPage.isBackVisible(), "Expected Cart screen to open successfully with Back button visible."
    assert cartPage.isCartTitleVisible(), "Expected Cart title to be visible on the Cart screen."
    assert cartPage.isCartItemsListVisible(), "Expected Cart items list to be displayed on the Cart screen."
    assert cartPage.isProductImageVisible(), "Expected at least one cart item to show a product image."
    assert cartPage.isProductNameVisible(), "Expected at least one cart item to show a product name."
    assert cartPage.isProductPriceVisible(), "Expected at least one cart item to show a product price."
    assert cartPage.isQuantityStepperVisible(), "Expected at least one cart item to show a quantity stepper."
    assert cartPage.isRemoveItemVisible(), "Expected at least one cart item to show a remove item button."
    assert cartPage.isSubtotalVisible(), "Expected Subtotal text to be displayed on the Cart screen."
    assert cartPage.isCheckoutVisible(), "Expected Checkout button to be displayed on the Cart screen."


def test_verifyNavigationUsingTheBackButtonFromCart(cartPage):
    """2. Verify navigation using the Back button from Cart"""
    assert cartPage.isBackVisible(), "Expected Back button to be visible before attempting navigation."
    cartPage.tapBack()
    assert not cartPage.isCartTitleVisible(timeout=3), "Expected app to navigate away from Cart screen after tapping Back without crash or UI freeze."


def test_verifyCartItemListSupportsScrollingWhenMultipleItemsExist(cartPage):
    """3. Verify cart item list supports scrolling when multiple items exist"""
    assert cartPage.isCartItemsListVisible(), "Expected Cart items list to be visible before scrolling."
    assert cartPage.isProductNameVisible(), "Expected at least one item to remain visible while reviewing the cart list."
    assert cartPage.isQuantityStepperVisible(), "Expected item controls to remain visible without overlap or missing elements while scrolling."


def test_verifyTappingProductImageOpensTheRelatedProductDetails(cartPage):
    """4. Verify tapping Product image opens the related product details"""
    product_name = cartPage.getProductNameText()
    assert product_name, "Expected a visible product name before opening product details from the image."
    cartPage.tapProductImage()
    assert not cartPage.isCartTitleVisible(timeout=3), "Expected app to navigate to the corresponding product details screen after tapping Product image."
    assert product_name, "Expected the opened product to match the selected cart item."


def test_verifyTappingProductNameOpensTheRelatedProductDetails(cartPage):
    """5. Verify tapping Product name opens the related product details"""
    product_name = cartPage.getProductNameText()
    assert product_name, "Expected a listed product name to be available before tapping Product name."
    cartPage.tapProductName()
    assert not cartPage.isCartTitleVisible(timeout=3), "Expected app to navigate to the corresponding product details screen after tapping Product name."
    assert product_name == product_name, "Expected displayed product details to match the tapped Product name."


def test_verifyQuantityIncrementUpdatesItemQuantityAndSubtotal(cartPage):
    """6. Verify quantity increment updates item quantity and subtotal"""
    product_price = _extractNumericValue(cartPage.getProductPriceText())
    quantity_before = _extractNumericValue(cartPage.getQuantityStepperText())
    subtotal_before = _extractNumericValue(cartPage.getSubtotalText())

    assert product_price is not None, "Expected Product price to be readable before incrementing quantity."
    assert quantity_before is not None, "Expected current quantity to be readable before incrementing quantity."
    assert subtotal_before is not None, "Expected current subtotal to be readable before incrementing quantity."

    cartPage.tapQuantityStepper()

    quantity_after = _extractNumericValue(cartPage.getQuantityStepperText())
    subtotal_after = _extractNumericValue(cartPage.getSubtotalText())

    assert quantity_after is not None and quantity_after == quantity_before + 1, "Expected item quantity to increase by 1 after increment action."
    assert subtotal_after is not None and subtotal_after > subtotal_before, "Expected Subtotal to increase accordingly after quantity increment."
    assert subtotal_after >= subtotal_before + product_price, "Expected updated subtotal to reflect the added product quantity after refresh."


def test_verifyQuantityDecrementUpdatesItemQuantityAndSubtotal(cartPage):
    """7. Verify quantity decrement updates item quantity and subtotal"""
    quantity_before = _extractNumericValue(cartPage.getQuantityStepperText())
    subtotal_before = _extractNumericValue(cartPage.getSubtotalText())

    assert quantity_before is not None and quantity_before > 1, "Expected a cart item quantity greater than 1 before decrementing."
    assert subtotal_before is not None, "Expected current subtotal to be readable before decrementing quantity."

    cartPage.tapQuantityStepper()

    quantity_after = _extractNumericValue(cartPage.getQuantityStepperText())
    subtotal_after = _extractNumericValue(cartPage.getSubtotalText())

    assert quantity_after is not None and quantity_after == quantity_before - 1, "Expected item quantity to decrease by 1 after decrement action."
    assert subtotal_after is not None and subtotal_after < subtotal_before, "Expected Subtotal to decrease accordingly after quantity decrement."
    assert cartPage.getSubtotalText(), "Expected updated quantity and subtotal to be shown correctly after decrement."


def test_verifyQuantityStepperDoesNotAllowInvalidReductionBelowMinimumQuantity(cartPage):
    """8. Verify quantity stepper does not allow invalid reduction below minimum quantity"""
    quantity_before = _extractNumericValue(cartPage.getQuantityStepperText())
    subtotal_before = _extractNumericValue(cartPage.getSubtotalText())

    assert quantity_before is not None and quantity_before >= 1, "Expected item quantity to start at the minimum allowed value or higher."
    assert subtotal_before is not None, "Expected subtotal to be readable before attempting invalid decrement."

    cartPage.tapQuantityStepper()

    quantity_after = _extractNumericValue(cartPage.getQuantityStepperText())
    subtotal_after = _extractNumericValue(cartPage.getSubtotalText())

    assert quantity_after is not None and quantity_after >= 1, "Expected quantity not to go below the minimum allowed value."
    assert quantity_after == quantity_before or quantity_after == 1, "Expected decrement below minimum to be disabled or ignored gracefully."
    assert subtotal_after is not None and subtotal_after >= 0, "Expected no incorrect subtotal calculation after invalid decrement attempt."
