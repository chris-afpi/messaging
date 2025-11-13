#!/usr/bin/env python3
"""
Demo: Names Service

This demo shows how to use the UIService class to send random names
every 11 seconds.
"""
import asyncio
import random
from datetime import datetime
from ui_service import UIService


# Demo data
NAMES = [
    "Alice", "Bob", "Charlie", "Diana", "Edward",
    "Fiona", "George", "Hannah", "Isaac", "Julia",
    "Kevin", "Laura", "Michael", "Nancy", "Oliver",
    "Patricia", "Quentin", "Rachel", "Samuel", "Teresa"
]


def handle_response(response_data):
    """Custom response handler for word-length demo."""
    word = response_data.get('word', 'unknown')
    length = response_data.get('length', 0)
    origin = response_data.get('origin_service')
    is_own = response_data.get('is_from_this_service')

    timestamp = datetime.now().strftime('%H:%M:%S')

    if is_own:
        print(f"[{timestamp}] [ui1] Response: '{word}' has length {length}")
    else:
        print(f"[{timestamp}] [ui1] Response from {origin}: '{word}' has length {length}")


async def send_names_periodically(service: UIService, interval: int = 11):
    """Send random names at regular intervals."""
    print(f"Starting to send names every {interval} seconds...")

    while True:
        try:
            name = random.choice(NAMES)
            await service.send_message({'word': name})  # Send as dict
            await asyncio.sleep(interval)
        except Exception as e:
            print(f"Error sending name: {e}")
            await asyncio.sleep(1)


async def main():
    # Create service instance with custom response handler
    service = UIService(
        service_id="ui1",
        user_id="alice",
        on_response=handle_response
    )

    try:
        # Connect and register
        await service.connect()
        await service.register_session()

        # Start both sending and receiving concurrently
        await asyncio.gather(
            send_names_periodically(service, interval=11),
            service.start_receiving()
        )
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        await service.close()


if __name__ == "__main__":
    asyncio.run(main())
