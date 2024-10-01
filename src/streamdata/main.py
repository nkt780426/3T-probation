import pandas as pd
import mysql.connector
from mysql.connector import Error
import time
import logging  # Thêm mô-đun logging
import json  # Thêm mô-đun json

# Cấu hình logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

mysql_config = {
    'host': 'db-app',
    'port': 3306,
    'user': 'vohoang',
    'password': '123456678',
    'database': 'raw'
}

create_table_query = """
    CREATE TABLE IF NOT EXISTS sales_pipeline (
        opportunity_id VARCHAR(255) NOT NULL,
        sales_agent VARCHAR(255) NOT NULL,
        product VARCHAR(255) NOT NULL,
        account VARCHAR(255) NULL,
        deal_stage ENUM('Prospecting', 'Engaging', 'Won', 'Lost') NOT NULL,
        engage_date DATE NOT NULL,
        close_date DATE NULL,
        close_value DECIMAL(20, 2) NULL
    );
"""

try:
    connection = mysql.connector.connect(**mysql_config)
    if connection.is_connected():
        cursor = connection.cursor()
        cursor.execute(create_table_query)
        data = pd.read_csv('./data/sales_pipeline.csv')

        sql_query = '''INSERT INTO sales_pipeline (opportunity_id, sales_agent, product, account, deal_stage, engage_date, close_date, close_value) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'''
                        
        # Import dữ liệu
        for i, row in data.iterrows():
            # Thay thế giá trị NaN bằng None
            values = tuple(None if pd.isna(value) else value for value in row)
            cursor.execute(sql_query, values)
            connection.commit()  # Cam kết sau mỗi lần chèn
            
            # Log thông điệp dưới dạng JSON
            log_entry = {
                "Opportunity ID": row['opportunity_id'],
                "Sales Agent": row['sales_agent'],
                "Product": row['product'],
                "Account": row['account'],
                "Deal Stage": row['deal_stage'],
                "Engage Date": row['engage_date'],
                "Close Date": row['close_date'],
                "Close Value": row['close_value']
            }
            logging.info(f"Insert record has data: {json.dumps(log_entry, indent=4)}")  # Ghi log ở định dạng JSON
            time.sleep(3)  # Đợi 3 giây trước khi chèn record tiếp theo

except Error as e:
    logging.error(f'Lỗi khi kết nối MySQL: {e}')
finally:
    if connection.is_connected():
        cursor.close()
        connection.close()
