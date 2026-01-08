from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from functools import wraps
from extensions import db
from models import Product, User

products_bp = Blueprint("products", __name__)

def validate_product(data):
    if not data:
        return "No data provided"
    if not data.get("name"):
        return "Product name is required"
    if not isinstance(data.get("price"), (int, float)):
        return "Price must be a number"
    if not isinstance(data.get("stock"), int):
        return "Stock must be an integer"
    return None


def admin_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        user = User.query.get(int(get_jwt_identity()))
        if not user or user.role != "admin":
            return jsonify({"error": "Admin access required"}), 403
        return fn(*args, **kwargs)
    return wrapper


@products_bp.route("/api/products", methods=["POST"])
@jwt_required()
def create_product():
    data = request.get_json()
    error = validate_product(data)

    if error:
        return jsonify({"error": error}), 400

    product = Product(
        name=data["name"],
        price=data["price"],
        stock=data["stock"],
        created_by=int(get_jwt_identity())
    )

    db.session.add(product)
    db.session.commit()

    return jsonify({
        "id": product.id,
        "name": product.name,
        "price": product.price,
        "stock": product.stock
    }), 201


@products_bp.route("/api/products", methods=["GET"])
@jwt_required()
def get_products():
    user_id = int(get_jwt_identity())
    products = Product.query.filter_by(created_by=user_id).all()

    return jsonify([
        {"id": p.id, "name": p.name, "price": p.price, "stock": p.stock}
        for p in products
    ]), 200


@products_bp.route("/api/products/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_product(id):
    user_id = int(get_jwt_identity())
    product = Product.query.filter_by(id=id, created_by=user_id).first()

    if not product:
        return jsonify({"error": "Unauthorized or not found"}), 403

    db.session.delete(product)
    db.session.commit()

    return jsonify({"message": "Product deleted"}), 200


@products_bp.route("/api/admin/users", methods=["GET"])
@admin_required
def get_all_users():
    users = User.query.all()
    return jsonify([
        {"id": u.id, "name": u.name, "email": u.email, "role": u.role}
        for u in users
    ]), 200
