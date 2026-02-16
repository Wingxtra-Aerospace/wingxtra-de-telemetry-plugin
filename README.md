# Wingxtra DroneEngage Telemetry Plugin
**Repository:** wingxtra-de-telemetry-plugin  
**Owner:** Wingxtra Aerospace  
**Role:** Drone-side telemetry sender for Wingxtra Fleet API

---

## 1. What this plugin does (plain language)

This plugin runs on **each drone’s Raspberry Pi** alongside DroneEngage.

It:
- Subscribes to telemetry inside DroneEngage using **DataBus**
- Converts telemetry into a fixed JSON schema
- Sends telemetry to `wingxtra-fleet-api` at **2–5 Hz**
- Starts automatically on boot
- Works without a laptop or GCS connection

This is **not** a UI.  
This is **not** a MAVLink router.  
This is a **background service**.

---

## 2. Integration point (NO GUESSING)

### Official integration target
Use **only**:

Wingxtra-Aerospace/droneengage_databus


This repository already exists in the Wingxtra-Aerospace GitHub org and is the **approved extension layer**.

### Language choice (LOCKED)
- **Python**
- Start from the template in:

droneengage_databus/python/


### Communicator defaults
- `DE_COMM_HOST=127.0.0.1`
- `DE_COMM_PORT=60000` (UDP)
- Must be configurable via environment variables

---

## 3. What this plugin must NOT do

- ❌ Do NOT modify:
  - `droneengage_mavlink`
  - `droneengage_communication`
  - `droneengage_server`
- ❌ Do NOT parse MAVLink directly
- ❌ Do NOT require Mission Planner, QGC, or a laptop
- ❌ Do NOT hardcode API keys

All telemetry access must be via **DataBus subscription**.

---

## 4. Authoritative data flow

Flight Controller
|
| MAVLink
v
DroneEngage Core Modules
|
| DataBus (UDP 60000)
v
wingxtra-de-telemetry-plugin
|
| HTTPS POST (JSON, 2–5 Hz)
v
wingxtra-fleet-api


---

## 5. Telemetry schema (MUST MATCH BACKEND)


{
  "schema_version": 1,
  "drone_id": "WX-DRN-001",
  "ts": "2026-02-16T12:34:56.123Z",

  "position": {
    "lat": 5.6037,
    "lon": -0.1870,
    "alt_m": 120.3
  },

  "attitude": {
    "yaw_deg": 45.0
  },

  "velocity": {
    "groundspeed_mps": 12.4
  },

  "state": {
    "armed": true,
    "mode": "AUTO"
  },

  "battery": {
    "voltage_v": 22.1,
    "remaining_pct": 67
  },

  "link": {
    "rssi_dbm": -62
  }
}
Missing fields are allowed — send what is available.

## 6. Environment variables
Required
DRONE_ID=WX-DRN-001
API_URL=https://yourdomain.com/api/v1/telemetry
API_KEY=secret
Optional
SEND_HZ=3
DE_COMM_HOST=127.0.0.1
DE_COMM_PORT=60000
HTTP_TIMEOUT_SECONDS=3
OFFLINE_BACKOFF_SECONDS=1
LOG_LEVEL=INFO
SIMULATE=false
## 7. Reliability rules (CRITICAL)
Send telemetry at 2–5 Hz only

If POST fails:

do NOT crash

apply exponential backoff

keep only latest telemetry

When internet returns:

resume immediately

Telemetry history is server responsibility, not plugin responsibility

## 8. Simulation mode (MANDATORY)
When:

SIMULATE=true
The plugin:

Generates fake telemetry

Does NOT require DroneEngage running

Allows multi-drone testing by changing DRONE_ID

Example:

SIMULATE=true DRONE_ID=WX-DRN-001 python main.py
SIMULATE=true DRONE_ID=WX-DRN-002 python main.py
## 9. Raspberry Pi deployment (PRODUCTION)
systemd service (REQUIRED)
Create:

/etc/systemd/system/wingxtra-telemetry.service
[Unit]
Description=Wingxtra Drone Telemetry Sender
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory=/opt/wingxtra-de-telemetry-plugin
Environment=DRONE_ID=WX-DRN-001
Environment=API_URL=https://yourdomain.com/api/v1/telemetry
Environment=API_KEY=CHANGE_ME
Environment=SEND_HZ=3
ExecStart=/opt/wingxtra-de-telemetry-plugin/.venv/bin/python main.py
Restart=always
RestartSec=2

[Install]
WantedBy=multi-user.target
Enable:

sudo systemctl daemon-reload
sudo systemctl enable wingxtra-telemetry
sudo systemctl start wingxtra-telemetry
## 10. Expected repo structure
.
├── main.py
├── wingxtra_plugin/
│   ├── databus_client.py
│   ├── telemetry_mapper.py
│   ├── sender.py
│   ├── simulate.py
│   ├── config.py
│   └── __init__.py
├── tests/
└── README.md
#  11. Acceptance tests (MUST PASS)
Local
Run wingxtra-fleet-api

Run plugin twice in SIMULATE mode with different DRONE_IDs

GET /api/v1/telemetry/latest shows both drones

On drone
Boot Raspberry Pi

DroneEngage starts

Plugin starts automatically

Backend shows live updates every second

## 12. Locked roadmap
Phase 2: per-drone API keys

Phase 3: onboard health telemetry (CPU, temp)

Phase 4: command/downlink (separate repo)
