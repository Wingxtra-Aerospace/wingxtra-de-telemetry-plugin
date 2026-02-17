#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/opt/wingxtra-de-telemetry-plugin"
ENV_FILE="/etc/wingxtra-telemetry.env"
SERVICE_FILE="/etc/systemd/system/wingxtra-telemetry.service"

echo "[1/6] Installing system packages..."
sudo apt-get update -y
sudo apt-get install -y python3-full python3-venv

echo "[2/6] Installing app to ${APP_DIR}..."
sudo rm -rf "${APP_DIR}"
sudo mkdir -p "${APP_DIR}"
sudo cp -a . "${APP_DIR}"
sudo chown -R root:root "${APP_DIR}"

echo "[3/6] Creating venv and installing deps..."
sudo python3 -m venv "${APP_DIR}/.venv"
sudo "${APP_DIR}/.venv/bin/python" -m pip install -U pip
sudo "${APP_DIR}/.venv/bin/python" -m pip install -e "${APP_DIR}"

echo "[4/6] Installing env file..."
if [ ! -f "${ENV_FILE}" ]; then
  sudo cp "${APP_DIR}/deploy/wingxtra-telemetry.env.example" "${ENV_FILE}"
  sudo chmod 600 "${ENV_FILE}"
  echo "Created ${ENV_FILE}. Edit it now to match your API_URL/API_KEY/DRONE_ID."
else
  echo "${ENV_FILE} already exists; leaving it unchanged."
fi

echo "[5/6] Installing systemd service..."
sudo cp "${APP_DIR}/deploy/wingxtra-telemetry.service" "${SERVICE_FILE}"
sudo systemctl daemon-reload

echo "[6/6] Enabling + starting service..."
sudo systemctl enable wingxtra-telemetry.service
sudo systemctl restart wingxtra-telemetry.service

echo "DONE."
echo "Check: sudo systemctl status wingxtra-telemetry.service --no-pager"
echo "Logs : sudo journalctl -u wingxtra-telemetry.service -f"
