from unittest.mock import MagicMock

import pytest

from fastbootpy.transport.usb_transport import UsbTransport


class TestTransport:
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