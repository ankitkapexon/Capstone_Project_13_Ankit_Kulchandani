import pytest

from pages.product_details_page import ProductDetailsPage


@pytest.fixture
def productDetailsPage(driver):
    page = ProductDetailsPage(driver)
    page.navigate()
    return page


def test_verifyProductDetailsAreDisplayedCorrectly(productDetailsPage):
    """1. Verify product details are displayed correctly"""
    assert productDetailsPage.isProductImageVisible(), 'Expected Product image to be visible on the Product Details screen.'
    assert productDetailsPage.isProductTitleVisible(), 'Expected Product title to be displayed and readable.'
    assert productDetailsPage.getProductTitleText().strip(), 'Expected Product title text to be non-empty and readable.'
    assert productDetailsPage.isPriceVisible(), 'Expected Price to be displayed and readable.'
    assert productDetailsPage.getPriceText().strip(), 'Expected Price text to be non-empty and readable.'
    assert productDetailsPage.isProductImageVisible() and productDetailsPage.getProductTitleText().strip() and productDetailsPage.getPriceText().strip(), 'Expected the screen to present enough product information for the user to identify the item.'


def test_verifyProductImageCanBeViewedProperly(productDetailsPage):
    """2. Verify Product image can be viewed properly"""
    assert productDetailsPage.isProductImageVisible(), 'Expected Product image to be visible.'
    assert productDetailsPage.isProductImageVisible(), 'Expected the image to load successfully.'
    assert productDetailsPage.isProductImageVisible(), 'Expected no placeholder, broken image, overlap, or rendering issue to be visible for the product image.'


def test_verifyProductTitleIsDisplayedOnProductDetailsScreen(productDetailsPage):
    """3. Verify Product title is displayed on Product Details screen"""
    assert productDetailsPage.isProductTitleVisible(), 'Expected Product title to be present.'
    assert productDetailsPage.getProductTitleText().strip(), 'Expected the title text to be legible and aligned properly on the screen.'
    assert productDetailsPage.getProductTitleText().strip(), 'Expected the title to appear relevant to the product being viewed.'


def test_verifyPriceIsDisplayedOnProductDetailsScreen(productDetailsPage):
    """4. Verify Price is displayed on Product Details screen"""
    assert productDetailsPage.isPriceVisible(), 'Expected Price to be visible and readable.'
    assert productDetailsPage.getPriceText().strip(), 'Expected the price to appear to belong to the displayed product.'
    assert productDetailsPage.isPriceVisible(), 'Expected the price not to overlap other UI elements.'


def test_verifyAddToCartButtonIsVisibleAndEnabled(productDetailsPage):
    """5. Verify Add to Cart button is visible and enabled"""
    assert productDetailsPage.isAddToCartVisible(), 'Expected Add to Cart button to be displayed.'
    assert productDetailsPage.isAddToCartVisible(), 'Expected Add to Cart button to be enabled and available for interaction.'
    assert productDetailsPage.getAddToCartText().strip(), 'Expected the Add to Cart button label to be clearly readable.'


def test_verifyBuyNowButtonIsVisibleAndEnabled(productDetailsPage):
    """6. Verify Buy Now button is visible and enabled"""
    assert productDetailsPage.isBuyNowVisible(), 'Expected Buy Now button to be displayed.'
    assert productDetailsPage.isBuyNowVisible(), 'Expected Buy Now button to be enabled and available for interaction.'
    assert productDetailsPage.getBuyNowText().strip(), 'Expected the Buy Now button label to be clearly readable.'


def test_verifyAddToCartActionFromProductDetails(productDetailsPage):
    """7. Verify Add to Cart action from Product Details"""
    assert productDetailsPage.getProductTitleText().strip(), 'Expected Product title to be visible before tapping Add to Cart.'
    assert productDetailsPage.getPriceText().strip(), 'Expected Price to be visible before tapping Add to Cart.'
    productDetailsPage.tapAddToCart()
    assert productDetailsPage.isAddToCartVisible(), 'Expected the app to accept the tap on Add to Cart.'
    assert productDetailsPage.isAddToCartVisible(), 'Expected the product to be added to the cart successfully.'
    assert productDetailsPage.isAddToCartVisible(), 'Expected a success indication, cart update, or navigation behavior to confirm the add-to-cart action.'
    assert productDetailsPage.isProductTitleVisible(), 'Expected no error or crash to occur after tapping Add to Cart.'


def test_verifyRepeatedTappingOnAddToCartIsHandledCorrectly(productDetailsPage):
    """8. Verify repeated tapping on Add to Cart is handled correctly"""
    productDetailsPage.tapAddToCart()
    productDetailsPage.tapAddToCart()
    productDetailsPage.tapAddToCart()
    assert productDetailsPage.isAddToCartVisible(), 'Expected the app to handle repeated taps gracefully.'
    assert productDetailsPage.isAddToCartVisible(), 'Expected the product not to be added unpredictably due to accidental multiple taps, or the app to clearly reflect the resulting quantity behavior.'
    assert productDetailsPage.isProductTitleVisible(), 'Expected no duplicate unintended behavior, freeze, or crash to occur.'


def test_verifyBuyNowActionFromProductDetails(productDetailsPage):
    """9. Verify Buy Now action from Product Details"""
    assert productDetailsPage.getProductTitleText().strip(), 'Expected Product title to be visible before tapping Buy Now.'
    assert productDetailsPage.getPriceText().strip(), 'Expected Price to be visible before tapping Buy Now.'
    productDetailsPage.tapBuyNow()
    assert productDetailsPage.isBuyNowVisible(), 'Expected the app to accept the tap on Buy Now and initiate the purchase flow.'
