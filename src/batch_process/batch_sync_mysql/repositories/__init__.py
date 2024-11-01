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
    access_key="7FtQ1iwnnZgdQWbr9YsO",
    secret_key="JEdFntys1p9QH1wCl19UKw9pDa6BZxUlnF5zPCez",
    secure=False
)