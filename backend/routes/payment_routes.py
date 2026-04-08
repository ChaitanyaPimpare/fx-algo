import razorpay
from flask import Blueprint, request, jsonify
from config import Config
import os
from werkzeug.utils import secure_filename
from datetime import datetime
from models.order import Order
from extensions import db

payment_bp = Blueprint("payment", __name__)

client = razorpay.Client(
    auth=(Config.RAZORPAY_KEY_ID, Config.RAZORPAY_KEY_SECRET)
)

# CREATE RAZORPAY ORDER
@payment_bp.post("/create-order")
def create_order():

    data = request.json
    order_id = data.get("order_id")
    amount = int(data.get("amount"))

    # create razorpay order
    razorpay_order = client.order.create({
        "amount": amount,
        "currency": "INR",
        "payment_capture": 1,
        "notes": {
            "order_id": order_id
        }
    })

    # SAVE RAZORPAY ORDER ID
    from models.order import Order
    from extensions import db

    order = Order.query.get(order_id)
    order.razorpay_order_id = razorpay_order["id"]
    db.session.commit()

    return jsonify({
        "key": Config.RAZORPAY_KEY_ID,
        "razorpay_order_id": razorpay_order["id"],
        "amount": razorpay_order["amount"]
    })

import hmac
import hashlib
from extensions import db
from models.order import Order

@payment_bp.post("/verify")
def verify_payment():

    data = request.json

    order_id = data["order_id"]
    razorpay_order_id = data["razorpay_order_id"]
    razorpay_payment_id = data["razorpay_payment_id"]
    razorpay_signature = data["razorpay_signature"]

    generated_signature = hmac.new(
        bytes(Config.RAZORPAY_KEY_SECRET, 'utf-8'),
        bytes(razorpay_order_id + "|" + razorpay_payment_id, 'utf-8'),
        hashlib.sha256
    ).hexdigest()

    if generated_signature != razorpay_signature:
        return {"error": "Invalid payment"}, 400

    order = Order.query.get(order_id)
    order.status = "paid"
    order.payment_status = "paid"
    order.razorpay_payment_id = razorpay_payment_id
    order.razorpay_signature = razorpay_signature

    db.session.commit()

    return {"message": "Payment verified"}

UPLOAD_FOLDER = "uploads/payment_proofs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@payment_bp.post("/upload-proof/<int:order_id>")
def upload_proof(order_id):

    order = Order.query.get(order_id)
    if not order:
        return {"error": "Order not found"}, 404

    file = request.files.get("screenshot")
    if not file:
        return {"error": "Screenshot required"}, 400

    filename = secure_filename(f"order_{order_id}_{file.filename}")
    path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(path)

    # mark awaiting admin approval
    order.payment_proof = path
    order.payment_status = "pending_verification"

    db.session.commit()

    return {"message": "Payment proof uploaded"}