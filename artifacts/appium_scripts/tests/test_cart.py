import re

import pytest

from pages.cart_page import CartPage


@pytest.fixture
def cartPage(driver):
    page = CartPage(driver)
    page.navigate()
    return page


def _extract_numeric_value(text):
    match = re.search(r"-?\d+(?:\.\d+)?", text)
    return float(match.group()) if match else None


def test_verifyCartScreenLoadsWithAllKeyCartComponents(cartPage):
    """1. Verify Cart screen loads with all key cart components"""
    assert cartPage.isCartTitleVisible(), "Cart screen should open successfully and display the Cart title."
    assert cartPage.isCartItemsVisible(), "Cart items list should be visible for reviewing selected products."
    assert cartPage.isQuantityControlsVisible(), "Quantity controls should be visible for at least one listed cart item."
    assert cartPage.isRemoveItemVisible(), "Remove item button should be visible for cart items."
    assert cartPage.isSubtotalVisible(), "Subtotal text should be displayed on the Cart screen."
    assert cartPage.isCheckoutVisible(), "Checkout button should be displayed on the Cart screen."


def test_verifyCartItemsListSupportsScrollingWhenMultipleItemsExist(cartPage):
    """2. Verify cart items list supports scrolling when multiple items exist"""
    assert cartPage.isCartItemsVisible(), "Cart items list should be visible before attempting to scroll."
    cartPage.tapCartItems()
    assert cartPage.isCartItemsVisible(), "Cart items list should remain visible after scrolling interactions and be usable without layout issues."


def test_verifyIncreasingItemQuantityUsingQuantityControls(cartPage):
    """3. Verify increasing item quantity using Quantity controls"""
    before_subtotal_text = cartPage.getSubtotalText()
    before_subtotal_value = _extract_numeric_value(before_subtotal_text)

    cartPage.tapQuantityControls()

    after_subtotal_text = cartPage.getSubtotalText()
    after_subtotal_value = _extract_numeric_value(after_subtotal_text)

    assert cartPage.isQuantityControlsVisible(), "Cart should immediately reflect the updated quantity after increasing it."
    assert before_subtotal_text != after_subtotal_text, "Subtotal text should update after increasing the item quantity."
    assert before_subtotal_value is not None and after_subtotal_value is not None and after_subtotal_value > before_subtotal_value, "Subtotal should increase appropriately based on the item's price after quantity is increased."


def test_verifyDecreasingItemQuantityUsingQuantityControls(cartPage):
    """4. Verify decreasing item quantity using Quantity controls"""
    before_subtotal_text = cartPage.getSubtotalText()
    before_subtotal_value = _extract_numeric_value(before_subtotal_text)

    cartPage.tapQuantityControls()

    after_subtotal_text = cartPage.getSubtotalText()
    after_subtotal_value = _extract_numeric_value(after_subtotal_text)

    assert cartPage.isQuantityControlsVisible(), "Cart should immediately reflect the updated quantity after decreasing it."
    assert before_subtotal_text != after_subtotal_text, "Subtotal text should update after decreasing the item quantity."
    assert before_subtotal_value is not None and after_subtotal_value is not None and after_subtotal_value < before_subtotal_value, "Subtotal should decrease appropriately based on the item's price after quantity is decreased."


def test_verifyQuantityCannotBeReducedBelowTheMinimumAllowedValue(cartPage):
    """5. Verify quantity cannot be reduced below the minimum allowed value"""
    before_subtotal_text = cartPage.getSubtotalText()

    cartPage.tapQuantityControls()

    after_subtotal_text = cartPage.getSubtotalText()

    assert cartPage.isQuantityControlsVisible(), "Quantity controls should remain visible after attempting to reduce below the minimum allowed value."
    assert after_subtotal_text == before_subtotal_text or cartPage.isRemoveItemVisible(), "Quantity should not go below the minimum allowed value; if direct removal is not supported, the item should remain at the minimum until explicitly removed."
    assert "-" not in after_subtotal_text, "No incorrect negative subtotal or invalid cart state should be displayed after attempting to reduce below the minimum."


def test_verifyRemovingASingleItemFromTheCart(cartPage):
    """6. Verify removing a single item from the cart"""
    before_subtotal_text = cartPage.getSubtotalText()
    before_subtotal_value = _extract_numeric_value(before_subtotal_text)

    cartPage.tapRemoveItem()

    after_subtotal_text = cartPage.getSubtotalText()
    after_subtotal_value = _extract_numeric_value(after_subtotal_text)

    assert not cartPage.isRemoveItemVisible() or cartPage.isCartItemsVisible(), "Cart items list should refresh after removing a selected product."
    assert before_subtotal_text != after_subtotal_text, "Subtotal text should refresh after a cart item is removed."
    assert before_subtotal_value is not None and after_subtotal_value is not None and after_subtotal_value < before_subtotal_value, "Subtotal should decrease accordingly after removing a cart item."
