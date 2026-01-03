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

app = Flask(__name__)
CORS(
    app,
    resources={r"/api/*": {"origins": "*"}},
    supports_credentials=True
)


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = "super-secret-key-change-this"
app.config["JWT_TOKEN_LOCATION"] = ["headers"]

db = SQLAlchemy(app)
jwt = JWTManager(app)


# ===================== MODELS =====================

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    created_by = db.Column(db.Integer, nullable=False)


# ===================== ROUTES =====================

@app.route("/")
def home():
    return jsonify({"message": "ecommerce backend is running"})


@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not name or not email or not password:
        return jsonify({"error": "All fields are required"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already exists"}), 409

    user = User(
        name=name,
        email=email,
        password=generate_password_hash(password)
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password, password):
        return jsonify({"error": "Invalid email or password"}), 401

    token = create_access_token(identity=str(user.id))


    return jsonify({
        "access_token": token,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email
        }
    }), 200


@app.route("/api/products", methods=["POST"])
@jwt_required()
def create_product():
    data = request.get_json()

    name = data.get("name")
    price = data.get("price")
    stock = data.get("stock")

    if not name or price is None or stock is None:
        return jsonify({"error": "All fields are required"}), 400

    user_id = int(get_jwt_identity())

    product = Product(
        name=name,
        price=price,
        stock=stock,
        created_by=user_id
    )

    db.session.add(product)
    db.session.commit()

    return jsonify({
        "id": product.id,
        "name": product.name,
        "price": product.price,
        "stock": product.stock
    }), 201


@app.route("/api/products", methods=["GET"])
@jwt_required()
def get_products():
    user_id = int(get_jwt_identity())


    products = Product.query.filter_by(created_by=user_id).all()

    return jsonify([
        {
            "id": p.id,
            "name": p.name,
            "price": p.price,
            "stock": p.stock
        }
        for p in products
    ]), 200


@app.route("/api/products/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_product(id):
    user_id = int(get_jwt_identity())


    product = Product.query.filter_by(id=id, created_by=user_id).first()

    if not product:
        return jsonify({"error": "Unauthorized or not found"}), 403

    db.session.delete(product)
    db.session.commit()

    return jsonify({"message": "Product deleted"}), 200


# ===================== RUN =====================

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
