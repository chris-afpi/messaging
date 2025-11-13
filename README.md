# Decoupled UI Services with Redis Streams

This is a proof of concept demonstrating multiple UI services decoupled from a Python async system using Redis Streams for bidirectional communication.

## Architecture

The system consists of:

1. **System Service** (`system_service.py`) - Main processing service that:
   - Listens for messages from UI services via Redis Streams
   - Calculates the length of received words
   - Sends responses back to the originating UI service

2. **UI Service 1** (`ui_service_1.py`) - Sends random name words every 11 seconds

3. **UI Service 2** (`ui_service_2.py`) - Sends random fruit words every 13 seconds

### Communication Flow

```
UI Services ──[word]──> ui-to-system stream ──> System Service
                                                       │
UI Services <──[length]── system-to-ui{1,2} <─────────┘
```

## Prerequisites

- Python 3.8+
- Redis server running locally or accessible via network

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure Redis is running:
```bash
# If using Docker
docker run -d -p 6379:6379 redis:latest

# Or install Redis locally and start it
redis-server
```

## Running the Services

You'll need 3 separate terminal windows/tabs to run all services:

### Terminal 1: Start the System Service
```bash
python system_service.py
```

### Terminal 2: Start UI Service 1
```bash
python ui_service_1.py
```

### Terminal 3: Start UI Service 2
```bash
python ui_service_2.py
```

## Expected Output

### System Service
```
Created consumer group 'system-processors' on stream 'ui-to-system'
System service listening on stream 'ui-to-system'...
[17:30:11] Received from ui1: 'Alice'
[17:30:11] Sent to ui1: length=5
[17:30:13] Received from ui2: 'banana'
[17:30:13] Sent to ui2: length=6
```

### UI Service 1
```
[UI1] Connected to Redis
[UI1] Starting to send names every 11 seconds...
[UI1] Listening for responses on stream 'system-to-ui1'...
[17:30:11] [UI1] Sent: 'Alice'
[17:30:11] [UI1] Response: 'Alice' has length 5
[17:30:22] [UI1] Sent: 'Bob'
[17:30:22] [UI1] Response: 'Bob' has length 3
```

### UI Service 2
```
[UI2] Connected to Redis
[UI2] Starting to send fruits every 13 seconds...
[UI2] Listening for responses on stream 'system-to-ui2'...
[17:30:13] [UI2] Sent: 'banana'
[17:30:13] [UI2] Response: 'banana' has length 6
[17:30:26] [UI2] Sent: 'cherry'
[17:30:26] [UI2] Response: 'cherry' has length 6
```

## Key Features

- **Fully Asynchronous**: All services use Python's asyncio for non-blocking I/O
- **Decoupled Architecture**: UI services are completely independent from the system service
- **Bidirectional Communication**: Messages flow both ways through Redis Streams
- **Consumer Groups**: System service uses consumer groups for reliable message processing
- **Concurrent Operations**: Each UI service sends and receives messages concurrently
- **Configurable Logging**: Easy switch between print statements and logging.Logger (see [LOGGING_GUIDE.md](LOGGING_GUIDE.md))
- **Multi-device Sync**: Same user can be connected on multiple services with synchronized views
- **Generic Base Classes**: Reusable StreamService, UIService, and SystemService classes for building custom applications

## Stopping the Services

Press `Ctrl+C` in each terminal to gracefully shutdown the services.

## Documentation

- **[LOGGING_GUIDE.md](LOGGING_GUIDE.md)** - How to use the configurable logging system
- **[DEMO_GUIDE.md](DEMO_GUIDE.md)** - Complete guide to running all demos
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Detailed architecture and file organization
- **[GENERIC_REFACTORING.md](GENERIC_REFACTORING.md)** - How the library was made generic and reusable

## Logging

The services support both simple print statements (default) and proper logging infrastructure:

```python
# Default mode - uses print()
service = UIService("ui1", "alice")

# Logging mode - uses logging.Logger
import logging
logging.basicConfig(level=logging.INFO)
service = UIService("ui1", "alice", use_logging=True)
```

Run `demo_logging.py` to see all logging modes in action. See [LOGGING_GUIDE.md](LOGGING_GUIDE.md) for full details.

## Customization

You can easily extend this POC by:
- Creating custom services that extend `SystemService` with your own business logic
- Building custom UI clients using the `UIService` class as a library
- Adding more UI services with different behaviors
- Implementing multi-device sync for users across multiple services
- Switching to proper logging for production deployments
- Adding message persistence and replay features using Redis Stream features
