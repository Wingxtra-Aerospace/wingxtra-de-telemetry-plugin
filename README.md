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
export DE_COMM_HOST=127.0.0.1
export DE_COMM_PORT=60000
export DE_LISTEN_HOST=0.0.0.0
export DE_LISTEN_PORT=61233
python main.py
```

Notes:
- DataBus library code is vendored under `wingxtra_plugin/databus_lib/` so the plugin is self-contained.
- The plugin registers as module class `MODULE_CLASS_GENERIC` with module name `WX_TELEMETRY_SENDER` by default.
- The plugin connects to communicator port `60000` and listens on its own unique local port (`DE_LISTEN_PORT`, default `61233`).
- API authentication uses `X-API-Key: <API_KEY>`.
- Mapper normalizes common position key variants and only emits `position` once valid latitude/longitude are available (avoids fake 0,0 coordinates).

## Environment variables

Required:
- `DRONE_ID`
- `API_URL`
- `API_KEY`

Optional:
- `SEND_HZ` (default: `3`)
- `DE_COMM_HOST` (default: `127.0.0.1`)
- `DE_COMM_PORT` (default: `60000`)
- `DE_LISTEN_HOST` (default: `0.0.0.0`)
- `DE_LISTEN_PORT` (default: `61233`)
- `DE_MODULE_NAME` (default: `WX_TELEMETRY_SENDER`)
- `DE_SUBSCRIPTIONS` (default: `1002,1003,1036`)
- `HTTP_TIMEOUT_SECONDS` (default: `3`)
- `OFFLINE_BACKOFF_SECONDS` (default: `1`)
- `LOG_LEVEL` (default: `INFO`)
- `SIMULATE` (default: `false`)

## Tests

```bash
python -m pytest
```
