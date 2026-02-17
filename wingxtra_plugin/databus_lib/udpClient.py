from __future__ import annotations

import socket
from typing import Optional


class UdpClient:
    def __init__(self, listen_host: str, listen_port: int, packet_size: int = 8192) -> None:
        self._packet_size = packet_size
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.bind((listen_host, listen_port))
        self._sock.settimeout(1.0)

    def send(self, host: str, port: int, payload: bytes) -> None:
        if len(payload) <= self._packet_size:
            self._sock.sendto(payload, (host, port))
            return

        index = 0
        for chunk_start in range(0, len(payload), self._packet_size):
            chunk = payload[chunk_start : chunk_start + self._packet_size]
            header = f"{index}|".encode("utf-8")
            self._sock.sendto(header + chunk, (host, port))
            index += 1

    def recv(self) -> Optional[bytes]:
        try:
            packet, _addr = self._sock.recvfrom(self._packet_size + 64)
        except socket.timeout:
            return None

        # best-effort chunk strip: "<index>|<data>"
        if b"|" in packet[:16]:
            prefix, remainder = packet.split(b"|", 1)
            if prefix.isdigit():
                return remainder
        return packet

    def close(self) -> None:
        self._sock.close()
