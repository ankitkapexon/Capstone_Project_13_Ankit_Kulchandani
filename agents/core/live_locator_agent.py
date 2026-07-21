from abc import ABC, abstractmethod
from typing import Any, Dict


class LiveLocatorAgent(ABC):
    """Base contract for resolving SSM elements to real locators using the live UI
    hierarchy (Appium page_source) of the screen currently on-device - as opposed to
    agents/locator_agent.py, which guesses from a hardcoded per-app dictionary with no
    device involved.

    Implementations never touch the driver themselves - that's services/appium_runtime.py's
    job. This contract only takes the SSM data plus the XML already dumped from the
    device, so it can be unit-tested with a canned page_source string and no emulator."""

    @abstractmethod
    def resolve(self, ssm_data: Dict[str, Any], page_source_xml: str) -> Dict[str, Any]:
        """Return {"screen": <name>, "elements": [{"element", "element_type", "action",
        "locator_strategy", "locator_value", "input_value"?}, ...]} - the same schema
        already used by artifacts/locator_output/*.json, so nothing downstream changes."""
        raise NotImplementedError()
