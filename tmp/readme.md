# Airflow vs Celery
## Excutor
Có nhiều loại executor trong airflow. Project chạy với celery executor
1. SequentialExecutor (không bao h dùng)
- Chạy 1 task tại 1 thời điểm
- Thích hợp cho môi trường development và testing, không dùng trong môi trường production
2. LocalExcutor (dùng trong môi trường development)
- Chạy các task đồng thời trong các tiến trình riêng biệt trên cùng 1 máy chủ
- Thích hợp cho môi trường development và môi trường production phải chạy nhiều task nhưng không cần 1 hệ thống phân tán phức tạp
3. CeleryExecutor (dùng trong môi trường production)
- Sử dụng Celery để phân phối và xử lý các task. Celery là một hệ thống phân tán cho phép thực hiện các tác vụ song song.
- Thích hợp cho môi trường production với quy mô lớn hơn, nơi cần phân phối và quản lý việc thực thi task trên nhiều worker.
- Có khả năng mở rộng tốt với nhiều worker
- Cần phải cấu hình thêm Redis hoặc RabbitMQ làm broker và 1 backend để lưu trữ kết quả
4. DaskExecutor
- Sử dụng Dask, một thư viện Python cho tính toán phân tán, để thực thi các task.
- Thích hợp cho các công việc tính toán phức tạp yêu cầu khả năng mở rộng và phân tán, đặc biệt khi các task cần xử lý khối lượng dữ liệu lớn.
- Hỗ trợ tính toán phân tán và có thể tích hợp với các công cụ phân tích dữ liệu khác.
5. KubernetesExecutor
- Chạy các task trong các pod Kubernetes riêng biệt. Mỗi task sẽ chạy trong một pod độc lập.
- Thích hợp cho các môi trường sử dụng Kubernetes, giúp tận dụng khả năng mở rộng và quản lý tài nguyên của Kubernetes.
## Celery
Overview toàn bộ về [celery](https://www.youtube.com/watch?v=hFIkEGtW6vE).
- Giả sử có 1 api backend thuộc dạng POST, tại đó yêu cầu server generate 1 csv file và trả về kết quả thành công hay không. Có thể nhận thấy api sẽ bị block tại hàm generate_csv_report.

![block api](images/block_api.png).

- Giải pháp là sử dụng 1 machine khác với vai trò worker để thực hiện các task từ queue. Trong đó cần thêm 1 broker có thể là RabbitMQ, redis hay AWS SQS. Khi thực hiện đến hàm generate_csv_report, thay vì block request và thực hiện nó, ta ném nó vào broker để worker thực hiện, còn server chỉ cần return về kết quả. Làm vậy sẽ không bị block.

![async api](images/aysn_api.png).

![celery lib](images/celery_lib.png).

Celery bản chất là 1 giải pháp để tạo producer và consumer của 1 broker nào đó. Để sử dụng producer có thể publish lên broker, sử dụng hàm delay(). Để worker sử dụng lib để định nghĩa cách xử lý các task có thể nhận được từ broker.

Celery thường được sử dụng trong các hoạt động như send email, notification (thông báo), generate_report, ...

Worker của celery có 1 process pool riêng như task slot trong flink hay thread pool. Bạn phải khai báo số lượng process tối đa 1 worker có thể xử lý

Celery có thể lên lịch tạo các task đẩy vào queue bằng cách tạo 1 celery beat.

![celery beat](images/celery%20beat.png).
## CeleryExcutor
Trong file [docker-compose](https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html) của hãng mặc định sử dụng celery excutor. Nó có các service sau
1. postgres: nơi lưu trữ metadata của cả airflow (dags, logs, plugin, ...)
2. redis: cung cấp dịch vụ redis dùng như broker cho Celery Excutor
3. airlflow-webserver: Cung cấp giao diện web của Airflow để quản lý và giám sát các DAGs.
4. airflow-scheduler: Điều phối và lên lịch thực hiện các DAGs và tasks trong Airflow.
5. airflow-worker: Thực thi các task của Airflow khi sử dụng Celery Executor.
6. airflow-triggerer: Xử lý các trigger job, để xử lý các DAGs cần phải được kích hoạt.
7. airflow-init: Thực hiện các bước khởi tạo cần thiết trước khi các dịch vụ chính của Airflow được khởi động, chẳng hạn như tạo người dùng quản trị và thiết lập cơ sở dữ liệu.
8. airflow-cli: Cung cấp một container để thực thi các lệnh Airflow từ dòng lệnh.
9. flower: Cung cấp giao diện web để giám sát và quản lý các worker của Celery. (mở port 5555 để nhiìn giao diện flower)
# CDC (Change data capture)
Mục đích: capture lại thay đổi dữ liệu realtime phục vụ xử lsy realtime và backup dữ liệu
Các công nghệ CDC phổ biến.
1. Debezium
- Opensource được xây dựng dựa trên kafka, hỗ trợ nhiều hệ quản trị cơ sở dữ liệu như mysql, postgresSQL, MongoDB, ...
- Ưu điểm: dễ tích hợp với kafka.
- Use case: thường dùng kết hợp với kafka để xử lý streaming
2. Oracle Goldengate
- Ưu điểm: đồng bộ rất tốt với hệ thống của oracle thậm chí cả các sản phẩm của oracle.
- Usecase: Sử dụng trong các doanh nghiệp lớn với nhu cầu xử lý và sao chép dữ liệu phức tạp trong các hệ thống Oracle hoặc không phải Oracle.
3. AWS Database Migration Service (AWS DMS)
- Usecase: Di chuyển hoặc đồng bộ hóa dữ liệu từ các hệ thống on-premise hoặc trên cloud sang AWS.
4. Kafka Connect vs Source Connector
- Kafka Connect là một thành phần của Apache Kafka, cho phép dễ dàng tích hợp các hệ thống khác với Kafka. Các source connectors hỗ trợ CDC cho các cơ sở dữ liệu như MySQL, PostgreSQL, và Oracle.
5. SQL Server Change Data Capture
- Tích hợp sẵn trong Microsoft SQL server mà không cần sử dụng công cụ CDC khác
6. Striim
- Striim là một nền tảng CDC có khả năng sao chép dữ liệu theo thời gian thực và tích hợp dữ liệu từ nhiều nguồn, bao gồm các cơ sở dữ liệu và hệ thống đám mây.
7. Google Cloud Datastream
# Fact vs Dim table
Trong khái niệm mô hình hóa dữ liệu 

    # Cài supper set: https://superset.apache.org/docs/installation/docker-compose/
# Cài kafka: https://www.confluent.io/blog/how-to-use-kafka-docker-composer/
- Sử dụng giao thức external
bootstrapserver = localhost:9091, 9093
- Sử dụng giao thức plaintext với producer và consumer nằm trong cùng 1 network
bootstrap_servers=['kafka-1:19094', 'kafka-2:19095', 'kafka-3:19096']

# Minio
Sử dụng port 9001
# DB
# Airflow
Web sử dụng port 8080 của máy
Sử dụng port của network:

docker build -t initdb:v01 .