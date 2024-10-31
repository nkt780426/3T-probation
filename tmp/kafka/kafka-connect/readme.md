# Bài 10: (Hands On) Run a Self-Managed Connector in Docker

Đọc file docker-compose cụm kafka connect tại [đây](https://github.com/confluentinc/learn-kafka-courses/blob/main/kafka-connect-101/self-managed-connect.yml) và hướng dẫn hiểu file từ mục "[Running a Self-Managed Connector with Confluent Cloud exercise steps"](https://developer.confluent.io/courses/kafka-connect/self-managed-connect-hands-on/) trở đi.

Mục tiêu: Bài này thực hiện CDC bằng debezium-mysql connector từ Mysql DB vào kafka cluster. Sau đó sử dụng elasticsearch và neo4j sink connector để đẩy dữ liệu từ kafka topic vào các sink này.

Ý nghĩa các config:

1. Mỗi kafka connect worker khai báo cụm kafka mà nó sẽ giao tiếp và group id của cluster mà nó thuộc về.

    ![Kafka Broker Env](images/10.%20Kafka%20Broker%20Env.png)

    Các kafka connect cùng 1 group id sẽ cùng 1 cluster và ở chế độ distributed mode.
    Tên các topic mặc định mà kafka connect cluster dùng để giao tiếp nội bộ với nhau.

2. Cấu hình key-value converter mà worker này sẽ sử dụng

    ![Converter Env](images/10.%20Converter%20Env.png)

3. Load các connector plugins

    ![Connector Plugin](images/10.%20Connector%20Plugin.png)

4. Chạy lệnh sau để chắc chắn cụm kafka connect đã sẵn sàng. 8083 là cổng của worker 1, do đó khi tương tác với cụm kafka connect, ta chỉ cần quan tâm 1 worker.

    ```sh
    bash -c ' \
    echo -e "\n\n=============\nWaiting for Kafka Connect to start listening on localhost ⏳\n=============\n"
    while [ $(curl -s -o /dev/null -w %{http_code} http://localhost:8083/connectors) -ne 200 ] ; do
    echo -e "\t" $(date) " Kafka Connect listener HTTP state: " $(curl -s -o /dev/null -w %{http_code} http://localhost:8083/connectors) " (waiting for 200)"
    sleep 15
    done
    echo -e $(date) "\n\n--------------\n\o/ Kafka Connect is ready! Listener HTTP state: " $(curl -s -o /dev/null -w %{http_code} http://localhost:8083/connectors) "\n--------------\n"
    '
    ```

5. Xác nhận các connector plugin đã cài đặt có những plugin cần thiết

    ```sh
    curl -s localhost:8083/connector-plugins | jq '.[].class'|egrep 'Neo4jSinkConnector|MySqlConnector|ElasticsearchSinkConnector'
    # Đầu ra mong đợi sẽ như sau
    "io.confluent.connect.elasticsearch.ElasticsearchSinkConnector"
    "io.debezium.connector.mysql.MySqlConnector"
    "streams.kafka.connect.sink.Neo4jSinkConnector"
    ```

6. Run source connector instance là Stream CDC mysql đến kafka topic

    ```sh
    curl -i -X PUT -H  "Content-Type:application/json" \
        http://localhost:8083/connectors/source-debezium-orders-01/config \
        -d '{
                "connector.class": "io.debezium.connector.mysql.MySqlConnector",
                "value.converter": "io.confluent.connect.json.JsonSchemaConverter",
                "value.converter.schemas.enable": "true",
                "value.converter.schema.registry.url": "'$SCHEMA_REGISTRY_URL'",
                "value.converter.basic.auth.credentials.source": "'$BASIC_AUTH_CREDENTIALS_SOURCE'",
                "value.converter.basic.auth.user.info": "'$SCHEMA_REGISTRY_BASIC_AUTH_USER_INFO'",
                "database.hostname": "mysql",
                "database.port": "3306",
                "database.user": "kc101user",
                "database.password": "kc101pw",
                "database.server.id": "42",
                "database.server.name": "asgard",
                "table.whitelist": "demo.orders",
                "database.history.kafka.bootstrap.servers": "'$BOOTSTRAP_SERVERS'",
                "database.history.consumer.security.protocol": "SASL_SSL",
                "database.history.consumer.sasl.mechanism": "PLAIN",
                "database.history.consumer.sasl.jaas.config": "org.apache.kafka.common.security.plain.PlainLoginModule required username=\"'$CLOUD_KEY'\" password=\"'$CLOUD_SECRET'\";",
                "database.history.producer.security.protocol": "SASL_SSL",
                "database.history.producer.sasl.mechanism": "PLAIN",
                "database.history.producer.sasl.jaas.config": "org.apache.kafka.common.security.plain.PlainLoginModule required username=\"'$CLOUD_KEY'\" password=\"'$CLOUD_SECRET'\";",
                "database.history.kafka.topic": "dbhistory.demo",
                "topic.creation.default.replication.factor": "3",
                "topic.creation.default.partitions": "3",
                "decimal.handling.mode": "double",
                "include.schema.changes": "true",
                "transforms": "unwrap,addTopicPrefix",
                "transforms.unwrap.type": "io.debezium.transforms.ExtractNewRecordState",
                "transforms.addTopicPrefix.type":"org.apache.kafka.connect.transforms.RegexRouter",
                "transforms.addTopicPrefix.regex":"(.*)",
                "transforms.addTopicPrefix.replacement":"mysql-debezium-$1"
        }'
    ```

    Để kiểm tra connector instance vừa tạo chạy lệnh
    ```sh
    curl -s "http://localhost:8083/connectors?expand=info&expand=status" | \
        jq '. | to_entries[] | [ .value.info.type, .key, .value.status.connector.state,.value.status.tasks[].state,.value.info.config."connector.class"]|join(":|:")' | \
        column -s : -t| sed 's/\"//g'| sort
    # Đầu ra mong đợi sẽ như sau
    source  |  source-debezium-orders-01  |  RUNNING  |  RUNNING  |  io.debezium.connector.mysql.MySqlConnector
    ```

7. Stream data từ kafka topic đến elasticsearch
    ```sh
    curl -i -X PUT -H  "Content-Type:application/json" \
        http://localhost:8083/connectors/sink-elastic-orders-01/config \
        -d '{
                "connector.class": "io.confluent.connect.elasticsearch.ElasticsearchSinkConnector",
                "value.converter": "io.confluent.connect.json.JsonSchemaConverter",
                "value.converter.schemas.enable": "true",
                "value.converter.schema.registry.url": "'$SCHEMA_REGISTRY_URL'",
                "value.converter.basic.auth.credentials.source": "'$BASIC_AUTH_CREDENTIALS_SOURCE'",
                "value.converter.basic.auth.user.info": "'$SCHEMA_REGISTRY_BASIC_AUTH_USER_INFO'",
                "topics": "mysql-debezium-asgard.demo.ORDERS",
                "connection.url": "http://elasticsearch:9200",
                "key.ignore": "true",
                "schema.ignore": "true",
                "tasks.max": "2"
        }'
    ```
    Kiếm tra connector instance vừa chạy
    ```sh
    curl -s "http://localhost:8083/connectors?expand=info&expand=status" | \
        jq '. | to_entries[] | [ .value.info.type, .key, .value.status.connector.state,.value.status.tasks[].state,.value.info.config."connector.class"]|join(":|:")' | \
        column -s : -t| sed 's/\"//g'| sort | grep ElasticsearchSinkConnector
    # Đầu ra mong đợi
    source  |  source-debezium-orders-01  |  RUNNING  |  RUNNING  | RUNNING  |  io.confluent.connect.elasticsearch.ElasticsearchSinkConnector
    ```

8. Stream data từ kafka topic đến Neo4j (tương tự)
    ```sh
    curl -i -X PUT -H  "Content-Type:application/json" \
        http://localhost:8083/connectors/sink-neo4j-orders-01/config \
        -d '{
                "connector.class": "streams.kafka.connect.sink.Neo4jSinkConnector",
            "value.converter": "io.confluent.connect.json.JsonSchemaConverter",
                "value.converter.schemas.enable": "true",
                "value.converter.schema.registry.url": "'$SCHEMA_REGISTRY_URL'",
                "value.converter.basic.auth.credentials.source": "'$BASIC_AUTH_CREDENTIALS_SOURCE'",
                "value.converter.basic.auth.user.info": "'$SCHEMA_REGISTRY_BASIC_AUTH_USER_INFO'",
                "topics": "mysql-debezium-asgard.demo.ORDERS",
                "tasks.max": "2",
                "neo4j.server.uri": "bolt://neo4j:7687",
                "neo4j.authentication.basic.username": "neo4j",
                "neo4j.authentication.basic.password": "connect",
                "neo4j.topic.cypher.mysql-debezium-asgard.demo.ORDERS": "MERGE (city:city{city: event.delivery_city}) MERGE (customer:customer{id: event.customer_id, delivery_address: event.delivery_address, delivery_city: event.delivery_city, delivery_company: event.delivery_company}) MERGE (vehicle:vehicle{make: event.make, model:event.model}) MERGE (city)<-[:LIVES_IN]-(customer)-[:BOUGHT{order_total_usd:event.order_total_usd,order_id:event.id}]->(vehicle)"
            } '
    ```
    Kiểm  tra connector instance vừa chạy
    ```sh
    curl -s "http://localhost:8083/connectors?expand=info&expand=status" | \
        jq '. | to_entries[] | [ .value.info.type, .key, .value.status.connector.state,.value.status.tasks[].state,.value.info.config."connector.class"]|join(":|:")' | \
        column -s : -t| sed 's/\"//g'| sort | grep Neo4jSinkConnector
    # Đầu ra mong đợi
    source  |  source-debezium-orders-01  |  RUNNING  |  RUNNING  | RUNNING  |  io.confluent.connect.elasticsearch.Neo4jSinkConnector
    ```