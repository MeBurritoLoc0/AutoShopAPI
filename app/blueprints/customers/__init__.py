from flask import Blueprint

customers_bp = Blueprint("customers", __name__)

# make sure routes are imported
from . import routes
