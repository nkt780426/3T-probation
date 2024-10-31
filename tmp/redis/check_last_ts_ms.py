from redis import Redis
import time

# Connect to Redis server
redis_client = Redis(host='localhost', port=6379, db=0)

while True:
    print(redis_client.get('probation:last_ts_ms').decode())
    time.sleep(1)