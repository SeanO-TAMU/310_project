from flask import Blueprint, request, jsonify
from db import get_db_connection

books_bp = Blueprint("books", __name__, url_prefix="/books")

@books_bp.get("/")
def get_all_books():
    pass

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

@books_bp.post("/")
def create_book():
    pass

@books_bp.put("/<int:id>")
def update_book():
    pass