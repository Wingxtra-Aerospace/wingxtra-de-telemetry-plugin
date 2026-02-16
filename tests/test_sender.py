from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from wingxtra_plugin.sender import TelemetrySender


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
