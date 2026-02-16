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
        "position": _extract_position(data),
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


def _extract_position(data: dict[str, Any]) -> dict[str, Any]:
    position_candidates = [
        data.get("position"),
        data.get("global_position"),
        data.get("gps"),
        data.get("location"),
    ]

    source = next((item for item in position_candidates if isinstance(item, dict)), {})

    lat = _first_available(source, data, keys=("lat", "latitude"))
    lon = _first_available(source, data, keys=("lon", "lng", "longitude"))
    alt = _first_available(
        source,
        data,
        keys=("alt_m", "alt", "altitude", "altitude_m", "relative_alt"),
    )

    return {
        "lat": _coerce_float(lat, 0.0),
        "lon": _coerce_float(lon, 0.0),
        "alt_m": _coerce_float(alt, 0.0),
    }


def _first_available(primary: dict[str, Any], fallback: dict[str, Any], keys: tuple[str, ...]) -> Any:
    for key in keys:
        if key in primary and primary[key] is not None:
            return primary[key]
    for key in keys:
        if key in fallback and fallback[key] is not None:
            return fallback[key]
    return None


def _coerce_float(value: Any, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default
