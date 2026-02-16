from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    drone_id: str
    api_url: str
    api_key: str
    send_hz: float = 3.0
    de_comm_host: str = "127.0.0.1"
    de_comm_port: int = 60000
    http_timeout_seconds: float = 3.0
    offline_backoff_seconds: float = 1.0
    log_level: str = "INFO"
    simulate: bool = False
    de_module_name: str = "wingxtra_de_telemetry"
    de_subscriptions: tuple[str, ...] = ("telemetry",)

    @property
    def send_interval_seconds(self) -> float:
        return 1.0 / max(0.1, self.send_hz)

    @classmethod
    def from_env(cls) -> "Config":
        return cls(
            drone_id=_required_env("DRONE_ID"),
            api_url=_required_env("API_URL"),
            api_key=_required_env("API_KEY"),
            send_hz=_float_env("SEND_HZ", 3.0),
            de_comm_host=os.getenv("DE_COMM_HOST", "127.0.0.1"),
            de_comm_port=_int_env("DE_COMM_PORT", 60000),
            http_timeout_seconds=_float_env("HTTP_TIMEOUT_SECONDS", 3.0),
            offline_backoff_seconds=_float_env("OFFLINE_BACKOFF_SECONDS", 1.0),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            simulate=_bool_env("SIMULATE", False),
            de_module_name=os.getenv("DE_MODULE_NAME", "wingxtra_de_telemetry"),
            de_subscriptions=_csv_env("DE_SUBSCRIPTIONS", ("telemetry",)),
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


def _csv_env(name: str, default: tuple[str, ...]) -> tuple[str, ...]:
    raw = os.getenv(name)
    if not raw:
        return default
    values = tuple(item.strip() for item in raw.split(",") if item.strip())
    return values or default
