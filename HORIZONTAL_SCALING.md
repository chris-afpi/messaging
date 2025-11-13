# Horizontal Scaling Guide

## Overview

UIService now supports horizontal scaling through Redis consumer groups. You can deploy multiple workers for the same `service_id`, and messages will be automatically load-balanced across them.

## How It Works

### Consumer Groups

When a UIService connects, it creates a consumer group named `{service_id}-workers`. Each worker instance has a unique `consumer_name` within that group.

```
service_id: "ui1"
├── Consumer Group: "ui1-workers"
│   ├── worker-1 (default)
│   ├── worker-2
│   └── worker-3
```

**Load Balancing**: When the system service sends a response to `system-to-ui1`, Redis automatically distributes messages across available workers in the consumer group. Each message is delivered to exactly one worker.

**Reliability**: Messages are acknowledged after processing. If a worker crashes before acknowledging, Redis can reassign the message to another worker.

## Usage

### Single Worker (Default Behavior)

Existing code works without changes:

```python
from ui_service import UIService

service = UIService("ui1", "alice")
# Uses default consumer_name: "ui1-worker-1"
```

### Multiple Workers (Horizontal Scaling)

Deploy multiple workers with unique names:

```python
# Worker 1
service1 = UIService("ui1", "alice", consumer_name="worker-1")

# Worker 2
service2 = UIService("ui1", "alice", consumer_name="worker-2")

# Worker 3
service3 = UIService("ui1", "alice", consumer_name="worker-3")

# All workers connect to the same service_id
# Messages are load-balanced across them
```

### Dynamic Worker Names

For production deployments, generate unique worker names:

```python
import socket
import os

hostname = socket.gethostname()
pid = os.getpid()
worker_name = f"worker-{hostname}-{pid}"

service = UIService("ui1", "alice", consumer_name=worker_name)
```

Or use UUIDs:

```python
import uuid

worker_name = f"worker-{uuid.uuid4().hex[:8]}"
service = UIService("ui1", "alice", consumer_name=worker_name)
```

## Example: Load Balancing in Action

```python
import asyncio
from ui_service import UIService

async def run_worker(worker_name):
    """Run a single worker."""
    service = UIService(
        service_id="api-service",
        user_id="system",
        consumer_name=worker_name
    )

    await service.connect()
    await service.register_session()

    print(f"[{worker_name}] Ready to process messages")
    await service.start_receiving()

async def main():
    # Deploy 3 workers
    workers = [
        asyncio.create_task(run_worker("worker-1")),
        asyncio.create_task(run_worker("worker-2")),
        asyncio.create_task(run_worker("worker-3")),
    ]

    # Workers will now load-balance incoming messages
    await asyncio.gather(*workers)

if __name__ == "__main__":
    asyncio.run(main())
```

## Testing Horizontal Scaling

Run the test script to see load balancing in action:

```bash
# Terminal 1: Start the system service
python word_length_service.py

# Terminal 2: Run the horizontal scaling test
python test_horizontal_scaling.py
```

The test creates 3 workers and sends 10 messages. You'll see messages distributed across workers:

```
[worker-1] ✓ Received: 'apple' -> 5 chars
[worker-2] ✓ Received: 'banana' -> 6 chars
[worker-3] ✓ Received: 'cherry' -> 6 chars
[worker-1] ✓ Received: 'date' -> 4 chars
[worker-2] ✓ Received: 'elderberry' -> 10 chars
...
```

## Architecture Comparison

### Before: Dedicated Streams (No Scaling)

```
system-to-ui1 ──> ui1 (single instance)
system-to-ui2 ──> ui2 (single instance)
```

- Each service_id has one consumer
- Cannot horizontally scale a single service

### After: Consumer Groups (Scalable)

```
system-to-ui1 ──> [ui1-workers consumer group]
                  ├── worker-1
                  ├── worker-2
                  └── worker-3
```

- Multiple workers per service_id
- Redis load-balances messages
- Automatic failover if worker crashes

## Benefits

