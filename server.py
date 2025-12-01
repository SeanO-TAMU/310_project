from flask import Flask, jsonify, request

from routes.users import users_bp
from routes.books import books_bp
from routes.auth import auth_bp
from routes.billings import billings_bp

app = Flask(__name__)

app.register_blueprint(users_bp)
app.register_blueprint(users_bp)

if __name__ == '__main__':
    app.run(debug=True)