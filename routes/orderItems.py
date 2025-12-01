from flask import Blueprint, request, jsonify
from db import get_db_connection
from auth import require_token


orderitems_bp = Blueprint("orderitems", __name__, url_prefix="/orderitems")

# need to get all orderItems, get orderItems by billingID, create orderItems

@orderitems_bp.get("/")
def get_all_orderitems():
    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500
    
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
    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT orderitemID, bookID, billingID, price, order_type FROM OrderItems WHERE orderitemID = %s", (id,))
    orderitem = cursor.fetchone()
    cursor.close()
    conn.close()

    if orderitem is None:
        return jsonify({'error': 'OrderItem not found in database'}), 404
    
    return jsonify({'orderitem': orderitem})

@orderitems_bp.get("/billing/<int:id>")
def get_orderitem_by_billing(id):
    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT orderitemID, bookID, billingID, price, order_type FROM OrderItems WHERE billingID = %s", (id,))
    orderitems = cursor.fetchall()
    cursor.close()
    conn.close()

    if orderitems == []:
        return jsonify({'error': 'OrderItems not found in database'}), 404
    
    return jsonify({'orderitems': orderitems})

@orderitems_bp.post("/")
def create_orderitem():
    data = request.json
    bookID = int(data.get("bookID"))
    billingID = int(data.get("billingID"))
    price = float(data.get("price"))
    order_type = data.get("order_type")

    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)
    
    user, error = require_token()
    if error:
        return error
    
    cursor.execute("INSERT INTO OrderItems (bookID, billingID, price, order_type) VALUES (%s, %s, %s, %s)", (bookID, billingID, price, order_type))
    
    orderitem_id = cursor.lastrowid
    conn.commit()
    cursor.close()
    conn.close()

    return {
        "message": "Order Item created successfully",
        "orderitemID": orderitem_id
    }, 201