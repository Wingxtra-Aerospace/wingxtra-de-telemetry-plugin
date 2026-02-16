from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class DEFacadeBase(ABC):
    @abstractmethod
    def on_receive(self, message: dict[str, Any]) -> None:
        raise NotImplementedError
