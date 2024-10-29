import pandas as pd
import mysql.connector
from mysql.connector import Error

# Thông tin kết nối MySQL
mysql_config = {
    'host': 'localhost',
    'port': 3307,
    'user': 'vohoang',
    'password': '12345678',
    'database': 'raw'
}

# Đọc file CSV bằng pandas
csv_files = {
    'accounts': './data/accounts.csv',
    'products': './data/products.csv',
    'sales_teams': './data/sales_teams.csv',
}

# Các câu truy vấn tạo bảng tương ứng
create_table_queries = {
    'accounts': """
        CREATE TABLE IF NOT EXISTS accounts (
            account VARCHAR(255) NOT NULL,
            sector VARCHAR(255) NOT NULL,
            year_established INT NOT NULL,
            revenue DECIMAL(20, 2) NOT NULL,
            employees INT NOT NULL,
            office_location VARCHAR(255) NOT NULL,
            subsidiary_of VARCHAR(255) NULL,
            PRIMARY KEY (account)
        );
    """,
    'products': """
        CREATE TABLE IF NOT EXISTS products (
            product VARCHAR(255),
            series VARCHAR(255),
            sales_price DECIMAL(10, 2),
            PRIMARY KEY (product)
        );
    """,
    'sales_teams': """
        CREATE TABLE IF NOT EXISTS sales_teams (
            sales_agent VARCHAR(255),
            manager VARCHAR(255),
            regional_office VARCHAR(255),
            PRIMARY KEY (sales_agent)
        );
    """,
    'sales_pipeline': """
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
}

# Kết nối tới MySQL
try:
    connection = mysql.connector.connect(**mysql_config)
    if connection.is_connected():
        cursor = connection.cursor()

        for table_name, csv_file in csv_files.items():
            # Tạo bảng nếu chưa tồn tại
            cursor.execute(create_table_queries[table_name])
            print(f"Bảng '{table_name}' đã được tạo hoặc đã tồn tại.")

            # Đọc file CSV bằng pandas
            data = pd.read_csv(csv_file)

            # Tạo câu truy vấn để insert dữ liệu vào bảng
            sql_query = None
            if table_name == 'accounts':
                sql_query = """INSERT INTO accounts (account, sector, year_established, revenue, employees, office_location, subsidiary_of) 
                               VALUES (%s, %s, %s, %s, %s, %s, %s)"""
            elif table_name == 'products':
                sql_query = """INSERT INTO products (product, series, sales_price) VALUES (%s, %s, %s)"""
            elif table_name == 'sales_teams':
                sql_query = """INSERT INTO sales_teams (sales_agent, manager, regional_office) VALUES (%s, %s, %s)"""
            # elif table_name == 'sales_pipeline':
            #     sql_query = """INSERT INTO sales_pipeline (opportunity_id, sales_agent, product, account, deal_stage, engage_date, close_date, close_value) 
            #                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""

            # Import dữ liệu
            for i, row in data.iterrows():
                # Thay thế giá trị NaN bằng None
                values = tuple(None if pd.isna(value) else value for value in row)
                cursor.execute(sql_query, values)

            connection.commit()
            print(f"Dữ liệu đã được import thành công vào bảng '{table_name}'.")
        
        cursor.execute(create_table_queries['sales_pipeline'])
        connection.commit()

except Error as e:
    print(f"Lỗi khi kết nối MySQL: {e}")

finally:
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("Kết nối MySQL đã đóng.")
