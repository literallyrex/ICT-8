import mysql.connector
from utils.config import db_config

def migrate_v7():
    """Add age, gender, course_category, program_type, specialization, and year_level to users table."""
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        print("Checking for new columns in 'users' table...")
        
        # New columns to add
        new_columns = [
            ("age", "INT"),
            ("gender", "VARCHAR(20)"),
            ("course_category", "VARCHAR(50)"),
            ("program_type", "VARCHAR(50)"),
            ("specialization", "VARCHAR(100)"),
            ("year_level", "VARCHAR(20)")
        ]
        
        for col_name, col_type in new_columns:
            try:
                cursor.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}")
                print(f"Added column: {col_name}")
            except mysql.connector.Error as err:
                if err.errno == 1060: # Duplicate column name
                    print(f"Column {col_name} already exists.")
                else:
                    print(f"Error adding {col_name}: {err}")

        conn.commit()
        print("Migration v7 completed successfully!")
        conn.close()
    except mysql.connector.Error as err:
        print(f"Database error during migration: {err}")

if __name__ == "__main__":
    migrate_v7()
