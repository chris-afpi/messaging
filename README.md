# Decoupled UI Services with Redis Streams

This is a proof of concept demonstrating multiple UI services decoupled from a Python async system using Redis Streams for bidirectional communication.

## Architecture

The system consists of:

1. **System Service** (`word_length_service.py`) - Main processing service that:
   - Listens for messages from UI services via Redis Streams
   - Calculates the length of received words
   - Sends responses back to the originating UI service

2. **Demo: Names** (`demo_names.py`) - Example UI service that sends random name words every 11 seconds

3. **Demo: Fruits** (`demo_fruits.py`) - Example UI service that sends random fruit words every 13 seconds

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
python word_length_service.py
```

### Terminal 2: Start Demo Names (alice@ui1)
```bash
python demo_names.py
```

### Terminal 3: Start Demo Fruits (bob@ui2)
```bash
python demo_fruits.py
```

## Expected Output

### System Service (word_length_service.py)
```
[23:29:39] [WordLengthService] Created consumer group 'system-processors' on stream 'ui-to-system'
[23:29:39] [WordLengthService] System service listening on stream 'ui-to-system'...
[23:29:48] [WordLengthService] Registered alice on ui1
[23:29:48] [WordLengthService] Received from alice@ui1: {..., 'word': 'George'}
[23:29:48] [WordLengthService] Sent to ui1 for user alice
```

### Demo Names (demo_names.py - alice@ui1)
```
[23:29:48] [UIService] Created consumer group 'ui1-workers' on stream 'system-to-ui1'
[23:29:48] [UIService] [ui1] Ready to communicate (consumer: ui1-worker-1)
Starting to send names every 11 seconds...
[23:29:48] [UIService] [ui1] Sent: {'word': 'George'}
[23:29:48] [ui1] Response: 'George' has length 6
```

### Demo Fruits (demo_fruits.py - bob@ui2)
```
[23:18:07] [UIService] Created consumer group 'ui2-workers' on stream 'system-to-ui2'
[23:18:07] [UIService] [ui2] Ready to communicate (consumer: ui2-worker-1)
Starting to send fruits every 13 seconds...
[23:18:07] [UIService] [ui2] Sent: {'word': 'lemon'}
[23:18:07] [ui2] Response: 'lemon' has length 5
```

## Key Features

- **Fully Asynchronous**: All services use Python's asyncio for non-blocking I/O
- **Decoupled Architecture**: UI services are completely independent from the system service
- **Bidirectional Communication**: Messages flow both ways through Redis Streams
- **Consumer Groups**: Both UI and System services use consumer groups for reliable processing
- **Horizontal Scaling**: Deploy multiple workers for any service with automatic load balancing (see [HORIZONTAL_SCALING.md](HORIZONTAL_SCALING.md))
- **Concurrent Operations**: Each UI service sends and receives messages concurrently
- **Configurable Logging**: Easy switch between print statements and logging.Logger (see [LOGGING_GUIDE.md](LOGGING_GUIDE.md))
- **Multi-device Sync**: Same user can be connected on multiple services with synchronized views
- **Generic Base Classes**: Reusable StreamService, UIService, and SystemService classes for building custom applications

## Stopping the Services

Press `Ctrl+C` in each terminal to gracefully shutdown the services.

## Documentation

- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Common issues and solutions
- **[HORIZONTAL_SCALING.md](HORIZONTAL_SCALING.md)** - How to horizontally scale services with load balancing
- **[LOGGING_GUIDE.md](LOGGING_GUIDE.md)** - How to use the configurable logging system
- **[DEMO_GUIDE.md](DEMO_GUIDE.md)** - Complete guide to running all demos
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Detailed architecture and file organization

## Horizontal Scaling

UIService now supports horizontal scaling through consumer groups. Deploy multiple workers for load balancing:

```python
# Single worker (default)
service = UIService("ui1", "alice")

# Multiple workers for horizontal scaling
worker1 = UIService("ui1", "alice", consumer_name="worker-1")
worker2 = UIService("ui1", "alice", consumer_name="worker-2")
worker3 = UIService("ui1", "alice", consumer_name="worker-3")
# Messages are automatically load-balanced across workers
```

Run `test_horizontal_scaling.py` to see load balancing in action. See [HORIZONTAL_SCALING.md](HORIZONTAL_SCALING.md) for full details.

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
- Deploying multiple workers per service for horizontal scaling and load balancing
- Adding more UI services with different behaviors
- Implementing multi-device sync for users across multiple services
- Switching to proper logging for production deployments
- Adding message persistence and replay features using Redis Stream features
