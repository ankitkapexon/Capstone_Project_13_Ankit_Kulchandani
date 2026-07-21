from abc import ABC, abstractmethod
from typing import Any, Dict


class AppiumScriptAgent(ABC):
    """Base contract for turning an SSM + manual test cases into a Page Object Model
    Appium test bundle for one screen."""

    @abstractmethod
    def generate(self, ssm_data: Dict[str, Any], testcases_text: str, **kwargs) -> Dict[str, str]:
        """Return a dict mapping relative output paths to file contents, e.g.
        {"pages/login_page.py": "...", "tests/test_login.py": "..."}."""
        raise NotImplementedError()
