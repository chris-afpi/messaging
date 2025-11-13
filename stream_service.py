#!/usr/bin/env python3
"""
Stream Service Base Class

Common base class for all Redis Stream-based services.
Provides shared functionality for connection management, sending, and receiving.
"""
import asyncio
import redis.asyncio as redis
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, Dict, Any


class StreamService(ABC):
    """
    Abstract base class for Redis Stream services.

    Provides common functionality:
    - Redis connection management
    - Sending messages to streams
    - Lifecycle management (connect, close)

    Subclasses must implement:
    - process_message(): How to handle incoming messages
    - run(): Main service loop
    """

    def __init__(self, redis_url: str = "redis://localhost"):
        """
        Initialize the stream service.

        Args:
            redis_url: Redis connection URL
        """
        self.redis_url = redis_url
        self.redis_client: Optional[redis.Redis] = None

    async def connect(self):
        """Connect to Redis."""
        self.redis_client = await redis.from_url(
            self.redis_url,
            decode_responses=True
        )
        print(f"[{self.__class__.__name__}] Connected to Redis at {self.redis_url}")

    async def close(self):
        """Close Redis connection and clean up resources."""
        if self.redis_client:
            await self.redis_client.close()
            print(f"[{self.__class__.__name__}] Disconnected from Redis")

    async def send_to_stream(self, stream: str, data: Dict[str, Any]) -> str:
        """
        Send a message to a Redis stream.

        Args:
            stream: Name of the stream
            data: Message data as a dictionary

        Returns:
            Message ID from Redis
        """
        if not self.redis_client:
            raise RuntimeError("Not connected to Redis. Call connect() first.")

        message_id = await self.redis_client.xadd(stream, data)
        return message_id

    async def read_from_stream(
        self,
        stream: str,
        last_id: str = '$',
        count: int = 10,
        block: int = 1000
    ):
        """
        Read messages from a stream using xread.

        Args:
            stream: Name of the stream to read from
            last_id: Last message ID seen (use '$' for latest)
            count: Maximum number of messages to read
            block: Block for this many milliseconds waiting for messages

        Returns:
            List of messages
        """
        if not self.redis_client:
            raise RuntimeError("Not connected to Redis. Call connect() first.")

        return await self.redis_client.xread(
            {stream: last_id},
            count=count,
            block=block
        )

    async def read_from_stream_group(
        self,
        group: str,
        consumer: str,
        stream: str,
        count: int = 10,
        block: int = 1000
    ):
        """
        Read messages from a stream using consumer groups (xreadgroup).

        Args:
            group: Consumer group name
            consumer: Consumer name within the group
            stream: Name of the stream to read from
            count: Maximum number of messages to read
            block: Block for this many milliseconds waiting for messages

        Returns:
            List of messages
        """
        if not self.redis_client:
            raise RuntimeError("Not connected to Redis. Call connect() first.")

        return await self.redis_client.xreadgroup(
            group,
            consumer,
            {stream: '>'},
            count=count,
            block=block
        )

    async def acknowledge_message(self, stream: str, group: str, message_id: str):
        """
        Acknowledge a message in a consumer group.

        Args:
            stream: Stream name
            group: Consumer group name
            message_id: Message ID to acknowledge
        """
        if not self.redis_client:
            raise RuntimeError("Not connected to Redis. Call connect() first.")

        await self.redis_client.xack(stream, group, message_id)

    def log(self, message: str):
        """Log a message with timestamp and service name."""
        timestamp = datetime.now().strftime('%H:%M:%S')
        service_name = self.__class__.__name__
        print(f"[{timestamp}] [{service_name}] {message}")

    @abstractmethod
    async def process_message(self, message_id: str, message_data: Dict[str, Any]):
        """
        Process a single message. Must be implemented by subclasses.

        Args:
            message_id: Redis message ID
            message_data: Message data as a dictionary
        """
        pass

    async def run(self):
        """
        Main service loop. Optional - only needed for services that have a main loop.

        Subclasses can override this if they need a run() method.
        UIService doesn't need this - it uses connect() + register_session() + start_receiving().
        SystemService does need this - it has a main processing loop.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} does not implement run(). "
            "Either implement run() or use the service's methods directly."
        )
