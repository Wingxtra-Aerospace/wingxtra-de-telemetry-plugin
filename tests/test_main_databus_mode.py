from __future__ import annotations

import pytest

import main
from wingxtra_plugin.config import Config


class _Done(Exception):
    pass


def test_main_uses_comm_and_listen_ports_in_databus_mode(monkeypatch) -> None:
    captured: dict[str, object] = {}

    cfg = Config(
        drone_id="WX-DRN-001",
        api_url="https://example.com/api/v1/telemetry",
        api_key="secret",
        simulate=False,
        de_comm_host="127.0.0.1",
        de_comm_port=60000,
        de_listen_host="0.0.0.0",
        de_listen_port=61233,
        de_module_name="WX_TELEMETRY_SENDER",
        de_subscriptions=(1002, 1003, 1036),
    )

    class FakeDataBusClient:
        def __init__(self, comm_host, comm_port, listen_host, listen_port, module_name, message_filter):
            captured["comm_host"] = comm_host
            captured["comm_port"] = comm_port
            captured["listen_host"] = listen_host
            captured["listen_port"] = listen_port
            captured["module_name"] = module_name
            captured["message_filter"] = message_filter

        def read_one_databus_message(self):
            return {"mt": 9102, "ms": {"la": 56037000, "ln": -1870000, "ha": 120.3, "y": 45}}

    def fake_send_loop(*, get_payload, sender, send_interval_seconds, offline_backoff_seconds):
        payload = get_payload()
        captured["mapped_drone_id"] = payload["drone_id"]
        captured["lat"] = payload["position"]["lat"]
        raise _Done()

    monkeypatch.setattr(main.Config, "from_env", classmethod(lambda cls: cfg))
    monkeypatch.setattr(main, "DataBusClient", FakeDataBusClient)
    monkeypatch.setattr(main, "send_loop", fake_send_loop)

    with pytest.raises(_Done):
        main.main()

    assert captured["comm_host"] == "127.0.0.1"
    assert captured["comm_port"] == 60000
    assert captured["listen_host"] == "0.0.0.0"
    assert captured["listen_port"] == 61233
    assert captured["module_name"] == "WX_TELEMETRY_SENDER"
    assert captured["message_filter"] == [1002, 1003, 1036]
    assert captured["mapped_drone_id"] == "WX-DRN-001"
    assert captured["lat"] == 5.6037
