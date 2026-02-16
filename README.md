# Wingxtra DroneEngage Telemetry Plugin

Drone-side Python service that reads telemetry from DroneEngage DataBus (or simulation mode), maps it into the Wingxtra telemetry schema, and posts updates to the Fleet API.

## Build

```bash
python -m pip wheel . -w dist --no-build-isolation
```

## Run (simulation mode)

```bash
export DRONE_ID=WX-DRN-001
export API_URL=https://yourdomain.com/api/v1/telemetry
export API_KEY=secret
export SIMULATE=true
python main.py
```

## Run (DroneEngage DataBus mode)

```bash
export DRONE_ID=WX-DRN-001
export API_URL=https://yourdomain.com/api/v1/telemetry
export API_KEY=secret
export SIMULATE=false
python main.py
```

Notes:
- In non-simulate mode the plugin expects the official `droneengage_databus/python` client/template APIs.
- The plugin connects to communicator host/port (`DE_COMM_HOST:DE_COMM_PORT`, default `127.0.0.1:60000`) and uses a separate local receive port (`DE_RECEIVE_PORT`, default `60001`) so it does not steal communicator port `60000`.
- Use `DE_MODULE_NAME=WX_TELEMETRY` (default) for module registration; adjust if needed.
- API authentication uses `X-API-Key: <API_KEY>`.
- Mapper always emits `position` (required by backend `TelemetryIn`) and will normalize common position key variants (`position`, `global_position`, `gps`, `location`).

## Environment variables

Required:
- `DRONE_ID`
- `API_URL`
- `API_KEY`

Optional:
- `SEND_HZ` (default: `3`)
- `DE_COMM_HOST` (default: `127.0.0.1`)
- `DE_COMM_PORT` (default: `60000`)
- `DE_RECEIVE_PORT` (default: `60001`)
- `DE_MODULE_NAME` (default: `WX_TELEMETRY`)
- `DE_SUBSCRIPTIONS` (default: `telemetry`)
- `HTTP_TIMEOUT_SECONDS` (default: `3`)
- `OFFLINE_BACKOFF_SECONDS` (default: `1`)
- `LOG_LEVEL` (default: `INFO`)
- `SIMULATE` (default: `false`)

## Tests

```bash
python -m pytest
```

Smoke test command (runs two simulated drones and verifies `GET /api/v1/telemetry/latest` has both):

```bash
python -m pytest tests/test_smoke_simulation.py
```
