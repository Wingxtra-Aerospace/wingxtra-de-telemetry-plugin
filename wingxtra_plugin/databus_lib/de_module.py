from __future__ import annotations

import json
import logging
from typing import Any, Callable

from .messages import ANDRUAV_PROTOCOL_MESSAGE_TYPE
from .udpClient import UdpClient

MODULE_CLASS_GENERIC = "MODULE_CLASS_GENERIC"
MODULE_FEATURE_RECEIVING_TELEMETRY = "MODULE_FEATURE_RECEIVING_TELEMETRY"
MODULE_FEATURE_SENDING_TELEMETRY = "MODULE_FEATURE_SENDING_TELEMETRY"


class CModule:
    def __init__(self) -> None:
        self.m_OnReceive: Callable[[dict[str, Any]], None] | None = None
        self._udp: UdpClient | None = None
        self._comm_host = "127.0.0.1"
        self._comm_port = 60000
        self._listen_host = "0.0.0.0"
        self._listen_port = 61233
        self._features: list[str] = []
        self._message_filter: list[int] = []
        self._logger = logging.getLogger(__name__)

    def defineModule(
        self,
        module_class: str,
        module_name: str,
        module_key: str,
        module_version: str,
        message_filter: list[int],
    ) -> None:
        self._module_info = {
            "module_class": module_class,
            "module_name": module_name,
            "module_key": module_key,
            "module_version": module_version,
        }
        self._message_filter = list(message_filter)

    def addModuleFeatures(self, feature: str) -> None:
        self._features.append(feature)

    def initUDPChannel(
        self,
        target_ip: str,
        target_port: int,
        listen_ip: str,
        listen_port: int,
        packet_size: int = 8192,
    ) -> None:
        self._comm_host = target_ip
        self._comm_port = target_port
        self._listen_host = listen_ip
        self._listen_port = listen_port
        self._udp = UdpClient(listen_ip, listen_port, packet_size=packet_size)

    def connect(self) -> None:
        if self._udp is None:
            raise RuntimeError("UDP channel not initialized")
        hello = {
            "event": "register",
            "module": self._module_info,
            "features": self._features,
            "message_filter": self._message_filter,
        }
        self._udp.send(self._comm_host, self._comm_port, json.dumps(hello).encode("utf-8"))

    def receive_message(self) -> dict[str, Any]:
        if self._udp is None:
            raise RuntimeError("UDP channel not initialized")

        while True:
            packet = self._udp.recv()
            if packet is None:
                continue
            message = json.loads(packet.decode("utf-8"))
            if not isinstance(message, dict):
                continue

            msg_type = message.get(ANDRUAV_PROTOCOL_MESSAGE_TYPE)
            if self._message_filter and isinstance(msg_type, int) and msg_type not in self._message_filter:
                continue

            if self.m_OnReceive:
                try:
                    self.m_OnReceive(message)
                except Exception:  # pragma: no cover
                    self._logger.exception("m_OnReceive callback failed")
            return message
