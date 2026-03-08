import mysql.connector
import config
import json

conn = mysql.connector.connect(**config.db_config)
cursor = conn.cursor(dictionary=True)

# Schema
cursor.execute('DESCRIBE users')
schema = cursor.fetchall()
with open('schema.json', 'w') as f:
    json.dump(schema, f, indent=2)

# Sample Data
cursor.execute('SELECT * FROM users LIMIT 10')
data = cursor.fetchall()
with open('data.json', 'w') as f:
    json.dump(data, f, indent=2)

conn.close()
