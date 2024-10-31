from repositories.MinioRepository import MinioRepository
from repositories.MysqlRepository import MysqlReposotory

from utils.LogConfig import get_logger

from datetime import datetime
import os
import json

class BatchSyncService:
    def __init__(self) -> None:
        self.__logger = get_logger('BatchSyncService')
        self.__minio_repository = MinioRepository()
        self.__mysql_repository = MysqlReposotory()
        
    def batch_sync_service(self, table_name: str) -> None:
        # Get the number of rows to batch process
        total_rows = self.__mysql_repository.count_rows(table_name)
        
        # Select list of IDs to batch process
        valid_ids = self.__mysql_repository.get_valid_ids(table_name, total_rows)
        
        self.__logger.info(f'There are {len(valid_ids)} row need batch process.')
        
        for record_id in valid_ids:
            # Get the file path from MinIO
            file_path = self.__get_batch_file_in_minio(table_name, record_id)
            if not file_path is None:
            # Load batch data from the JSON file
                with open(file_path) as json_file:
                    batch_data = json.load(json_file)

                # Find the key with the maximum timestamp
                max_timestamp = max(batch_data.keys(), key=int)  # Get the maximum key
                max_entry = batch_data[max_timestamp]  # Get the corresponding entry

                # Process the max_entry as needed (e.g., save it back to MySQL or perform any operation)
                self.__process_batch_entry(table_name, max_entry)
            else:
                self.__logger.warning(f"No data found for ID '{record_id}' in table '{table_name}'.")
                break
            
    def __get_batch_file_in_minio(self, table_name: str, record_id: str) -> str:
        tmp_dir = '/tmp'
        batch_file = None
        timestamp_folders = []
        download_attempts = 0
        max_download_attempts = 3

        # Lấy danh sách các thư mục hợp lệ và sắp xếp theo timestamp
        for batch_folder in os.listdir(tmp_dir):
            batch_folder_path = os.path.join(tmp_dir, batch_folder)
            if os.path.isdir(batch_folder_path):
                try:
                    # Chuyển đổi tên thư mục thành timestamp
                    current_timestamp = datetime.strptime(batch_folder, "%Y_%m_%d_%H_%M_%S")
                    timestamp_folders.append((current_timestamp, batch_folder_path))
                except ValueError:
                    continue

        # Sắp xếp các thư mục theo timestamp giảm dần
        timestamp_folders.sort(key=lambda x: x[0], reverse=True)

        # Hàm kiểm tra file sau mỗi lần tải xuống
        def check_record_file(batch_folder_path):
            table_folder_path = os.path.join(batch_folder_path, table_name)
            if os.path.isdir(table_folder_path):
                record_file_path = os.path.join(table_folder_path, f"{record_id}.json")
                return os.path.isfile(record_file_path)
            return False

        # Kiểm tra từng thư mục từ lớn đến nhỏ
        while download_attempts < max_download_attempts:
            for timestamp, batch_folder_path in timestamp_folders:
                if check_record_file(batch_folder_path):
                    batch_file = os.path.join(batch_folder_path, table_name, f"{record_id}.json")
                    return batch_file  # Trả về file nếu tìm thấy

            # Nếu không tìm thấy file, gọi hàm download_latest_folder_before
            if len(timestamp_folders) > 0:
                # Lấy timestamp nhỏ nhất từ danh sách đã sắp xếp
                smallest_timestamp = timestamp_folders[-1][0]
            else:
                # Sử dụng timestamp hiện tại nếu không có thư mục nào hợp lệ
                smallest_timestamp = datetime.now()

            smallest_timestamp_str = smallest_timestamp.strftime("%Y_%m_%d_%H_%M_%S")
                    
            # Gọi hàm download_latest_folder_before
            self.__minio_repository.download_latest_folder_before("probation", smallest_timestamp_str)
            download_attempts += 1

            # Cập nhật lại danh sách thư mục sau khi tải xuống
            timestamp_folders.clear()  # Xóa danh sách cũ
            for batch_folder in os.listdir(tmp_dir):
                batch_folder_path = os.path.join(tmp_dir, batch_folder)
                if os.path.isdir(batch_folder_path):
                    try:
                        # Chuyển đổi tên thư mục thành timestamp
                        current_timestamp = datetime.strptime(batch_folder, "%Y_%m_%d_%H_%M_%S")
                        if current_timestamp < smallest_timestamp:  # Chỉ thêm thư mục nhỏ hơn smallest_timestamp
                            timestamp_folders.append((current_timestamp, batch_folder_path))
                    except ValueError:
                        continue

            # Sắp xếp lại danh sách thư mục sau khi tải xuống
            timestamp_folders.sort(key=lambda x: x[0], reverse=True)

        return batch_file  # Trả về đường dẫn file nếu tìm thấy, nếu không sẽ là None

    def __process_batch_entry(self, table_name: str, entry: dict) -> None:
        if isinstance(entry, str):
            entry = json.loads(entry)
        data = entry['after']
        data['batch_ts'] = entry['ts_ms']
        self.__mysql_repository.update_row(table_name, data)