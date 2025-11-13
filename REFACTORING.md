# Refactoring Documentation

## Overview

The codebase has been refactored to separate **reusable library code** from **demo/application code**. This makes the messaging client reusable for any application.

## New Structure

### Core Library

**`ui_service.py`** - Reusable UIService class
- ✅ Connection management
- ✅ Session registration
- ✅ Send single messages
- ✅ Receive responses with callbacks
- ✅ No hardcoded demo logic
- ✅ Can be imported and used by any application

### Demo Scripts

**`demo_names.py`** - Clean example using UIService
- Sends random names every 11 seconds
- Shows how to use the library for periodic sending

**`demo_fruits.py`** - Clean example using UIService
- Sends random fruits every 13 seconds
- Same pattern as demo_names.py

**`demo_custom_usage.py`** - Advanced example
- Shows how to use custom response callbacks
- Demonstrates library usage for custom applications
- Example of how you'd integrate into a web app, GUI, etc.

### Backward Compatible Scripts

**`ui_service_1.py`** - Now uses UIService internally
- Maintains same behavior as before
- Exists for backward compatibility

**`ui_service_2.py`** - Now uses UIService internally
- Maintains same behavior as before
- Keeps UIService2 class for demo_multi_device.py compatibility

## Usage Examples

### Basic Usage (Library Pattern)

```python
from ui_service import UIService

# Create service
service = UIService(
    service_id="my-app",
    user_id="john"
)

# Connect and register
await service.connect()
await service.register_session()

# Send a message
await service.send_message("hello")

# Start receiving (runs in background)
await service.start_receiving()
```

### With Custom Callback

```python
def my_response_handler(response_data):
    word = response_data['word']
    length = response_data['length']
    print(f"Got response: {word} = {length}")

service = UIService(
    service_id="my-app",
    user_id="john",
    on_response=my_response_handler  # Custom callback!
)
```

### In a Web Application

```python
class MyWebApp:
    def __init__(self):
        self.service = UIService(
            service_id="web-ui",
            user_id=self.get_current_user_id(),
            on_response=self.handle_response
        )
        self.results = []

    def handle_response(self, response_data):
        # Store result for display in web UI
        self.results.append(response_data)
        # Could also emit websocket event, update database, etc.

    async def process_user_input(self, word):
        await self.service.send_message(word)
```

## Running the Demos

### Original Demos (Backward Compatible)
```bash
python system_service.py     # Terminal 1
python ui_service_1.py       # Terminal 2 (alice, names)
python ui_service_2.py       # Terminal 3 (bob, fruits)
```

### New Clean Demos
```bash
python system_service.py     # Terminal 1
python demo_names.py         # Terminal 2 (alice, names)
python demo_fruits.py        # Terminal 3 (bob, fruits)
```

### Custom Usage Demo
```bash
python system_service.py     # Terminal 1
python demo_custom_usage.py  # Terminal 2
```

## Benefits of Refactoring

### Before (Monolithic)
```python
class UIService1:
    def __init__(self):
        self.names = [...]  # Demo data baked in

    async def send_messages(self):
        # Hardcoded periodic sending
        while True:
            name = random.choice(self.names)
            await self.send(name)
            await asyncio.sleep(11)  # Hardcoded interval
```

**Problems:**
- Can't reuse for other applications
- Demo logic mixed with core functionality
- Hard to test
- Can't customize behavior

### After (Separation of Concerns)
```python
# Library (ui_service.py)
class UIService:
    async def send_message(self, word: str):
        # Just send the message
        await self.redis_client.xadd(...)

# Application (demo_names.py)
async def send_names_periodically(service, interval=11):
    while True:
        name = random.choice(NAMES)
        await service.send_message(name)
        await asyncio.sleep(interval)
```

**Benefits:**
- ✅ Core class is reusable
- ✅ Demo logic separated
- ✅ Easy to create custom applications
- ✅ Easy to test
- ✅ Flexible intervals, data sources, etc.

## Migration Guide

### Old Code
```python
from ui_service_1 import UIService1
service = UIService1()
await service.run()  # Hardcoded behavior
```

### New Code
```python
from ui_service import UIService

service = UIService(service_id="ui1", user_id="alice")
await service.connect()
await service.register_session()

# Now YOU control what happens
await service.send_message("any text you want")
await service.start_receiving()
```

## Key Takeaway

**Before:** The classes were demos masquerading as libraries.
**After:** Clean library with demos showing how to use it.

This follows the **Single Responsibility Principle** - the UIService class is now responsible ONLY for messaging, not for generating demo data.
