from __future__ import annotations

import logging

from wingxtra_plugin.config import Config
from wingxtra_plugin.databus_client import DataBusClient
from wingxtra_plugin.sender import TelemetrySender, send_loop
from wingxtra_plugin.simulate import TelemetrySimulator
from wingxtra_plugin.telemetry_mapper import map_databus_to_payload


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
            config.de_comm_host,
            config.de_comm_port,
            module_name=config.de_module_name,
            subscriptions=config.de_subscriptions,
        )

        def get_payload() -> dict:
            return map_databus_to_payload(config.drone_id, client.receive())

    send_loop(
        get_payload=get_payload,
        sender=sender,
        send_interval_seconds=config.send_interval_seconds,
        offline_backoff_seconds=config.offline_backoff_seconds,
    )


if __name__ == "__main__":
    main()
