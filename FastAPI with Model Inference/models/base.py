from typing import Any


class BaseModel:
    """Minimal interface for models loaded into memory.

    Subclass this and implement `load` and `predict`.
    """

    name: str = "base"

    def __init__(self, **kwargs: Any):
        self._is_loaded = False

    def load(self) -> None:
        """Load model into memory. May perform I/O or heavy initialization."""
        raise NotImplementedError()

    def predict(self, prompt: str) -> str:
        """Synchronous prediction API. Override to call the model."""
        raise NotImplementedError()

    @property
    def is_loaded(self) -> bool:
        return self._is_loaded
