#!/usr/bin/env python3
"""
Demo: Logging Feature

This demo shows how to use the configurable logging system.
By default, services use print() for simple console output.
For production use, you can enable proper logging with logging.Logger.
"""
import asyncio
import logging
from ui_service import UIService


def handle_response(response_data):
    """Custom response handler for word-length demo."""
    word = response_data.get('word', 'unknown')
    length = response_data.get('length', 0)
    origin = response_data.get('origin_service')
    is_own = response_data.get('is_from_this_service')
    msg_id = response_data.get('_message_id', 'unknown')

    if is_own:
        print(f"✓ Response: '{word}' has length {length} (msg_id: {msg_id})")
    else:
        print(f"✓ Response from {origin}: '{word}' has length {length} (msg_id: {msg_id})")


async def demo_with_print():
    """Demo using default print() output."""
    print("\n" + "="*60)
    print("DEMO 1: Default mode (using print)")
    print("="*60 + "\n")

    # Default mode - uses print()
    service = UIService(
        service_id="logging-demo-print",
        user_id="demo-user",
        on_response=handle_response
        # use_logging=False is the default
    )

    await service.connect()
    await service.register_session()

    # Start receiving in the background
    receive_task = asyncio.create_task(service.start_receiving())

    # Send a test message
    await service.send_message({'word': 'Hello'})
    await asyncio.sleep(2)

    await service.close()
    await receive_task


async def demo_with_logging():
    """Demo using logging.Logger."""
    print("\n" + "="*60)
    print("DEMO 2: Logging mode (using logging.Logger)")
    print("="*60 + "\n")

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )

    # Enable logging mode
    service = UIService(
        service_id="logging-demo-logger",
        user_id="demo-user",
        on_response=handle_response,
        use_logging=True  # Enable logging mode
        # logger='CustomLogger'  # Optional: specify custom logger name
    )

    await service.connect()
    await service.register_session()

    # Start receiving in the background
    receive_task = asyncio.create_task(service.start_receiving())

    # Send a test message
    await service.send_message({'word': 'World'})
    await asyncio.sleep(2)

    await service.close()
    await receive_task


async def demo_with_custom_logger():
    """Demo using a custom logger instance."""
    print("\n" + "="*60)
    print("DEMO 3: Custom logger instance")
    print("="*60 + "\n")

    # Create a custom logger with specific configuration
    custom_logger = logging.getLogger('MyAppLogger')
    custom_logger.setLevel(logging.DEBUG)

    # Add custom handler with specific format
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(
        '🔵 [%(asctime)s] %(name)s | %(levelname)s | %(message)s',
        datefmt='%H:%M:%S'
    ))
    custom_logger.addHandler(handler)

    # Pass custom logger instance
    service = UIService(
        service_id="logging-demo-custom",
        user_id="demo-user",
        on_response=handle_response,
        logger=custom_logger,  # Pass custom logger instance
        use_logging=True
    )

    await service.connect()
    await service.register_session()

    # Start receiving in the background
    receive_task = asyncio.create_task(service.start_receiving())

    # Send a test message
    await service.send_message({'word': 'Python'})
    await asyncio.sleep(2)

    await service.close()
    await receive_task


async def main():
    print("\nLogging Feature Demo")
    print("====================")
    print("\nThis demo shows three ways to configure logging:\n")
    print("1. Default mode - uses print() for simple console output")
    print("2. Logging mode - uses logging.Logger with basicConfig")
    print("3. Custom logger - uses a custom logger instance with specific formatting")
    print("\nNote: Make sure word_length_service.py is running in another terminal!\n")

    try:
        # Run the three demos sequentially
        await demo_with_print()
        await demo_with_logging()
        await demo_with_custom_logger()

        print("\n" + "="*60)
        print("All demos completed!")
        print("="*60 + "\n")

    except KeyboardInterrupt:
        print("\nShutting down...")


if __name__ == "__main__":
    asyncio.run(main())
