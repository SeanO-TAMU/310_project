from flask import Blueprint, request, jsonify
from db import get_db_connection
import bcrypt
from .auth import require_token

# use this when creating salted password, the below is what should be stored in db
# hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
users_bp = Blueprint("users", __name__, url_prefix="/users")

# used to create the user when logging in
# call the login route in the frontend after this one completes
@users_bp.post("/")
def create_user():
    data = request.json
    name = data.get("name")
    email = data.get("email")

    if not name or not email or not data.get("password"):
        return jsonify({"error": "Missing required fields"}), 400

    password = bcrypt.hashpw(data.get("password").encode(), bcrypt.gensalt()).decode()

    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT userID FROM Users WHERE email=%s", (email,))
    if cursor.fetchone():
        cursor.close()
        conn.close()
        return {"error": "Email already exists"}, 409

    cursor.execute("INSERT INTO Users (name, email, password) VALUES (%s, %s, %s)", (name, email, password))
    conn.commit()
    cursor.close()
    conn.close()

    return {"message": "User created successfully"}, 201


@users_bp.post("/manager")
def create_manager():
    data = request.json
    name = data.get("name")
    email = data.get("email")

    if not name or not email or not data.get("password"):
        return jsonify({"error": "Missing required fields"}), 400

    password = bcrypt.hashpw(data.get("password").encode(), bcrypt.gensalt()).decode()

    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT userID FROM Users WHERE email=%s", (email,))
    if cursor.fetchone():
        cursor.close()
        conn.close()
        return {"error": "Email already exists"}, 409

    cursor.execute("INSERT INTO Users (name, email, password, role) VALUES (%s, %s, %s, %s)", (name, email, password, 'manager'))
    conn.commit()
    cursor.close()
    conn.close()

    return {"message": "Manager created successfully"}, 201



