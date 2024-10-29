import pandas as pd
import mysql.connector
from mysql.connector import Error
import time
import logging  # Thêm mô-đun logging
import json  # Thêm mô-đun json

# Cấu hình logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

mysql_config = {
    'host': 'localhost',
    'port': 3307,
    'user': 'vohoang',
    'password': '12345678',
    'database': 'raw'
}

create_table_query = """
    CREATE TABLE IF NOT EXISTS sales_pipeline (
        opportunity_id VARCHAR(255),
        sales_agent VARCHAR(255),
        product VARCHAR(255),
        account VARCHAR(255),
        deal_stage ENUM('Prospecting', 'Engaging', 'Won', 'Lost'),
        engage_date DATE,
        close_date DATE,
        close_value DECIMAL(20, 2),
        PRIMARY KEY (opportunity_id),
        FOREIGN KEY (sales_agent) REFERENCES sales_teams(sales_agent),
        FOREIGN KEY (product) REFERENCES products(product),
        FOREIGN KEY (account) REFERENCES accounts(account)
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
            time.sleep(2)  # Đợi 3 giây trước khi chèn record tiếp theo

except Error as e:
    logging.error(f'Lỗi khi kết nối MySQL: {e}')
finally:
    if connection.is_connected():
        cursor.close()
        connection.close()
