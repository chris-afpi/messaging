#!/usr/bin/env python3
"""
Stream Service Base Class

Common base class for all Redis Stream-based services.
Provides shared functionality for connection management, sending, and receiving.
"""
import asyncio
import redis.asyncio as redis
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, Dict, Any, Union


class StreamService(ABC):
    """
    Abstract base class for Redis Stream services.

    Provides common functionality:
    - Redis connection management
    - Sending messages to streams
    - Lifecycle management (connect, close)
    - Configurable logging (print or logger)

    Subclasses must implement:
    - process_message(): How to handle incoming messages
    - run(): Main service loop
    """

    def __init__(
        self,
        redis_url: str = "redis://localhost",
        logger: Optional[Union[logging.Logger, str]] = None,
        use_logging: bool = False
    ):
        """
        Initialize the stream service.

        Args:
            redis_url: Redis connection URL
            logger: Optional logger instance or logger name. If None, uses service class name
            use_logging: If True, use logging.Logger; if False, use print (default)
        """
        self.redis_url = redis_url
        self.redis_client: Optional[redis.Redis] = None
        self.use_logging = use_logging

        # Setup logger
        if use_logging:
            if isinstance(logger, logging.Logger):
                self.logger = logger
            else:
                logger_name = logger or self.__class__.__name__
                self.logger = logging.getLogger(logger_name)
        else:
            self.logger = None

    async def connect(self):
        """Connect to Redis."""
        self.redis_client = await redis.from_url(
            self.redis_url,
            decode_responses=True
        )
        self.log(f"Connected to Redis at {self.redis_url}")

    async def close(self):
        """Close Redis connection and clean up resources."""
        if self.redis_client:
            await self.redis_client.close()
            self.log("Disconnected from Redis")

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

    def log(self, message: str, level: str = 'info'):
        """
        Log a message with timestamp and service name.

        Args:
            message: Message to log
            level: Log level ('debug', 'info', 'warning', 'error', 'critical')
        """
        if self.use_logging and self.logger:
            # Use proper logging
            log_method = getattr(self.logger, level.lower(), self.logger.info)
            log_method(message)
        else:
            # Use print with timestamp and service name
            timestamp = datetime.now().strftime('%H:%M:%S')
            service_name = self.__class__.__name__
            print(f"[{timestamp}] [{service_name}] {message}")

    def log_debug(self, message: str):
        """Log a debug message."""
        self.log(message, level='debug')

    def log_info(self, message: str):
        """Log an info message."""
        self.log(message, level='info')

    def log_warning(self, message: str):
        """Log a warning message."""
        self.log(message, level='warning')

    def log_error(self, message: str):
        """Log an error message."""
        self.log(message, level='error')

    def log_critical(self, message: str):
        """Log a critical message."""
        self.log(message, level='critical')

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
