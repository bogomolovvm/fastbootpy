import usb.core
from .base import AbstractTransport, Response
from .. import exceptions


class UsbTransport(AbstractTransport):
    def __init__(self, serial: str,
                 read_timeout=AbstractTransport.BASE_READ_TIMEOUT,
                 write_timeout=AbstractTransport.BASE_WRITE_TIMEOUT):
        self.usb_device = None
        self.read_endpoint = None
        self.write_endpoint = None
        self.serial = serial
        self.read_timeout = read_timeout
        self.write_timeout = write_timeout
        self._setup_connection()

    def send(self, data: bytes) -> None:
        try:
            self.write_endpoint.write(data, self.write_timeout)
        except usb.USBError as e:
            raise exceptions.USBError(serial=self.usb_device.serial_number, exception=e)

    def recv(self) -> Response:
        device_response = b""
        buffer = b""
        while True:
            try:
                buffer = self.read_endpoint.read(
                    4096,
                    self.read_timeout,
                )
            except usb.USBError:
                break

            if buffer is None or buffer == b"":
                break
            else:
                device_response += buffer

        return Response(status=device_response[:4], result=device_response[4:])

    def _make_pyusb_device(self) -> usb.core.Device | None:
        for pyusb_device in usb.core.find(find_all=True):
            for cfg in pyusb_device:
                dev = usb.util.find_descriptor(
                    cfg,
                    bInterfaceClass=AbstractTransport.FASTBOOT_CLASS,
                    bInterfaceSubClass=AbstractTransport.FASTBOOT_SUBCLASS,
                    bInterfaceProtocol=AbstractTransport.FASTBOOT_PROTOCOL,
                )
                if dev is None:
                    continue
                else:
                    try:
                        if pyusb_device.serial_number == self.serial:
                            return pyusb_device
                    except ValueError:
                        pass
        return None

    def _get_r_w_endpoints(self, usb_device: usb.core.Device) -> tuple[usb.core.Endpoint | None, usb.core.Endpoint | None]:
        write_endpoint, read_endpoint = None, None
        for cfg in usb_device:
            for iface in cfg:
                for endpoint in iface:
                    if usb.core.util.endpoint_direction(endpoint.bEndpointAddress) == usb.core.util.ENDPOINT_IN:
                        read_endpoint = endpoint
                    else:
                        write_endpoint = endpoint
        return read_endpoint, write_endpoint

    def _setup_connection(self):
        device = self._make_pyusb_device()
        if device is None:
            raise exceptions.DeviceNotFoundError(serial=self.serial)
        self.usb_device = device
        self.read_endpoint, self.write_endpoint =  self._get_r_w_endpoints(device)

    def _flush_buffer(self) -> None:
        while True:
            try:
                buffer = self.read_endpoint.read(
                    4096,
                    self.read_timeout,
                )
            except usb.USBError:
                break

            if buffer is None or buffer == b"":
                break


