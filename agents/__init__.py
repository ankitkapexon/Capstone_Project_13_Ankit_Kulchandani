from .core.vision_agent import VisionAgent
from .core import TestCaseAgent
from .locator_agent import LocatorAgent

try:
    from .vision_agent import OpenAIVisionAgent, MockVisionAgent, create_vision_agent
except ImportError:
    OpenAIVisionAgent = None
    MockVisionAgent = None

    def create_vision_agent(provider: str = "openai", prompt_template: str = None):
        raise ImportError("The optional 'openai' package is required to use vision agents.")

__all__ = [
    "VisionAgent",
    "OpenAIVisionAgent",
    "MockVisionAgent",
    "create_vision_agent",
    "TestCaseAgent",
    "LocatorAgent",
]
