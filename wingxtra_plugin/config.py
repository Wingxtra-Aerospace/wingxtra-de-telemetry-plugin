from __future__ import annotations

import os
from dataclasses import dataclass

from .databus_lib.messages import (
    TYPE_AndruavMessage_GPS,
    TYPE_AndruavMessage_NAV_INFO,
    TYPE_AndruavMessage_POWER,
)


@dataclass(frozen=True)
class Config:
    drone_id: str
    api_url: str
    api_key: str
    send_hz: float = 3.0
    de_comm_host: str = "127.0.0.1"
    de_comm_port: int = 60000
    de_listen_host: str = "0.0.0.0"
    de_listen_port: int = 61233
    de_subscriptions: tuple[int, ...] = (
        TYPE_AndruavMessage_GPS,
        TYPE_AndruavMessage_POWER,
        TYPE_AndruavMessage_NAV_INFO,
    )
    http_timeout_seconds: float = 3.0
    offline_backoff_seconds: float = 1.0
    log_level: str = "INFO"
    simulate: bool = False
    de_module_name: str = "WX_TELEMETRY_SENDER"

    @property
    def send_interval_seconds(self) -> float:
        return 1.0 / max(0.1, self.send_hz)

    @property
    def de_receive_port(self) -> int:
        """Alias for compatibility with older naming in comments/docs."""
        return self.de_listen_port

    @classmethod
    def from_env(cls) -> "Config":
        return cls(
            drone_id=_required_env("DRONE_ID"),
            api_url=_required_env("API_URL"),
            api_key=_required_env("API_KEY"),
            send_hz=_float_env("SEND_HZ", 3.0),
            de_comm_host=os.getenv("DE_COMM_HOST", "127.0.0.1"),
            de_comm_port=_int_env("DE_COMM_PORT", 60000),
            de_listen_host=os.getenv("DE_LISTEN_HOST", "0.0.0.0"),
            de_listen_port=_int_env("DE_LISTEN_PORT", 61233),
            de_subscriptions=_int_csv_env(
                "DE_SUBSCRIPTIONS",
                (
                    TYPE_AndruavMessage_GPS,
                    TYPE_AndruavMessage_POWER,
                    TYPE_AndruavMessage_NAV_INFO,
                ),
            ),
            http_timeout_seconds=_float_env("HTTP_TIMEOUT_SECONDS", 3.0),
            offline_backoff_seconds=_float_env("OFFLINE_BACKOFF_SECONDS", 1.0),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            simulate=_bool_env("SIMULATE", False),
            de_module_name=os.getenv("DE_MODULE_NAME", "WX_TELEMETRY_SENDER"),
        )


def _required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ValueError(f"Missing required environment variable: {name}")
    return value


def _float_env(name: str, default: float) -> float:
    raw = os.getenv(name)
    return float(raw) if raw else default


def _int_env(name: str, default: int) -> int:
    raw = os.getenv(name)
    return int(raw) if raw else default


def _bool_env(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _int_csv_env(name: str, default: tuple[int, ...]) -> tuple[int, ...]:
    raw = os.getenv(name)
    if not raw:
        return default
    parsed = tuple(int(item.strip()) for item in raw.split(",") if item.strip())
    return parsed or default
