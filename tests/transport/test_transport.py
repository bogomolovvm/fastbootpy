from unittest.mock import MagicMock

import pytest

from fastbootpy.transport.usb_transport import UsbTransport


class TestUSBTransportSend:
    def test_send_write_to_endpoint(self):
        # Arrange
        mock_write_ep = MagicMock()
        transport = UsbTransport(
            serial="ABC",
            usb_device=MagicMock(),
            read_endpoint=MagicMock(),
            write_endpoint=mock_write_ep,
            write_timeout=100
        )

        # Act
        transport.send(b"getvar:all")

        # Assert
        mock_write_ep.write.assert_called_once_with(b"getvar:all", 100)

class TestUSBTransportRecv:
    def test_recv_w_size_and_timeout_from_endpoint(self):
        # Arrange
        mock_read_ep = MagicMock()
        timeout = 100
        transport = UsbTransport(
            serial="ABC",
            usb_device=MagicMock(),
            read_endpoint=mock_read_ep,
            write_endpoint=MagicMock(),
            read_timeout=timeout
        )
        size = 128

        # Act
        package = transport.receive(size=size)

        # Assert
        mock_read_ep.read.assert_called_once_with(size, timeout)