#!/usr/bin/env python3
import redis

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

print('Streams in Redis:')
for key in r.keys('*-to-*'):
    print(f'  {key}: {r.xlen(key)} messages')

print('\nUser → Services Mapping:')
for key in r.keys('user:*:sessions'):
    user_id = key.split(':')[1]
    services = r.smembers(key)
    print(f'  {user_id} is on: {services}')

print('\nService → Users Mapping:')
for key in r.keys('service:*:users'):
    service_id = key.split(':')[1]
    users = r.smembers(key)
    print(f'  {service_id} has users: {users}')

print('\nRecent messages in system-to-ui1:')
messages = r.xrevrange('system-to-ui1', count=3)
for msg_id, msg_data in messages:
    print(f'  {msg_id}: {msg_data}')
