import secrets
from flask import Blueprint, request, jsonify
from db import get_db_connection
import bcrypt

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


def require_token():
    header = request.headers.get("Authorization")

    if not header or not header.startswith("Bearer "):
        return None, ({"error": "Missing or invalid token"}, 401)

    token = header.split(" ")[1]

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM Users WHERE auth_token=%s", (token,))
    user = cursor.fetchone()

    cursor.close()
    conn.close()

    if not user:
        return None, ({"error": "Invalid token"}, 401)

    return user, None

@auth_bp.post("/login")
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM Users WHERE email=%s", (email,))
    user = cursor.fetchone()

    if not user:
        cursor.close()
        conn.close()
        return {"error": "Invalid credentials"}, 401

    stored_hash = user["password"].encode()

    if not bcrypt.checkpw(password.encode(), stored_hash):
        cursor.close()
        conn.close()
        return {"error": "Invalid credentials"}, 401

   
    token = secrets.token_hex(32)

    
    cursor.execute("UPDATE Users SET auth_token=%s WHERE userID=%s", (token, user["userID"]))
    conn.commit()

    cursor.close()
    conn.close()

    return {"token": token, "role": user["role"], "userID": user["userID"]}

@auth_bp.post("/logout")
def logout():
    user, error = require_token()
    if error:
        return error

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE Users SET auth_token=NULL WHERE userID=%s", (user["userID"],))
    conn.commit()
    cursor.close()
    conn.close()

    return {"message": "Logged out"}
