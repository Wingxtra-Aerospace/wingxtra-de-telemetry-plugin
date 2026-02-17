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

## Run (DroneEngage DataBus mode, sniffing)

```bash
export DRONE_ID=WX-DRN-001
export API_URL=https://yourdomain.com/api/v1/telemetry
export API_KEY=secret
export SIMULATE=false
export SNIFF_MODE=true
export SNIFF_IFACE=lo
export DE_COMM_PORT=60000
python main.py
```

Notes:
- DataBus library code is vendored under `wingxtra_plugin/databus_lib/`.
- In sniff mode, plugin does **not** bind communicator port 60000; it sniffs UDP traffic for that destination port.
- DataBus processing path accepts only `mt == 9102` with non-null `ms`; `la`/`ln` are converted by `/1e7`.
- API authentication uses `X-API-Key: <API_KEY>`.

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
- `SNIFF_MODE` (default: `true`)
- `SNIFF_IFACE` (default: `lo`)
- `HTTP_TIMEOUT_SECONDS` (default: `3`)
- `OFFLINE_BACKOFF_SECONDS` (default: `1`)
- `LOG_LEVEL` (default: `INFO`)
- `SIMULATE` (default: `false`)

## Deployment

See `deploy/README_DEPLOY.md` and `install.sh` for one-command install + systemd setup.

## Tests

```bash
python -m pytest
```
