#!/usr/bin/env python3
"""
Word Length Service - Demo implementation of SystemService.

This service calculates the length of words sent by UI services.
This is application-specific business logic - your own service would
implement different logic.
"""
from typing import Dict, Any
from system_service import SystemService


class WordLengthService(SystemService):
    """
    Demo service that calculates word lengths.

    This is an example of how to extend SystemService with custom business logic.
    """

    async def process_data(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate the length of the word in the message.

        Args:
            message_data: Must contain 'word' field

        Returns:
            Dictionary with 'word' and 'length' fields

        Raises:
            ValueError: If 'word' field is missing
        """
        word = message_data.get('word')

        if not word:
            raise ValueError("Message must contain 'word' field")

        word_length = len(word)

        return {
            'word': word,
            'length': word_length
        }


async def main():
    service = WordLengthService()
    try:
        await service.run()
    except KeyboardInterrupt:
        print("\nShutting down word length service...")
    finally:
        await service.close()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
