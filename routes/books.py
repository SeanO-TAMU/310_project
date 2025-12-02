from flask import Blueprint, request, jsonify
from db import get_db_connection

from auth import require_token 

books_bp = Blueprint("books", __name__, url_prefix="/books")

@books_bp.get("/")
def get_all_books():
    user, error = require_token()
    if error:
        return error
    
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
    user, error = require_token()
    if error:
        return error
    
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

@books_bp.get("/search")
def search_books():
    user, error = require_token()
    if error:
        return error
    
    query = request.args.get("query", "")
    if query == "":
        return {"error": "Missing search query"}, 400
    
    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)
    
    param = query + "%"
    
    cursor.execute("SELECT * FROM Books WHERE title LIKE %s or author LIKE %s", (param, param))
    books = cursor.fetchall()
    cursor.close()
    conn.close()

    if books == []:
        return jsonify({'error': 'No matching books in database'}), 404
    
    return jsonify({'books': books})
    


# need auth token on the below routes, also need to check for role
@books_bp.post("/")
def create_book():
    data = request.json
    title = data.get("title")
    author = data.get("author")
    rental_price = float(data.get("rental_price"))
    buy_price = float(data.get("buy_price"))
    quantity = int(data.get("quantity"))

    user, error = require_token()
    if error:
        return error
    
    if user["role"] != "manager":
        return {"error": "Forbidden"}, 403

    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("INSERT INTO Books (title, author, rental_price, buy_price, quantity) VALUES (%s, %s, %s, %s, %s)", (title, author, rental_price, buy_price, quantity))
    conn.commit()
    cursor.close()
    conn.close()

    return {"message": "Book created successfully"}, 201


# think about how we need to handle update. Do we want users to be able to change quantity available when they make an order?
@books_bp.put("/<int:id>")
def update_book(id):
    data = request.json
    title = data.get("title")
    author = data.get("author")
    rental_price = float(data.get("rental_price"))
    buy_price = float(data.get("buy_price"))
    quantity = int(data.get("quantity"))

    user, error = require_token()
    if error:
        return error
    
    if user["role"] != "manager":
        return {"error": "Forbidden"}, 403

    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("UPDATE Books SET title=%s, author=%s, rental_price=%s, buy_price=%s, quantity=%s WHERE bookID=%s", (title, author, rental_price, buy_price, quantity, id))
    conn.commit()
    cursor.close()
    conn.close()

    return {"message": "Book updated successfully"}, 200