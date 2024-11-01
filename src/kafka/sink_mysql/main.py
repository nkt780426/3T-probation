from confluent_kafka import DeserializingConsumer, KafkaError, KafkaException
from confluent_kafka.schema_registry.avro import AvroDeserializer
from confluent_kafka.schema_registry import SchemaRegistryClient
from services.DebeziumMessageProcess import DebeziumMessageProcess
import mysql.connector

# Tạo Schema Registry Client để lấy schema của topic
schema_registry_conf = {'url': 'http://localhost:8081'}
schema_registry_client = SchemaRegistryClient(schema_registry_conf)

# Tạo đối tượng AvroDeserializer cho cả key và value
key_avro_deserializer = AvroDeserializer(schema_registry_client)
value_avro_deserializer = AvroDeserializer(schema_registry_client)

# Cấu hình consumer
consumer_conf = {
    'bootstrap.servers': 'localhost:9091',
    'group.id': 'mysql-sink-v01',
    'key.deserializer': key_avro_deserializer,
    'value.deserializer': value_avro_deserializer,
    'auto.offset.reset': 'earliest'  # Đọc từ đầu nếu không có offset
}

# Tạo đối tượng kafka consumer để đọc dữ liệu từ 4 topic
consumer = DeserializingConsumer(consumer_conf)
consumer.subscribe(['probation.raw.accounts', 'probation.raw.products', 'probation.raw.sales_teams', 'probation.raw.sales_pipeline'])

mysql_config = {
    'host': 'localhost',
    'port': 3308,
    'user': 'vohoang',
    'password': '12345678',
    'database': 'report'
}

mysql_connection = mysql.connector.connect(**mysql_config)

# Lưu trữ các instance của DebeziumMessageProcess theo topic
topic_handlers = {}

def handle_kafka_message(topic, message_key, message_value):
    if topic not in topic_handlers:
        topic_handlers[topic] = DebeziumMessageProcess(mysql_connection, message_value)
    
    topic_handlers[topic].process_message(message_key, message_value)

# Vòng lặp chính để nhận và xử lý message
try:
    while True:
        msg = consumer.poll(1.0)  # Chờ nhận message trong 1 giây

        if msg is None:
            continue
        
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                # Kafka EOF: không có message mới
                continue
            else:
                print(f"Kafka error: {msg.error()}")
                raise KafkaException(msg.error())

        # Deserialize key và value
        message_key = msg.key()
        message_value = msg.value()

        # Lấy topic từ message
        topic = msg.topic()

        # Xử lý message
        handle_kafka_message(topic, message_key, message_value)

except KeyboardInterrupt:
    print("Đã dừng consumer.")

finally:
    consumer.close()
    mysql_connection.close()