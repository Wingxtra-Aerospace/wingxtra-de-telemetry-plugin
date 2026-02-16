from __future__ import annotations

import importlib
import json
from typing import Any


class DataBusClient:
    """Wrapper around the official DroneEngage DataBus Python client.

    The plugin does not open/bind raw UDP sockets directly. Instead, it expects
    the DroneEngage DataBus client library to handle module registration,
    subscription/filtering, chunking and payload reassembly.
    """

    def __init__(
        self,
        host: str,
        port: int,
        module_name: str = "wingxtra_de_telemetry",
        subscriptions: tuple[str, ...] = ("telemetry",),
        databus_client: Any | None = None,
    ) -> None:
        self._host = host
        self._port = port
        self._module_name = module_name
        self._subscriptions = subscriptions
        self._client = databus_client

    def _ensure_connected(self) -> None:
        if self._client is None:
            self._client = _load_official_databus_client(self._host, self._port)

        _call_first(self._client, ("register_module", "register", "hello"), self._module_name)

        for topic in self._subscriptions:
            _call_first(
                self._client,
                ("subscribe", "add_subscription", "set_filter"),
                topic,
            )

    def receive(self) -> dict[str, Any]:
        self._ensure_connected()
        message = _call_first(
            self._client,
            ("receive", "recv", "next_message", "read_message"),
        )
        parsed = _normalize_message_payload(message)
        if not isinstance(parsed, dict):
            raise ValueError("DataBus payload must be a JSON object")
        return parsed


def _load_official_databus_client(host: str, port: int) -> Any:
    candidates = (
        "droneengage_databus.python.client",
        "droneengage_databus.client",
        "droneengage_databus",
    )
    last_error: Exception | None = None

    for module_name in candidates:
        try:
            module = importlib.import_module(module_name)
        except Exception as exc:  # pragma: no cover - import candidate probing
            last_error = exc
            continue

        # common constructor names used by SDK-style libraries
        for ctor_name in ("DataBusClient", "Client", "create_client"):
            ctor = getattr(module, ctor_name, None)
            if ctor is None:
                continue
            if callable(ctor):
                return ctor(host=host, port=port)

    raise RuntimeError(
        "Could not load DroneEngage DataBus Python client. "
        "Install/attach the official droneengage_databus python package/template."
    ) from last_error


def _call_first(target: Any, names: tuple[str, ...], *args: Any) -> Any:
    for name in names:
        fn = getattr(target, name, None)
        if callable(fn):
            return fn(*args)
    raise RuntimeError(f"DataBus client missing required methods. Tried: {', '.join(names)}")


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
