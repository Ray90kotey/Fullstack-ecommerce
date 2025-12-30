from flask import Flask, jsonify, abort , request
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (JWTManager, create_access_token, jwt_required, get_jwt_identity)

app = Flask(__name__)
CORS(app)

app.config["JWT_SECRET_KEY"] = "super-secret"  # Change this in a real application
jwt = JWTManager(app)

# Temporary in-memory data store
products = [
    {"id": 1, 
     "name": "Laptop", 
     "price": 999.99, 
     "Grade": "A"},
    {"id": 2, 
     "name": "Smartphone", 
     "price": 499.99, 
     "Grade": "A"},
    {"id": 3, 
     "name": "Headphones", 
     "price": 199.99,
     "Grade": "B"
     },
]
users = []
def create_user(email, password):
  hashed_password = generate_password_hash(password)
  user = {
    "id": len(users) + 1,
    "email": email,
    "password": hashed_password
  }
  users.append(user)
  return user

def get_user_by_email(email):
  return next((user for user in users if user["email"] == email), None)

@app.route("/")
def home():
    return jsonify({
      "message": "ecommerce backend is running"
      })
  
@app.route("/api/products", methods=["GET"]) 
def get_products():
    return jsonify(products) 
   

@app.route("/api/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
  product = next((p for p in products if p["id"] == product_id), None)
  if product is None:
    abort(404)
  return jsonify(product)

@app.route("/api/products", methods=["POST"])
@jwt_required()
def add_product():
    current_user = get_jwt_identity()

    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400

    name = data.get("name")
    price = data.get("price")
    stock = data.get("stock")

    if not name or price is None or stock is None:
        return jsonify({"error": "All fields required"}), 400

    product = {
        "id": len(products) + 1,
        "name": name,
        "price": price,
        "stock": stock,
        "created_by": current_user
    }

    products.append(product)
    return jsonify(product), 201

@app.route("/api/register", methods=["POST"])
def register_user():
  data = request.get_json()
  if not data:
    return jsonify({"error": "no data provided"}), 400
  
  email = data.get("email")
  password = data.get("password")
  
  if not email or not password:
    return jsonify({"error": "missing fields"}), 400
  if get_user_by_email(email):
    return jsonify({"error": "User already exists"}), 400
  
  user = create_user(email, password)
  return jsonify({"message": "user registration successful", "id": user["id"], "email": user["email"]}), 201

@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    user = get_user_by_email(email)

    if not user:
        return jsonify({"error": "Invalid email or password"}), 401

    if not check_password_hash(user["password"], password):
        return jsonify({"error": "Invalid email or password"}), 401

    access_token = create_access_token(identity=user["email"])

    return jsonify({
        "message": "Login successful",
        "access_token": access_token,
        "user": {
            "id": user["id"],
            "email": user["email"]
        }
    }), 200
  
if __name__ == "__main__":
    app.run(debug=True)