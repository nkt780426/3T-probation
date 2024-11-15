# Giới thiệu
![](images/1.%20logo.png)

**DBT - Data build tool** là 1 công cụ giúp transform dữ liệu trong data warehouse chỉ bằng các câu lệnh sql.

Hiện có 2 phiên bản dbt-core (open source) và dbt-cloud. Dbt đang được sử dụng rộng rãi bởi các nhà phân tích dữ liệu trong nước cũng như thế giới.

Các tính năng nổi bật có thể kể đến như.
- *Tạo mô hình dữ liệu*: dbt cho phép bạn định nghĩa các data model dưới dạng các tập lệnh sql, có thể liên kết được với nhau theo thứ tự cần thiết để xây dựng pipeline transform dữ liệu và tự động hóa việc tạo pipeline theo thứ tự phụ thuộc lẫn nhau của các model.
- *Kiểm thử dữ liệu và tạo doc*: dbt tích hợp các kiểm thử dữ liệu nhằm đảm bảo chất lượng dữ liệu. (file schema.yml)
- **Quản lý phiên bản mã nguồn**: dbt là mã nguồn nên có thể tích hợp với Git, giúp các Data Analysis dễ dàng cộng tác và kiểm soát phiên bản các mô hình dữ liệu. 
- **Dễ dàng mở rộng**: dbt có thể tích hợp với nhiều kho dữ liệu phổ biến như BigQuery, Snowflake, Redshift, và PostgreSQL, giúp linh hoạt khi triển khai trên nhiều nền tảng. Muốn thay đổi nền tảng chỉ cần thay đổi dbt-adapter.
- *Giao diện người dùng nhẹ*: dbt cloud mới có
- *Dockerization*: có image trên docker hỗ trợ đóng gói mã nguồn thành container.
Tóm lại, dbt giúp đơn giản hóa và tổ chức quá trình chuyển đổi dữ liệu, giúp các nhà phân tích và kỹ sư dữ liệu dễ dàng xây dựng các pipeline xử lý dữ liệu và đảm bảo chất lượng dữ liệu trước khi đưa vào phân tích.

# Thành phần
Gồm 3 folder chính
- Models: chứa các data model được xây dựng bằng sql
- Seeds: dữ liệu khởi đầu để tạo các data model
- Snapshots: chứa các bản sao của dữ liệu trong quá khứ phục vụ mục đích phân tích
