from __future__ import annotations

import json
import socket
import time
from typing import Any


def sniff_de_databus_json(port: int, iface: str = "lo", timeout_s: float = 1.0) -> dict[str, Any] | None:
    """Sniff one UDP JSON payload destined for `port` on `iface`.

    Requires Linux raw socket privileges (root / CAP_NET_RAW).
    """
    try:
        sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(0x0003))
    except OSError:
        return None

    try:
        sock.bind((iface, 0))
        sock.settimeout(0.2)
        deadline = time.time() + timeout_s

        while time.time() < deadline:
            try:
                packet = sock.recv(65535)
            except socket.timeout:
                continue

            payload = _extract_udp_payload_for_dst_port(packet, port)
            if payload is None:
                continue

            try:
                decoded = json.loads(payload.decode("utf-8", errors="ignore"))
            except json.JSONDecodeError:
                continue
            if isinstance(decoded, dict):
                return decoded
        return None
    finally:
        sock.close()


def _extract_udp_payload_for_dst_port(packet: bytes, dst_port: int) -> bytes | None:
    if len(packet) < 42:
        return None
    eth_proto = int.from_bytes(packet[12:14], "big")
    if eth_proto != 0x0800:  # IPv4 only
        return None

    ip_start = 14
    if len(packet) < ip_start + 20:
        return None
    ihl = (packet[ip_start] & 0x0F) * 4
    protocol = packet[ip_start + 9]
    if protocol != 17:  # UDP
        return None

    udp_start = ip_start + ihl
    if len(packet) < udp_start + 8:
        return None

    dst = int.from_bytes(packet[udp_start + 2 : udp_start + 4], "big")
    if dst != dst_port:
        return None

    udp_len = int.from_bytes(packet[udp_start + 4 : udp_start + 6], "big")
    payload_start = udp_start + 8
    payload_end = payload_start + max(0, udp_len - 8)
    if payload_end > len(packet):
        payload_end = len(packet)
    return packet[payload_start:payload_end]
