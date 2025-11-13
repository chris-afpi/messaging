#!/usr/bin/env python3
"""
UI Service 2 - Legacy compatibility wrapper.

For backward compatibility, this re-exports the UIService class.
For new projects, import directly from ui_service.py instead.

Example:
    from ui_service_2 import UIService2
    # is equivalent to:
    from ui_service import UIService as UIService2
"""
from ui_service import UIService

# Backward compatibility alias
UIService2 = UIService

__all__ = ['UIService2']
