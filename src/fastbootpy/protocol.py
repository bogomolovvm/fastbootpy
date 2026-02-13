from transport.base import AbstractTransport
from enum import Enum


class AnswerType(Enum):
    OKAY = b"OKAY"
    FAIL = b"FAIL"
    TEXT = b"TEXT"
    INFO = b"INFO"


class FastbootProtocol:
    def __init__(self, transport: AbstractTransport):
        self.transport = transport

    def _send(self, data: bytes) -> None:
        self.transport.send(data)

    def _receive(self):
        packet = self.transport.receive()
        return self._handler(packet[:4], packet[4:])

    @staticmethod
    def _handler(header: bytes, payload: bytes) -> None | bytes:
        if header is AnswerType.INFO:
            print(f"(bootloader) + {payload.decode()}")
        elif header is AnswerType.TEXT:
            print(f"{payload.decode()}", end="")
        elif header is AnswerType.OKAY:
            return payload
        elif header is AnswerType.FAIL:
            print(f"FAIL{payload.decode(errors='ignore')}")
            return None
        else:
            raise ValueError  # TODO: custom exc

    def getvar(self, variable: str) -> None | bytes:
        self.transport.send(f"getvar:{variable}".encode())
        return self._receive()
