#!/usr/bin/env python3
"""
UI Service Base Class - Reusable messaging client for the system.

This class provides the core functionality for connecting to the system service,
registering sessions, sending messages, and receiving responses. It's designed
to be used as a library by other applications.
"""
import asyncio
from datetime import datetime
from typing import Optional, Callable, Dict, Any
from stream_service import StreamService


class UIService(StreamService):
    """
    UI Service class for communicating with the system service via Redis Streams.

    Args:
        service_id: Unique identifier for this service instance (e.g., 'ui1', 'ui2', 'mobile-app')
        user_id: User identifier for multi-device sync
        redis_url: Redis connection URL
        on_response: Optional callback function called when a response is received
    """

    def __init__(
        self,
        service_id: str,
        user_id: str,
        redis_url: str = "redis://localhost",
        on_response: Optional[Callable[[Dict[str, Any]], None]] = None,
        logger = None,
        use_logging: bool = False
    ):
        super().__init__(redis_url, logger=logger, use_logging=use_logging)
        self.service_id = service_id
        self.user_id = user_id
        self.output_stream = "ui-to-system"
        self.input_stream = f"system-to-{self.service_id}"
        self.on_response = on_response
        self._receiving = False

    async def connect(self):
        """Connect to Redis."""
        await super().connect()
        self.log(f"[{self.service_id}] Ready to communicate")

    async def register_session(self):
        """Register this user's session with the system."""
        registration = {
            'type': 'register',
            'user_id': self.user_id,
            'service_id': self.service_id,
            'timestamp': datetime.now().isoformat()
        }
        await self.send_to_stream(self.output_stream, registration)
        self.log(f"[{self.service_id}] Registered user '{self.user_id}' on service '{self.service_id}'")

    async def send_message(self, data: Dict[str, Any]):
        """
        Send a message to the system service.

        Args:
            data: Dictionary containing the data to send (application-specific fields)

        Returns:
            Message ID from Redis
        """
        message = {
            'user_id': self.user_id,
            'service_id': self.service_id,
            'timestamp': datetime.now().isoformat(),
            **data  # Merge in application-specific data
        }

        message_id = await self.send_to_stream(self.output_stream, message)
        self.log(f"[{self.service_id}] Sent: {data} (msg_id: {message_id})")
        return message_id

    async def start_receiving(self):
        """
        Start listening for responses from the system.
        This runs in a loop until stop_receiving() is called.
        """
        if self._receiving:
            self.log(f"[{self.service_id}] Already receiving messages")
            return

        self._receiving = True
        self.log(f"[{self.service_id}] Listening for responses on stream '{self.input_stream}'...")

        last_id = '$'

        while self._receiving:
            try:
                messages = await self.read_from_stream(
                    self.input_stream,
                    last_id=last_id,
                    count=10,
                    block=1000
                )

                for stream_name, stream_messages in messages:
                    for message_id, message_data in stream_messages:
                        # Add message_id to data for tracking
                        message_data['_message_id'] = message_id
                        await self.process_message(message_id, message_data)
                        last_id = message_id

            except Exception as e:
                if self._receiving:  # Only log if we're supposed to be receiving
                    self.log_error(f"[{self.service_id}] Error receiving response: {e}")
                await asyncio.sleep(1)

    async def process_message(self, message_id: str, message_data: Dict[str, Any]):
        """
        Process a received message.

        Args:
            message_id: Redis message ID
            message_data: Message data dictionary (application-specific fields)
        """
        origin = message_data.get('origin_service')

        # Add metadata to the response data
        response_data = {
            **message_data,  # Pass through all application data
            'is_from_this_service': origin == self.service_id
        }

        # Call the callback if provided
        if self.on_response:
            self.on_response(response_data)
        else:
            # Default behavior: print to console
            self._default_response_handler(response_data)

    def _default_response_handler(self, response_data: Dict[str, Any]):
        """
        Default handler for responses when no callback is provided.

        This is a generic handler that works with any response format.
        For custom formatting, provide an on_response callback.
        """
        origin = response_data.get('origin_service', 'unknown')
        msg_id = response_data.get('_message_id', 'unknown')

        # Remove internal fields for cleaner display
        display_data = {k: v for k, v in response_data.items()
                       if k not in ['is_from_this_service', 'origin_service', '_message_id']}

        if response_data.get('is_from_this_service'):
            self.log(f"[{self.service_id}] Response: {display_data} (msg_id: {msg_id})")
        else:
            self.log(f"[{self.service_id}] Response from {origin}: {display_data} (msg_id: {msg_id})")

    async def stop_receiving(self):
        """Stop listening for responses."""
        self._receiving = False

    async def close(self):
        """Clean up resources."""
        await self.stop_receiving()
        await super().close()
