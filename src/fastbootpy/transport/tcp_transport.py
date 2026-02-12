import socket

from fastbootpy.exceptions import TCPDeviceNotFound
from fastbootpy.transport.base import AbstractTransport


class TCPTransport(AbstractTransport):
    def __init__(self, serial, read_timeout, write_timeout, client_socket):
        self.serial = serial
        self.read_timeout = read_timeout
        self.write_timeout = write_timeout
        self.client_socket = client_socket

    def send(self, data: bytes) -> None:
        self.client_socket.sendall(len(data).to_bytes(8, byteorder="big") + data)

    def receive(self, size: int = 256) -> bytes:
        header = TCPTransport._recv_all(self.client_socket, 8)
        packet_len = int.from_bytes(header, "big")
        return TCPTransport._recv_all(self.client_socket, packet_len)

    def close(self) -> None:
        self.client_socket.close()

    @classmethod
    def _recv_all(cls, sock, n: int) -> bytes:
        buf = bytearray()
        while len(buf) < n:
            chunk = sock.recv(n - len(buf))
            if not chunk:
                raise ConnectionError("peer closed")
            buf += chunk
        return bytes(buf)

    @classmethod
    def connect(cls, serial: str, read_timeout: int, write_timeout: int):
        if ":" in serial:
            host, port_str = serial.rsplit(":", 1)
            port = int(port_str)
        else:
            host = serial
            port = AbstractTransport.FASTBOOT_DEFAULT_TCP_PORT

        client = socket.socket()
        client.settimeout(read_timeout)
        client.connect((host, port))

        client.sendall(AbstractTransport.FASTBOOT_TCP_HANDSHAKE)
        data = cls._recv_all(client, 4)
        decoded = data.decode()

        if len(decoded) != 4:
            raise ConnectionError("Invalid handshake response length") # TODO: raise custom exc

        if decoded[:2] == "FB" and int(decoded[2:]) == AbstractTransport.PROTO_TCP_VERSION:
            return cls(serial, read_timeout, write_timeout, client)
        else:
            client.close()
            raise TCPDeviceNotFound(serial)     # TODO: raise NotFastBootDevice

