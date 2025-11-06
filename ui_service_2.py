#!/usr/bin/env python3
"""
UI Service 2 - Sends random fruit words every 13 seconds.
Listens for responses from the system.
"""
import asyncio
import redis.asyncio as redis
import random
from datetime import datetime


class UIService2:
    def __init__(self, redis_url="redis://localhost"):
        self.redis_url = redis_url
        self.redis_client = None
        self.service_id = "ui2"
        self.output_stream = "ui-to-system"
        self.input_stream = f"system-to-{self.service_id}"
        self.send_interval = 13  # seconds

        # Random fruits to send
        self.fruits = [
            "apple", "banana", "cherry", "date", "elderberry",
            "fig", "grape", "honeydew", "kiwi", "lemon",
            "mango", "nectarine", "orange", "papaya", "quince",
            "raspberry", "strawberry", "tangerine", "watermelon"
        ]

    async def connect(self):
        """Connect to Redis."""
        self.redis_client = await redis.from_url(
            self.redis_url,
            decode_responses=True
        )
        print(f"[UI2] Connected to Redis")

    async def send_messages(self):
        """Send random fruit words periodically."""
        print(f"[UI2] Starting to send fruits every {self.send_interval} seconds...")

        while True:
            try:
                # Pick a random fruit
                fruit = random.choice(self.fruits)

                # Send to system
                message = {
                    'sender': self.service_id,
                    'word': fruit,
                    'timestamp': datetime.now().isoformat()
                }

                await self.redis_client.xadd(self.output_stream, message)
                print(f"[{datetime.now().strftime('%H:%M:%S')}] [UI2] Sent: '{fruit}'")

                await asyncio.sleep(self.send_interval)

            except Exception as e:
                print(f"[UI2] Error sending message: {e}")
                await asyncio.sleep(1)

    async def receive_responses(self):
        """Listen for responses from the system."""
        print(f"[UI2] Listening for responses on stream '{self.input_stream}'...")

        # Start reading from the latest messages
        last_id = '$'

        while True:
            try:
                # Read new messages
                messages = await self.redis_client.xread(
                    {self.input_stream: last_id},
                    count=10,
                    block=1000  # Block for 1 second
                )

                for stream_name, stream_messages in messages:
                    for message_id, message_data in stream_messages:
                        word = message_data.get('word')
                        length = message_data.get('length')
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] [UI2] Response: '{word}' has length {length}")
                        last_id = message_id

            except Exception as e:
                print(f"[UI2] Error receiving response: {e}")
                await asyncio.sleep(1)

    async def run(self):
        """Main run loop."""
        await self.connect()

        # Run send and receive tasks concurrently
        await asyncio.gather(
            self.send_messages(),
            self.receive_responses()
        )

    async def close(self):
        """Clean up resources."""
        if self.redis_client:
            await self.redis_client.close()


async def main():
    service = UIService2()
    try:
        await service.run()
    except KeyboardInterrupt:
        print("\n[UI2] Shutting down...")
    finally:
        await service.close()


if __name__ == "__main__":
    asyncio.run(main())
