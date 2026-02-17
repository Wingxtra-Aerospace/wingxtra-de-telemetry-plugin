from __future__ import annotations

from main import _build_payload_from_9102


def test_build_payload_from_9102_scales_lat_lon() -> None:
    payload = _build_payload_from_9102(
        "WX-DRN-001",
        {"mt": 9102, "ms": {"la": 56037000, "ln": -1870000, "ha": 100, "y": 45}},
    )

    assert payload is not None
    assert payload["position"]["lat"] == 5.6037
    assert payload["position"]["lon"] == -0.187
    assert payload["attitude"]["yaw_deg"] == 45.0
