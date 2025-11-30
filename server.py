from flask import Flask, jsonify, request
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

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


# --- API Endpoints ---

# @app.route('/student/<int:id>', methods=['GET'])
# def get_student(id):
#     conn = get_db_connection()
#     if conn is None:
#         return jsonify({'error': 'Database connection failed'}), 500

#     cursor = conn.cursor(dictionary=True)
#     cursor.execute("SELECT id, name, address FROM Students WHERE id = %s", (id,))
#     student = cursor.fetchone()
#     cursor.close()
#     conn.close()

#     if student is None:
#         return jsonify({'error': 'Student not found'}), 404
#     return jsonify({'student': student})


if __name__ == '__main__':
    app.run(debug=True)