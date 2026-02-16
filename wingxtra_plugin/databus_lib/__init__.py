"""Vendored DroneEngage DataBus-compatible library surface."""

from .de_module import CModule
from .messages import *  # noqa: F403

__all__ = ["CModule"]
