from __future__ import annotations

import pytest

from wingxtra_plugin.databus_client import DataBusClient


class FakeDataBus:
    def __init__(self) -> None:
        self.registered: str | None = None
        self.subscriptions: list[str] = []

    def register_module(self, module_name: str) -> None:
        self.registered = module_name

    def subscribe(self, topic: str) -> None:
        self.subscriptions.append(topic)

    def receive(self) -> dict[str, object]:
        return {"state": {"mode": "AUTO"}}


class FakeWrappedPayloadBus(FakeDataBus):
    def receive(self) -> dict[str, object]:
        return {"payload": {"battery": {"remaining_pct": 99}}}


class FakeBadBus(FakeDataBus):
    def receive(self) -> str:
        return "not-json"


def test_databus_client_registers_and_subscribes() -> None:
    fake = FakeDataBus()
    client = DataBusClient("127.0.0.1", 60000, module_name="wingxtra", subscriptions=("telemetry",), databus_client=fake)

    message = client.receive()

    assert message["state"]["mode"] == "AUTO"
    assert fake.registered == "wingxtra"
    assert fake.subscriptions == ["telemetry"]


def test_databus_client_unwraps_payload_field() -> None:
    fake = FakeWrappedPayloadBus()
    client = DataBusClient("127.0.0.1", 60000, databus_client=fake)

    message = client.receive()

    assert message["battery"]["remaining_pct"] == 99


def test_databus_client_rejects_non_json_payload() -> None:
    fake = FakeBadBus()
    client = DataBusClient("127.0.0.1", 60000, databus_client=fake)

    with pytest.raises(Exception):
        client.receive()
