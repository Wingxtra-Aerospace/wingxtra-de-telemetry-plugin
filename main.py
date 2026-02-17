from __future__ import annotations

import logging

from wingxtra_plugin.config import Config
from wingxtra_plugin.databus_client import DataBusClient
from wingxtra_plugin.sender import TelemetrySender, send_loop
from wingxtra_plugin.simulate import TelemetrySimulator
from wingxtra_plugin.telemetry_mapper import iso_utc_now, map_databus_to_payload


def _extract_cmd(message: dict) -> dict | None:
    cmd = message.get("ms")
    if cmd is None:
        cmd = message.get("cmd")
    return cmd if isinstance(cmd, dict) else None


def _build_payload_from_9102(drone_id: str, message: dict) -> dict | None:
    mt = message.get("mt", message.get("message_type"))
    try:
        mt_int = int(mt)
    except (TypeError, ValueError):
        return None

    if mt_int != 9102:
        return None

    ms = _extract_cmd(message)
    if ms is None:
        return None

    lat = ms.get("la")
    lon = ms.get("ln")
    ha = ms.get("ha")
    yaw = ms.get("y")

    if lat is None or lon is None:
        return None

    lat = float(lat) / 1e7
    lon = float(lon) / 1e7

    payload: dict = {
        "schema_version": 1,
        "drone_id": drone_id,
        "ts": iso_utc_now(),
        "position": {
            "lat": lat,
            "lon": lon,
            "alt_m": float(ha) if ha is not None else 0.0,
        },
    }

    if yaw is not None:
        payload["attitude"] = {"yaw_deg": float(yaw)}

    return payload


def main() -> None:
    config = Config.from_env()
    logging.basicConfig(
        level=getattr(logging, config.log_level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s :: %(message)s",
    )

    sender = TelemetrySender(config.api_url, config.api_key, timeout_seconds=config.http_timeout_seconds)

    if config.simulate:
        sim = TelemetrySimulator()

        def get_payload() -> dict:
            return map_databus_to_payload(config.drone_id, sim.next())

    else:
        client = DataBusClient(
            comm_host=config.de_comm_host,
            comm_port=config.de_comm_port,
            listen_host=config.de_listen_host,
            listen_port=config.de_listen_port,
            module_name=config.de_module_name,
            message_filter=list(config.de_subscriptions),
        )

        def get_payload() -> dict:
            while True:
                message = client.read_one_databus_message()
                if not isinstance(message, dict):
                    continue
                payload = _build_payload_from_9102(config.drone_id, message)
                if payload is not None:
                    return payload

    send_loop(
        get_payload=get_payload,
        sender=sender,
        send_interval_seconds=config.send_interval_seconds,
        offline_backoff_seconds=config.offline_backoff_seconds,
    )


if __name__ == "__main__":
    main()
