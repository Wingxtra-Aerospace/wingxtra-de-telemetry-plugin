# Wingxtra DroneEngage Telemetry Plugin

Drone-side Python service that reads telemetry (DroneEngage DataBus or simulation mode), maps it into the Wingxtra telemetry schema, and posts updates to the fleet API.

## Build

```bash
python -m pip install --upgrade build
python -m build
```

## Run

```bash
export DRONE_ID=WX-DRN-001
export API_URL=https://yourdomain.com/api/v1/telemetry
export API_KEY=secret
export SIMULATE=true
python main.py
```

## Environment variables

Required:
- `DRONE_ID`
- `API_URL`
- `API_KEY`

Optional:
- `SEND_HZ` (default: `3`)
- `DE_COMM_HOST` (default: `127.0.0.1`)
- `DE_COMM_PORT` (default: `60000`)
- `HTTP_TIMEOUT_SECONDS` (default: `3`)
- `OFFLINE_BACKOFF_SECONDS` (default: `1`)
- `LOG_LEVEL` (default: `INFO`)
- `SIMULATE` (default: `false`)

## Tests

```bash
python -m pytest
```
