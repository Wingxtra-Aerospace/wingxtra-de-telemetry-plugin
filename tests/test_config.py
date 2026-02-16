from wingxtra_plugin.config import Config


def test_config_from_env_defaults(monkeypatch):
    monkeypatch.setenv("DRONE_ID", "WX-DRN-001")
    monkeypatch.setenv("API_URL", "https://example.com/api/v1/telemetry")
    monkeypatch.setenv("API_KEY", "secret")
    monkeypatch.delenv("SIMULATE", raising=False)

    config = Config.from_env()

    assert config.de_comm_host == "127.0.0.1"
    assert config.de_comm_port == 60000
    assert config.de_receive_port == 60001
    assert config.de_module_name == "WX_TELEMETRY"
    assert config.de_subscriptions == ("telemetry",)
    assert config.simulate is False
    assert config.send_hz == 3.0


def test_config_parses_subscription_list(monkeypatch):
    monkeypatch.setenv("DRONE_ID", "WX-DRN-002")
    monkeypatch.setenv("API_URL", "https://example.com/api/v1/telemetry")
    monkeypatch.setenv("API_KEY", "secret")
    monkeypatch.setenv("DE_SUBSCRIPTIONS", "telemetry, attitude ,battery")

    config = Config.from_env()

    assert config.de_subscriptions == ("telemetry", "attitude", "battery")
