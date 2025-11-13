#!/usr/bin/env python3
"""
Main system service that processes messages from UI services via Redis Streams.
Generic base class - business logic is implemented by subclasses.
"""
import asyncio
import redis.asyncio as redis
from datetime import datetime
from typing import Dict, Any, Optional
from stream_service import StreamService


class SystemService(StreamService):
    """
    Central system service that processes messages from UI services.

    This is a generic base class that handles:
    - Session tracking (user ↔ services)
    - Message routing and broadcasting
    - Consumer group management

    Subclasses must implement:
    - process_data(): Application-specific business logic
    """

    def __init__(self, redis_url="redis://localhost"):
        super().__init__(redis_url)
        self.input_stream = "ui-to-system"
        self.consumer_group = "system-processors"
        self.consumer_name = "system-worker-1"

    async def connect(self):
        """Connect to Redis and create consumer group if needed."""
        await super().connect()

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

    async def register_user_session(self, user_id: str, service_id: str):
        """Track that a user is active on a service (bidirectional tracking)."""
        # Track which services this user is on
        user_session_key = f"user:{user_id}:sessions"
        await self.redis_client.sadd(user_session_key, service_id)
        await self.redis_client.expire(user_session_key, 3600)  # 1 hour TTL

        # Track which users are on this service
        service_users_key = f"service:{service_id}:users"
        await self.redis_client.sadd(service_users_key, user_id)
        await self.redis_client.expire(service_users_key, 3600)  # 1 hour TTL

        self.log(f"Registered {user_id} on {service_id}")

    async def get_user_services(self, user_id: str):
        """Get all services a user is active on."""
        session_key = f"user:{user_id}:sessions"
        services = await self.redis_client.smembers(session_key)
        return services if services else set()

    async def get_service_users(self, service_id: str):
        """Get all users active on a service."""
        service_key = f"service:{service_id}:users"
        users = await self.redis_client.smembers(service_key)
        return users if users else set()

    async def process_data(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process incoming message data and return response data.

        This method contains application-specific business logic and must be
        implemented by subclasses.

        Args:
            message_data: The incoming message data (contains application-specific fields)

        Returns:
            Dictionary with response data (application-specific fields)

        Raises:
            NotImplementedError: If not overridden by subclass
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement process_data() method. "
            "This method should contain your application-specific business logic."
        )

    async def process_message(self, message_id: str, message_data: Dict[str, Any]):
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
                    self.log("Skipping registration with missing user_id or service_id")

                # Acknowledge the message
                await self.acknowledge_message(self.input_stream, self.consumer_group, message_id)
                return

            # Handle regular messages
            user_id = message_data.get('user_id')
            service_id = message_data.get('service_id')

            # Skip messages with missing required fields
            if not user_id or not service_id:
                self.log(f"Skipping message with missing user_id or service_id: {message_data}")
                await self.acknowledge_message(self.input_stream, self.consumer_group, message_id)
                return

            self.log(f"Received from {user_id}@{service_id}: {message_data}")

            # Process the data (application-specific logic)
            try:
                response_data = await self.process_data(message_data)
            except Exception as e:
                self.log(f"Error processing data: {e}")
                await self.acknowledge_message(self.input_stream, self.consumer_group, message_id)
                return

            # Get all services this user is connected to
            user_services = await self.get_user_services(user_id)

            # If user has no registered sessions, fall back to the service that sent the message
            if not user_services:
                user_services = {service_id}

            # Send response to ALL services the user is on
            response = {
                'user_id': user_id,
                'origin_service': service_id,
                'processed_at': datetime.now().isoformat(),
                **response_data  # Merge in application-specific response data
            }

            for target_service in user_services:
                response_stream = f"system-to-{target_service}"
                await self.send_to_stream(response_stream, response)
                self.log(f"Sent to {target_service} for user {user_id}")

            # Acknowledge the message
            await self.acknowledge_message(self.input_stream, self.consumer_group, message_id)

        except Exception as e:
            print(f"Error handling message {message_id}: {e}")
            import traceback
            traceback.print_exc()
            # Still acknowledge to prevent reprocessing
            try:
                await self.acknowledge_message(self.input_stream, self.consumer_group, message_id)
            except:
                pass

    async def run(self):
        """Main run loop."""
        await self.connect()

        print(f"System service listening on stream '{self.input_stream}'...")

        while True:
            try:
                # Read messages from the stream using consumer group
                messages = await self.read_from_stream_group(
                    self.consumer_group,
                    self.consumer_name,
                    self.input_stream,
                    count=10,
                    block=1000
                )

                for stream_name, stream_messages in messages:
                    for message_id, message_data in stream_messages:
                        await self.process_message(message_id, message_data)

            except Exception as e:
                print(f"Error processing messages: {e}")
                await asyncio.sleep(1)


# SystemService is now a base class - use a subclass like WordLengthService
# See word_length_service.py for an example implementation

if __name__ == "__main__":
    print("SystemService is a base class. Use a subclass like:")
    print("  python word_length_service.py")
    print("\nOr create your own subclass that implements process_data()")
    import sys
    sys.exit(1)
