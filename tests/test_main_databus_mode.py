from __future__ import annotations

import pytest

import main
from wingxtra_plugin.config import Config


class _Done(Exception):
    pass


def test_main_uses_comm_and_receive_ports_in_databus_mode(monkeypatch) -> None:
    captured: dict[str, object] = {}

    cfg = Config(
        drone_id="WX-DRN-001",
        api_url="https://example.com/api/v1/telemetry",
        api_key="secret",
        simulate=False,
        de_comm_host="127.0.0.1",
        de_comm_port=60000,
        de_receive_port=60001,
        de_module_name="WX_TELEMETRY",
        de_subscriptions=("telemetry",),
    )

    class FakeDataBusClient:
        def __init__(self, host, comm_port, receive_port, module_name, subscriptions):
            captured["host"] = host
            captured["comm_port"] = comm_port
            captured["receive_port"] = receive_port
            captured["module_name"] = module_name
            captured["subscriptions"] = subscriptions

        def receive(self):
            return {"position": {"lat": 1, "lon": 2, "alt_m": 3}}

    def fake_send_loop(*, get_payload, sender, send_interval_seconds, offline_backoff_seconds):
        payload = get_payload()
        captured["mapped_drone_id"] = payload["drone_id"]
        raise _Done()

    monkeypatch.setattr(main.Config, "from_env", classmethod(lambda cls: cfg))
    monkeypatch.setattr(main, "DataBusClient", FakeDataBusClient)
    monkeypatch.setattr(main, "send_loop", fake_send_loop)

    with pytest.raises(_Done):
        main.main()

    assert captured["host"] == "127.0.0.1"
    assert captured["comm_port"] == 60000
    assert captured["receive_port"] == 60001
    assert captured["module_name"] == "WX_TELEMETRY"
    assert captured["subscriptions"] == ("telemetry",)
    assert captured["mapped_drone_id"] == "WX-DRN-001"
