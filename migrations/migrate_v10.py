import mysql.connector
import sys
from pathlib import Path

# Allow this migration to run both ways:
# - python -m migrations.migrate_v10
# - python migrations/migrate_v10.py
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from database import get_connection, initialize_db


def migrate():
    try:
        # Make sure the database and base tables already exist before altering them.
        initialize_db()

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SHOW COLUMNS FROM users")
        columns = [row["Field"] for row in cursor.fetchall()]

        if "profile_picture" in columns:
            print("profile_picture column already exists in users table.")
            return

        if "section" in columns:
            query = "ALTER TABLE users ADD COLUMN profile_picture VARCHAR(255) DEFAULT NULL AFTER section"
        else:
            query = "ALTER TABLE users ADD COLUMN profile_picture VARCHAR(255) DEFAULT NULL"

        cursor.execute(query)
        conn.commit()
        print("Added profile_picture column to users table.")
    except mysql.connector.Error as err:
        print(f"Migration v10 error: {err}")
    finally:
        if "conn" in locals() and conn.is_connected():
            conn.close()


if __name__ == "__main__":
    migrate()
