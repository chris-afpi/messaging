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

    async def register_user_session(self, user_id, service_id):
        """Track that a user is active on a service."""
        session_key = f"user:{user_id}:sessions"
        await self.redis_client.sadd(session_key, service_id)
        await self.redis_client.expire(session_key, 3600)  # 1 hour TTL
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Registered {user_id} on {service_id}")

    async def get_user_services(self, user_id):
        """Get all services a user is active on."""
        session_key = f"user:{user_id}:sessions"
        services = await self.redis_client.smembers(session_key)
        return services if services else set()

    async def handle_message(self, message_id, message_data):
        """Process a single message and send response."""
        try:
            message_type = message_data.get('type', 'message')

            # Handle session registration
            if message_type == 'register':
                user_id = message_data.get('user_id')
                service_id = message_data.get('service_id')

                if user_id and service_id:
                    await self.register_user_session(user_id, service_id)
                else:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Skipping registration with missing user_id or service_id")

                # Acknowledge the message
                await self.redis_client.xack(
                    self.input_stream,
                    self.consumer_group,
                    message_id
                )
                return

            # Handle regular messages
            user_id = message_data.get('user_id')
            service_id = message_data.get('service_id')
            word = message_data.get('word')
            timestamp = message_data.get('timestamp')

            # Skip messages with missing required fields (likely old messages)
            if not user_id or not service_id or not word:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Skipping message with missing fields: {message_data}")
                await self.redis_client.xack(
                    self.input_stream,
                    self.consumer_group,
                    message_id
                )
                return

            print(f"[{datetime.now().strftime('%H:%M:%S')}] Received from {user_id}@{service_id}: '{word}'")

            # Calculate word length
            word_length = len(word)

            # Get all services this user is connected to
            user_services = await self.get_user_services(user_id)

            # If user has no registered sessions, fall back to the service that sent the message
            if not user_services:
                user_services = {service_id}

            # Send response to ALL services the user is on
            response = {
                'user_id': user_id,
                'origin_service': service_id,
                'word': word,
                'length': word_length,
                'processed_at': datetime.now().isoformat()
            }

            for target_service in user_services:
                response_stream = f"system-to-{target_service}"
                await self.redis_client.xadd(response_stream, response)
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Sent to {target_service} for user {user_id}: length={word_length}")

            # Acknowledge the message
            await self.redis_client.xack(
                self.input_stream,
                self.consumer_group,
                message_id
            )

        except Exception as e:
            print(f"Error handling message {message_id}: {e}")
            import traceback
            traceback.print_exc()
            # Still acknowledge to prevent reprocessing
            try:
                await self.redis_client.xack(
                    self.input_stream,
                    self.consumer_group,
                    message_id
                )
            except:
                pass

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
