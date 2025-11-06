Yes! The system service **can** already send messages to the UI services on its own - the infrastructure is already in place. The UI services are simply listening to their respective streams (`system-to-ui1`, `system-to-ui2`) and will process whatever messages arrive, regardless of whether they're responses to requests or unsolicited messages.

However, the current code only sends messages as **responses** to incoming requests. To enable the system service to send unsolicited messages, you'd just need to add some logic to write to those streams independently.

**Current Architecture:**
- UI services listen on `system-to-ui1` and `system-to-ui2` (line 18 in ui_service_1.py)
- They read messages using `xread` and process the `word` and `length` fields (lines 80-82)
- They don't care *why* the message was sent - they just display it

**To enable unsolicited messages**, you'd just need to add a new async task in the system service. For example:

```python
async def send_periodic_notifications(self):
    """Send periodic notifications to UI services."""
    while True:
        await asyncio.sleep(20)  # Every 20 seconds

        # Send notification to ui1
        notification = {
            'word': 'SYSTEM_ALERT',
            'length': 999,
            'processed_at': datetime.now().isoformat()
        }
        await self.redis_client.xadd('system-to-ui1', notification)
        print(f"Sent notification to ui1")
```

Then update the `run()` method to include this task:
```python
await asyncio.gather(
    self.process_messages(),
    self.send_periodic_notifications()
)
```

**Would you like me to:**
1. Add this capability to your system service so it can send unsolicited messages?
2. Create a demo that shows the system service broadcasting alerts to all UI services?
3. Add different message types (responses vs notifications) so UI services can handle them differently?
