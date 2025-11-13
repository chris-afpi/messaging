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
        on_response: Optional[Callable[[Dict[str, Any]], None]] = None
    ):
        super().__init__(redis_url)
        self.service_id = service_id
        self.user_id = user_id
        self.output_stream = "ui-to-system"
        self.input_stream = f"system-to-{self.service_id}"
        self.on_response = on_response
        self._receiving = False

    async def connect(self):
        """Connect to Redis."""
        await super().connect()
        print(f"[{self.service_id}] Ready to communicate")

    async def register_session(self):
        """Register this user's session with the system."""
        registration = {
            'type': 'register',
            'user_id': self.user_id,
            'service_id': self.service_id,
            'timestamp': datetime.now().isoformat()
        }
        await self.send_to_stream(self.output_stream, registration)
        print(f"[{self.service_id}] Registered user '{self.user_id}' on service '{self.service_id}'")

    async def send_message(self, word: str):
        """
        Send a message to the system service.

        Args:
            word: The word to send for processing
        """
        message = {
            'user_id': self.user_id,
            'service_id': self.service_id,
            'word': word,
            'timestamp': datetime.now().isoformat()
        }

        await self.send_to_stream(self.output_stream, message)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [{self.service_id}] Sent: '{word}'")

    async def start_receiving(self):
        """
        Start listening for responses from the system.
        This runs in a loop until stop_receiving() is called.
        """
        if self._receiving:
            print(f"[{self.service_id}] Already receiving messages")
            return

        self._receiving = True
        print(f"[{self.service_id}] Listening for responses on stream '{self.input_stream}'...")

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
                        await self.process_message(message_id, message_data)
                        last_id = message_id

            except Exception as e:
                if self._receiving:  # Only log if we're supposed to be receiving
                    print(f"[{self.service_id}] Error receiving response: {e}")
                await asyncio.sleep(1)

    async def process_message(self, message_id: str, message_data: Dict[str, Any]):
        """
        Process a received message.

        Args:
            message_id: Redis message ID
            message_data: Message data dictionary
        """
        user_id = message_data.get('user_id')
        origin = message_data.get('origin_service')
        word = message_data.get('word')
        length = message_data.get('length')

        response_data = {
            'user_id': user_id,
            'origin_service': origin,
            'word': word,
            'length': length,
            'is_from_this_service': origin == self.service_id
        }

        # Call the callback if provided
        if self.on_response:
            self.on_response(response_data)
        else:
            # Default behavior: print to console
            self._default_response_handler(response_data)

    def _default_response_handler(self, response_data: Dict[str, Any]):
        """Default handler for responses when no callback is provided."""
        word = response_data['word']
        length = response_data['length']
        origin = response_data['origin_service']

        if response_data['is_from_this_service']:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] [{self.service_id}] Response: '{word}' has length {length}")
        else:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] [{self.service_id}] Response from {origin}: '{word}' has length {length}")

    async def stop_receiving(self):
        """Stop listening for responses."""
        self._receiving = False

    async def run(self):
        """
        Main run loop. For backward compatibility.
        Most applications should use start_receiving() directly instead.
        """
        await self.connect()
        await self.register_session()
        await self.start_receiving()

    async def close(self):
        """Clean up resources."""
        await self.stop_receiving()
        await super().close()
