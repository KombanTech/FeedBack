import mysql.connector
import bcrypt

# MySQL configuration
db_config = {
    'host': 'localhost',
    'user': 'root',  # Replace with your MySQL username
    'password': 'komban',  # Replace with your MySQL password
    'database': 'feedback_db'
}

# Admin details
staff_id = 'admin123'
password = 'admin'  # Replace with a secure password
hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

# Connect to the database and insert the admin user
try:
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO admin_login (staff_id, password) VALUES (%s, %s)', 
                   (staff_id, hashed_password.decode('utf-8')))
    conn.commit()
    print("Admin user created successfully.")
except mysql.connector.Error as err:
    print(f"Error: {err}")
finally:
    cursor.close()
    conn.close()
