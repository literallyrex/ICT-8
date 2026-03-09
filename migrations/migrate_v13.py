import sys
from pathlib import Path

# Add project root to path so we can import from database
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from database.database import get_connection

def migrate():
    print("Starting migration v13: Adding text_color to users table...")
    conn = get_connection()
    if not conn:
        print("Failed to connect to database. Migration aborted.")
        return

    try:
        cursor = conn.cursor()
        
        cursor.execute("SHOW COLUMNS FROM users LIKE 'text_color'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE users ADD COLUMN text_color VARCHAR(50) DEFAULT 'Default'")
            print("Added text_color column.")

        conn.commit()
        print("Migration v13 completed successfully.")

    except Exception as e:
        print(f"Error during migration: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    migrate()
