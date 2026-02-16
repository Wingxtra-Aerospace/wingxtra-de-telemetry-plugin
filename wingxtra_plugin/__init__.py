"""Wingxtra telemetry plugin package."""

from .config import Config
from .sender import TelemetrySender

__all__ = ["Config", "TelemetrySender"]
