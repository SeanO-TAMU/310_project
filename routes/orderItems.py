from flask import Blueprint, request, jsonify
from db import get_db_connection
from .auth import require_token

orderitems_bp = Blueprint("orderitems", __name__, url_prefix="/orderitems")

# need to get all orderItems, get orderItems by billingID, create orderItems

@orderitems_bp.get("/")
def get_all_orderitems():
    user, error = require_token()
    if error:
        return error
    
    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500
    
    if user["role"] != "manager":
        return {"error": "Forbidden"}, 403
    
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM OrderItems")
    orderitems = cursor.fetchall()
    cursor.close()
    conn.close()

    if orderitems == []:
        return jsonify({'error': 'No orderitems in database'}), 404
    
    return jsonify({'orderitems': orderitems})


@orderitems_bp.get("/<int:id>")
def get_orderitem(id):
    user, error = require_token()
    if error:
        return error
    
    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT orderitemID, bookID, billingID, price, order_type FROM OrderItems WHERE orderitemID = %s", (id,))
    orderitem = cursor.fetchone()

    if orderitem is None:
        return jsonify({'error': 'OrderItem not found in database'}), 404

    #check to make sure user is either a manager or the userid matches the one that is in the borderItems billing
    cursor.execute("SELECT userID from Billings WHERE billingID = %s", (orderitem["billingID"],))
    billing = cursor.fetchone()

    if user["role"] != "manager" and billing["userID"] != user["userID"]:
        return {"error": "Forbidden"}, 403

    cursor.close()
    conn.close()

    
    return jsonify({'orderitem': orderitem})

@orderitems_bp.get("/billing/<int:id>")
def get_orderitems_by_billing(id):
    user, error = require_token()
    if error:
        return error
    
    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT orderitemID, bookID, billingID, price, order_type FROM OrderItems WHERE billingID = %s", (id,))
    orderitems = cursor.fetchall()

    if orderitems == []:
        return jsonify({'error': 'OrderItems not found in database'}), 404

    cursor.execute("SELECT userID from Billings WHERE billingID = %s", (id,))
    billingID = cursor.fetchone()

    if user["role"] != "manager" and billingID["userID"] != user["userID"]:
        return {"error": "Forbidden"}, 403

    cursor.close()
    conn.close()
    
    return jsonify({'orderitems': orderitems})

@orderitems_bp.post("/")
def create_orderitem():
    data = request.json
    bookID = int(data.get("bookID"))
    billingID = int(data.get("billingID"))
    price = float(data.get("price"))
    order_type = data.get("order_type")

    user, error = require_token()
    if error:
        return error

    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)
    
    if user["role"] == "manager":
        return {"error": "Forbidden"}, 403
    
    cursor.execute("SELECT userID FROM Billings WHERE billingID = %s", (billingID,))
    billing = cursor.fetchone()

    if billing is None:
        return {"error": "Billing not found"}, 404
    
    if billing["userID"] != user["userID"]:
        return {"error": "Forbidden"}, 403
    
    cursor.execute("INSERT INTO OrderItems (bookID, billingID, price, order_type) VALUES (%s, %s, %s, %s)", (bookID, billingID, price, order_type))
    
    orderitem_id = cursor.lastrowid
    conn.commit()
    cursor.close()
    conn.close()

    return {
        "message": "Order Item created successfully",
        "orderitemID": orderitem_id
    }, 201