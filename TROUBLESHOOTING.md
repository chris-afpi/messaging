# Troubleshooting Guide

## Common Issues and Solutions

### Problem: Messages Going to Wrong Service / Message Stealing

**Symptoms:**
- Messages sent by one service appear as responses in another
- Responses randomly distributed between services
- Duplicate consumer name warnings

**Example:**
```
# Service A sends
[23:18:20] [ui2] Sent: {'word': 'orange'}

# But Service B receives the response!
[23:18:20] [ui2] Response: 'orange' has length 6
```

**Cause:** Two service instances using the same `service_id` without different `consumer_name` values.

**Solution 1: Use Different service_ids**
```python
# DON'T: Both using "ui2"
service_a = UIService("ui2", "alice")
service_b = UIService("ui2", "bob")    # ❌ Conflict!

# DO: Use different service_ids
service_a = UIService("ui1", "alice")
service_b = UIService("ui2", "bob")    # ✓ No conflict
```

**Solution 2: Use Different consumer_names (for intentional scaling)**
```python
# If you WANT load balancing across workers:
worker_1 = UIService("ui2", "alice", consumer_name="worker-1")
worker_2 = UIService("ui2", "alice", consumer_name="worker-2")
# Messages will be load-balanced - this is intentional!
```

### Problem: Receiving Old Messages on Startup

**Symptoms:**
- When starting a service, immediately receives dozens of old messages
- Messages from previous demo runs

**Example:**
```
[23:18:07] [ui2] Response: 'nectarine' (msg_id: 1762997476466-0)  # Old!
[23:18:07] [ui2] Response: 'date' (msg_id: 1762997489466-0)       # Old!
... (30+ more old messages)
[23:18:07] [ui2] Response: 'lemon' (msg_id: 1763011087750-0)      # Current
```

**Cause:** Consumer groups now start at `id='$'` (new messages only as of latest fix). If you still see old messages, the consumer group was created before the fix.

**Solution: Delete Old Consumer Groups**
```bash
# Clear Redis completely
redis-cli FLUSHALL

# Or delete specific consumer group
redis-cli XGROUP DESTROY system-to-ui1 ui1-workers
redis-cli XGROUP DESTROY system-to-ui2 ui2-workers
```

After deletion, restart your services and they'll create new consumer groups starting from current messages.

### Problem: Demo Multi-Device Doesn't Show Sync

**Symptoms:**
- Running multi-device demo but not seeing messages synced
- Only seeing responses from own service

**Cause:** Running wrong combination of demos.

**Wrong Combination:**
```bash
python demo_fruits.py        # bob@ui2
python demo_multi_device.py  # alice@ui2
# ❌ Both use ui2 - causes conflict, not multi-device sync!
```

**Correct Combination:**
```bash
python demo_names.py         # alice@ui1
python demo_multi_device.py  # alice@ui2
# ✓ Same user (alice) on different services (ui1, ui2)
```

The demo shows **same user** on **different devices** (service_ids).

### Problem: Service Won't Start - Address Already in Use

**Symptoms:**
```
Error: Address already in use
OSError: [Errno 48] Address already in use
```

**Cause:** Another instance of the service is already running.

**Solution:**
```bash
# Find the process
ps aux | grep python | grep demo

# Kill it
kill <pid>

# Or kill all Python processes (careful!)
pkill -f "python.*demo"
```

### Problem: Redis Connection Refused

**Symptoms:**
```
ConnectionRefusedError: [Errno 111] Connection refused
redis.exceptions.ConnectionError: Error connecting to Redis
```

**Cause:** Redis server is not running.

**Solution:**
```bash
# Check if Redis is running
redis-cli ping
# Should return: PONG

# If not running, start it:
redis-server

# Or with Docker:
docker run -d -p 6379:6379 redis:latest
```

### Problem: Horizontal Scaling Not Working

**Symptoms:**
- Deployed multiple workers but all messages go to one
- Load not balanced

**Cause:** Workers using different service_ids instead of same service_id with different consumer_names.

