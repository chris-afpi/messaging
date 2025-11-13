#!/usr/bin/env python3
"""
UI Service 1 - Legacy compatibility wrapper.

For backward compatibility, this re-exports the UIService class.
For new projects, import directly from ui_service.py instead.

Example:
    from ui_service_1 import UIService1
    # is equivalent to:
    from ui_service import UIService as UIService1
"""
from ui_service import UIService

# Backward compatibility alias
UIService1 = UIService

__all__ = ['UIService1']
