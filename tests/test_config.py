from wingxtra_plugin.config import Config


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
    assert config.de_module_name == "WX_TELEMETRY_SENDER"
    assert config.simulate is False
    assert config.send_hz == 3.0
