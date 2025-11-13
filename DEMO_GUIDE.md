# Demo Guide: Multi-Device Sync

This guide shows how to run both the original demo and the new multi-device sync demo.

## Prerequisites

- Redis server running on localhost:6379
- Python 3.8+
- Dependencies installed: `pip install -r requirements.txt`

## Important: First Time Setup / Upgrading

If you're upgrading from an older version or want a clean start, clear the Redis streams:

```bash
python3 -c "import redis; r = redis.Redis(host='localhost', port=6379, decode_responses=True); r.delete('ui-to-system', 'system-to-ui1', 'system-to-ui2'); r.delete('user:alice:sessions', 'user:bob:sessions'); print('Cleared Redis streams')"
```

Or simply:
```bash
redis-cli FLUSHALL
```

## Demo 1: Two Independent Users

This demonstrates two different users using separate UI services independently.

### Terminal Setup

**Terminal 1 - System Service:**
```bash
python word_length_service.py
```

**Terminal 2 - Demo Names (User: alice, Service: ui1):**
```bash
python demo_names.py
```

**Terminal 3 - Demo Fruits (User: bob, Service: ui2):**
```bash
python demo_fruits.py
```

### Expected Behavior

- **demo_names.py (alice@ui1)**: Sends random names every 11 seconds, receives only its own responses
- **demo_fruits.py (bob@ui2)**: Sends random fruits every 13 seconds, receives only its own responses
- **word_length_service.py**: Processes messages from both services and routes responses back to the sender only

### Example Output

**UI Service 1:**
```
[UI1] Connected to Redis
[UI1] Registered user 'alice' on service 'ui1'
[UI1] Starting to send names every 11 seconds...
[17:30:11] [UI1] Sent: 'Charlie'
[17:30:11] [UI1] Response: 'Charlie' has length 7
```

**UI Service 2:**
```
[UI2] Connected to Redis
[UI2] Registered user 'bob' on service 'ui2'
[UI2] Starting to send fruits every 13 seconds...
[17:30:13] [UI2] Sent: 'banana'
[17:30:13] [UI2] Response: 'banana' has length 6
```

**System Service:**
```
[17:30:11] Registered alice on ui1
[17:30:11] Received from alice@ui1: 'Charlie'
[17:30:11] Sent to ui1 for user alice: length=7
[17:30:13] Registered bob on ui2
[17:30:13] Received from bob@ui2: 'banana'
[17:30:13] Sent to ui2 for user bob: length=6
```

---

## Demo 2: Multi-Device Sync

This demonstrates the same user logged into multiple UI services simultaneously, with all instances staying synchronized.

### Option A: Using Python Scripts Directly

**Terminal 1 - System Service:**
```bash
python word_length_service.py
```

**Terminal 2 - Demo Names (User: alice on ui1):**
```bash
python demo_names.py
```

**Terminal 3 - Demo Multi-Device (User: alice on ui2):**
```bash
python demo_multi_device.py
```

### Expected Behavior

- **Both UI services belong to the same user (alice)**
- When UI Service 1 sends a name:
  - UI Service 1 shows: "Response: 'Charlie' has length 7"
  - UI Service 2 shows: "Response from ui1: 'Charlie' has length 7"
- When UI Service 2 sends a fruit:
  - UI Service 2 shows: "Response: 'banana' has length 6"
  - UI Service 1 shows: "Response from ui2: 'banana' has length 6"
- **Both services stay perfectly in sync!**

### Example Output

**UI Service 1 (alice):**
```
[UI1] Connected to Redis
[UI1] Registered user 'alice' on service 'ui1'
[UI1] Starting to send names every 11 seconds...
[17:30:11] [UI1] Sent: 'Charlie'
[17:30:11] [UI1] Response: 'Charlie' has length 7
[17:30:13] [UI1] Response from ui2: 'banana' has length 6  ← Synced from UI2!
```

**UI Service 2 (alice):**
```
[UI2] Connected to Redis
[UI2] Registered user 'alice' on service 'ui2'
[UI2] Starting to send fruits every 13 seconds...
[17:30:11] [UI2] Response from ui1: 'Charlie' has length 7  ← Synced from UI1!
[17:30:13] [UI2] Sent: 'banana'
[17:30:13] [UI2] Response: 'banana' has length 6
```

**System Service:**
```
[17:30:11] Registered alice on ui1
[17:30:11] Received from alice@ui1: 'Charlie'
[17:30:11] Sent to ui1 for user alice: length=7
[17:30:11] Sent to ui2 for user alice: length=7  ← Broadcast to both!
[17:30:13] Registered alice on ui2
[17:30:13] Received from alice@ui2: 'banana'
[17:30:13] Sent to ui1 for user alice: length=6  ← Broadcast to both!
[17:30:13] Sent to ui2 for user alice: length=6
```

---

## Understanding the Multi-Device Sync

### How It Works

1. **Session Registration**: When a UI service starts, it registers the user with the system service
   - Message: `{'type': 'register', 'user_id': 'alice', 'service_id': 'ui1'}`
   - System service tracks: `alice` is on services `['ui1']`

2. **Second Device Connects**: When alice connects from ui2
   - Message: `{'type': 'register', 'user_id': 'alice', 'service_id': 'ui2'}`
   - System service updates: `alice` is on services `['ui1', 'ui2']`

3. **Message Broadcast**: When alice sends a message from ui1
   - System looks up alice's active services: `['ui1', 'ui2']`
   - Sends response to **both** `system-to-ui1` and `system-to-ui2` streams
   - Both UI services receive and display the message

### Key Features

- ✅ **Backward compatible**: Single-device users work exactly as before
- ✅ **Zero configuration**: Just pass the same `user_id` to multiple services
- ✅ **Cross-service sync**: Users see activity from all their devices
- ✅ **Origin tracking**: Messages show which service they originated from
- ✅ **Session expiration**: Sessions expire after 1 hour of inactivity

---

## Advanced Testing

### Test Multiple Devices for Same User

```bash
# Terminal 1: System Service
python word_length_service.py

# Terminal 2: Alice on UI1 (sends names)
python demo_names.py

# Terminal 3: Alice on UI2 (sends fruits)
python demo_multi_device.py
```

Result: Alice sees messages from both her devices synced!

### Test Multiple Users

```bash
# Terminal 1: System Service
python word_length_service.py

# Terminal 2: Alice on ui1
python demo_names.py

# Terminal 3: Bob on ui2
python demo_fruits.py
```

Result: Alice and Bob see only their own messages (independent users).

---

## Cleanup

To clear Redis streams between tests:

```bash
redis-cli FLUSHALL
```

Or to remove specific streams:

```bash
redis-cli DEL ui-to-system system-to-ui1 system-to-ui2
redis-cli DEL user:alice:sessions user:bob:sessions
```

---

## Troubleshooting

### "Connection refused" error
- Ensure Redis is running: `redis-server` or check with `ps aux | grep redis`
- Verify Redis is on port 6379: `netstat -ln | grep 6379`

### Messages not appearing in sync
- Check that both UI services use the same `user_id`
- Verify system service is running and registered the sessions
- Check Redis for session data: `redis-cli SMEMBERS user:alice:sessions`

### Old messages appearing
- Clear Redis streams with `redis-cli FLUSHALL`
- Restart all services
