from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity
)

# ✅ CREATE APP FIRST
app = Flask(__name__)
CORS(app)

# ✅ CONFIGURE APP AFTER CREATION
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = "super-secret-key-change-this"

# ✅ INIT EXTENSIONS AFTER CONFIG
db = SQLAlchemy(app)
jwt = JWTManager(app)


# Temporary in-memory data store
@app.route("/api/products", methods=["POST"])
@jwt_required()
def create_product():
    data = request.get_json()

    name = data.get("name")
    price = data.get("price")
    stock = data.get("stock")

    current_user_id = get_jwt_identity()

    product = Product(
        name=name,
        price=price,
        stock=stock,
        created_by=current_user_id
    )

    db.session.add(product)
    db.session.commit()

    return jsonify({
        "id": product.id,
        "name": product.name,
        "price": product.price,
        "stock": product.stock,
        "created_by": product.created_by
    }), 201


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default="user")

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    created_by = db.Column(db.String(120))



def create_user(email, password):
    user = User(
        email=email,
        password=generate_password_hash(password)
    )
    db.session.add(user)
    db.session.commit()
    return user


def get_user_by_email(email):
    return User.query.filter_by(email=email).first()


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
  with app.app_context():
      db.create_all()
      app.run(debug=True)