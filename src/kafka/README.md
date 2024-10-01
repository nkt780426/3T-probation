# Kiểm tra các connector plugin đã cài đặt
curl localhost:8083/connector-plugins | jq

# Cấu hình debezium
0. Kịch bản
```sh
version: '3'
services:
  zookeeper:
    image: confluentinc/cp-zookeeper:latest
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000

  kafka:
    image: confluentinc/cp-kafka:latest
    depends_on:
      - zookeeper
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
    ports:
      - 9092:9092

  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: rootpassword
      MYSQL_USER: debeziumuser
      MYSQL_PASSWORD: dbz
      MYSQL_DATABASE: inventory
    ports:
      - 3306:3306
    command: --default-authentication-plugin=mysql_native_password --gtid-mode=ON --enforce-gtid-consistency=ON --binlog-format=ROW --log-bin=/var/lib/mysql/mysql-bin --server-id=223344

  debezium:
    image: debezium/connect:latest
    ports:
      - 8083:8083
    environment:
      BOOTSTRAP_SERVERS: kafka:9092
      GROUP_ID: 1
      CONFIG_STORAGE_TOPIC: debezium_connect_config
      OFFSET_STORAGE_TOPIC: debezium_connect_offsets
      STATUS_STORAGE_TOPIC: debezium_connect_status
      KEY_CONVERTER_SCHEMAS_ENABLE: false
      VALUE_CONVERTER_SCHEMAS_ENABLE: false
      VALUE_CONVERTER: org.apache.kafka.connect.json.JsonConverter
      KEY_CONVERTER: org.apache.kafka.connect.json.JsonConverter
    depends_on:
      - kafka
      - mysql
```
1. Capture toàn bộ dữ liệu
```sh
curl -i -X POST -H "Accept:application/json" \
  -H "Content-Type:application/json" http://localhost:8083/connectors/ \
  -d '{
    "name": "inventory-connector",
    "config": {
        "connector.class": "io.debezium.connector.mysql.MySqlConnector",
        "tasks.max": "1",
        "database.hostname": "mysql",
        "database.port": "3306",
        "database.user": "debeziumuser",
        "database.password": "dbz",
        "database.server.id": "223344",
        "database.server.name": "dbserver1",
        "database.whitelist": "inventory",         # Để capture toàn bộ database
        "database.history.kafka.bootstrap.servers": "kafka:9092",
        "database.history.kafka.topic": "schema-changes.inventory"
    }
}'
```
2. Capture 1 số table. Có thêm trường table.whilelist
```sh
curl -i -X POST -H "Accept:application/json" \
  -H "Content-Type:application/json" http://localhost:8083/connectors/ \
  -d '{
    "name": "inventory-connector",
    "config": {
        "connector.class": "io.debezium.connector.mysql.MySqlConnector",
        "tasks.max": "1",
        "database.hostname": "mysql",
        "database.port": "3306",
        "database.user": "debeziumuser",
        "database.password": "dbz",
        "database.server.id": "223344",
        "database.server.name": "dbserver1",
        "database.whitelist": "inventory",
        "table.whitelist": "inventory.customers,inventory.orders",  # Chỉ capture bảng customers và orders
        "database.history.kafka.bootstrap.servers": "kafka:9092",
        "database.history.kafka.topic": "schema-changes.inventory"
    }
}'
```

# Debezium connector for mysql

Mỗi chữ connector dưới đây chỉ kafka connector thuộc dạng debezium cho mysql.

## 0. Introduce

Debezium có 1 binary log (binlog) log lại toàn bộ các thay đổi trong cơ sở dữ liệu được commit lên database như các thao tác insert, update, delete, thay đổi schema, ... và mysql dùng nó để nhân bản hay recovery nếu có lỗi xảy ra.
Debezium Mysql connector đọc binlog và produce change events ở các mức thấp hơn (INSERT, UPDATE, DELETE) và emit changes lên kafka topics.
Bằng cách này ta có thể việc CDC ít ảnh hưởng đến hiệu suất làm việc của mysql, để nó có thể chuyên tâm phục vụ các app.

Nguồn tài liêu: vào confluent hub -> Search Debezium mysql -> Tìm đến nơi chứa doc
https://debezium.io/documentation/reference/2.7/connectors/mysql.html#supported-mysql-topologies

Debezium còn hoạt động với nhiều source khác nhau như mariadb, mongodb, postgresql, oracle, sql server, db2, cassandra, ...

## 1. How the connector works

### 1.1. Supported MySQL topologies

Có rất nhiều kiểu deloy mysql và debezium hỗ trợ tất cả.

### 1.2. Schema history topic

