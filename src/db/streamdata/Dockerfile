# Sử dụng image Python chính thức
FROM python:3.10

# Tạo thư mục làm việc
WORKDIR /app

# Sao chép toàn bộ thư mục hiện tại (bao gồm cả initdb.py, data và requirements.txt) vào thư mục /app trong container
COPY . .

# Cài đặt thư viện từ requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Chạy script khi container khởi động
CMD ["python", "main.py"]
