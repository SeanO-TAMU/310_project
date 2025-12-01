import mysql.connector
from mysql.connector import Error
# --- Database Configuration ---
db_config = {
    'host': 'localhost',
    'database': 'library',
    'user': 'root',      # <-- IMPORTANT: Change to your MySQL username
    'password': 'maggie1641' # <-- IMPORTANT: Change to your MySQL password
}

# --- Helper Function to get DB connection ---
def get_db_connection():
    """Establishes a connection to the database."""
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except Error as e:
        print(f"Error connecting to MySQL database: {e}")
        return None
