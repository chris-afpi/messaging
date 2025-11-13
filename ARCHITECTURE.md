# Architecture Documentation

## Clean Separation: Libraries vs Demos

This codebase follows a strict separation between **reusable library code** and **demo/application code**.

---

## 📚 Library Files (Reusable, No Demo Content)

### `ui_service.py` - Core Library
**Pure messaging client class with ZERO demo logic**

What it does:
- ✅ Connect to Redis
- ✅ Register user sessions
- ✅ Send individual messages
- ✅ Receive responses with optional callbacks
- ✅ Clean connection lifecycle management

What it does NOT do:
- ❌ No hardcoded word lists (names, fruits, etc.)
- ❌ No periodic sending loops
- ❌ No demo-specific logic
- ❌ No assumptions about what you're sending

**Usage:**
```python
from ui_service import UIService

service = UIService(
    service_id="my-app",
    user_id="user123"
)

await service.connect()
await service.register_session()
await service.send_message("any text")
await service.start_receiving()
```

### `system_service.py` - Central Processing Service Base Class
The backend service that:
- Listens for messages from UI services
- Processes them (calculates word length)
- Broadcasts responses to all user's active services
- Tracks user sessions bidirectionally

---

## 🎮 Demo Files (Application Logic)

### `demo_names.py`
**Demo: Sending random names periodically**

Contains:
- ✅ Names list (demo data)
- ✅ Periodic sending logic (11 seconds)
- ✅ Main loop
- ✅ Uses UIService library

**Run:** `python demo_names.py`

### `demo_fruits.py`
**Demo: Sending random fruits periodically**

Contains:
- ✅ Fruits list (demo data)
- ✅ Periodic sending logic (13 seconds)
- ✅ Main loop
- ✅ Uses UIService library

**Run:** `python demo_fruits.py`

### `demo_multi_device.py`
**Demo: Same user on two services (multi-device sync)**

Contains:
- ✅ Fruits list (demo data)
- ✅ Periodic sending logic
- ✅ Uses user_id='alice' to demo multi-device
- ✅ Shows synchronization across services

**Run:** `python demo_multi_device.py`
(alongside `demo_names.py` to see sync)

### `demo_custom_usage.py`
**Demo: Custom callback and integration pattern**

Shows how to:
- ✅ Use custom response callbacks
- ✅ Integrate into larger applications
- ✅ Send on-demand (not periodic)
- ✅ Track responses programmatically

**Run:** `python demo_custom_usage.py`

---

## 📁 File Organization

```
messaging/
├── Library (reusable, no demo content)
│   ├── stream_service.py      ← Base class for all services
│   ├── ui_service.py          ← UI client library
│   ├── system_service.py      ← System service base class
│   └── word_length_service.py ← Demo implementation of system service
│
├── Demos (application code)
│   ├── demo_names.py          ← Names sender (alice@ui1)
│   ├── demo_fruits.py         ← Fruits sender (bob@ui2)
│   ├── demo_multi_device.py   ← Multi-device sync (alice@ui2)
│   ├── demo_custom_usage.py   ← Custom integration example
│   ├── demo_logging.py        ← Logging feature demo
│   └── test_horizontal_scaling.py ← Horizontal scaling demo
│
├── Utilities
│   └── check_redis.py         ← Redis inspection tool
│
└── Documentation
    ├── README.md              ← Project overview
    ├── ARCHITECTURE.md        ← This file
    ├── DEMO_GUIDE.md          ← How to run demos
    ├── REFACTORING.md         ← Refactoring rationale
    └── improvements.md        ← Known limitations
```

---

## ✅ Design Principles

### 1. Single Responsibility
Each file has ONE clear purpose:
- Libraries: Provide reusable functionality
- Demos: Show how to use the libraries

### 2. Separation of Concerns
Demo data and logic are NEVER mixed with library code:
```python
# ❌ BAD (old way)
class UIService:
    def __init__(self):
        self.names = ["Alice", "Bob"]  # Demo data in library!

# ✅ GOOD (new way)
# Library:
class UIService:
    async def send_message(self, text): ...

# Demo:
NAMES = ["Alice", "Bob"]  # Demo data in demo file
```

### 3. Easy Testing
Libraries without demo logic are easier to test:
```python
# Test the library
service = UIService("test-id", "test-user")
await service.send_message("test")
# No need to mock random.choice() or sleep()!
```

### 4. Flexible Reuse
Library can be used for ANY application:
- Web apps
- Mobile apps
- CLI tools
- Batch processors
- Test scripts

---

## 🔄 Migration Examples

### Old Way (Monolithic Demo)
Early demos had hardcoded logic mixed with library code.

Problems:
- Can't change interval
- Can't change word list
- Can't send on-demand
- Can't reuse for other apps
- Demo logic embedded in library files

### New Way (Flexible Library)
```python
from ui_service import UIService

service = UIService(service_id="ui1", user_id="alice")
await service.connect()
await service.register_session()

# Now YOU control everything:
await service.send_message("custom text")
await service.send_message("any interval you want")
```

---

## 🎯 Key Takeaway

**Library files have ZERO demo content.**
**Demo files have ALL the demo content.**

This follows the principle: "Libraries provide capabilities, applications define behavior."
