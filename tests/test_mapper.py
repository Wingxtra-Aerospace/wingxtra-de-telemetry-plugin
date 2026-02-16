from wingxtra_plugin.telemetry_mapper import map_databus_to_payload


def test_map_databus_to_payload_contains_required_root_fields():
    payload = map_databus_to_payload("WX-DRN-001", {"state": {"armed": True, "mode": "AUTO"}})

    assert payload["schema_version"] == 1
    assert payload["drone_id"] == "WX-DRN-001"
    assert payload["state"]["mode"] == "AUTO"
    assert "ts" in payload
