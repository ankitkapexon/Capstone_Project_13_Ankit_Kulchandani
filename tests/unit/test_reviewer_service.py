import unittest

from app.schemas.review import ReviewResponse
from app.services.reviewer_service import ReviewerService


class ReviewerServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = ReviewerService()

    def test_analyze_script_detects_common_issues(self) -> None:
        script = """
from appium import webdriver
import time

def test_login():
    driver = webdriver.Remote('http://localhost:4723/wd/hub', {})
    time.sleep(5)
    element = driver.find_element_by_xpath('//android.widget.Button[@text="Login"]')
    element.click()
    assert True
        """

        response = self.service.analyze_script(script, app_name="Demo App")

        self.assertIsInstance(response, ReviewResponse)
        self.assertGreaterEqual(response.overall_score, 0)
        self.assertLessEqual(response.overall_score, 100)
        self.assertTrue(any(issue.category == "xpath_locator" for issue in response.issues))
        self.assertTrue(any(issue.category == "hardcoded_wait" for issue in response.issues))
        self.assertTrue(any(issue.category == "weak_assertion" for issue in response.issues))
        self.assertTrue(any(issue.category == "missing_explicit_wait" for issue in response.issues))
        self.assertTrue(response.optimized_script)

    def test_analyze_script_returns_structured_output(self) -> None:
        response = self.service.analyze_script("driver.find_element_by_id('login')")

        self.assertEqual(response.issues[0].severity, "medium")
        self.assertTrue(response.summary)
        self.assertIn("optimized", response.optimized_script.lower())


if __name__ == "__main__":
    unittest.main()
