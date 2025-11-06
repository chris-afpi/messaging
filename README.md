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

## Stopping the Services

Press `Ctrl+C` in each terminal to gracefully shutdown the services.

## Customization

You can easily extend this POC by:
- Adding more UI services (copy and modify `ui_service_2.py`)
- Changing send intervals in the service classes
- Modifying the word lists (names, fruits, etc.)
- Adding more complex processing logic in the system service
- Implementing message persistence and replay features using Redis Stream features
