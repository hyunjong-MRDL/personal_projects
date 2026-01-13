import mysql.connector
from mysql.connector import errorcode
import traceback

class DatabaseManager:
    def __init__(self, config):
        self.config = config
        self.cnx = None

    def connect(self):
        try:
            self.cnx = mysql.connector.connect(**self.config)
            print("Database connection successful.")
            self.create_results_table()
            return True
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password.")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist.")
            else:
                print(f"An error occurred: {err}")
            return False

    def close(self):
        if self.cnx and self.cnx.is_connected():
            self.cnx.close()
            print("Database connection closed.")

    def create_results_table(self):
        """
        Creates the 'analysis_results' table if it doesn't already exist.
        """
        cursor = self.cnx.cursor()
        table_description = """
        CREATE TABLE IF NOT EXISTS analysis_results (
          patient_id VARCHAR(255) NOT NULL,
          data_type VARCHAR(255),
          reproducibility FLOAT,
          lvl_mean FLOAT,
          lvl_std FLOAT,
          stability FLOAT,
          error_mean FLOAT,
          error_std FLOAT,
          PRIMARY KEY (patient_id)
        );
        """
        try:
            print("Creating table 'analysis_results'...")
            cursor.execute(table_description)
        except mysql.connector.Error as err:
            print(f"Failed to create table: {err}")
        finally:
            cursor.close()

    def insert_dataframe(self, df, table_name):
        cursor = self.cnx.cursor()

        columns = ', '.join(df.columns)
        placeholders = ', '.join(['%s'] * len(df.columns))
        
        insert_query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

        update_cols = [f"{col}=VALUES({col})" for col in df.columns if col != 'patient_id']
        on_duplicate_key_update = f"ON DUPLICATE KEY UPDATE {', '.join(update_cols)}"
        
        insert_query = f"{insert_query} {on_duplicate_key_update}"

        try:
            print(f"Inserting {len(df)} records into '{table_name}'...")
            for _, row in df.iterrows():
                cursor.execute(insert_query, tuple(row))
            self.cnx.commit()
            print("Data successfully inserted/updated.")
        except mysql.connector.Error as err:
            print(f"Failed to insert data: {err}")
            print(traceback.format_exc())
            self.cnx.rollback()
        finally:
            cursor.close()

    def fetch_all_results(self):
        results = []
        cursor = self.cnx.cursor(dictionary=True)
        query = "SELECT * FROM analysis_results"
        
        try:
            cursor.execute(query)
            results = cursor.fetchall()
            print("Data successfully fetched from database.")
        except mysql.connector.Error as err:
            print(f"Failed to fetch data: {err}")
        finally:
            cursor.close()
        
        return results