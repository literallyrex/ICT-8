import mysql.connector
from utils.config import db_config

def migrate():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        alter_queries = [
            "ALTER TABLE users ADD COLUMN status VARCHAR(50) DEFAULT 'Pending' AFTER user_role"
        ]
        
        for query in alter_queries:
            try:
                cursor.execute(query)
                print(f"Executed: {query}")
            except mysql.connector.Error as err:
                print(f"Skipped (probably exists): {err}")
                
        conn.commit()
        conn.close()
        print("Migration v4 (Status column) complete.")
    except Exception as e:
        print(f"Migration failed: {e}")

if __name__ == "__main__":
    migrate()
