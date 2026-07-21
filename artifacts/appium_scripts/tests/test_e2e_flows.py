"""Hand-composed end-to-end flows spanning multiple screens/Page Objects.

Unlike the per-screen generated tests (which each isolate a single screen behind
its own driver session), these flows chain the Login, Product Listing, Product
Details, and Cart Page Objects together in one session to exercise realistic
user journeys: browse -> select -> cart -> adjust/remove.
"""

import time

from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from pages.login_page import LoginPage
from pages.product_details_page import ProductDetailsPage
from pages.cart_page import CartPage

PRODUCT_IMAGE = (AppiumBy.ID, "com.saucelabs.mydemoapp.android:id/productIV")


def _select_nth_product(driver, index: int) -> None:
    """Tap the Nth product tile on the Product Listing screen (0-based)."""
    products = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(PRODUCT_IMAGE))
    products[index].click()


def _go_back_to_listing(driver) -> None:
    """Navigate back and give the recycler view a moment to settle before the next tap -
    this emulator is software-rendered and slow enough that an immediate re-tap can race
    the list's re-layout animation."""
    driver.back()
    time.sleep(2)
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(PRODUCT_IMAGE))


def test_login_then_browse_two_products_and_add_second_to_cart(driver):
    """Login -> view Product 1 -> back -> view Product 2 -> add Product 2 to cart."""
    login = LoginPage(driver)
    login.navigate()
    login.enterUsername("bod@example.com")
    login.enterPassword("10203040")
    login.tapLoginButton()

    _select_nth_product(driver, 0)
    details_first = ProductDetailsPage(driver)
    assert details_first.isProductTitleVisible(), "Expected first product's details screen to load."
    first_title = details_first.getProductTitleText()

    _go_back_to_listing(driver)
    _select_nth_product(driver, 1)
    details_second = ProductDetailsPage(driver)
    assert details_second.isProductTitleVisible(), "Expected second product's details screen to load."
    second_title = details_second.getProductTitleText()
    assert second_title != first_title, "Expected the two selected products to be different."

    details_second.tapAddToCart()

    cart = CartPage(driver)
    cart.navigate()
    assert cart.isCartTitleVisible(), "Expected Cart screen to load after adding an item."
    assert cart.isSubtotalVisible(), "Expected a non-empty cart to show a subtotal for the added item."


def test_add_two_different_products_then_remove_one_and_adjust_quantity(driver):
    """Select Product 1 -> add to cart -> select Product 2 -> add to cart -> remove one -> bump quantity of the other."""
    _select_nth_product(driver, 0)
    ProductDetailsPage(driver).tapAddToCart()
    _go_back_to_listing(driver)

    _select_nth_product(driver, 1)
    ProductDetailsPage(driver).tapAddToCart()
    _go_back_to_listing(driver)

    cart = CartPage(driver)
    cart.navigate()
    assert cart.isRemoveItemVisible(), "Expected at least one removable item in the cart."

    cart.tapRemoveItem()
    assert cart.isQuantityControlsVisible(), "Expected the remaining item's quantity controls to still be visible after removing the other item."

    cart.tapQuantityControls()
    assert cart.isSubtotalVisible(), "Expected the subtotal to still be visible after increasing quantity."


def test_add_single_product_to_cart_and_increase_quantity(driver):
    """Select a product -> add to cart -> increase its quantity from the Cart screen."""
    _select_nth_product(driver, 0)
    details = ProductDetailsPage(driver)
    details.tapAddToCart()

    cart = CartPage(driver)
    cart.navigate()
    assert cart.isQuantityControlsVisible(), "Expected quantity controls for the added item."

    cart.tapQuantityControls()
    assert cart.isSubtotalVisible(), "Expected subtotal to remain visible after increasing quantity."


def test_add_product_to_cart_then_remove_it_leaves_cart_empty(driver):
    """Select a product -> add to cart -> remove it -> cart should show its empty state again."""
    _select_nth_product(driver, 0)
    ProductDetailsPage(driver).tapAddToCart()

    cart = CartPage(driver)
    cart.navigate()
    assert cart.isRemoveItemVisible(), "Expected the added item to be removable."

    cart.tapRemoveItem()
    assert not cart.isRemoveItemVisible(timeout=5), "Expected cart to have no removable items after removing the only item."
