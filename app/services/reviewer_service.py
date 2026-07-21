from __future__ import annotations

import re
from typing import Optional

from app.core.config import settings
from app.core.logging_config import configure_logging
from app.repositories.review_repository import InMemoryReviewRepository
from app.schemas.review import ReviewIssue, ReviewResponse

try:
    from app.services.langchain_reviewer import LangChainReviewer
except ImportError:  # pragma: no cover - optional dependency path
    LangChainReviewer = None  # type: ignore[assignment]


class ReviewerService:
    """Heuristic reviewer for Appium Python test scripts.

    This implementation is intentionally deterministic so it is easy to unit test
    and does not require external LLM calls. It still provides a structured JSON-like
    interface that can be replaced later by a LangChain + Claude-backed implementation.
    """

    def __init__(self, repository: Optional[InMemoryReviewRepository] = None) -> None:
        self.repository = repository or InMemoryReviewRepository()
        self.logger = configure_logging()
        self.langchain_reviewer = LangChainReviewer() if settings.reviewer_provider == "langchain" and LangChainReviewer is not None else None

    def analyze_script(self, script: str, app_name: str = "Unknown App") -> ReviewResponse:
        if self.langchain_reviewer is not None:
            try:
                return self.langchain_reviewer.review(script, app_name=app_name)
            except Exception as exc:  # pragma: no cover - defensive fallback
                self.logger.warning("LangChain reviewer failed, falling back to heuristic analysis: %s", exc)

        issues: list[ReviewIssue] = []

        if re.search(r"find_element_by_xpath|find_elements_by_xpath", script, re.IGNORECASE):
            issues.append(self._make_issue(
                category="xpath_locator",
                severity="high",
                title="XPath locator detected",
                description="XPath locators are brittle and should be replaced with stable locators when possible.",
                recommendation="Prefer accessibility ids, resource ids, or robust UI selectors.",
                example_fix="driver.find_element('accessibility id', 'login_button')"
            ))

        if re.search(r"time\.sleep\(|sleep\(", script):
            issues.append(self._make_issue(
                category="hardcoded_wait",
                severity="high",
                title="Hardcoded wait found",
                description="A fixed sleep introduces flakiness and slows the suite.",
                recommendation="Replace hardcoded waits with explicit waits such as WebDriverWait.",
                example_fix="WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, 'login')));"
            ))

        if not re.search(r"WebDriverWait|wait_until|expected_conditions", script, re.IGNORECASE):
            issues.append(self._make_issue(
                category="missing_explicit_wait",
                severity="medium",
                title="Missing explicit wait",
                description="The script does not use explicit waits, which makes it susceptible to timing issues.",
                recommendation="Use explicit waits around UI interactions.",
                example_fix="wait = WebDriverWait(driver, 10); wait.until(EC.visibility_of_element_located((By.ID, 'login')));"
            ))

        if re.search(r"assert\s+True|assert\s+False|assert\s+\w+\s*==\s*\w+", script):
            issues.append(self._make_issue(
                category="weak_assertion",
                severity="medium",
                title="Weak or trivial assertion",
                description="The assertion does not validate meaningful app behavior.",
                recommendation="Assert on visible state, text, or a meaningful outcome.",
                example_fix="assert 'Welcome' in driver.page_source"
            ))

        if re.search(r"except\s*:\s*$", script, re.IGNORECASE | re.MULTILINE):
            pass
        else:
            issues.append(self._make_issue(
                category="missing_exception_handling",
                severity="medium",
                title="Missing exception handling",
                description="The script does not wrap interactions in a try/except block.",
                recommendation="Catch expected exceptions and log context for debugging.",
                example_fix="try:\n    element.click()\nexcept Exception as exc:\n    logger.exception('Failed to click login button')"
            ))

        if "logging" not in script.lower() and "logger" not in script.lower():
            issues.append(self._make_issue(
                category="missing_logging",
                severity="low",
                title="Missing logging",
                description="The script lacks structured logging for troubleshooting.",
                recommendation="Add concise logging around setup and key actions.",
                example_fix="logger.info('Attempting login flow')"
            ))

        if re.search(r"def\s+test_|class\s+Test", script):
            pass
        else:
            issues.append(self._make_issue(
                category="poor_naming",
                severity="low",
                title="Poor naming",
                description="The script is missing clear test naming conventions.",
                recommendation="Use descriptive test names that reflect the scenario.",
                example_fix="def test_user_can_log_in_successfully():"
            ))

        if issues:
            score = max(40, 100 - (len(issues) * 8))
        else:
            score = 100

        response = ReviewResponse(
            overall_score=score,
            summary=f"Reviewed {app_name} and found {len(issues)} actionable issues.",
            issues=issues,
            optimized_script=self._build_optimized_script(script),
        )

        self.repository.save_review(response.model_dump())
        self.logger.info("Reviewed script for %s with score %s", app_name, response.overall_score)
        return response

    def _make_issue(self, **kwargs) -> ReviewIssue:
        return ReviewIssue(**kwargs)

    def _build_optimized_script(self, script: str) -> str:
        return """
# Optimized Appium test example
from appium.webdriver.common.appiumby import By
from appium.webdriver.common.mobileby import MobileBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def test_user_can_log_in_successfully():
    logger.info('Starting login flow')
    wait = WebDriverWait(driver, 10)
    login_button = wait.until(EC.element_to_be_clickable((By.ID, 'login')))
    login_button.click()
    assert 'Welcome' in driver.page_source
""".strip()
