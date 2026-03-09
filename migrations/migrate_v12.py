import sys
from pathlib import Path

# Add project root to path so we can import from database
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from database.database import get_connection

def migrate():
    print("Starting migration v12: Adding UI customization preferences to users table...")
    conn = get_connection()
    if not conn:
        print("Failed to connect to database. Migration aborted.")
        return

    try:
        cursor = conn.cursor()
        
        # Check if columns already exist
        cursor.execute("SHOW COLUMNS FROM users LIKE 'ui_color'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE users ADD COLUMN ui_color VARCHAR(50) DEFAULT 'Blue'")
            print("Added ui_color column.")
            
        cursor.execute("SHOW COLUMNS FROM users LIKE 'button_color'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE users ADD COLUMN button_color VARCHAR(50) DEFAULT 'Standard'")
            print("Added button_color column.")
            
        cursor.execute("SHOW COLUMNS FROM users LIKE 'theme_mode'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE users ADD COLUMN theme_mode VARCHAR(20) DEFAULT 'Dark'")
            print("Added theme_mode column.")
            
        cursor.execute("SHOW COLUMNS FROM users LIKE 'background_style'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE users ADD COLUMN background_style VARCHAR(50) DEFAULT 'Solid'")
            print("Added background_style column.")
            
        cursor.execute("SHOW COLUMNS FROM users LIKE 'profile_accent_color'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE users ADD COLUMN profile_accent_color VARCHAR(50) DEFAULT 'Blue'")
            print("Added profile_accent_color column.")

        conn.commit()
        print("Migration v12 completed successfully.")

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
