from __future__ import annotations

from wingxtra_plugin.databus_client import DataBusClient
from wingxtra_plugin.databus_lib.messages import (
    ANDRUAV_PROTOCOL_MESSAGE_CMD,
    ANDRUAV_PROTOCOL_MESSAGE_TYPE,
    TYPE_AndruavMessage_GPS,
    TYPE_AndruavMessage_NAV_INFO,
    TYPE_AndruavMessage_POWER,
)


class FakeModule:
    def __init__(self):
        self.m_OnReceive = None
        self.connected = False
        self.init_args = None
        self.messages: list[dict] = []

    def defineModule(self, **kwargs):
        self.defined = kwargs

    def addModuleFeatures(self, feature):
        self.feature = feature

    def initUDPChannel(self, **kwargs):
        self.init_args = kwargs

    def connect(self):
        self.connected = True

    def receive_message(self):
        msg = self.messages.pop(0)
        if self.m_OnReceive:
            self.m_OnReceive(msg)
        return msg


def test_databus_client_uses_comm_and_listen_ports_and_updates_state() -> None:
    fake = FakeModule()
    fake.messages = [
        {ANDRUAV_PROTOCOL_MESSAGE_TYPE: TYPE_AndruavMessage_GPS, ANDRUAV_PROTOCOL_MESSAGE_CMD: {"lat": 1.2, "lon": 3.4, "alt": 5.6}},
        {ANDRUAV_PROTOCOL_MESSAGE_TYPE: TYPE_AndruavMessage_POWER, ANDRUAV_PROTOCOL_MESSAGE_CMD: {"voltage": 22.2, "battery_remaining": 66}},
        {ANDRUAV_PROTOCOL_MESSAGE_TYPE: TYPE_AndruavMessage_NAV_INFO, ANDRUAV_PROTOCOL_MESSAGE_CMD: {"groundspeed": 12.3, "yaw": 45, "armed": True, "mode": "AUTO"}},
    ]

    client = DataBusClient(
        comm_host="127.0.0.1",
        comm_port=60000,
        listen_host="0.0.0.0",
        listen_port=61233,
        module=fake,
    )

    payload1 = client.receive()
    payload2 = client.receive()
    payload3 = client.receive()

    assert fake.connected is True
    assert fake.init_args["target_port"] == 60000
    assert fake.init_args["listen_port"] == 61233
    assert payload1["position"]["lat"] == 1.2
    assert payload2["battery"]["remaining_pct"] == 66
    assert payload3["state"]["mode"] == "AUTO"


def test_databus_client_handles_string_message_type_and_mt_ms_keys() -> None:
    fake = FakeModule()
    fake.messages = [
        {"mt": "1002", "ms": {"latitude": 5.6037, "longitude": -0.187, "altitude": 120.3}},
    ]

    client = DataBusClient(
        comm_host="127.0.0.1",
        comm_port=60000,
        listen_host="0.0.0.0",
        listen_port=61233,
        module=fake,
    )

    payload = client.receive()

    assert payload["position"] == {"lat": 5.6037, "lon": -0.187, "alt_m": 120.3}
