from wingxtra_plugin.config import Config
from wingxtra_plugin.databus_lib.messages import (
    TYPE_AndruavMessage_GPS,
    TYPE_AndruavMessage_NAV_INFO,
    TYPE_AndruavMessage_POWER,
)


def test_config_from_env_defaults(monkeypatch):
    monkeypatch.setenv("DRONE_ID", "WX-DRN-001")
    monkeypatch.setenv("API_URL", "https://example.com/api/v1/telemetry")
    monkeypatch.setenv("API_KEY", "secret")
    monkeypatch.delenv("SIMULATE", raising=False)

    config = Config.from_env()

    assert config.de_comm_host == "127.0.0.1"
    assert config.de_comm_port == 60000
    assert config.de_listen_host == "0.0.0.0"
    assert config.de_listen_port == 61233
    assert config.de_receive_port == 61233
    assert config.de_module_name == "WX_TELEMETRY_SENDER"
    assert config.de_subscriptions == (
        TYPE_AndruavMessage_GPS,
        TYPE_AndruavMessage_POWER,
        TYPE_AndruavMessage_NAV_INFO,
    )
    assert config.simulate is False
    assert config.send_hz == 3.0


def test_config_parses_subscription_list(monkeypatch):
    monkeypatch.setenv("DRONE_ID", "WX-DRN-001")
    monkeypatch.setenv("API_URL", "https://example.com/api/v1/telemetry")
    monkeypatch.setenv("API_KEY", "secret")
    monkeypatch.setenv("DE_SUBSCRIPTIONS", "1002,1003,1036")

    config = Config.from_env()

    assert config.de_subscriptions == (1002, 1003, 1036)
