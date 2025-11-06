#!/usr/bin/env python3
"""
UI Service 1 - Sends random name words every 11 seconds.
Listens for responses from the system.
"""
import asyncio
import redis.asyncio as redis
import random
from datetime import datetime


class UIService1:
    def __init__(self, redis_url="redis://localhost"):
        self.redis_url = redis_url
        self.redis_client = None
        self.service_id = "ui1"
        self.output_stream = "ui-to-system"
        self.input_stream = f"system-to-{self.service_id}"
        self.send_interval = 11  # seconds

        # Random names to send
        self.names = [
            "Alice", "Bob", "Charlie", "Diana", "Edward",
            "Fiona", "George", "Hannah", "Isaac", "Julia",
            "Kevin", "Laura", "Michael", "Nancy", "Oliver",
            "Patricia", "Quentin", "Rachel", "Samuel", "Teresa"
        ]

    async def connect(self):
        """Connect to Redis."""
        self.redis_client = await redis.from_url(
            self.redis_url,
            decode_responses=True
        )
        print(f"[UI1] Connected to Redis")

    async def send_messages(self):
        """Send random name words periodically."""
        print(f"[UI1] Starting to send names every {self.send_interval} seconds...")

        while True:
            try:
                # Pick a random name
                name = random.choice(self.names)

                # Send to system
                message = {
                    'sender': self.service_id,
                    'word': name,
                    'timestamp': datetime.now().isoformat()
                }

                await self.redis_client.xadd(self.output_stream, message)
                print(f"[{datetime.now().strftime('%H:%M:%S')}] [UI1] Sent: '{name}'")

                await asyncio.sleep(self.send_interval)

            except Exception as e:
                print(f"[UI1] Error sending message: {e}")
                await asyncio.sleep(1)

    async def receive_responses(self):
        """Listen for responses from the system."""
        print(f"[UI1] Listening for responses on stream '{self.input_stream}'...")

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
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] [UI1] Response: '{word}' has length {length}")
                        last_id = message_id

            except Exception as e:
                print(f"[UI1] Error receiving response: {e}")
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
    service = UIService1()
    try:
        await service.run()
    except KeyboardInterrupt:
        print("\n[UI1] Shutting down...")
    finally:
        await service.close()


if __name__ == "__main__":
    asyncio.run(main())
