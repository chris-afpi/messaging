#!/usr/bin/env python3
"""
Main system service that processes messages from UI services via Redis Streams.
Listens for messages and replies with the word length.
"""
import asyncio
import redis.asyncio as redis
import json
from datetime import datetime


class SystemService:
    def __init__(self, redis_url="redis://localhost"):
        self.redis_url = redis_url
        self.redis_client = None
        self.input_stream = "ui-to-system"
        self.consumer_group = "system-processors"
        self.consumer_name = "system-worker-1"

    async def connect(self):
        """Connect to Redis and create consumer group if needed."""
        self.redis_client = await redis.from_url(
            self.redis_url,
            decode_responses=True
        )

        # Create consumer group (ignore error if it already exists)
        try:
            await self.redis_client.xgroup_create(
                self.input_stream,
                self.consumer_group,
                id='0',
                mkstream=True
            )
            print(f"Created consumer group '{self.consumer_group}' on stream '{self.input_stream}'")
        except redis.ResponseError as e:
            if "BUSYGROUP" not in str(e):
                raise
            print(f"Consumer group '{self.consumer_group}' already exists")

    async def process_messages(self):
        """Listen for messages and process them."""
        print(f"System service listening on stream '{self.input_stream}'...")

        while True:
            try:
                # Read messages from the stream using consumer group
                messages = await self.redis_client.xreadgroup(
                    self.consumer_group,
                    self.consumer_name,
                    {self.input_stream: '>'},
                    count=10,
                    block=1000  # Block for 1 second
                )

                for stream_name, stream_messages in messages:
                    for message_id, message_data in stream_messages:
                        await self.handle_message(message_id, message_data)

            except Exception as e:
                print(f"Error processing messages: {e}")
                await asyncio.sleep(1)

    async def handle_message(self, message_id, message_data):
        """Process a single message and send response."""
        try:
            sender = message_data.get('sender')
            word = message_data.get('word')
            timestamp = message_data.get('timestamp')

            print(f"[{datetime.now().strftime('%H:%M:%S')}] Received from {sender}: '{word}'")

            # Calculate word length
            word_length = len(word)

            # Send response back to sender's stream
            response_stream = f"system-to-{sender}"
            response = {
                'word': word,
                'length': word_length,
                'processed_at': datetime.now().isoformat()
            }

            await self.redis_client.xadd(response_stream, response)
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Sent to {sender}: length={word_length}")

            # Acknowledge the message
            await self.redis_client.xack(
                self.input_stream,
                self.consumer_group,
                message_id
            )

        except Exception as e:
            print(f"Error handling message {message_id}: {e}")

    async def run(self):
        """Main run loop."""
        await self.connect()
        await self.process_messages()

    async def close(self):
        """Clean up resources."""
        if self.redis_client:
            await self.redis_client.close()


async def main():
    service = SystemService()
    try:
        await service.run()
    except KeyboardInterrupt:
        print("\nShutting down system service...")
    finally:
        await service.close()


if __name__ == "__main__":
    asyncio.run(main())
