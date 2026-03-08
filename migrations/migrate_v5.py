import mysql.connector
from utils.config import db_config

def migrate():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        drop_queries = [
            "ALTER TABLE users DROP COLUMN room_number",
            "ALTER TABLE users DROP COLUMN check_in_date",
            "ALTER TABLE users DROP COLUMN employee_id",
            "ALTER TABLE users DROP COLUMN department"
        ]
        
        for query in drop_queries:
            try:
                cursor.execute(query)
                print(f"Executed: {query}")
            except mysql.connector.Error as err:
                print(f"Skipped (column may not exist): {err}")
                
        conn.commit()
        conn.close()
        print("Migration v5 (Drop unused columns) complete.")
    except Exception as e:
        print(f"Migration failed: {e}")

if __name__ == "__main__":
    migrate()
