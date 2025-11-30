from flask import Blueprint, request, jsonify
from db import get_db_connection

from auth import require_token 

books_bp = Blueprint("books", __name__, url_prefix="/books")

@books_bp.get("/")
def get_all_books():
    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM Books")
    books = cursor.fetchall()
    cursor.close()
    conn.close()

    if books == []:
        return jsonify({'error': 'No books in database'}), 404
    
    return jsonify({'books': books})

@books_bp.get("/<int:id>")
def get_book(id):
    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT bookID, title, author, rental_price, buy_price, quantity FROM Books WHERE bookID = %s", (id,))
    book = cursor.fetchone()
    cursor.close()
    conn.close()

    if book is None:
        return jsonify({'error': 'Book not found'}), 404
    
    return jsonify({'book': book})



# need auth token on the below routes, also need to check for role
@books_bp.post("/")
def create_book():
    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)

@books_bp.put("/<int:id>")
def update_book():
    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)

    user, error = require_token()
    if error:
        return error

    if user["role"] != "manager":
        return {"error": "Forbidden"}, 403