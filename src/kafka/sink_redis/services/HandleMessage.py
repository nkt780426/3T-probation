import json
from redis import Redis
from redis.exceptions import ResponseError
from services.LogConfig import get_logger
from decimal import Decimal

# Create logger
logger = get_logger('HandleMessage')

# Connect to Redis server
redis_client = Redis(host='localhost', port=6379, db=0)

def handle_kafka_message(topic, message_key, message_value):
    table_name = topic.split('.')[-1]
        
    # Extract ts_ms as part of the Redis key if available
    ts_ms = message_value.get("ts_ms")
    
    redis_key = f"probation:{table_name}:{next(iter(message_key.values()))}:{ts_ms}"

    # Convert message_value to JSON format
    try:
        json_value = json.dumps(message_value, default=lambda x: str(x) if isinstance(x, Decimal) else x)
    except (TypeError, ValueError) as e:
        logger.error(f"Failed to serialize message for topic {topic} with key {message_key}. Error: {e}")
        return
        
    # Store the message in Redis with the constructed key
    try:
        redis_client.set(redis_key, json_value)
        logger.info(f"Successfully inserted message from topic {topic} into Redis.\nKey: {redis_key}\nValue: {json.dumps(message_value, indent=4, default=lambda x: str(x) if isinstance(x, Decimal) else x)}")

        # Update the last ts_ms in Redis if the new ts_ms is greater
        last_ts_ms = redis_client.get('probation:last_ts_ms')
        if last_ts_ms is None or ts_ms > int(last_ts_ms.decode()):
            redis_client.set('probation:last_ts_ms', ts_ms)
            logger.info(f'Updated last_ts_ms to: {ts_ms}')

    except ResponseError as e:
        logger.error(f"Redis error while storing message for topic {topic} with key {redis_key}. Error: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error handling message for topic {topic} with key {redis_key}. Error: {e}")
        raise
