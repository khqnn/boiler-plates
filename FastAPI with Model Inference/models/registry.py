from typing import Dict, Type
from .base import BaseModel

# Internal registry mapping names to instantiated models
_MODELS: Dict[str, BaseModel] = {}
_TOKENIZERS: Dict[str, BaseModel] = {}


def register_model(name: str, model: BaseModel) -> None:
    """Register a model instance under a name. Overwrites if exists."""
    _MODELS[name] = model


def get_model(name: str) -> BaseModel:
    """Retrieve a model instance by name. Raises KeyError if missing."""
    return _MODELS[name]


def initialize() -> None:
    """Initialize all registered models by calling their `load` method.

    This function should be called on application startup.
    """
    for name, model in _MODELS.items():
        if not model.is_loaded:
            model.load()
