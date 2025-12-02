from flask import Blueprint, request, jsonify
from db import get_db_connection
from datetime import datetime

from .auth import require_token


# need a get all billings, get a single billing, create billing, update billing payment status

billings_bp = Blueprint("billings", __name__, url_prefix="/billings")


@billings_bp.get("/")
def get_all_billings():
    user, error = require_token()
    if error:
        return error
    
    if user["role"] != "manager":
        return {"error": "Forbidden"}, 403
    
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
    user, error = require_token()
    if error:
        return error
    
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

    if user["role"] != "manager" and user["userID"] != billing["userID"]:
        return {"error": "Forbidden"}, 403
    
    return jsonify({'billing': billing})

# need a route here that compiles all orders into an email for the customer
@billings_bp.post("/")
def create_billing():
    user, error = require_token()
    if error:
        return error
    
    if user["role"] == "manager":
        return {"error": "Forbidden"}, 403
    
    data = request.json
    total_cost = float(data.get("total_cost"))

    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("INSERT INTO Billings (userID, order_date, total_cost) VALUES (%s, %s, %s)", (user["userID"], datetime.now(),total_cost))
    
    billing_id = cursor.lastrowid
    conn.commit()
    cursor.close()
    conn.close()

    return {
        "message": "Billing created successfully",
        "billingID": billing_id
    }, 201

@billings_bp.put("/<int:id>")
def update_billing(id):
    user, error = require_token()
    if error:
        return error
    
    if user["role"] != "manager":
        return {"error": "Forbidden"}, 403

    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)

    
    cursor.execute("SELECT status FROM Billings WHERE billingID = %s", (id,))
    billing = cursor.fetchone()

    if billing is None:
        return jsonify({'error': 'Billing not found in database'}), 404

    status = ""
    if billing["status"] == "pending":
        status = "paid"
    else:
        return {"error": "Already paid"}, 403

    cursor.execute("UPDATE Billings SET status=%s WHERE billingID=%s", (status, id))
    conn.commit()
    cursor.close()
    conn.close()

    return {"message": "Billing updated successfully"}, 200