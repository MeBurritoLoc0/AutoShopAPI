from flask import request, jsonify

from . import service_tickets_bp
from .schemas import service_ticket_schema, service_tickets_schema
from ...extensions import db
from ...models import (
    ServiceTicket,
    Mechanic,
    ServiceTicketMechanic,
    Inventory,
    ServiceTicketInventory,
)
from ...auth import token_required


# ---------- BASIC SERVICE TICKET CRUD ----------

@service_tickets_bp.route("/", methods=["POST"])
def create_service_ticket():
    data = request.get_json() or {}

    if "customer_id" not in data:
        return jsonify({"error": "customer_id is required"}), 400

    ticket = service_ticket_schema.load(data)
    db.session.add(ticket)
    db.session.commit()
    return service_ticket_schema.jsonify(ticket), 201


@service_tickets_bp.route("/", methods=["GET"])
def get_service_tickets():
    tickets = ServiceTicket.query.all()
    return service_tickets_schema.jsonify(tickets), 200


@service_tickets_bp.route("/my-tickets", methods=["GET"])
@token_required
def get_my_tickets(customer_id):
    tickets = ServiceTicket.query.filter_by(customer_id=customer_id).all()
    return service_tickets_schema.jsonify(tickets), 200


# ---------- assign and remove single mechanic  ----------

@service_tickets_bp.route(
    "/<int:ticket_id>/assign-mechanic/<int:mechanic_id>",
    methods=["PUT"],
)
def assign_mechanic(ticket_id, mechanic_id):
    ticket = ServiceTicket.query.get_or_404(ticket_id)
    mechanic = Mechanic.query.get_or_404(mechanic_id)

    existing_link = next(
        (link for link in ticket.mechanics if link.mechanic_id == mechanic_id),
        None,
    )
    if existing_link:
        return service_ticket_schema.jsonify(ticket), 200

    link = ServiceTicketMechanic(
        ticket=ticket,
        mechanic=mechanic,
        hours_worked=0,
    )
    db.session.add(link)
    db.session.commit()
    return service_ticket_schema.jsonify(ticket), 200


@service_tickets_bp.route(
    "/<int:ticket_id>/remove-mechanic/<int:mechanic_id>",
    methods=["PUT"],
)
def remove_mechanic(ticket_id, mechanic_id):
    ticket = ServiceTicket.query.get_or_404(ticket_id)

    link = next(
        (link for link in ticket.mechanics if link.mechanic_id == mechanic_id),
        None,
    )
    if not link:
        return jsonify({"error": "Mechanic not assigned to this ticket"}), 404

    db.session.delete(link)
    db.session.commit()
    return service_ticket_schema.jsonify(ticket), 200


# ---------- edit multiple mechanics for one ticket ----------

@service_tickets_bp.route("/<int:ticket_id>/edit", methods=["PUT"])
def edit_ticket_mechanics(ticket_id):
    """
    Body example:
    {
      "add_ids": [1, 3],
      "remove_ids": [2]
    }
    """

    ticket = ServiceTicket.query.get_or_404(ticket_id)
    data = request.get_json() or {}

    add_ids = data.get("add_ids") or []
    remove_ids = data.get("remove_ids") or []

    # Build a map of current mechanic links for this ticket
    current_links = {link.mechanic_id: link for link in ticket.mechanics}

    # ---- ADD mechanics ----
    for mech_id in add_ids:
        if mech_id in current_links:
            continue

        mechanic = Mechanic.query.get(mech_id)
        if not mechanic:
            continue

        link = ServiceTicketMechanic(
            ticket=ticket,
            mechanic=mechanic,
            hours_worked=0,
        )
        db.session.add(link)

    # ---- REMOVE mechanics ----
    for mech_id in remove_ids:
        link = current_links.get(mech_id)
        if link:
            db.session.delete(link)

    db.session.commit()
    return service_ticket_schema.jsonify(ticket), 200


# ---------- add single part to ticket ----------

@service_tickets_bp.route("/<int:ticket_id>/add-part", methods=["POST"])
def add_part_to_ticket(ticket_id):
    """
    Body example:
    {
      "inventory_id": 5
    }
    """
    ticket = ServiceTicket.query.get_or_404(ticket_id)
    data = request.get_json() or {}

    inventory_id = data.get("inventory_id")
    if not inventory_id:
        return jsonify({"error": "inventory_id is required"}), 400

    part = Inventory.query.get(inventory_id)
    if not part:
        return jsonify({"error": "Inventory item not found"}), 404

    # check if this part is already linked to the ticket
    existing_link = (
        ServiceTicketInventory.query
        .filter_by(ticket_id=ticket.id, inventory_id=part.id)
        .first()
    )
    if existing_link:
        return jsonify({"message": "Part already added to this ticket"}), 200

    link = ServiceTicketInventory(ticket=ticket, part=part)
    db.session.add(link)
    db.session.commit()

    return service_ticket_schema.jsonify(ticket), 200
