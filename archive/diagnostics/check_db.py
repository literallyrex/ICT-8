import mysql.connector
from config import db_config

try:
    print(f"Connecting to {db_config['host']}...")
    conn = mysql.connector.connect(**db_config)
    print("Connection Successful!")
    conn.close()
except mysql.connector.Error as err:
    print(f"Connection Failed: {err}")
