#!/usr/bin/env python3
"""
Test: Horizontal Scaling

This script demonstrates UIService horizontal scaling by creating multiple workers
for the same service_id that will load-balance messages across them.
"""
import asyncio
from ui_service import UIService


def handle_response(worker_name):
    """Create a custom response handler that identifies which worker received the message."""
    def handler(response_data):
        word = response_data.get('word', 'unknown')
        length = response_data.get('length', 0)
        msg_id = response_data.get('_message_id', 'unknown')
        print(f"[{worker_name}] ✓ Received: '{word}' -> {length} chars (msg_id: {msg_id})")
    return handler


async def run_worker(worker_name, service_id="scaled-ui", user_id="alice"):
    """Run a single worker."""
    service = UIService(
        service_id=service_id,
        user_id=user_id,
        consumer_name=worker_name,  # Unique worker name
        on_response=handle_response(worker_name)
    )

    await service.connect()
    await service.register_session()

    print(f"[{worker_name}] Started - ready to receive messages")

    # Start receiving (this will run until the service is closed)
    await service.start_receiving()


async def send_messages(service_id="scaled-ui", user_id="alice", count=10):
    """Send test messages."""
    sender = UIService(
        service_id=service_id,
        user_id=user_id,
        consumer_name="sender"
    )

    await sender.connect()
    await sender.register_session()

    # Wait a bit for workers to be ready
    await asyncio.sleep(2)

    words = ["apple", "banana", "cherry", "date", "elderberry",
             "fig", "grape", "honeydew", "kiwi", "lemon"]

    print(f"\n{'='*60}")
    print(f"Sending {count} messages...")
    print(f"{'='*60}\n")

    for i in range(count):
        word = words[i % len(words)]
        await sender.send_message({'word': word})
        print(f"Sent #{i+1}: '{word}'")
        await asyncio.sleep(0.5)

    print(f"\n{'='*60}")
    print(f"All messages sent. Watch workers load-balance the responses!")
    print(f"{'='*60}\n")

    # Keep sender alive for a bit to see responses
    await asyncio.sleep(5)
    await sender.close()


async def main():
    print("\n" + "="*60)
    print("UIService Horizontal Scaling Test")
    print("="*60)
    print("\nThis demo shows multiple workers processing messages from")
    print("the same service_id with load balancing via consumer groups.")
    print("\nMake sure word_length_service.py is running!\n")
    print("="*60 + "\n")

    # Create 3 workers for the same service_id
    worker_tasks = [
        asyncio.create_task(run_worker("worker-1")),
        asyncio.create_task(run_worker("worker-2")),
        asyncio.create_task(run_worker("worker-3")),
    ]

    # Wait for workers to start
    await asyncio.sleep(1)

    # Send messages in a separate task
    sender_task = asyncio.create_task(send_messages(count=10))

    try:
        # Wait for sender to finish
        await sender_task

        # Keep workers running for a bit to process all messages
        await asyncio.sleep(3)

    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        # Cancel all worker tasks
        for task in worker_tasks:
            task.cancel()

        # Wait for cancellation
        await asyncio.gather(*worker_tasks, return_exceptions=True)

    print("\n" + "="*60)
    print("Test completed!")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
