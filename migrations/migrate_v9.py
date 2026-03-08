import mysql.connector

from utils.config import db_config


def migrate():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SHOW COLUMNS FROM users LIKE 'specialization'")
        if cursor.fetchone():
            cursor.execute("ALTER TABLE users DROP COLUMN specialization")
            conn.commit()
            print("Removed specialization column from users table.")
        else:
            print("specialization column does not exist in users table.")
    except mysql.connector.Error as err:
        print(f"Migration v9 error: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()


if __name__ == "__main__":
    migrate()
