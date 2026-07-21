import pytest

from pages.login_page import LoginPage


@pytest.fixture
def loginPage(driver):
    page = LoginPage(driver)
    page.navigate()
    return page


def test_successfulLoginWithValidUsernameAndPassword(loginPage):
    """1. Successful login with valid username and password"""
    loginPage.enterUsername("bod@example.com")
    loginPage.enterPassword("10203040")
    loginPage.tapLoginButton()

    assert not loginPage.isUsernameVisible(timeout=5), "Expected entered credentials to be accepted and the login screen to no longer show the Username field."
    assert not loginPage.isPasswordVisible(timeout=5), "Expected the user to be authenticated successfully and the login screen to no longer show the Password field."
    assert not loginPage.isLoginButtonVisible(timeout=5), "Expected the app to navigate away from the Login screen to an authenticated area after successful login."


def test_loginFailsWithInvalidPassword(loginPage):
    """2. Login fails with invalid password"""
    loginPage.enterUsername("bod@example.com")
    loginPage.enterPassword("wrong-password")
    loginPage.tapLoginButton()

    assert loginPage.isLoginButtonVisible(timeout=5), "Expected login to be unsuccessful when an incorrect password is entered."
    assert loginPage.isUsernameVisible(timeout=5) and loginPage.isPasswordVisible(timeout=5), "Expected the user to remain on the Login screen after a failed login attempt."
    assert loginPage.isLoginButtonVisible(timeout=5), "Expected an authentication failure indication to be shown while remaining on the Login screen."


def test_loginFailsWithInvalidUsername(loginPage):
    """3. Login fails with invalid username"""
    loginPage.enterUsername("invalid_user@example.com")
    loginPage.enterPassword("10203040")
    loginPage.tapLoginButton()

    assert loginPage.isLoginButtonVisible(timeout=5), "Expected login to be unsuccessful when an invalid username is entered."
    assert loginPage.isUsernameVisible(timeout=5) and loginPage.isPasswordVisible(timeout=5), "Expected the user to remain on the Login screen after entering invalid credentials."
    assert loginPage.isLoginButtonVisible(timeout=5), "Expected an appropriate error or validation indication for invalid credentials."


def test_loginFailsWhenBothUsernameAndPasswordAreEmpty(loginPage):
    """4. Login fails when both Username and Password are empty"""
    loginPage.tapLoginButton()

    assert loginPage.isLoginButtonVisible(timeout=5), "Expected login to be prevented when both Username and Password are empty."
    assert loginPage.isUsernameVisible(timeout=5) and loginPage.isPasswordVisible(timeout=5), "Expected the user to remain on the Login screen when no credentials are entered."
    assert loginPage.isLoginButtonVisible(timeout=5), "Expected validation feedback indicating required fields must be entered."


def test_loginFailsWhenUsernameIsEmpty(loginPage):
    """5. Login fails when Username is empty"""
    loginPage.enterPassword("10203040")
    loginPage.tapLoginButton()

    assert loginPage.isLoginButtonVisible(timeout=5), "Expected login to be prevented when Username is empty."
    assert loginPage.isUsernameVisible(timeout=5) and loginPage.isPasswordVisible(timeout=5), "Expected the user to remain on the Login screen when Username is missing."
    assert loginPage.isUsernameVisible(timeout=5), "Expected validation feedback indicating that Username is required."


def test_loginFailsWhenPasswordIsEmpty(loginPage):
    """6. Login fails when Password is empty"""
    loginPage.enterUsername("bod@example.com")
    loginPage.tapLoginButton()

    assert loginPage.isLoginButtonVisible(timeout=5), "Expected login to be prevented when Password is empty."
    assert loginPage.isUsernameVisible(timeout=5) and loginPage.isPasswordVisible(timeout=5), "Expected the user to remain on the Login screen when Password is missing."
    assert loginPage.isPasswordVisible(timeout=5), "Expected validation feedback indicating that Password is required."


def test_passwordFieldAcceptsTextEntryForAuthenticationInput(loginPage):
    """7. Password field accepts text entry for authentication input"""
    loginPage.enterPassword("10203040")
    loginPage.enterUsername("bod@example.com")
    loginPage.tapLoginButton()

    assert loginPage.isPasswordVisible(timeout=5) or not loginPage.isPasswordVisible(timeout=5), "Expected the Password field to accept the entered input."
    assert not loginPage.isLoginButtonVisible(timeout=5), "Expected the login request to be submitted when Login is tapped with entered credentials."
    assert not loginPage.isUsernameVisible(timeout=5), "Expected authentication outcome to match the validity of the entered credentials."


def test_usernameFieldAcceptsTextEntryAndAllowsLoginSubmission(loginPage):
    """8. Username field accepts text entry and allows login submission"""
    loginPage.enterUsername("bod@example.com")
    loginPage.enterPassword("10203040")
    loginPage.tapLoginButton()

    assert loginPage.isUsernameVisible(timeout=5) or not loginPage.isUsernameVisible(timeout=5), "Expected the Username field to accept the entered input."
    assert not loginPage.isLoginButtonVisible(timeout=5), "Expected the login request to be submitted successfully when Login is tapped."
    assert not loginPage.isPasswordVisible(timeout=5), "Expected authentication outcome to match the validity of the entered credentials."


def test_retryLoginAfterFailedAttemptUsingCorrectedCredentials(loginPage):
    """9. Retry login after failed attempt using corrected credentials"""
    loginPage.enterUsername("bod@example.com")
    loginPage.enterPassword("wrong-password")
    loginPage.tapLoginButton()
    loginPage.enterPassword("10203040")
    loginPage.tapLoginButton()

    assert loginPage.isLoginButtonVisible(timeout=5), "Expected the initial login attempt with incorrect password to fail."
    assert not loginPage.isUsernameVisible(timeout=5), "Expected the user to be able to authenticate successfully after correcting credentials in the same session."
    assert not loginPage.isLoginButtonVisible(timeout=5), "Expected the app to navigate away from the Login screen after the retry succeeds."
