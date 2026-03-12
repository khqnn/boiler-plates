import time
from .base import BaseModel


class DummyModel(BaseModel):
    name = "dummy"

    def __init__(self, delay: float = 0.1):
        super().__init__()
        self.delay = delay

    def load(self) -> None:
        # Simulate heavy initialization
        time.sleep(self.delay)
        self._is_loaded = True

    def predict(self, prompt: str) -> str:
        if not self.is_loaded:
            raise RuntimeError("Model not loaded")
        # Return a simple echoed response for demo/testing
        return f"[dummy prediction] {prompt}"
