from flask import Blueprint

inventory_bp = Blueprint("inventory", __name__)

# make sure routes are imported
from . import routes 
