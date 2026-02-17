from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from urllib import request


def test_simulate_two_drones_populates_latest_endpoint(tmp_path) -> None:
    latest: dict[str, dict] = {}

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):  # noqa: N802
            if self.path != "/api/v1/telemetry":
                self.send_response(404)
                self.end_headers()
                return
            body = self.rfile.read(int(self.headers.get("Content-Length", "0"))).decode("utf-8")
            payload = json.loads(body)
            latest[payload["drone_id"]] = payload
            self.send_response(200)
            self.end_headers()

        def do_GET(self):  # noqa: N802
            if self.path != "/api/v1/telemetry/latest":
                self.send_response(404)
                self.end_headers()
                return
            encoded = json.dumps(latest).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)

        def log_message(self, *_args):
            return

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()

    base_url = f"http://127.0.0.1:{server.server_address[1]}/api/v1/telemetry"
    common_env = {
        **os.environ,
        "API_URL": base_url,
        "API_KEY": "secret",
        "SIMULATE": "true",
        "SEND_HZ": "3",
        "PYTHONUNBUFFERED": "1",
    }

    p1 = subprocess.Popen([sys.executable, "main.py"], env={**common_env, "DRONE_ID": "WX-DRN-001"})
    p2 = subprocess.Popen([sys.executable, "main.py"], env={**common_env, "DRONE_ID": "WX-DRN-002"})

    try:
        deadline = time.time() + 8
        while time.time() < deadline:
            with request.urlopen(
                f"http://127.0.0.1:{server.server_address[1]}/api/v1/telemetry/latest", timeout=1
            ) as resp:
                observed = json.loads(resp.read().decode("utf-8"))
            if "WX-DRN-001" in observed and "WX-DRN-002" in observed:
                break
            time.sleep(0.2)
        else:
            raise AssertionError(f"did not observe both drones in latest endpoint: {observed}")
    finally:
        for proc in (p1, p2):
            proc.send_signal(signal.SIGTERM)
            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                proc.kill()
        server.shutdown()
        server.server_close()
