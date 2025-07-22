import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Mysql_123", 
        database="BookExchangeDB"
    )

def initialize_admin():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE is_admin=1")
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO users (name, email, password, is_admin) VALUES (%s, %s, %s, %s)",
                       ("Admin", "admin@bookexchange.com", "admin123", True))
        conn.commit()
    conn.close()
