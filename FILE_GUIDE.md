# File Guide

Quick reference for what each file does and whether you need it.

## Core Library Files (Required)

These 3 files are the essential library you need for your application:

| File | Purpose | Lines |
|------|---------|-------|
| **stream_service.py** | Base class for all services - Redis operations | ~225 |
| **ui_service.py** | UI client service - connect, send, receive | ~165 |
| **system_service.py** | System service base class - process messages | ~204 |

**Total: ~594 lines** - This is all you need to copy for a new project!

## Demo Implementation

Example of how to use the library:

| File | Purpose |
|------|---------|
| **word_length_service.py** | Demo system service (calculates word length) |

## Demo Applications

Example applications showing different usage patterns:

| File | Purpose |
|------|---------|
| **demo_names.py** | Basic usage - sends names periodically |
| **demo_fruits.py** | Basic usage - sends fruits periodically |
| **demo_multi_device.py** | Multi-device sync - same user on multiple services |
| **demo_custom_usage.py** | Custom callbacks - advanced integration example |
| **demo_logging.py** | Logging demo - shows print vs logging.Logger |
| **test_horizontal_scaling.py** | Scaling demo - 3 workers load balancing |

## Utilities

| File | Purpose |
|------|---------|
| **check_redis.py** | Debug tool - inspect Redis state |

## Documentation

| File | Purpose | For |
|------|---------|-----|
| **README.md** | Start here - overview and quick start | Everyone |
| **ARCHITECTURE.md** | System design and file organization | Developers |
| **DEMO_GUIDE.md** | How to run the demos | New users |
| **HORIZONTAL_SCALING.md** | Deploy multiple workers for scaling | Production |
| **LOGGING_GUIDE.md** | Configure logging (print vs logger) | Production |
| **TROUBLESHOOTING.md** | Fix common problems | When stuck |

## What to Copy for a New Project

### Minimum (Client Only)
```bash
cp stream_service.py your_project/
cp ui_service.py your_project/
```

### Full System (Client + Server)
```bash
cp stream_service.py your_project/
cp ui_service.py your_project/
cp system_service.py your_project/
# Then create your_custom_service.py extending SystemService
```

### Optional Reference
```bash
cp HORIZONTAL_SCALING.md your_project/  # If you need scaling
cp LOGGING_GUIDE.md your_project/       # If you need logging
cp TROUBLESHOOTING.md your_project/     # Common issues
```

## File Sizes

```
Core Library:
  stream_service.py       7.0K
  ui_service.py          7.8K
  system_service.py      8.0K
  ─────────────────────────────
  Total                 22.8K  ← Copy these!

Demos:                  ~15K
Documentation:          39K
```

## Quick Decision Tree

**I want to...**

→ **Build a client app that connects to a system**
  - Copy: `stream_service.py`, `ui_service.py`
  - See: `demo_custom_usage.py` for example

→ **Build both client and server**
  - Copy: `stream_service.py`, `ui_service.py`, `system_service.py`
  - See: `word_length_service.py` for server example
  - See: `demo_names.py` for client example

→ **Scale horizontally (multiple workers)**
  - Read: `HORIZONTAL_SCALING.md`
  - Test: `test_horizontal_scaling.py`

→ **Use proper logging instead of print**
  - Read: `LOGGING_GUIDE.md`
  - Test: `demo_logging.py`

→ **Something broke**
  - Read: `TROUBLESHOOTING.md`
  - Use: `check_redis.py` to inspect state

→ **Understand the architecture**
  - Read: `ARCHITECTURE.md`
  - Read: `README.md`
