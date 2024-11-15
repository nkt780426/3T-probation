# Giới thiệu
Apache Kafka là một nền tảng xử lý luồng dữ liệu phân tán, mã nguồn mở, được thiết kế để xử lý dữ liệu theo thời gian thực với tốc độ cao. Kafka ban đầu được phát triển bởi LinkedIn và sau đó trở thành một dự án của Apache Software Foundation. Nó được sử dụng để xây dựng các pipeline dữ liệu thời gian thực và ứng dụng truyền phát dữ liệu có khả năng mở rộng lớn.

![](images/1.%20Kafka.png)

Ngoài kafka broker, apache đã phát triển rất nhiều các project nhằm hỗ trợ việc thao tác với kafka trở nên thuận tiện hơn. Điều này đã tạo ra 1 hệ sinh thái apache kafka mạnh mẽ có thể kể đên như kafka stream, ksql DB, kafka connect, ...

# Kafka broker
## 1. Mind set
Bất kỳ 1 sản phẩm công nghệ nào ra đời đều phải dựa trên 1 mindset nào đó.
1. Request - Reponse protocol (Client - Server protocol)
    ![](images/1.%20Request%20and%20response%20protocol.png)

    Nhờ vào mindset này 1 số phương thức đã được triển khai trong thực tiễn. Ví dụ https.
    
    Nhược điểm:
    - A request sẽ treo chờ khi có response từ B mới hoạt động trở lại (dù web 2.0 đã cải thiện bằng cách gửi gói tin rỗng để thực hiện cơ chế async)
    - A phải biết địa chỉ chính xác của B. Thế nếu A phải nói chuyện với nhiều người tức là A phải biết tất cả các địa chỉ của họ và ngược lại.
    - A gửi request, B chết => Đợi mòn kiếp không có response => Dùng timeout nhưng điều này cũng đồng nghĩa với việc A phải đợi hết timeout.

2. publish - subcribe protocol
    ![](images/1.%20Publish%20and%20subcribe%20protocol.png)

    Được 1 ông kỹ sư đường ống nào đó nghĩ ra và được áp dụng trong rất nhiều lĩnh vực điển hình là iot. Nơi mà tần suất các cảm biến sinh ra dữ liệu là rất lớn.

    Ưu điểm:
    - các client (producer/consumer) hoàn toàn độc lập với nhau. Broker (nhà môi giới) sẽ đảm nhận nhiệm vụ giao tiếp giữa các client, các client không cần phải biết chính xác địa chỉ IP của nhau. Ví dụ ta có thể có 1000 consumer thì producer không cần quan tâm, nó chỉ gửi dữ liệu đến địa chỉ IP của broker.
    - back pressure: producer và consumer không cần phải đợi nhau phản hồi mà có thể tự do sản xuất và tiêu thu message theo khả năng tính toán của bản thân. 
    