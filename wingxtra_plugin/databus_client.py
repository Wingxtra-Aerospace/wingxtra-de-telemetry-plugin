from __future__ import annotations

import importlib
import json
from typing import Any


class DataBusClient:
    """Adapter for the official DroneEngage DataBus Python client/template APIs."""

    def __init__(
        self,
        host: str,
        comm_port: int,
        receive_port: int,
        module_name: str = "WX_TELEMETRY",
        subscriptions: tuple[str, ...] = ("telemetry",),
        databus_client: Any | None = None,
    ) -> None:
        self._host = host
        self._comm_port = comm_port
        self._receive_port = receive_port
        self._module_name = module_name
        self._subscriptions = subscriptions
        self._client = databus_client
        self._initialized = False

    def _ensure_connected(self) -> None:
        if self._client is None:
            self._client = _load_official_databus_client(
                host=self._host,
                comm_port=self._comm_port,
                receive_port=self._receive_port,
            )

        if self._initialized:
            return

        _call_first(self._client, ("connect", "start", "open"))
        _call_first(self._client, ("register_module", "register", "hello"), self._module_name)

        for topic in self._subscriptions:
            _call_first(
                self._client,
                (
                    "subscribe",
                    "add_subscription",
                    "set_filter",
                    "filter",
                ),
                topic,
            )
        self._initialized = True

    def receive(self) -> dict[str, Any]:
        self._ensure_connected()
        message = _call_first(
            self._client,
            ("receive", "recv", "next_message", "read_message", "get_message"),
        )
        parsed = _normalize_message_payload(message)
        if not isinstance(parsed, dict):
            raise ValueError("DataBus payload must be a JSON object")
        return parsed


def _load_official_databus_client(*, host: str, comm_port: int, receive_port: int) -> Any:
    candidates = (
        "droneengage_databus.python.client",
        "droneengage_databus.client",
        "droneengage_databus",
    )
    last_error: Exception | None = None

    kwargs_variants = (
        {"host": host, "comm_port": comm_port, "receive_port": receive_port},
        {"host": host, "port": comm_port, "listen_port": receive_port},
        {"communicator_host": host, "communicator_port": comm_port, "local_port": receive_port},
        {"host": host, "port": comm_port},
    )

    for module_name in candidates:
        try:
            module = importlib.import_module(module_name)
        except Exception as exc:  # pragma: no cover
            last_error = exc
            continue

        for ctor_name in ("DataBusClient", "Client", "create_client"):
            ctor = getattr(module, ctor_name, None)
            if not callable(ctor):
                continue
            for kwargs in kwargs_variants:
                try:
                    return ctor(**kwargs)
                except TypeError:
                    continue

    raise RuntimeError(
        "Could not load DroneEngage DataBus Python client/template. "
        "Install Wingxtra-Aerospace/droneengage_databus python client and configure DE_RECEIVE_PORT."
    ) from last_error


def _call_first(target: Any, names: tuple[str, ...], *args: Any) -> Any:
    for name in names:
        fn = getattr(target, name, None)
        if callable(fn):
            return fn(*args)
    if args:
        raise RuntimeError(f"DataBus client missing required methods. Tried: {', '.join(names)}")
    return None


def _normalize_message_payload(message: Any) -> Any:
    if isinstance(message, dict):
        for key in ("payload", "data", "body", "message"):
            if key in message:
                message = message[key]
                break
        else:
            return message

    if isinstance(message, (bytes, bytearray)):
        return json.loads(message.decode("utf-8"))
    if isinstance(message, str):
        return json.loads(message)
    return message
