from wingxtra_plugin.telemetry_mapper import map_databus_to_payload


def test_map_databus_to_payload_contains_required_root_fields():
    payload = map_databus_to_payload("WX-DRN-001", {"state": {"armed": True, "mode": "AUTO"}})

    assert payload["schema_version"] == 1
    assert payload["drone_id"] == "WX-DRN-001"
    assert payload["state"]["mode"] == "AUTO"
    assert "ts" in payload
    assert payload["position"] == {"lat": 0.0, "lon": 0.0, "alt_m": 0.0}


def test_mapper_supports_alternate_position_keys():
    payload = map_databus_to_payload(
        "WX-DRN-001",
        {
            "gps": {"latitude": "5.6037", "longitude": "-0.1870", "altitude": "120.3"},
        },
    )

    assert payload["position"] == {"lat": 5.6037, "lon": -0.187, "alt_m": 120.3}
