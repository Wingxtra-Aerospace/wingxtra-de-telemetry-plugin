from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def iso_utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def map_databus_to_payload(drone_id: str, data: dict[str, Any]) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "schema_version": 1,
        "drone_id": drone_id,
        "ts": iso_utc_now(),
    }

    if "position" in data:
        payload["position"] = {
            "lat": data["position"].get("lat"),
            "lon": data["position"].get("lon"),
            "alt_m": data["position"].get("alt_m"),
        }
    if "attitude" in data:
        payload["attitude"] = {"yaw_deg": data["attitude"].get("yaw_deg")}
    if "velocity" in data:
        payload["velocity"] = {"groundspeed_mps": data["velocity"].get("groundspeed_mps")}
    if "state" in data:
        payload["state"] = {
            "armed": data["state"].get("armed"),
            "mode": data["state"].get("mode"),
        }
    if "battery" in data:
        payload["battery"] = {
            "voltage_v": data["battery"].get("voltage_v"),
            "remaining_pct": data["battery"].get("remaining_pct"),
        }
    if "link" in data:
        payload["link"] = {"rssi_dbm": data["link"].get("rssi_dbm")}

    return payload
