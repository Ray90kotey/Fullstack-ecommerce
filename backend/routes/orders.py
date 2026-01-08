from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import Order, OrderItem, Product

orders_bp = Blueprint("orders", __name__)


@orders_bp.route("/api/checkout", methods=["POST"])
@jwt_required()
def checkout():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    if not data or "items" not in data:
        return jsonify({"error": "No items provided"}), 400

    items = data["items"]
    if not isinstance(items, list) or not items:
        return jsonify({"error": "Items must be a non-empty list"}), 400

    try:
        total = 0
        order = Order(user_id=user_id, total_amount=0)
        db.session.add(order)
        db.session.flush()  # get order.id

        for item in items:
            product_id = item.get("product_id")
            quantity = item.get("quantity")

            if not product_id or not isinstance(quantity, int) or quantity <= 0:
                db.session.rollback()
                return jsonify({"error": "Invalid product or quantity"}), 400

            product = Product.query.get(product_id)

            if not product or product.stock < quantity:
                db.session.rollback()
                return jsonify({"error": "Invalid product or insufficient stock"}), 400

            subtotal = product.price * quantity
            total += subtotal

            product.stock -= quantity

            db.session.add(OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=quantity,
                price=product.price
            ))

        order.total_amount = total
        db.session.commit()

        return jsonify({
            "message": "Order placed",
            "order_id": order.id,
            "total": total
        }), 201

    except Exception:
        db.session.rollback()
        return jsonify({"error": "Checkout failed"}), 500


@orders_bp.route("/api/orders", methods=["GET"])
@jwt_required()
def get_orders():
    user_id = int(get_jwt_identity())
    orders = Order.query.filter_by(user_id=user_id).all()

    return jsonify([
        {
            "id": o.id,
            "total": o.total_amount,
            "status": o.status,
            "created_at": o.created_at.isoformat()
        }
        for o in orders
    ]), 200


@orders_bp.route("/api/pay/<int:order_id>", methods=["POST"])
@jwt_required()
def pay_order(order_id):
    user_id = int(get_jwt_identity())

    order = Order.query.filter_by(id=order_id, user_id=user_id).first()

    if not order:
        return jsonify({"error": "Order not found"}), 404

    if order.status == "paid":
        return jsonify({"message": "Order already paid"}), 400

    # Simulated payment success
    order.status = "paid"
    db.session.commit()

    return jsonify({
        "message": "Payment successful",
        "order_id": order.id,
        "status": order.status
    }), 200
