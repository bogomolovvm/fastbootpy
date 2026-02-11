# transport/base.py - Strategy Interface
from dataclasses import dataclass
from abc import ABC, abstractmethod


class AbstractTransport(ABC):
    """Transport strategy"""
    BASE_READ_TIMEOUT = 500
    BASE_WRITE_TIMEOUT = 500

    FASTBOOT_CLASS = 0xFF
    FASTBOOT_SUBCLASS = 0x42
    FASTBOOT_PROTOCOL = 0x03

    @abstractmethod
    def send(self, data: bytes) -> None:
        pass

    @abstractmethod
    def receive(self, size: int) -> bytes:
        pass

    @abstractmethod
    def close(self) -> None:
        pass


@dataclass
class Response:
    status: bytes
    result: bytes
