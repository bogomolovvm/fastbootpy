from abc import ABC, abstractmethod


class AbstractTransport(ABC):
    """Strategy for transport layer"""

    @abstractmethod
    def send(self, data: bytes) -> None:
        """send byte data."""
        pass

    @abstractmethod
    def receive(self, size: int) -> bytes:
        """recive byte data"""
        pass

    @abstractmethod
    def close(self) -> None:
        """close connection"""
        pass
