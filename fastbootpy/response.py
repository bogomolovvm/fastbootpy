from dataclasses import dataclass

@dataclass
class Response:
    status: bytes
    result: bytes