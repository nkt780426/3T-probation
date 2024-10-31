import json
from datetime import datetime
from collections import defaultdict
from minio import Minio
from minio.error import S3Error
from redis import Redis
from services.LogConfig import get_logger
import io

# Create logger
logger = get_logger('BatchProcessor')

# Connect to Redis server
redis_client = Redis(host='db-redis', port=6379, db=0)

# Connect to MinIO
minio_client = Minio(
    endpoint="minio:9000",
    access_key="cE09RlehOwFVq98rGhMq",
    secret_key="7wdHR2pr1gZZcT9rHNHs9U5h15vyht8qwMSarqKA",
    secure=False
)

# Name of the bucket in MinIO
bucket_name = "probation"
date_folder = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

# Kiểm tra và tạo bucket nếu chưa tồn tại
if not minio_client.bucket_exists(bucket_name):
    minio_client.make_bucket(bucket_name)
    logger.info(f"Bucket '{bucket_name}' created successfully.")
else:
    logger.info(f"Bucket '{bucket_name}' already exists.")
    
def process_batch():
    # Get the last timestamp from Redis
    last_ts_ms = int(redis_client.get('probation:last_ts_ms').decode())
    if last_ts_ms is None:
        logger.error("No last_ts_ms found in Redis.")
        raise
    
    items_grouped_by_id = defaultdict(dict)  # Sử dụng dictionary để nhóm các key có cùng id
    
    # Snapshot and check all keys
    keys = [key.decode() for key in redis_client.keys("probation:*") if key.decode() != "probation:last_ts_ms"]
    
    # Nhóm các bản ghi cùng giá trị phần tử thứ ba (id)
    for key in keys:
        key_parts = key.split(":")
        topic_name = key_parts[1]           # Lấy tên topic
        unique_id = key_parts[2]            # Giá trị phần tử thứ ba là id duy nhất
        timestamp = int(key_parts[3])       # Giá trị timestamp

        # Nếu timestamp thỏa mãn điều kiện, thêm vào dictionary theo id
        if timestamp <= last_ts_ms:
            items_grouped_by_id[(topic_name, unique_id)][timestamp] = redis_client.get(key).decode()
    
    # Lưu items vào MinIO
    for (topic_name, unique_id), records in items_grouped_by_id.items():
        # Tạo đường dẫn folder theo ngày và tên topic
        minio_folder_path = f"{date_folder}/{topic_name}"
        minio_object_name = f"{minio_folder_path}/{unique_id}.json"
        
        # Convert records dictionary to JSON
        json_data = json.dumps(records, indent=4).encode("utf-8")
        json_data_stream = io.BytesIO(json_data)
        
        try:
            # Upload JSON data to MinIO
            minio_client.put_object(
                bucket_name,
                minio_object_name,
                data=json_data_stream,
                length=len(json_data),
                content_type="application/json"
            )
            logger.info(
                f"Successfully saved JSON data to MinIO.\n"
                f"Bucket: {bucket_name}\n"
                f"Folder Path: {minio_folder_path}\n"
                f"File Name: {unique_id}.json\n"
                f"Number of Records: {len(records)}\n"
            )
            
            # Xóa tất cả các key đã được lưu vào MinIO
            for timestamp in records:
                redis_key = f"probation:{topic_name}:{unique_id}:{timestamp}"
                redis_client.delete(redis_key)
                logger.info(f"Deleted key {redis_key} from Redis.")
        
        except S3Error as e:
            logger.error(f"Error saving to MinIO: {e}")
            
if __name__ == "__main__":
    logger.info(f"Begin batch process")
    process_batch()
    logger.info("End batch process")
