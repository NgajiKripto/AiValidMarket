from flask import Blueprint

validation_bp = Blueprint("validation", __name__)

from app.api import validation  # noqa: E402, F401
