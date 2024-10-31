from repositories import minio_client
from utils.LogConfig import get_logger

from minio.error import S3Error
from datetime import datetime
import os

class MinioRepository:
    def __init__(self) -> None:
        self.__minio_client = minio_client
        self.__logger = get_logger('MinioRepository')
    
    def __download_folder(self, bucket_name, folder_name):
        # Tạo đường dẫn tải xuống
        download_path = "/tmp"
        os.makedirs(download_path, exist_ok=True)

        # Lấy danh sách các đối tượng trong thư mục
        objects = self.__minio_client.list_objects(bucket_name, prefix=folder_name, recursive=True)

        for obj in objects:
            # Xác định đường dẫn tải xuống
            file_path = os.path.join(download_path, obj.object_name)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            # Tải xuống đối tượng
            self.__minio_client.fget_object(bucket_name, obj.object_name, file_path)
            self.__logger.info(f"Downloaded {obj.object_name} to {file_path}.")
            
    def download_latest_folder_before(self, bucket_name, time_input):
        # Chuyển đổi chuỗi thời gian đầu vào thành đối tượng datetime
        input_time = datetime.strptime(time_input, "%Y_%m_%d_%H_%M_%S")

        closest_folder_time = None
        closest_folder_name = None

        try:
            # Lấy danh sách các đối tượng trong bucket
            objects = self.__minio_client.list_objects(bucket_name, recursive=False)

            # Duyệt qua các thư mục để tìm thư mục gần nhất nhỏ hơn input_time
            for obj in objects:
                folder_time_str = obj.object_name.rstrip('/')  # Tên folder tương ứng với thời gian

                # Chuyển đổi tên folder về datetime
                folder_time = datetime.strptime(folder_time_str, "%Y_%m_%d_%H_%M_%S")

                # Kiểm tra điều kiện gần nhất
                if folder_time < input_time:
                    if closest_folder_time is None or folder_time > closest_folder_time:
                        closest_folder_time = folder_time
                        closest_folder_name = folder_time_str  # Lưu lại tên folder

            if closest_folder_name:
                # Tải xuống thư mục gần nhất nhỏ hơn input_time
                self.__download_folder(bucket_name, closest_folder_name)
                self.__logger.info(f"Downloaded folder {closest_folder_name}.")
            else:
                self.__logger.error(f"No folder found before {time_input}.")
                return
            
        except S3Error as e:
            self.__logger.error(f"Error accessing MinIO: {e}")
            raise