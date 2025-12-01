from flask import Blueprint, request, jsonify
from db import get_db_connection
from auth import require_token
from datetime import datetime


# need a get all billings, get a single billing, create billing, update billing payment status

billings_bp = Blueprint("billings", __name__, url_prefix="/billings")


@billings_bp.get("/")
def get_all_billings():
    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM Billings")
    billings = cursor.fetchall()
    cursor.close()
    conn.close()

    if billings == []:
        return jsonify({'error': 'No billings in database'}), 404
    
    return jsonify({'billings': billings})


@billings_bp.get("/<int:id>")
def get_billing(id):
    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT billingID, userID, order_date, total_cost, status FROM Billings WHERE billingID = %s", (id,))
    billing = cursor.fetchone()
    cursor.close()
    conn.close()

    if billing is None:
        return jsonify({'error': 'Billing not found in database'}), 404
    
    return jsonify({'billing': billing})

@billings_bp.post("/")
def create_billing():
    data = request.json
    total_cost = float(data.get("total_cost"))

    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)
    
    user, error = require_token()
    if error:
        return error
    
    cursor.execute("INSERT INTO Billings (userID, order_date, total_cost) VALUES (%s, %s, %s)", (user["userID"], datetime.now(),total_cost))
    conn.commit()
    cursor.close()
    conn.close()

    return {"message": "Billing created successfully"}, 201

@billings_bp.put("/<int:id>")
def update_billing(id):
    data = request.json

    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)

    user, error = require_token()
    if error:
        return error

    if user["role"] != "manager":
        return {"error": "Forbidden"}, 403
    
    cursor.execute("SELECT status FROM Billings WHERE billingID = %s", (id,))
    billing = cursor.fetchone()

    if billing is None:
        return jsonify({'error': 'Billing not found in database'}), 404

    status = ""
    if billing["status"] == "pending":
        status = "paid"
    else:
        status = "pending"

    cursor.execute("UPDATE Billings SET status=%s WHERE billingID=%s", (status, id))
    conn.commit()
    cursor.close()
    conn.close()

    return {"message": "Billing updated successfully"}, 201