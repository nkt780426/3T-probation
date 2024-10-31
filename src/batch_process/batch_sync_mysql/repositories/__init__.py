import mysql.connector
from minio import Minio

mysql_config = {
    'host': 'db-report',
    'port': 3306,
    'user': 'vohoang',
    'password': '12345678',
    'database': 'report',
    'autocommit': False
}

mysql_connection = mysql.connector.connect(**mysql_config)

# Connect to MinIO
minio_client = Minio(
    endpoint="minio:9000",
    access_key="5CH777EgLxJZxi6FtQES",
    secret_key="UttcxebvGxcWtywcqG6oicgm6jgNdri0IDHuVFKB",
    secure=False
)