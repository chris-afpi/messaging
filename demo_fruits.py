#!/usr/bin/env python3
"""
Demo: Fruits Service

This demo shows how to use the UIService class to send random fruits
every 13 seconds.
"""
import asyncio
import random
from ui_service import UIService


# Demo data
FRUITS = [
    "apple", "banana", "cherry", "date", "elderberry",
    "fig", "grape", "honeydew", "kiwi", "lemon",
    "mango", "nectarine", "orange", "papaya", "quince",
    "raspberry", "strawberry", "tangerine", "watermelon"
]


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
    # Create service instance
    service = UIService(
        service_id="ui2",
        user_id="bob"
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
