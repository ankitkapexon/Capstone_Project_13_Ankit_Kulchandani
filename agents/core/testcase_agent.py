from abc import ABC, abstractmethod
from typing import Any, Dict


class TestCaseAgent(ABC):
    """Base contract for turning SSM JSON into manual test cases."""

    @abstractmethod
    def generate_from_ssm(self, ssm_data: Dict[str, Any], **kwargs) -> str:
        raise NotImplementedError()
