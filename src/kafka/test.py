import logging
from confluent_kafka import KafkaException, KafkaError, Consumer, Producer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer, AvroDeserializer
from collections import deque
import time

#######################################################################################
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

# Cấu hình Schema Registry
schema_registry_conf = {
    'url': 'http://localhost:8081'
}
schema_registry_client = SchemaRegistryClient(schema_registry_conf)

# Hàm lấy schema cho từng topic
def get_schemas(topic):
    key_schema = schema_registry_client.get_latest_schema(f"{topic}-key").schema_str
    value_schema = schema_registry_client.get_latest_schema(f"{topic}-value").schema_str
    key_serializer = AvroSerializer(schema_registry_client, key_schema)
    value_serializer = AvroSerializer(schema_registry_client, value_schema)
    key_deserializer = AvroDeserializer(schema_registry_client, key_schema)
    value_deserializer = AvroDeserializer(schema_registry_client, value_schema)
    return key_serializer, value_serializer, key_deserializer, value_deserializer

# Cấu hình Kafka Producer
producer_conf = {
    'bootstrap.servers': 'localhost:9091'
}
producer = Producer(producer_conf)

# Cấu hình Kafka Consumer
consumer_conf = {
    'bootstrap.servers': 'localhost:9091',
    'group.id': 'super-init',
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': False
}
consumer = Consumer(consumer_conf)

# Đăng ký các topic
topics = ['probation.raw.accounts', 'probation.raw.products', 'probation.raw.sales_teams', 'probation.raw.sales_pipeline']
consumer.subscribe(topics)
#######################################################################################

event_queue = deque()

# Hàm lấy timestamp từ message
def get_event_timestamp(value):
    return value['source']['ts_ms']

# Hàm xử lý sắp xếp queue và gửi message
def process_and_send_events():
    # Sắp xếp queue theo timestamp (tăng dần) và đảm bảo sales_pipeline ở cuối cùng nếu cùng timestamp
    sorted_events = sorted(event_queue, key=lambda x: (x[0], x[2]['source']['table'] == 'sales_pipeline'))

    # Gửi các message theo thứ tự vào topic super-init
    for event in sorted_events:
        _, key, value, topic = event
        key_serializer, value_serializer, _, _ = get_schemas(topic)  # Lấy schema tương ứng
        producer.produce(topic='super-init', key=key_serializer(key, None), value=value_serializer(value, None))
    
    producer.flush()
    logging.info(f"Sending {len(sorted_events)} events to topic 'super-init'")
    event_queue.clear()
    
start_time = time.time()

try:
    while True:
        msg = consumer.poll(1.0)  # Thời gian chờ 1 giây
        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue
            else:
                logging.error(f"Consumer error: {msg.error()}")
                raise KafkaException(msg.error())
        
        # Lấy topic của message hiện tại
        topic = msg.topic()
        
        # Lấy serializers và deserializers tương ứng với topic
        key_serializer, value_serializer, key_deserializer, value_deserializer = get_schemas(topic)
        
        # Deserialize key và value từ Avro
        key = key_deserializer(msg.key(), None)
        value = value_deserializer(msg.value(), None)
    
        # Lấy timestamp từ message
        timestamp = get_event_timestamp(value)
        
        # Thêm message vào queue
        event_queue.append((timestamp, key, value, topic))
        
        # Kiểm tra xem đã 3 giây chưa để xử lý batch
        if time.time() - start_time >= 3:
            process_and_send_events()
            start_time = time.time()
            
except Exception as e:
    logging.error(f"Exception occurred: {e}")
finally:
    consumer.close()
