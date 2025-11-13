# Generic Refactoring - Removing Demo Logic from Libraries

## Summary

All demo-specific logic has been removed from reusable classes. The libraries are now truly generic and can be used for any message processing application.

---

## Changes Made

### 1. UIService - Generic Message Sending

**Before (demo-specific):**
```python
async def send_message(self, word: str):  # ← Assumes "word"!
    message = {'word': word, ...}
```

**After (generic):**
```python
async def send_message(self, data: Dict[str, Any]):  # ← Any data!
    message = {**data, ...}  # Merge user data
```

**Usage in demos:**
```python
# Old way
await service.send_message("hello")

# New way
await service.send_message({'word': 'hello'})
# Or any other data format:
await service.send_message({'temperature': 72, 'unit': 'F'})
await service.send_message({'calculation': 'sum', 'values': [1, 2, 3]})
```

### 2. UIService - Generic Response Processing

**Before (demo-specific):**
```python
async def process_message(self, message_id, message_data):
    word = message_data.get('word')     # ← Expects 'word'!
    length = message_data.get('length') # ← Expects 'length'!
    response_data = {'word': word, 'length': length, ...}
```

**After (generic):**
```python
async def process_message(self, message_id, message_data):
    response_data = {**message_data, ...}  # ← Pass through all data!
```

Now works with ANY response format - temperature, calculations, images, etc.

### 3. SystemService - Business Logic Extracted

**Before (demo logic baked in):**
```python
class SystemService:
    async def process_message(self, ...):
        word = message_data.get('word')  # ← Demo-specific!
        word_length = len(word)          # ← Word-length logic!
        response = {'word': word, 'length': word_length}
```

**After (generic base + demo subclass):**

**system_service.py (generic base):**
```python
class SystemService:
    async def process_message(self, ...):
        # Generic routing, broadcasting, session tracking
        response_data = await self.process_data(message_data)  # ← Pluggable!
        # Broadcast response...

    async def process_data(self, message_data) -> Dict[str, Any]:
        raise NotImplementedError("Subclasses implement business logic")
```

**word_length_service.py (demo implementation):**
```python
class WordLengthService(SystemService):
    async def process_data(self, message_data) -> Dict[str, Any]:
        word = message_data['word']
        return {'word': word, 'length': len(word)}
```

---

## File Structure

### Reusable Libraries (No Demo Logic)

```
stream_service.py       - Base class for all services
├── ui_service.py       - Generic UI client
└── system_service.py   - Generic message processor (base)
```

### Demo Implementation

```
word_length_service.py  - Word-length calculator (extends SystemService)
```

### Demo Applications

```
demo_names.py
demo_fruits.py
demo_multi_device.py
demo_custom_usage.py
```

---

## Running the Demos

**OLD way (broken):**
```bash
python system_service.py  # ← Now shows error message
```

**NEW way:**
```bash
# Terminal 1: Use the demo implementation
python word_length_service.py

# Terminal 2-3: Demos work as before
python demo_names.py
python demo_fruits.py
```

---

## Creating Your Own Service

### Example: Temperature Converter Service

**temperature_service.py:**
```python
from system_service import SystemService

class TemperatureService(SystemService):
    async def process_data(self, message_data):
        celsius = message_data['celsius']
        fahrenheit = (celsius * 9/5) + 32
        return {
            'celsius': celsius,
            'fahrenheit': fahrenheit
        }

if __name__ == "__main__":
    import asyncio
    service = TemperatureService()
    asyncio.run(service.run())
```

**temperature_client.py:**
```python
from ui_service import UIService

service = UIService('temp-ui', 'user123')
await service.connect()
await service.register_session()

# Send temperature for conversion
await service.send_message({'celsius': 25})

# Response: {'celsius': 25, 'fahrenheit': 77, ...}
```

### Example: Calculator Service

**calculator_service.py:**
```python
from system_service import SystemService

class CalculatorService(SystemService):
    async def process_data(self, message_data):
        op = message_data['operation']
        values = message_data['values']

        if op == 'sum':
            result = sum(values)
        elif op == 'product':
            result = 1
            for v in values:
                result *= v
        else:
            raise ValueError(f"Unknown operation: {op}")

        return {
            'operation': op,
            'values': values,
            'result': result
        }
```

**Usage:**
```python
await service.send_message({
    'operation': 'sum',
    'values': [1, 2, 3, 4, 5]
})
# Response: {'operation': 'sum', 'values': [1,2,3,4,5], 'result': 15}
```

---

## Benefits

### Before (Demo Logic in Libraries)

❌ UIService only works for word-length calculator
❌ SystemService hardcodes word-length calculation
❌ Can't use for temperature, calculations, images, etc.
❌ Business logic mixed with infrastructure

### After (Generic Libraries)

✅ UIService works with ANY data format
✅ SystemService is a reusable base class
✅ Create your own service by implementing one method
✅ Clear separation: infrastructure vs business logic
✅ Can build temperature, calculator, image processing, etc.

---

## Migration Guide

### For Demos

**Old code:**
```python
await service.send_message("hello")
```

**New code:**
```python
await service.send_message({'word': 'hello'})
```

### For System Service

**Old way:**
```bash
python system_service.py  # Ran word-length service
```

**New way:**
```bash
python word_length_service.py  # Explicit demo implementation
```

---

## Key Takeaway

**Before:** Libraries were disguised demos
**After:** Libraries are truly generic, demos are separate

Now you can build:
- Temperature converter
- Calculator
- Image processor
- Data validator
- Any message-based service!

Just extend SystemService and implement `process_data()`.
