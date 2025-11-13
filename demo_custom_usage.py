#!/usr/bin/env python3
"""
Demo: Custom Usage

This demo shows how to use the UIService class as a library with custom
response handling. This example could be adapted for a web app, GUI, etc.
"""
import asyncio
from ui_service import UIService


class WordLengthApp:
    """Example application that uses UIService."""

    def __init__(self):
        self.service = UIService(
            service_id="custom-app",
            user_id="demo-user",
            on_response=self.handle_response  # Custom callback
        )
        self.response_count = 0

    def handle_response(self, response_data):
        """Custom response handler - could update a GUI, database, etc."""
        self.response_count += 1
        word = response_data['word']
        length = response_data['length']
        origin = response_data['origin_service']

        print(f"✓ Response #{self.response_count}: '{word}' -> {length} chars (from {origin})")

        # You could do anything here:
        # - Update a GUI
        # - Store in a database
        # - Send a webhook
        # - Update analytics
        # etc.

    async def send_word(self, word: str):
        """Send a word to be processed."""
        await self.service.send_message({'word': word})  # Send as dict

    async def run(self):
        """Run the application."""
        # Connect and register
        await self.service.connect()
        await self.service.register_session()

        # Start receiving responses in the background
        receive_task = asyncio.create_task(self.service.start_receiving())

        # Demo: send some words
        words_to_send = ["hello", "world", "Python", "Redis", "Streams"]

        for word in words_to_send:
            await self.send_word(word)
            await asyncio.sleep(2)  # Wait 2 seconds between sends

        print("\nAll words sent. Press Ctrl+C to exit (or wait 10 seconds)...")

        # Keep running to receive responses
        try:
            await asyncio.sleep(10)
        except KeyboardInterrupt:
            pass

        await receive_task

    async def close(self):
        """Clean up."""
        await self.service.close()


async def main():
    app = WordLengthApp()
    try:
        await app.run()
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        await app.close()


if __name__ == "__main__":
    asyncio.run(main())