1. **Load Balancing**: Distribute work across multiple workers
2. **Scalability**: Add/remove workers dynamically as load changes
3. **Reliability**: Messages are acknowledged - unprocessed messages can be retried
4. **Backward Compatible**: Existing single-worker deployments work unchanged
5. **Flexibility**: Mix single-worker and multi-worker services in the same system

## Production Considerations

### 1. Worker Naming

Use unique, stable names for workers:

```python
# Good: hostname + pid (unique per process)
worker_name = f"worker-{socket.gethostname()}-{os.getpid()}"

# Good: container ID in Kubernetes/Docker
worker_name = f"worker-{os.environ.get('HOSTNAME', 'unknown')}"

# Avoid: hardcoded names when scaling
worker_name = "worker-1"  # ⚠️ Don't use same name on multiple instances!
```

### 2. Message Ordering

**Important**: Consumer groups provide load balancing but **not guaranteed ordering**. If your application requires strict message ordering, use a single worker per service_id.

### 3. Monitoring

Monitor consumer group health:

```bash
# Check consumer group info
redis-cli XINFO GROUPS system-to-ui1

# Check consumer details
redis-cli XINFO CONSUMERS system-to-ui1 ui1-workers

# Check pending messages
redis-cli XPENDING system-to-ui1 ui1-workers
```

### 4. Deployment Strategies

**Rolling Updates**:
```bash
# Deploy new workers
start worker-4
start worker-5
start worker-6

# Gracefully stop old workers (let them finish processing)
stop worker-1
stop worker-2
stop worker-3
```

**Auto Scaling** (Kubernetes HPA example):
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: ui-service
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ui-service
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

### 5. Graceful Shutdown

Ensure workers finish processing before shutdown:

```python
async def graceful_shutdown(service):
    """Gracefully shutdown a worker."""
    print("Shutting down worker...")

    # Stop accepting new messages
    await service.stop_receiving()

    # Close connections
    await service.close()

    print("Worker shutdown complete")
```

## Multi-Device vs Horizontal Scaling

The system now supports **both**:

### Multi-Device Sync (Per-User)

Same user on multiple devices - each device is a different service_id:

```python
# Alice's laptop
laptop = UIService("ui-laptop", "alice")

# Alice's phone
phone = UIService("ui-phone", "alice")
```

Both receive messages when alice sends data (multi-device sync).

### Horizontal Scaling (Per-Service)

Multiple workers behind one service_id:

```python
# Multiple workers for "ui-laptop"
worker1 = UIService("ui-laptop", "alice", consumer_name="worker-1")
worker2 = UIService("ui-laptop", "alice", consumer_name="worker-2")
```

Messages to `system-to-ui-laptop` are load-balanced across workers.

### Combined

You can have both:

```python
# Alice's laptop - 3 workers for high load
laptop_w1 = UIService("ui-laptop", "alice", consumer_name="laptop-w1")
laptop_w2 = UIService("ui-laptop", "alice", consumer_name="laptop-w2")
laptop_w3 = UIService("ui-laptop", "alice", consumer_name="laptop-w3")

# Alice's phone - 1 worker (low load)
phone = UIService("ui-phone", "alice")
```

When alice sends a message:
- Response goes to BOTH laptop and phone (multi-device)
- On laptop: load-balanced across 3 workers
- On phone: processed by single worker

## Migration from Old Code

If you have existing UIService code, **no changes needed**! The new implementation is backward compatible:

```python
# Old code - still works
service = UIService("ui1", "alice")

# Automatically uses:
# - consumer_group: "ui1-workers"
# - consumer_name: "ui1-worker-1"
```

To enable scaling, just add more workers:

```python
# Add worker 2 (no code changes to worker 1)
service2 = UIService("ui1", "alice", consumer_name="worker-2")
```

## Summary

- ✅ UIService now supports horizontal scaling via consumer groups
- ✅ Backward compatible - existing code works unchanged
- ✅ Load balancing - messages distributed across workers
- ✅ Reliable - messages acknowledged after processing
- ✅ Flexible - mix single and multi-worker deployments
- ✅ Production ready - works with containers, auto-scaling, etc.
