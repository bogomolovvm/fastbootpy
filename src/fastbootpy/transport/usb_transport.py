import usb.core
import usb.util
from .base import AbstractTransport
from .. import exceptions


class UsbTransport(AbstractTransport):
    def __init__(
        self,
        serial: str,
        usb_device: usb.core.Device,
        read_endpoint: usb.core.Endpoint,
        write_endpoint: usb.core.Endpoint,
        read_timeout: int = AbstractTransport.BASE_READ_TIMEOUT,
        write_timeout: int = AbstractTransport.BASE_WRITE_TIMEOUT,
    ):
        self.serial = serial
        self.usb_device = usb_device
        self.read_endpoint = read_endpoint
        self.write_endpoint = write_endpoint
        self.read_timeout = read_timeout
        self.write_timeout = write_timeout

    @classmethod
    def connect(
        cls,
        serial: str,
        read_timeout: int = AbstractTransport.BASE_READ_TIMEOUT,
        write_timeout: int = AbstractTransport.BASE_WRITE_TIMEOUT,
    ):
        device = cls._find_device(serial)
        if device is None:
            raise exceptions.DeviceNotFoundError(serial=serial)

        try:
            device.reset()
            if device.is_kernel_driver_active(0):
                device.detach_kernel_driver(0)
        except usb.core.USBError as e:
            raise exceptions.USBError(serial=serial, exception=e)

        read_ep, write_ep = cls._get_endpoints(device)
        if read_ep is None or write_ep is None:
            raise exceptions.USBError(serial=serial)

        transport = cls(serial, device, read_ep, write_ep, read_timeout, write_timeout)
        transport._flush_buffer()
        return transport

    def send(self, data: bytes) -> None:
        try:
            self.write_endpoint.write(data, self.write_timeout)
        except usb.core.USBError as e:
            raise exceptions.USBError(serial=self.serial, exception=e)

    def receive(self, size: int = 256) -> bytes:
        try:
            return bytes(self.read_endpoint.read(size, self.read_timeout))
        except usb.core.USBError as e:
            raise exceptions.USBError(serial=self.serial, exception=e)

    def close(self) -> None:
        usb.util.dispose_resources(self.usb_device)

    @staticmethod
    def _find_device(serial: str) -> usb.core.Device | None:
        for device in usb.core.find(find_all=True):
            for cfg in device:
                iface = usb.util.find_descriptor(
                    cfg,
                    bInterfaceClass=AbstractTransport.FASTBOOT_CLASS,
                    bInterfaceSubClass=AbstractTransport.FASTBOOT_SUBCLASS,
                    bInterfaceProtocol=AbstractTransport.FASTBOOT_PROTOCOL,
                )
                if iface is not None:
                    try:
                        if device.serial_number == serial:
                            return device
                    except ValueError:
                        pass
        return None

    @staticmethod
    def _get_endpoints(device: usb.core.Device) -> tuple:
        read_ep, write_ep = None, None
        for cfg in device:
            for iface in cfg:
                for ep in iface:
                    if usb.util.endpoint_direction(ep.bEndpointAddress) == usb.util.ENDPOINT_IN:
                        read_ep = ep
                    else:
                        write_ep = ep
        return read_ep, write_ep

    def _flush_buffer(self) -> None:
        while True:
            try:
                data = self.read_endpoint.read(4096, 100)
            except usb.core.USBError:
                break
            if data is None or len(data) == 0:
                break
