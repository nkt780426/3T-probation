from services.LogConfig import get_logger
import json
from decimal import Decimal

class DebeziumMessageProcess:
    def __init__(self, connection, message_value):
        self.connection = connection
        self.__table_name = message_value['source']['table']
        
        data = message_value['after'] if message_value['op'] in ['c', 'u', 'r'] else message_value['before']
        self.__create_table_if_not_exists(data)
        self.__logger = get_logger('DebeziumMessageProcess')

    def process_message(self, message_key, message_value):
        if message_value['op'] in ['c', 'u', 'r']:
            self.__handle_insert_or_update(message_value)
        elif message_value['op'] == 'd':
            self.__handle_delete(message_key)
        else:
            return

    ## Private Func
    def __create_table_if_not_exists(self, data: dict):
        columns = list(data.keys())
        column_definitions = []

        for col in columns:
            value = data[col]
            column_type = "INT" if isinstance(value, int) else "DECIMAL(10, 2)" if isinstance(value, float) else "VARCHAR(255)"
            column_definitions.append(f"{col} {column_type}")

        # Thêm các trường stream_ts và batch_ts
        column_definitions.append("stream_ts BIGINT")
        column_definitions.append("batch_ts BIGINT DEFAULT NULL")
        
        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {self.__table_name} (
            {', '.join(column_definitions)},
            PRIMARY KEY ({columns[0]})
        );
        """
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(create_table_sql)
                self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            self.__logger.error('Failed to create table {self.__table_name}')
            raise
        
    def __handle_insert_or_update(self, message_value: dict):
        data = message_value['after']
        columns = list(data.keys())
        values = [data[column] for column in columns]
        columns.append('stream_ts')
        values.append(message_value['ts_ms'])
        
        placeholders = ', '.join(['%s'] * len(columns))
        update_clause = ', '.join([f"{col} = %s" for col in columns])
        
        sql = f"""
        INSERT INTO {self.__table_name} ({', '.join(columns)})
        VALUES ({placeholders})
        ON DUPLICATE KEY UPDATE {update_clause}
        """

        combined_values = values + values

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(sql, combined_values)
                self.connection.commit()
                
            # Sử dụng message_str đã được xử lý Decimal để log
            message_str = json.dumps(message_value, indent=4, default=lambda x: str(x) if isinstance(x, Decimal) else x)
            self.__logger.info(f"Inserting or updating record in table '{self.__table_name}' with message:\n{message_str}")
        except Exception as e:
            message_str = json.dumps(message_value, indent=4, default=lambda x: str(x) if isinstance(x, Decimal) else x)
            self.connection.rollback()
            self.__logger.error(f"Failed to insert or update record in table '{self.__table_name}' with message:\n{message_str}\nError: {e}")
    
    # Tạm thời không xử lý delete.
    def __handle_delete(self, key: dict):
        key_name = list(key.keys())[0]
        key_value = key[key_name]
        
        sql = f"""
        DELETE FROM {self.__table_name} WHERE {key_name} = %s
        """

        with self.connection.cursor() as cursor:
            cursor.execute(sql, (key_value,))
            self.connection.commit()
