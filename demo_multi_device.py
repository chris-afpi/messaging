#!/usr/bin/env python3
"""
Multi-Device Demo Script

This script runs UI Service 2 with user_id='alice' to demonstrate
multi-device synchronization. Run this alongside ui_service_1.py
to see the same user on two different services staying in sync.

Usage:
    python demo_multi_device.py
"""
import asyncio
from ui_service_2 import UIService2


async def main():
    print("=" * 60)
    print("Multi-Device Sync Demo")
    print("=" * 60)
    print("This is UI Service 2 running as user 'alice'")
    print("Run ui_service_1.py in another terminal to see sync in action!")
    print("=" * 60)
    print()

    # Create UI Service 2 but with user_id='alice' instead of default 'bob'
    service = UIService2(user_id='alice')
    try:
        await service.run()
    except KeyboardInterrupt:
        print('\n[UI2] Shutting down...')
    finally:
        await service.close()


if __name__ == "__main__":
    asyncio.run(main())
