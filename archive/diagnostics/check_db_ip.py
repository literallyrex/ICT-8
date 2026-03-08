import mysql.connector
from config import db_config

config = db_config.copy()
config['host'] = '127.0.0.1'

try:
    print(f"Connecting to {config['host']}...")
    conn = mysql.connector.connect(**config)
    print("Connection Successful via 127.0.0.1!")
    conn.close()
except mysql.connector.Error as err:
    print(f"Connection Failed via 127.0.0.1: {err}")
