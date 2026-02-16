from __future__ import annotations

import json

from wingxtra_plugin.databus_lib.de_module import CModule
from wingxtra_plugin.databus_lib.messages import TYPE_AndruavMessage_GPS


class FakeUdp:
    def __init__(self, packets: list[bytes]):
        self._packets = packets

    def recv(self):
        if not self._packets:
            return None
        return self._packets.pop(0)

    def send(self, host: str, port: int, payload: bytes):
        self.sent = (host, port, payload)


def test_demodule_filters_using_numeric_string_message_type() -> None:
    module = CModule()
    module.defineModule(
        module_class="MODULE_CLASS_GENERIC",
        module_name="WX_TELEMETRY_SENDER",
        module_key="123456789012",
        module_version="0.1.0",
        message_filter=[TYPE_AndruavMessage_GPS],
    )

    accepted = {"mt": "1002", "ms": {"lat": 1, "lon": 2}}
    module._udp = FakeUdp([json.dumps(accepted).encode("utf-8")])

    msg = module.receive_message()

    assert msg["mt"] == "1002"
