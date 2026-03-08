import mysql.connector
from utils.config import db_config

def migrate():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        alter_queries = [
            "ALTER TABLE users ADD COLUMN address VARCHAR(255) AFTER phone",
            "ALTER TABLE users ADD COLUMN student_id VARCHAR(50) AFTER address",
            "ALTER TABLE users ADD COLUMN course_year VARCHAR(100) AFTER student_id",
            "ALTER TABLE users ADD COLUMN room_number VARCHAR(50) AFTER course_year",
            "ALTER TABLE users ADD COLUMN check_in_date VARCHAR(50) AFTER room_number",
            "ALTER TABLE users ADD COLUMN employee_id VARCHAR(50) AFTER check_in_date",
            "ALTER TABLE users ADD COLUMN department VARCHAR(100) AFTER employee_id"
        ]
        
        for query in alter_queries:
            try:
                cursor.execute(query)
                print(f"Executed: {query}")
            except mysql.connector.Error as err:
                print(f"Skipped (probably exists): {err}")
                
        conn.commit()
        conn.close()
        print("Migration v3 complete.")
    except Exception as e:
        print(f"Migration failed: {e}")

if __name__ == "__main__":
    migrate()