Khi database client query database, client sẽ follow schema hiện tại của database. Tuy nhiên schema của database có thể thay đổi theo thời gian. Điều này đồng nghĩa connector phải có khả năng xác định schema của table mỗi khi CDC. Ngoài ra các consumer không thể apply schema hiện tại của connector để sử lý message cũ => Schema Registry trong Kafka confluent.

Trong binlog của mysql, không chỉ có mỗi row-change được ghi log mà còn có cả các câu lệnh DDL đã được table apply. Mỗi khi connector đọc đến đây, nó sẽ thực hiện điều chỉnh table schema trong cache của nó để apply cho các binlog tiếp theo.

Schema History Topic: ghi lại các câu lệnh DDL và vị trí của nó trong binlog.

Khi có sự cố xảy ra, connector phải stop và restart lại => Table schema trong cache không còn, connector sẽ đọc binlog tại vị trí bất kỳ (thường là vị trí cuối cùng mà nó capture). Connector dựa vào shcema history topic để tạo thành schema table dựa vào các câu lệnh DDL và vị trí cuả chúng sao cho khớp với vị trí hiện tại.

Hiển nhiên topic này chỉ nên dùng bởi connector.

When the MySQL connector captures changes in a table to which a schema change tool such as gh-ost or pt-online-schema-change is applied, there are helper tables created during the migration process. You must configure the connector to capture changes that occur in these helper tables. If consumers do not need the records the connector generates for helper tables, configure a single message transform (SMT) to remove these records from the messages that the connector emits.

<!-- Không có gì đảm bảo schema của table luôn không thay đổi theo thời gian. Điều này đồng nghiã với connector phải có khả năng xác định schema id và version tại mỗi thao tác insert/update/delete capture được. Các message trong topic của connector thu thập được không nhất thiết phải có schema giống nhau mà có thể thay đổi theo version. Binlog của mysql không chỉ có row-level changes mà còn log cả các DDL statements được database apply.

Để nó thể chắc chắn connector xử lý schema chính xác trước khi producer message trên kafka, mỗi khi gặp phải câu lệnh DDL trong binlog sẽ thực hiện phân tích câu lệnh và update lại schema vào cache. Connector sử dụng schema trong cache với mỗi thao tác CDC thu thập tiếp theo. Ngoài topic lưu trữ cần có 1 topic khác gọi là schema history topic để lưu lại các câu lệnh DDL và vị trí mà connector đã thu thập được trong binlog.

Mỗi khi có sự cố xảy ra, connector phải shutdown và restart lại và được yêu cầu đọc binlog lại từ 1 vị trí bất kỳ (không nhất thiết phải là cuối cùng) nó sẽ thực hiện rebuild lại schema của table tại thời điểm đó dựa vào topic schema history topic.

Schema history topic này chỉ cho phép connector sử dụng và connector có thể emit đó đến các consumer phục vụ cho tiêu thụ message.

When the MySQL connector captures changes in a table to which a schema change tool such as gh-ost or pt-online-schema-change is applied, there are helper tables created during the migration process. You must configure the connector to capture changes that occur in these helper tables. If consumers do not need the records the connector generates for helper tables, configure a single message transform (SMT) to remove these records from the messages that the connector emits. -->

### 1.3. Schema change topic

Hoàn toàn có thể config connector để nó produce schema change lên 1 topic khác, thường tên topic sẽ là <topic prefix>.prefix

Mỗi message sẽ có dạng như ![hình](../../doc/schema%20change.png)

## 2. Data change events

Do kafka lưu dữ liệu theo kiểu key-value nên 1 trường trong table CDC sẽ được chọn làm key trong kafka (thường là private key luôn) => Nếu 1 record thay đổi thì các message thay đổi ghi được trong kafka có cùng key-event.

Các mục *Change event keys, Change event values* mô tả message và connector gen ra. Trong đó Change event key đại diện cho việc thay đổi key của tables và change event values đại diện cho thay đổi gía trị của trường dữ liệu
- Change event keys: change key of record. Do key của record được lấy làm key của message trong kafkfa.
- Change event values: 

Connector này sẽ đọc binlog và convert nó thành các event (json) như các phần trong doc. Sau đó sẽ đi qua transform và được converter. Do đó cái chuỗi json không phải thứ sẽ lưu vào kafka topic mà phải vào kafka topic mà đọc.

Do đó không cần quan tâm nhiều về debezium mà cứ dựng lên đi mà nhìn message đỡ mất thời gian.

## 3. Data type mappings

## 4. Custom converters

## 5. Setting up mysql

## 6. Deployment

## 7. Mornitoring