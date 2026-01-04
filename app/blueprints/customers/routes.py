from flask import request, jsonify, abort
from marshmallow import ValidationError

from ...extensions import db, ma, limiter, cache
from ...models import Customer
from ...auth import encode_token, token_required

from . import customers_bp
from .schemas import customer_schema, customers_schema, login_schema


# ---------- login route
@customers_bp.route("/login", methods=["POST"])
def login():
    """
    Login with email + password.
    Returns a JWT token if credentials are valid.
    """
    try:
        data = login_schema.load(request.get_json() or {})
    except ValidationError as err:
        return jsonify(err.messages), 400

    email = data["email"]
    password = data["password"]

    customer = Customer.query.filter_by(email=email).first()

    if not customer or customer.password != password:
        return jsonify({"error": "Invalid email or password"}), 401

    token = encode_token(customer.id)
    return jsonify({"token": token}), 200


# ---------- CRUD routes

# CREATE customer
@customers_bp.route("/", methods=["POST"])
def create_customer():
    try:
        data = customer_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400

    db.session.add(data)
    db.session.commit()
    return customer_schema.jsonify(data), 201


# READ all customers
@customers_bp.route("/", methods=["GET"])
@limiter.limit("20 per minute")
@cache.cached(timeout=20, query_string=True)
def get_customers():
    
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    pagination = Customer.query.paginate(page=page, per_page=per_page, error_out=False)

    data = {
        "items": customers_schema.dump(pagination.items),
        "page": page,
        "per_page": per_page,
        "total": pagination.total,
        "pages": pagination.pages,
    }
    return jsonify(data), 200


# UPDATE customer
@limiter.limit("10 per minute")
@customers_bp.route("/<int:customer_id>", methods=["PUT", "PATCH"])
def update_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)

    try:
        data = customer_schema.load(request.json, partial=True)
    except ValidationError as err:
        return jsonify(err.messages), 400

    # because load_instance=True, data is a Customer-like object
    customer.name = data.name if getattr(data, "name", None) is not None else customer.name
    customer.email = data.email if getattr(data, "email", None) is not None else customer.email
    customer.phone = data.phone if getattr(data, "phone", None) is not None else customer.phone

    db.session.commit()
    return customer_schema.jsonify(customer), 200


# DELETE customer
@limiter.limit("5 per minute")
@customers_bp.route("/<int:customer_id>", methods=["DELETE"])
def delete_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    db.session.delete(customer)
    db.session.commit()
    return "", 204



@customers_bp.route("/<int:customer_id>", methods=["GET"])
def get_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    return customer_schema.jsonify(customer), 200