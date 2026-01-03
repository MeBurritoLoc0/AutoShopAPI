from flask import request, jsonify

from . import inventory_bp
from .schemas import inventory_schema, inventories_schema
from ...extensions import db
from ...models import Inventory


# ---------- CREATE part ----------
@inventory_bp.route("/", methods=["POST"])
def create_part():
    data = request.get_json() or {}
    if "name" not in data or "price" not in data:
        return jsonify({"error": "name and price are required"}), 400

    part = inventory_schema.load(data)
    db.session.add(part)
    db.session.commit()
    return inventory_schema.jsonify(part), 201


# ---------- READ all parts ----------
@inventory_bp.route("/", methods=["GET"])
def get_parts():
    parts = Inventory.query.all()
    return inventories_schema.jsonify(parts), 200


# ---------- READ single part ----------
@inventory_bp.route("/<int:part_id>", methods=["GET"])
def get_part(part_id):
    part = Inventory.query.get_or_404(part_id)
    return inventory_schema.jsonify(part), 200


# ---------- UPDATE part ----------
@inventory_bp.route("/<int:part_id>", methods=["PUT", "PATCH"])
def update_part(part_id):
    part = Inventory.query.get_or_404(part_id)
    data = request.get_json() or {}

    # allow partial updates
    if "name" in data:
        part.name = data["name"]
    if "price" in data:
        part.price = data["price"]

    db.session.commit()
    return inventory_schema.jsonify(part), 200


# ---------- DELETE part
@inventory_bp.route("/<int:part_id>", methods=["DELETE"])
def delete_part(part_id):
    part = Inventory.query.get_or_404(part_id)
    db.session.delete(part)
    db.session.commit()
    return "", 204
