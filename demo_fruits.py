#!/usr/bin/env python3
"""
Demo: Fruits Service

This demo shows how to use the UIService class to send random fruits
every 13 seconds.
"""
import asyncio
import random
from datetime import datetime
from ui_service import UIService


# Demo data
FRUITS = [
    "apple", "banana", "cherry", "date", "elderberry",
    "fig", "grape", "honeydew", "kiwi", "lemon",
    "mango", "nectarine", "orange", "papaya", "quince",
    "raspberry", "strawberry", "tangerine", "watermelon"
]


def handle_response(response_data):
    """Custom response handler for word-length demo."""
    word = response_data.get('word', 'unknown')
    length = response_data.get('length', 0)
    origin = response_data.get('origin_service')
    is_own = response_data.get('is_from_this_service')

    timestamp = datetime.now().strftime('%H:%M:%S')

    if is_own:
        print(f"[{timestamp}] [ui2] Response: '{word}' has length {length}")
    else:
        print(f"[{timestamp}] [ui2] Response from {origin}: '{word}' has length {length}")


async def send_fruits_periodically(service: UIService, interval: int = 13):
    """Send random fruits at regular intervals."""
    print(f"Starting to send fruits every {interval} seconds...")

    while True:
        try:
            fruit = random.choice(FRUITS)
            await service.send_message(fruit)
            await asyncio.sleep(interval)
        except Exception as e:
            print(f"Error sending fruit: {e}")
            await asyncio.sleep(1)


async def main():
    # Create service instance with custom response handler
    service = UIService(
        service_id="ui2",
        user_id="bob",
        on_response=handle_response
    )

    try:
        # Connect and register
        await service.connect()
        await service.register_session()

        # Start both sending and receiving concurrently
        await asyncio.gather(
            send_fruits_periodically(service, interval=13),
            service.start_receiving()
        )
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        await service.close()


if __name__ == "__main__":
    asyncio.run(main())
