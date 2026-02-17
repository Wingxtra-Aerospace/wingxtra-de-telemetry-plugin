from __future__ import annotations

import logging
import os
import random
from dataclasses import dataclass, field
from typing import Any

from .databus_lib.de_module import (
    MODULE_CLASS_GENERIC,
    MODULE_FEATURE_RECEIVING_TELEMETRY,
    CModule,
)
from .databus_lib.messages import (
    ALT_PROTOCOL_MESSAGE_CMD_KEYS,
    ALT_PROTOCOL_MESSAGE_TYPE_KEYS,
    ANDRUAV_PROTOCOL_MESSAGE_CMD,
    ANDRUAV_PROTOCOL_MESSAGE_TYPE,
    TYPE_AndruavMessage_GPS,
    TYPE_AndruavMessage_NAV_INFO,
    TYPE_AndruavMessage_POWER,
)
from .sniffer import sniff_de_databus_json


@dataclass
class TelemetryState:
    position: dict[str, Any] = field(default_factory=dict)
    velocity: dict[str, Any] = field(default_factory=dict)
    state: dict[str, Any] = field(default_factory=dict)
    battery: dict[str, Any] = field(default_factory=dict)
    attitude: dict[str, Any] = field(default_factory=dict)
    link: dict[str, Any] = field(default_factory=dict)

    def to_payload(self) -> dict[str, Any]:
        payload: dict[str, Any] = {}
        for key in ("position", "velocity", "state", "battery", "attitude", "link"):
            value = getattr(self, key)
            if value:
                payload[key] = dict(value)
        return payload


class DataBusClient:
    def __init__(
        self,
        comm_host: str,
        comm_port: int,
        listen_port: int,
        listen_host: str = "0.0.0.0",
        module_name: str = "WX_TELEMETRY_SENDER",
        module_version: str = "0.1.0",
        message_filter: list[int] | None = None,
        module: CModule | None = None,
        sniff_mode: bool | None = None,
    ) -> None:
        self._logger = logging.getLogger(__name__)
        self._state = TelemetryState()
        self._module = module or CModule()
        self._message_filter = message_filter or [
            TYPE_AndruavMessage_GPS,
            TYPE_AndruavMessage_POWER,
            TYPE_AndruavMessage_NAV_INFO,
        ]

        env_sniff = os.getenv("SNIFF_MODE", "true").lower() in ("1", "true", "yes")
        self._sniff_mode = env_sniff if sniff_mode is None else sniff_mode
        self._sniff_port = int(os.getenv("DE_COMM_PORT", str(comm_port)))
        self._sniff_iface = os.getenv("SNIFF_IFACE", "lo")

        module_key = "".join(str(random.randint(0, 9)) for _ in range(12))
        self._module.defineModule(
            module_class=MODULE_CLASS_GENERIC,
            module_name=module_name,
            module_key=module_key,
            module_version=module_version,
            message_filter=self._message_filter,
        )
        self._module.addModuleFeatures(MODULE_FEATURE_RECEIVING_TELEMETRY)
        self._module.m_OnReceive = self._on_receive

        if not self._sniff_mode:
            self._module.initUDPChannel(
                target_ip=comm_host,
                target_port=comm_port,
                listen_ip=listen_host,
                listen_port=listen_port,
                packet_size=8192,
            )
            self._module.connect()

    def read_one_databus_message(self) -> dict[str, Any] | None:
        if self._sniff_mode:
            return sniff_de_databus_json(self._sniff_port, iface=self._sniff_iface, timeout_s=1.0)
        return self._module.receive_message()

    def receive(self) -> dict[str, Any]:
        message = self.read_one_databus_message()
        if message is None:
            return self._state.to_payload()
        self._on_receive(message)
        return self._state.to_payload()

    def _on_receive(self, jMsg: dict[str, Any]) -> None:
        msg_type = jMsg.get(ANDRUAV_PROTOCOL_MESSAGE_TYPE)
        if msg_type is None:
            for key in ALT_PROTOCOL_MESSAGE_TYPE_KEYS:
                if key in jMsg:
                    msg_type = jMsg[key]
                    break

        msg_type = _normalize_message_type(msg_type)

        cmd = jMsg.get(ANDRUAV_PROTOCOL_MESSAGE_CMD)
        if cmd is None:
            for key in ALT_PROTOCOL_MESSAGE_CMD_KEYS:
                if key in jMsg:
                    cmd = jMsg[key]
                    break
        if not isinstance(cmd, dict):
            cmd = {}

        if cmd:
            self._logger.debug("DataBus message type=%s cmd.keys=%s", msg_type, sorted(cmd.keys()))

        if msg_type == TYPE_AndruavMessage_GPS:
            self._update_gps(cmd)
        elif msg_type == TYPE_AndruavMessage_POWER:
            self._update_power(cmd)
        elif msg_type == TYPE_AndruavMessage_NAV_INFO:
            self._update_nav(cmd)

    def _update_gps(self, cmd: dict[str, Any]) -> None:
        self._state.position = {
            "lat": _coalesce(cmd, "lat", "latitude", "y"),
            "lon": _coalesce(cmd, "lon", "lng", "longitude", "x"),
            "alt_m": _coalesce(cmd, "alt", "alt_m", "altitude", "z"),
        }

    def _update_power(self, cmd: dict[str, Any]) -> None:
        self._state.battery = {
            "voltage_v": _coalesce(cmd, "voltage", "voltage_v", "vbat"),
            "remaining_pct": _coalesce(cmd, "battery_remaining", "remaining", "remaining_pct"),
        }

    def _update_nav(self, cmd: dict[str, Any]) -> None:
        self._state.velocity = {
            "groundspeed_mps": _coalesce(cmd, "groundspeed", "groundspeed_mps", "speed"),
        }
        self._state.attitude = {"yaw_deg": _coalesce(cmd, "yaw", "yaw_deg", "heading")}
        self._state.state = {
            "armed": bool(_coalesce(cmd, "armed", default=False)),
            "mode": _coalesce(cmd, "mode", "flight_mode", default="UNKNOWN"),
        }
        self._state.link = {"rssi_dbm": _coalesce(cmd, "rssi", "rssi_dbm", default=None)}


def _coalesce(data: dict[str, Any], *keys: str, default: Any = None) -> Any:
    for key in keys:
        if key in data and data[key] is not None:
            return data[key]
    return default


def _normalize_message_type(value: Any) -> int | None:
    try:
        if value is None:
            return None
        return int(value)
    except (TypeError, ValueError):
        return None
