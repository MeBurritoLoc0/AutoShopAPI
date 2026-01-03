from .extensions import db


class Customer(db.Model):
    __tablename__ = "customers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    phone = db.Column(db.String(20))
    password = db.Column(db.String(128), nullable=False)

    # One customer to many service tickets
    service_tickets = db.relationship(
        "ServiceTicket",
        back_populates="customer",
        cascade="all, delete-orphan",
    )


class Mechanic(db.Model):
    __tablename__ = "mechanics"

    mechanic_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True)
    phone = db.Column(db.String(20))
    hire_date = db.Column(db.Date)
    hourly_rate = db.Column(db.Numeric(10, 2))

    # One mechanic to many service_ticket_mechanics rows
    service_ticket_links = db.relationship(
        "ServiceTicketMechanic",
        back_populates="mechanic",
        cascade="all, delete-orphan",
    )


class ServiceTicket(db.Model):
    __tablename__ = "service_tickets"

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(
        db.Integer,
        db.ForeignKey("customers.id"),
        nullable=False,
    )
    service_date = db.Column(db.Date)
    description = db.Column(db.String(255))
    car_vin = db.Column(db.String(50))
    status = db.Column(db.String(50))
    total_cost = db.Column(db.Numeric(10, 2))

    # relationships
    customer = db.relationship("Customer", back_populates="service_tickets")

    mechanics = db.relationship(
        "ServiceTicketMechanic",
        back_populates="ticket",
        cascade="all, delete-orphan",
    )

    # new relationship to parts (inventory items) via junction table
    parts = db.relationship(
        "ServiceTicketInventory",
        back_populates="ticket",
        cascade="all, delete-orphan",
    )


class ServiceTicketMechanic(db.Model):
    __tablename__ = "service_ticket_mechanics"

    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(
        db.Integer,
        db.ForeignKey("service_tickets.id"),
        nullable=False,
    )
    mechanic_id = db.Column(
        db.Integer,
        db.ForeignKey("mechanics.mechanic_id"),
        nullable=False,
    )
    hours_worked = db.Column(db.Numeric(10, 2))

    # relationships
    ticket = db.relationship(
        "ServiceTicket",
        back_populates="mechanics",
    )
    mechanic = db.relationship(
        "Mechanic",
        back_populates="service_ticket_links",
    )


# =============
# inventory and junction table
# ==============

class Inventory(db.Model):
    __tablename__ = "inventory"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)

    # relationship to junction
    tickets = db.relationship(
        "ServiceTicketInventory",
        back_populates="part",
        cascade="all, delete-orphan",
    )


class ServiceTicketInventory(db.Model):
    __tablename__ = "service_ticket_inventory"

    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(
        db.Integer,
        db.ForeignKey("service_tickets.id"),
        nullable=False,
    )
    inventory_id = db.Column(
        db.Integer,
        db.ForeignKey("inventory.id"),
        nullable=False,
    )

    ticket = db.relationship(
        "ServiceTicket",
        back_populates="parts",
    )
    part = db.relationship(
        "Inventory",
        back_populates="tickets",
    )
