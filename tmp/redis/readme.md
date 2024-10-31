1. Các giá trị liên quan đến kafka mà mọi consumer/producer phải có
    "connector.class"
    "tasks.max"
    "topics"
    "key.converter": "io.confluent.connect.avro.AvroConverter",
    "value.converter": "io.confluent.connect.avro.AvroConverter",
    "key.converter.schema.registry.url": "http://schema-registry-1:8081", 
    "value.converter.schema.registry.url": "http://schema-registry-1:8081"
2. Địa chỉ/user+pass của database
    "redis.host"
    "redis.port"
3. Type của value trong redis
    "redis.value.type": "json"
4. Key trong redis
    "redis.key.prefix": "probation", => Thêm tiền tố 'probation' làm key đầu tiên khi lưu vào redis
    "redis.key.field": "account:counter", => Chỉ định key sau tiền tố, counter trong redis là từ khóa đặc biệt chỉ việc nó sẽ thay bằng interger tăng dần theo thời gian.
    "redis.hash.key.field": "", => Trường này chỉ định một trường trong giá trị của message Kafka mà bạn muốn sử dụng để tạo ra một hash key trong Redis. Thông thường, nếu bạn sử dụng Redis như một database key-value đơn giản, bạn không cần phải sử dụng hash. Tuy nhiên, nếu bạn muốn lưu dữ liệu dưới dạng hash trong Redis, bạn có thể chỉ định trường này.

https://docs.confluent.io/kafka-connectors/redis/current/connector_config.html#redis-sink-connector-config

# Không có plugin nào có thể chạy với avro format.
Nguồn: https://redis.io/docs/latest/operate/redisinsight/