from abc import ABC, abstractmethod
from typing import Any, Dict


class VisionAgent(ABC):
    """Single shared abstraction for screenshot understanding agents."""

    def __init__(self, model_name: str | None = None, **kwargs):
        self.model_name = model_name

    @abstractmethod
    def analyze_image(self, image_path: str, **kwargs) -> Dict[str, Any]:
        """Analyze a screenshot and return a structured result."""
        raise NotImplementedError

    def validate_configuration(self) -> None:
        """Ensure the agent configuration is valid before runtime."""
        return None


__all__ = ["VisionAgent"]
