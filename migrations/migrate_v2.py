import mysql.connector
from utils.config import db_config

def migrate():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        alter_queries = [
            "ALTER TABLE users ADD COLUMN full_name VARCHAR(255) AFTER password_hash",
            "ALTER TABLE users ADD COLUMN email VARCHAR(255) AFTER full_name",
            "ALTER TABLE users ADD COLUMN phone VARCHAR(50) AFTER email"
        ]
        
        for query in alter_queries:
            try:
                cursor.execute(query)
                print(f"Executed: {query}")
            except mysql.connector.Error as err:
                print(f"Skipped (probably exists): {err}")
                
        conn.commit()
        conn.close()
        print("Migration complete.")
    except Exception as e:
        print(f"Migration failed: {e}")

if __name__ == "__main__":
    migrate()
