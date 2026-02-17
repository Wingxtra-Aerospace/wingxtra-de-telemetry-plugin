import json
import socket
import time
from typing import Optional, Dict, Any


def _extract_first_json_object(payload: bytes) -> Optional[Dict[str, Any]]:
    """
    DroneEngage databus UDP payload often contains a JSON object at the start,
    sometimes followed by binary data. We extract the first JSON object safely.
    """
    # Find the first '{'
    start = payload.find(b"{")
    if start < 0:
        return None

    # Balance braces to find end of the first JSON object
    depth = 0
    in_str = False
    esc = False

    for i in range(start, len(payload)):
        b = payload[i]
        if in_str:
            if esc:
                esc = False
            elif b == 92:  # backslash \
                esc = True
            elif b == 34:  # quote "
                in_str = False
            continue

        if b == 34:  # quote "
            in_str = True
            continue

        if b == 123:  # {
            depth += 1
        elif b == 125:  # }
            depth -= 1
            if depth == 0:
                blob = payload[start : i + 1]
                try:
                    return json.loads(blob.decode("utf-8", errors="strict"))
                except Exception:
                    return None
    return None


def sniff_de_databus_json(
    udp_port: int,
    iface: str = "lo",
    timeout_s: float = 1.0,
) -> Optional[Dict[str, Any]]:
    """
    Sniff UDP packets on an interface using a raw socket (Linux).
    Requires CAP_NET_RAW (or root).

    We filter for UDP destination port == udp_port and return the first parsed JSON dict.
    """
    # AF_PACKET gives us ethernet frames. Works on Linux.
    # Note: On 'lo' interface, you still get frames.
    s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(0x0003))
    s.bind((iface, 0))
    s.settimeout(timeout_s)

    deadline = time.time() + timeout_s
    while time.time() < deadline:
        try:
            frame, _addr = s.recvfrom(65535)
        except socket.timeout:
            return None
        except Exception:
            return None

        # Minimal IPv4 + UDP parsing
        # Ethernet header is 14 bytes for eth0, but on lo it differs; we search for IPv4 header by protocol marker.
        # Safer: locate IPv4 header by looking for version nibble 4 and IHL >= 5.
        for off in (14, 16, 0):  # common offsets
            if len(frame) < off + 20:
                continue
            vihl = frame[off]
            version = vihl >> 4
            ihl = (vihl & 0x0F) * 4
            if version != 4 or ihl < 20:
                continue
            proto = frame[off + 9]
            if proto != 17:  # UDP
                continue

            total_len = int.from_bytes(frame[off + 2 : off + 4], "big")
            ip_header_end = off + ihl
            if len(frame) < ip_header_end + 8:
                continue

            dst_port = int.from_bytes(frame[ip_header_end + 2 : ip_header_end + 4], "big")
            if dst_port != udp_port:
                continue

            udp_payload_start = ip_header_end + 8
            udp_payload_end = off + total_len
            if udp_payload_end <= udp_payload_start or udp_payload_end > len(frame):
                udp_payload_end = len(frame)

            payload = frame[udp_payload_start:udp_payload_end]
            obj = _extract_first_json_object(payload)
            if obj is not None:
                return obj

    return None
