from __future__ import annotations

import math
import time
from typing import Any


class TelemetrySimulator:
    def __init__(self) -> None:
        self._start = time.time()

    def next(self) -> dict[str, Any]:
        elapsed = time.time() - self._start
        return {
            "position": {
                "lat": 5.6037 + (math.sin(elapsed / 20.0) * 0.001),
                "lon": -0.1870 + (math.cos(elapsed / 20.0) * 0.001),
                "alt_m": 120.0 + (math.sin(elapsed / 5.0) * 5),
            },
            "attitude": {"yaw_deg": (elapsed * 15.0) % 360},
            "velocity": {"groundspeed_mps": 10.0 + abs(math.sin(elapsed / 4.0) * 5)},
            "state": {"armed": True, "mode": "AUTO"},
            "battery": {
                "voltage_v": 22.2 - min(2.2, elapsed / 1800.0),
                "remaining_pct": max(5, int(100 - (elapsed / 45.0))),
            },
            "link": {"rssi_dbm": -60 - int(abs(math.sin(elapsed / 3.0) * 10))},
        }