**Wrong:**
```python
# These are separate services, not workers of the same service
worker1 = UIService("ui1", "alice", consumer_name="worker-1")
worker2 = UIService("ui2", "alice", consumer_name="worker-2")
# ❌ Different service_ids - no load balancing!
```

**Correct:**
```python
# These are workers of the same service
worker1 = UIService("ui1", "alice", consumer_name="worker-1")
worker2 = UIService("ui1", "alice", consumer_name="worker-2")
# ✓ Same service_id - load balancing works!
```

### Problem: Consumer Group Already Exists Error

**Symptoms:**
```
ResponseError: BUSYGROUP Consumer Group name already exists
```

**Solution:** This is normal and handled automatically. The error is caught and logged as info, not an error. If you want to recreate the group:

```bash
# Delete the consumer group
redis-cli XGROUP DESTROY system-to-ui1 ui1-workers

# Restart your service - it will recreate the group
```

## Demo Combinations Reference

### Valid Demo Combinations

| Terminal 1 | Terminal 2 | Terminal 3 | Purpose |
|------------|------------|------------|---------|
| word_length_service.py | demo_names.py | - | Single service demo |
| word_length_service.py | demo_fruits.py | - | Single service demo |
| word_length_service.py | demo_names.py | demo_multi_device.py | Multi-device sync (alice on ui1 & ui2) |
| word_length_service.py | demo_names.py | demo_fruits.py | Two users (alice@ui1, bob@ui2) |
| word_length_service.py | test_horizontal_scaling.py | - | Horizontal scaling demo (3 workers) |

### Invalid Demo Combinations

| Terminal 1 | Terminal 2 | Terminal 3 | Problem |
|------------|------------|------------|---------|
| word_length_service.py | demo_fruits.py | demo_multi_device.py | ❌ Both use ui2 - conflict! |
| word_length_service.py | demo_custom_usage.py | demo_multi_device.py | ❌ Both use ui2 - conflict! |

## Debugging Tips

### Check Redis Streams

```bash
# List all streams
redis-cli KEYS "*"

# Check stream length
redis-cli XLEN ui-to-system
redis-cli XLEN system-to-ui1

# View stream contents (last 10 messages)
redis-cli XREVRANGE ui-to-system + - COUNT 10

# Check consumer groups
redis-cli XINFO GROUPS system-to-ui1

# Check consumers in a group
redis-cli XINFO CONSUMERS system-to-ui1 ui1-workers

# Check pending messages
redis-cli XPENDING system-to-ui1 ui1-workers
```

### Enable Debug Logging

```python
import logging

# Enable debug logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

service = UIService("ui1", "alice", use_logging=True)
# Now you'll see detailed debug output
```

### Monitor Message Flow

Add custom logging to see exactly what's happening:

```python
def debug_response_handler(response_data):
    """Debug handler that shows all fields."""
    print(f"\n=== RECEIVED RESPONSE ===")
    for key, value in response_data.items():
        print(f"  {key}: {value}")
    print("=" * 40 + "\n")

service = UIService("ui1", "alice", on_response=debug_response_handler)
```

## Clean Slate / Fresh Start

If you want to completely reset and start fresh:

```bash
# 1. Kill all running demos
pkill -f "python.*demo"
pkill -f "python.*word_length"
pkill -f "python.*test_"

# 2. Flush Redis (WARNING: Deletes ALL data)
redis-cli FLUSHALL

# 3. Restart your demos
python word_length_service.py
python demo_names.py
```

## Getting Help

If you're still having issues:

1. Check the logs for error messages
2. Verify Redis is running: `redis-cli ping`
3. Check for consumer name conflicts
4. Verify you're running the correct demo combination
5. Try a fresh start (flush Redis, restart services)
6. Enable debug logging to see detailed message flow

## Prevention Best Practices

1. **Use unique service_ids** unless you intentionally want load balancing
2. **Clear Redis between test runs** to avoid old message confusion
3. **Check demo documentation** before running multiple demos together
4. **Use explicit consumer_names** in production to avoid accidents
5. **Monitor consumer groups** with `redis-cli XINFO CONSUMERS`
