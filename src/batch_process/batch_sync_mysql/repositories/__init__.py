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
    access_key="mPu6afx3W3SnGX2GWJ84",
    secret_key="jsQbHNbZP6ZNqzhoKfN6DZc9ua1cXTm2nshEvwGZ",
    secure=False
)