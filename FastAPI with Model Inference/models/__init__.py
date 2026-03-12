"""Model registry package.

Expose a simple `get_model(name)` function to retrieve initialized models.
Models are registered during application startup by calling `models.registry.initialize()`.
"""
from .registry import get_model, register_model, initialize

__all__ = ["get_model", "register_model", "initialize"]
