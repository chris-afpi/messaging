# Logging Guide

All services in this messaging system support configurable logging, making it easy to switch between simple print statements and proper logging infrastructure.

## Overview

By default, all services use `print()` for console output with timestamps. For production use, you can enable `logging.Logger` support.

## Usage

### Default Mode (Print)

By default, services use print statements with timestamps:

```python
from ui_service import UIService

service = UIService("ui1", "alice")
# Uses print() by default
```

Output:
```
[12:34:56] [UIService] Connected to Redis at redis://localhost
[12:34:56] [UIService] [ui1] Ready to communicate
```

### Logging Mode (logging.Logger)

Enable logging by setting `use_logging=True`:

```python
import logging
from ui_service import UIService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

service = UIService(
    service_id="ui1",
    user_id="alice",
    use_logging=True  # Enable logging
)
```

Output:
```
12:34:56 - UIService - INFO - Connected to Redis at redis://localhost
12:34:56 - UIService - INFO - [ui1] Ready to communicate
```

### Custom Logger Instance

You can pass a custom logger instance for more control:

```python
import logging
from ui_service import UIService

# Create custom logger
custom_logger = logging.getLogger('MyApp')
custom_logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter(
    '[%(levelname)s] %(name)s: %(message)s'
))
custom_logger.addHandler(handler)

service = UIService(
    service_id="ui1",
    user_id="alice",
    logger=custom_logger,  # Pass custom logger
    use_logging=True
)
```

### Custom Logger Name

You can specify a logger name as a string:

```python
service = UIService(
    service_id="ui1",
    user_id="alice",
    logger='MyCustomLogger',  # Logger name
    use_logging=True
)
```

If no logger name is provided, it defaults to the class name (e.g., "UIService", "SystemService").

## Available Log Levels

When using logging mode, you can use different log levels:

```python
# In custom service implementation
self.log_debug("Detailed debug information")
self.log_info("General information")
self.log_warning("Warning message")
self.log_error("Error message")
self.log_critical("Critical error")

# Or use the generic log() method
self.log("Custom message", level='info')
```

## Logging in Custom Services

All services that inherit from `StreamService` automatically support logging:

```python
from system_service import SystemService

class MyCustomService(SystemService):
    async def process_data(self, message_data):
        # Use logging methods
        self.log_info("Processing message")
        self.log_debug(f"Data: {message_data}")

        try:
            result = self.do_processing(message_data)
            return result
        except Exception as e:
            self.log_error(f"Processing failed: {e}")
            raise
```

## Running the Demo

See `demo_logging.py` for a complete example showing all three modes:

```bash
# Terminal 1: Start the system service
python word_length_service.py

# Terminal 2: Run the logging demo
python demo_logging.py
```

The demo will show output in all three modes:
1. Default print mode
2. Logging mode with basicConfig
3. Custom logger with custom formatting

## Production Recommendations

For production deployments:

1. **Enable logging mode**: Set `use_logging=True`
2. **Configure proper logging**: Use logging configuration files or dictConfig
3. **Set appropriate levels**: Use INFO for normal operation, DEBUG for troubleshooting
4. **Add log rotation**: Configure rotating file handlers to manage log size
5. **Structure your logs**: Use structured logging (JSON) for better parsing

Example production configuration:

```python
import logging
import logging.config

# Configure logging from a config file
logging.config.fileConfig('logging.conf')

# Or use dictConfig
LOGGING_CONFIG = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'detailed',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'app.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'formatter': 'detailed',
        }
    },
    'formatters': {
        'detailed': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['console', 'file']
    }
}

logging.config.dictConfig(LOGGING_CONFIG)

# Now create services with logging enabled
service = UIService("ui1", "alice", use_logging=True)
```

## Benefits

- **Development**: Use default print mode for simple console output
- **Testing**: Enable logging with timestamps and levels for better debugging
- **Production**: Use proper logging infrastructure with rotation, filtering, and remote logging
- **Flexibility**: Switch between modes without changing code throughout your services
