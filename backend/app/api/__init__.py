from flask import Blueprint

validation_bp = Blueprint("validation", __name__)
memory_bp = Blueprint("memory", __name__)

from app.api import validation  # noqa: E402, F401
from app.api import memory  # noqa: E402, F401
