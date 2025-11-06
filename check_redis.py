#!/usr/bin/env python3
import redis

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

print('Streams in Redis:')
for key in r.keys('*-to-*'):
    print(f'  {key}: {r.xlen(key)} messages')

print('\nSessions:')
for key in r.keys('user:*:sessions'):
    print(f'  {key}: {r.smembers(key)}')

print('\nRecent messages in system-to-ui1:')
messages = r.xrevrange('system-to-ui1', count=3)
for msg_id, msg_data in messages:
    print(f'  {msg_id}: {msg_data}')
