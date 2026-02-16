from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from wingxtra_plugin.sender import TelemetrySender, send_loop


class _Done(Exception):
    pass


def test_sender_uses_x_api_key_header() -> None:
    payload = {"schema_version": 1, "drone_id": "WX-DRN-001"}

    with patch("wingxtra_plugin.sender.request.urlopen") as mock_urlopen:
        response = MagicMock()
        response.status = 200
        mock_urlopen.return_value.__enter__.return_value = response

        sender = TelemetrySender("https://example.com/api/v1/telemetry", "top-secret")
        sender.send(payload)

    request_obj = mock_urlopen.call_args.args[0]
    assert request_obj.get_header("X-api-key") == "top-secret"
    assert request_obj.get_header("Authorization") is None
    assert json.loads(request_obj.data.decode("utf-8")) == payload


def test_send_loop_sends_latest_payload_after_failure(monkeypatch) -> None:
    payloads = [{"seq": 1}, {"seq": 2}]
    sent: list[dict] = []

    def get_payload() -> dict:
        return payloads.pop(0)

    class FakeSender:
        def send(self, payload: dict) -> None:
            sent.append(payload)
            if payload["seq"] == 1:
                raise RuntimeError("offline")

    sleep_calls = {"count": 0}

    def fake_sleep(_seconds: float) -> None:
        sleep_calls["count"] += 1
        if sleep_calls["count"] >= 2:
            raise _Done()

    monkeypatch.setattr("wingxtra_plugin.sender.time.sleep", fake_sleep)

    with pytest.raises(_Done):
        send_loop(
            get_payload=get_payload,
            sender=FakeSender(),
            send_interval_seconds=0.1,
            offline_backoff_seconds=0.1,
        )

    assert sent == [{"seq": 1}, {"seq": 2}]
