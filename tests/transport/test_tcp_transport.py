from unittest.mock import MagicMock
from fastbootpy.transport.tcp_transport import TCPTransport


class TestTCPTransportSend:
    def test_recv_from_socket(self):
        # Arrange
        mock_socket = MagicMock()
        transport = TCPTransport(
            serial="emulator:4445",
            read_timeout=100,
            write_timeout=100,
            client_socket=mock_socket
        )
        mock_socket.recv.side_effect = [len("hello").to_bytes(8, byteorder="big"), b"he", b"l", b"l", b"o"]
        # Act
        packet = transport.receive(4096)

        # Assert
        assert packet == b"hello"