import ast
import unittest

from services.appium_agent import (
    MockAppiumScriptAgent,
    _check_appium_script,
    _check_pom_consistency,
    _screen_contract,
)


class MockAppiumScriptAgentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.ssm_data = {
            "screen_name": "Login",
            "screen_purpose": "Authenticate user",
            "elements": [
                {"label": "Username", "type": "textfield", "actions": ["enter_text"]},
                {"label": "Password", "type": "textfield", "actions": ["enter_text"]},
                {"label": "Login", "type": "button", "actions": ["tap"]},
            ],
        }
        self.testcases_text = (
            "Screen: Login\n\n"
            "Test Case 1: Successful login with valid credentials\n"
            "Description: Verify login succeeds.\n"
            "Steps:\n  1. Enter username.\n  2. Enter password.\n  3. Tap Login.\n"
            "Expected Result:\n  - User is authenticated.\n"
        )

    def test_generates_page_object_and_test_module(self) -> None:
        agent = MockAppiumScriptAgent()
        files = agent.generate(self.ssm_data, self.testcases_text)

        self.assertEqual(set(files.keys()), {"pages/login_page.py", "tests/test_login.py"})

    def test_page_object_is_valid_python_with_camelcase_pom_shape(self) -> None:
        agent = MockAppiumScriptAgent()
        files = agent.generate(self.ssm_data, self.testcases_text)
        page_source = files["pages/login_page.py"]

        ast.parse(page_source)
        self.assertIn("class LoginPage(BasePage):", page_source)
        self.assertIn("from core.base_page import BasePage", page_source)
        self.assertIn("LOCATORS", page_source)
        self.assertIn('"ios": {}', page_source)
        self.assertIn("def enterUsername(self, value):", page_source)
        self.assertIn("def tapLogin(self):", page_source)
        self.assertIn("AppiumBy.ACCESSIBILITY_ID", page_source)
        self.assertNotIn("driver.find_element", page_source)

    def test_test_module_is_valid_python_and_uses_page_object_only(self) -> None:
        agent = MockAppiumScriptAgent()
        files = agent.generate(self.ssm_data, self.testcases_text)
        test_source = files["tests/test_login.py"]

        ast.parse(test_source)
        self.assertIn("from pages.login_page import LoginPage", test_source)
        self.assertIn("def loginPage(driver):", test_source)
        self.assertIn("return LoginPage(driver)", test_source)
        self.assertIn("def test_", test_source)
        self.assertNotIn("AppiumBy", test_source)
        self.assertNotIn("driver.find_element", test_source)

    def test_generated_files_have_no_flagged_anti_patterns(self) -> None:
        agent = MockAppiumScriptAgent()
        files = agent.generate(self.ssm_data, self.testcases_text)

        for content in files.values():
            self.assertEqual(_check_appium_script(content), [])

    def test_generated_files_are_cross_file_consistent(self) -> None:
        agent = MockAppiumScriptAgent()
        files = agent.generate(self.ssm_data, self.testcases_text)

        issues = _check_pom_consistency(
            files["pages/login_page.py"], files["tests/test_login.py"], "loginPage", "LoginPage"
        )
        self.assertEqual(issues, [])

    def test_handles_screen_with_no_elements(self) -> None:
        agent = MockAppiumScriptAgent()
        files = agent.generate({"screen_name": "Empty", "elements": []}, "Test Case 1: Load screen\n")

        ast.parse(files["pages/empty_page.py"])
        ast.parse(files["tests/test_empty.py"])
        self.assertIn("No SSM elements available", files["pages/empty_page.py"])


class ScreenContractTests(unittest.TestCase):
    def test_multi_word_screen_name(self) -> None:
        contract = _screen_contract("Product Details")
        self.assertEqual(contract["class_name"], "ProductDetailsPage")
        self.assertEqual(contract["fixture_name"], "productDetailsPage")
        self.assertEqual(contract["page_file"], "pages/product_details_page.py")
        self.assertEqual(contract["test_file"], "tests/test_product_details.py")


class CheckAppiumScriptTests(unittest.TestCase):
    def test_flags_hardcoded_sleep(self) -> None:
        issues = _check_appium_script("import time\ntime.sleep(5)\n")
        self.assertTrue(any("sleep" in issue.lower() for issue in issues))

    def test_flags_invalid_syntax(self) -> None:
        issues = _check_appium_script("def broken(:\n")
        self.assertTrue(any("syntax" in issue.lower() for issue in issues))

    def test_clean_script_has_no_issues(self) -> None:
        issues = _check_appium_script("def test_ok(driver):\n    assert driver is not None\n")
        self.assertEqual(issues, [])


class CheckPomConsistencyTests(unittest.TestCase):
    def test_flags_method_called_by_test_but_not_defined_on_page(self) -> None:
        page_source = "class LoginPage(BasePage):\n    def tapLogin(self):\n        pass\n"
        test_source = "def test_x(loginPage):\n    loginPage.tapLoginBtn()\n"

        issues = _check_pom_consistency(page_source, test_source, "loginPage", "LoginPage")
        self.assertTrue(any("tapLoginBtn" in issue for issue in issues))

    def test_no_issues_when_methods_match(self) -> None:
        page_source = "class LoginPage(BasePage):\n    def tapLogin(self):\n        pass\n"
        test_source = "def test_x(loginPage):\n    loginPage.tapLogin()\n"

        issues = _check_pom_consistency(page_source, test_source, "loginPage", "LoginPage")
        self.assertEqual(issues, [])

    def test_flags_missing_expected_class(self) -> None:
        page_source = "class WrongName(BasePage):\n    pass\n"
        test_source = "def test_x(loginPage):\n    pass\n"

        issues = _check_pom_consistency(page_source, test_source, "loginPage", "LoginPage")
        self.assertTrue(any("LoginPage" in issue for issue in issues))


if __name__ == "__main__":
    unittest.main()
