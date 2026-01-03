from flask import request, jsonify
from sqlalchemy import func

from ...extensions import db, limiter, cache
from ...models import Mechanic, ServiceTicketMechanic
from . import mechanics_bp
from .schemas import mechanic_schema, mechanics_schema


# ---------- CREATE mechanic ----------
@mechanics_bp.route("/", methods=["POST"])
def create_mechanic():
    data = request.get_json() or {}

    if "name" not in data:
        return jsonify({"error": "name is required"}), 400

    mechanic = mechanic_schema.load(data)
    db.session.add(mechanic)
    db.session.commit()
    return mechanic_schema.jsonify(mechanic), 201


# ---------- READ one mechanic ----------
@mechanics_bp.route("/<int:mechanic_id>", methods=["GET"])
def get_mechanic(mechanic_id):
    mechanic = Mechanic.query.get_or_404(mechanic_id)
    return mechanic_schema.jsonify(mechanic), 200


# ---------- UPDATE mechanic ----------
@mechanics_bp.route("/<int:mechanic_id>", methods=["PUT"])
def update_mechanic(mechanic_id):
    mechanic = Mechanic.query.get_or_404(mechanic_id)
    data = request.get_json() or {}

    mechanic.name = data.get("name", mechanic.name)
    mechanic.email = data.get("email", mechanic.email)
    mechanic.phone = data.get("phone", mechanic.phone)
    mechanic.hire_date = data.get("hire_date", mechanic.hire_date)
    mechanic.hourly_rate = data.get("hourly_rate", mechanic.hourly_rate)

    db.session.commit()
    return mechanic_schema.jsonify(mechanic), 200


# ---------- DELETE mechanic ----------
@mechanics_bp.route("/<int:mechanic_id>", methods=["DELETE"])
def delete_mechanic(mechanic_id):
    mechanic = Mechanic.query.get_or_404(mechanic_id)
    db.session.delete(mechanic)
    db.session.commit()
    return "", 204


# ---------- GET all mechanics ----------
@mechanics_bp.route("/", methods=["GET"])
@cache.cached(timeout=30, key_prefix="all_mechanics")
@limiter.limit("20 per minute")
def get_mechanics():
    mechanics = Mechanic.query.all()
    return mechanics_schema.jsonify(mechanics), 200


# ---------- top workers ----------
@mechanics_bp.route("/top-workers", methods=["GET"])
def get_mechanics_by_ticket_count():
    """
    Mechanics ordered by how many service tickets they have worked on.
    """
    mechanics_with_counts = (
        db.session.query(
            Mechanic,
            func.count(ServiceTicketMechanic.id).label("ticket_count"),
        )
        .join(
            ServiceTicketMechanic,
            Mechanic.mechanic_id == ServiceTicketMechanic.mechanic_id,
        )
        .group_by(Mechanic.mechanic_id)
        .order_by(func.count(ServiceTicketMechanic.id).desc())
        .all()
    )

    result = []
    for mechanic, count in mechanics_with_counts:
        mech_data = mechanic_schema.dump(mechanic)
        mech_data["ticket_count"] = count
        result.append(mech_data)

    return jsonify(result), 200
