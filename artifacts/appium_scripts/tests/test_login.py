import pytest

from pages.login_page import LoginPage


@pytest.fixture
def loginPage(driver):
    return LoginPage(driver)


def test_successfulLoginWithValidUsernameAndPassword(loginPage):
    """1. Successful login with valid username and password"""
    loginPage.enterUsername("valid_user")
    loginPage.enterPassword("ValidPassword123!")
    loginPage.tapLogin()

    assert not loginPage.isErrorMessageVisible(timeout=3), "Expected no authentication error to be shown for valid credentials."
    assert loginPage.isAuthorizedAreaVisible(timeout=5), "Expected the user to be authenticated and navigated to the authorized area."
    assert not loginPage.isLoginScreenVisible(timeout=3), "Expected the app to leave the Login screen after successful login."


def test_loginAttemptWithInvalidPassword(loginPage):
    """2. Login attempt with invalid password"""
    loginPage.enterUsername("valid_user")
    loginPage.enterPassword("WrongPassword123!")
    loginPage.tapLogin()

    assert not loginPage.isAuthorizedAreaVisible(timeout=3), "Expected login to be rejected for an incorrect password."
    assert loginPage.isLoginScreenVisible(timeout=5), "Expected the user to remain on the Login screen after a failed login attempt."
    assert loginPage.isErrorMessageVisible(timeout=5), "Expected an authentication failure message or other clear denial indicator to be shown."


def test_loginAttemptWithUnregisteredUsername(loginPage):
    """3. Login attempt with unregistered username"""
    loginPage.enterUsername("unknown_user")
    loginPage.enterPassword("AnyPassword123!")
    loginPage.tapLogin()

    assert not loginPage.isAuthorizedAreaVisible(timeout=3), "Expected login to be rejected for an unregistered username."
    assert loginPage.isLoginScreenVisible(timeout=5), "Expected the user to stay on the Login screen when the account does not exist."
    assert loginPage.isErrorMessageVisible(timeout=5), "Expected a clear invalid-credentials or unknown-account error indication to be shown."


def test_loginWithBothUsernameAndPasswordLeftBlank(loginPage):
    """4. Login with both Username and Password left blank"""
    loginPage.tapLogin()

    assert not loginPage.isAuthorizedAreaVisible(timeout=3), "Expected the app not to log the user in when both credentials are blank."
    assert (
        loginPage.isUsernameRequiredMessageVisible(timeout=5)
        or loginPage.isPasswordRequiredMessageVisible(timeout=5)
        or loginPage.isErrorMessageVisible(timeout=5)
    ), "Expected required-field validation to be displayed or submission to be blocked clearly."
    assert loginPage.isLoginScreenVisible(timeout=5), "Expected the user to remain on the Login screen when login is attempted with blank credentials."


def test_loginWithBlankUsernameOnly(loginPage):
    """5. Login with blank Username only"""
    loginPage.enterPassword("ValidPassword123!")
    loginPage.tapLogin()

    assert not loginPage.isAuthorizedAreaVisible(timeout=3), "Expected login not to be performed when the Username field is blank."
    assert (
        loginPage.isUsernameRequiredMessageVisible(timeout=5)
        or loginPage.isErrorMessageVisible(timeout=5)
    ), "Expected the app to indicate that the Username field is required or invalid."
    assert loginPage.isLoginScreenVisible(timeout=5), "Expected the user to stay on the Login screen when Username is blank."


def test_loginWithBlankPasswordOnly(loginPage):
    """6. Login with blank Password only"""
    loginPage.enterUsername("valid_user")
    loginPage.tapLogin()

    assert not loginPage.isAuthorizedAreaVisible(timeout=3), "Expected login not to be performed when the Password field is blank."
    assert (
        loginPage.isPasswordRequiredMessageVisible(timeout=5)
        or loginPage.isErrorMessageVisible(timeout=5)
    ), "Expected the app to indicate that the Password field is required or invalid."
    assert loginPage.isLoginScreenVisible(timeout=5), "Expected the user to stay on the Login screen when Password is blank."


def test_passwordFieldAcceptsSecureInputDuringEntry(loginPage):
    """7. Password field accepts secure input during entry"""
    password_value = "P@ssw0rd!234"
    loginPage.enterPassword(password_value)

    assert loginPage.getPasswordText() is not None, "Expected the Password field to accept input."
    assert loginPage.getPasswordText() != password_value, "Expected entered password characters to be masked or otherwise protected from plain visibility during input."


def test_usernameFieldAcceptsStandardUsernameInput(loginPage):
    """8. Username field accepts standard username input"""
    username_value = "standard_user"
    loginPage.enterUsername(username_value)

    assert loginPage.getUsernameText() == username_value, "Expected the Username field to accept and display the entered username correctly."
    assert loginPage.isLoginScreenVisible(timeout=5), "Expected the entered username to remain visible and editable on the Login screen."


def test_loginWithTrimmedOrAccidentalLeadingAndTrailingSpacesInUsernameAndPassword(loginPage):
    """9. Login with trimmed or accidental leading and trailing spaces in Username and Password"""
    loginPage.enterUsername("  valid_user  ")
    loginPage.enterPassword("  ValidPassword123!  ")
    loginPage.tapLogin()

    assert loginPage.isAuthorizedAreaVisible(timeout=5) or loginPage.isErrorMessageVisible(timeout=5), "Expected the app to handle leading and trailing spaces consistently according to credential rules."
    assert loginPage.isAuthorizedAreaVisible(timeout=5) or loginPage.isLoginScreenVisible(timeout=5), "Expected login either to succeed with trimmed values or to keep the user on the Login screen if spaces are treated literally."
    assert loginPage.isAuthorizedAreaVisible(timeout=5) or loginPage.isErrorMessageVisible(timeout=5), "Expected a clear success path or an invalid credential response when spaces are entered around credentials."
