from __future__ import annotations

import json
import socket
from typing import Any


class DataBusClient:
    def __init__(self, host: str, port: int, timeout_seconds: float = 1.0) -> None:
        self._host = host
        self._port = port
        self._timeout = timeout_seconds

    def receive(self) -> dict[str, Any]:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.bind((self._host, self._port))
            sock.settimeout(self._timeout)
            message, _ = sock.recvfrom(65535)
        parsed = json.loads(message.decode("utf-8"))
        if not isinstance(parsed, dict):
            raise ValueError("DataBus payload must be a JSON object")
        return parsed
