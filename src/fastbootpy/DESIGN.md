### Project structure
```
fastbootpy/
├── src/
│   └── fastbootpy/
│       ├── __init__.py           
│       ├── device.py             # Application Layer/Factory
│       ├── manager.py            # Application Layer/Repository
│       ├── protocol.py           # Domain Layer
│       ├── transport/            # Infrastructure Layer
│       │   ├── __init__.py
│       │   ├── base.py           # AbstractTransport
│       │   ├── usb.py            # UsbTransport
│       │   └── tcp.py            # TcpTransport
│       ├── exceptions.py         # Exceptions
│       └── py.typed              # Type hints marker
```

### Architecture
```
┌────────────────────────────────────────┐
│   Application Layer                    │  
│   (Public API)                         │
├────────────────────────────────────────┤
│   Domain Layer                         │
│   (Protocol logic)                     │
├────────────────────────────────────────┤
│   Infrastructure Layer                 │ 
│   (Transport layer)                    │
└────────────────────────────────────────┘
```
