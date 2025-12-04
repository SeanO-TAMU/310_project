import secrets
from flask import Blueprint, request, jsonify
from db import get_db_connection
import bcrypt
import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
load_dotenv()

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
    name = data.get("name")
    password = data.get("password")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM Users WHERE name=%s", (name,))
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

@auth_bp.post("/send_email")
def email_route():
    user, error = require_token()
    if error:
        return error

    data = request.json
    billing_id = data.get("billing_id")

    if not billing_id:
        return {"error": "billing_id required"}, 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # get billing + user email
    cursor.execute("""
        SELECT Billings.billingID, Billings.total_cost, Billings.order_date,
               Users.email, Users.name
        FROM Billings
        JOIN Users ON Billings.userID = Users.userID
        WHERE Billings.billingID=%s
    """, (billing_id,))
    billing = cursor.fetchone()

    if not billing:
        cursor.close()
        conn.close()
        return {"error": "Billing not found"}, 404

    # get order items
    cursor.execute("""
        SELECT OrderItems.orderitemID, OrderItems.bookID, OrderItems.price,
               OrderItems.order_type, Books.title
        FROM OrderItems
        JOIN Books ON OrderItems.bookID = Books.bookID
        WHERE OrderItems.billingID=%s
    """, (billing_id,))
    items = cursor.fetchall()

    cursor.close()
    conn.close()

    # email body text
    body = (
        f"Hello {billing['name']},\n\n"
        f"Your billing summary:\n"
        f"Billing ID: {billing['billingID']}\n"
        f"Date: {billing['order_date']}\n"
        f"Total: ${billing['total_cost']}\n\n"
        "Items:\n"
    )

    for item in items:
        body += f"- {item['title']} (${item['price']}) [{item['order_type']}]\n"

    body += "\nThank you!"

    # send email
    success = send_email(billing["email"], "Your Billing Receipt", body)

    if success:
        return {"message": "Email sent"}, 200
    else:
        return {"error": "Failed to send email"}, 500

def send_email(to_email, subject, body):
    sender = os.getenv("EMAIL_ADDRESS")
    password = os.getenv("EMAIL_PASSWORD")

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = to_email

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.sendmail(sender, to_email, msg.as_string())

        return True
    except Exception as e:
        print("Email error:", e)
        return False