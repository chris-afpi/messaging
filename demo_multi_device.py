#!/usr/bin/env python3
"""
Multi-Device Demo Script

This demo shows the same user (alice) logged into two different services
simultaneously, with both services staying in sync. When alice sends a
message from one service, it appears on the other.

Run this alongside demo_names.py (both as user 'alice') to see
multi-device synchronization in action!

Usage:
    Terminal 1: python system_service.py
    Terminal 2: python demo_names.py
    Terminal 3: python demo_multi_device.py
"""
import asyncio
import random
from datetime import datetime
from ui_service import UIService


# Demo data - fruits
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
    print("=" * 60)
    print("Multi-Device Sync Demo")
    print("=" * 60)
    print("This is UI Service 2 running as user 'alice'")
    print("Run demo_names.py in another terminal to see sync in action!")
    print("Both services will show messages from each other.")
    print("=" * 60)
    print()

    # Create UI Service 2 but with user_id='alice' instead of default 'bob'
    # This means alice is logged into BOTH ui1 and ui2
    service = UIService(
        service_id="ui2",
        user_id="alice",  # Same user as demo_names.py!
        on_response=handle_response
    )

    try:
        await service.connect()
        await service.register_session()

        # Start both sending and receiving concurrently
        await asyncio.gather(
            send_fruits_periodically(service, interval=13),
            service.start_receiving()
        )
    except KeyboardInterrupt:
        print('\n[UI2] Shutting down...')
    finally:
        await service.close()


if __name__ == "__main__":
    asyncio.run(main())
