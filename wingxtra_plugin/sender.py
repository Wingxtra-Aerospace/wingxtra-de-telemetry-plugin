from __future__ import annotations

import json
import logging
import time
from typing import Any
from urllib import error, request


class TelemetrySender:
    def __init__(self, api_url: str, api_key: str, timeout_seconds: float = 3.0) -> None:
        self._api_url = api_url
        self._api_key = api_key
        self._timeout = timeout_seconds

    def send(self, payload: dict[str, Any]) -> None:
        body = json.dumps(payload).encode("utf-8")
        req = request.Request(
            self._api_url,
            data=body,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "X-API-Key": self._api_key,
            },
        )
        with request.urlopen(req, timeout=self._timeout) as resp:
            status = getattr(resp, "status", 200)
            if status >= 400:
                raise error.HTTPError(self._api_url, status, "HTTP error", hdrs=resp.headers, fp=None)


def send_loop(
    *,
    get_payload,
    sender: TelemetrySender,
    send_interval_seconds: float,
    offline_backoff_seconds: float,
) -> None:
    logger = logging.getLogger(__name__)
    failures = 0

    while True:
        payload = get_payload()
        try:
            sender.send(payload)
            failures = 0
            time.sleep(send_interval_seconds)
        except Exception as exc:  # intentionally broad for resilience
            failures += 1
            delay = min(30.0, offline_backoff_seconds * (2 ** min(failures, 8)))
            logger.warning("Send failed (%s). Retrying in %.1fs", exc, delay)
            time.sleep(delay)
