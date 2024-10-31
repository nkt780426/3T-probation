from repositories import mysql_connection
from utils.LogConfig import get_logger

class MysqlReposotory:
    def __init__(self) -> None:
        self.__logger = get_logger('MysqlReposotory')
        self.__mysql_connection = mysql_connection
    
    def count_rows(self, table_name: str) -> int:
        """Count the number of rows in a specified table."""
        try:
            cursor = self.__mysql_connection.cursor()
            query = f"SELECT COUNT(*) FROM {table_name};"
            cursor.execute(query)
            count = cursor.fetchone()[0]
            self.__logger.info(f"Counted {count} rows in table '{table_name}'.")
            return count
        except Exception as e:
            self.__logger.error(f"Error counting rows in table '{table_name}': {e}")
            raise

    def get_valid_ids(self, table_name: str, n: int) -> list[int]:
        """Return a list of IDs from the specified table where stream_ts > batch_ts or batch_ts is NULL."""
        try:
            cursor = self.__mysql_connection.cursor()

            # Step 1: Select the IDs that satisfy the conditions
            query = f"""
                SELECT id 
                FROM {table_name} 
                WHERE stream_ts > batch_ts OR batch_ts IS NULL 
                LIMIT %s;
            """
            cursor.execute(query, (n,))

            # Step 2: Fetch the results
            valid_ids = [row[0] for row in cursor.fetchall()]

            self.__logger.info(f"Retrieved {len(valid_ids)} valid IDs from table '{table_name}'.")
            return valid_ids

        except Exception as e:
            self.__logger.error(f"Error retrieving valid IDs from table '{table_name}': {e}")
            raise

    def update_row(self, table_name: str, data: dict) -> None:
        try:
            # Extract the id from data
            id = data.get('id')
            
            # Step 1: Connect to MySQL and start a transaction
            cursor = self.__mysql_connection.cursor()

            # Step 2: Select the current row to get stream_ts
            select_query = f"SELECT stream_ts FROM {table_name} WHERE id = %s;"
            cursor.execute(select_query, (id,))
            result = cursor.fetchone()

            # Check if the row exists
            if result is None:
                self.__logger.error(f"No row found in table '{table_name}' with id '{id}'. Update aborted.")
                return
            
            current_stream_ts = result[0]
            batch_ts = data.get('batch_ts')  # Assuming batch_ts is part of the data dict
            
            # Step 3: Compare stream_ts with batch_ts
            if current_stream_ts > batch_ts:
                self.__logger.info(f"No update performed for row with id '{id}' in table '{table_name}' because stream_ts is greater than batch_ts.")
                return
            
            # Step 4: Proceed with the update
            set_clause = ', '.join([f"{key} = %s" for key in data.keys() if key != 'id'])
            update_query = f"UPDATE {table_name} SET {set_clause} WHERE id = %s;"
            cursor.execute(update_query, list(data.values())[1:] + [id])
            
            # Commit the transaction
            self.__mysql_connection.commit()
            self.__logger.info(f"Updated row in table '{table_name}' with id '{id}'.")

        except Exception as e:
            # Rollback the transaction in case of error
            if self.__mysql_connection.is_connected():
                self.__mysql_connection.rollback()
            self.__logger.error(f"Error updating row in table '{table_name}': {e}")
            raise