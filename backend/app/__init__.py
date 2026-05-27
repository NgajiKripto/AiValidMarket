from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from app.config import Config
from app.middleware.security import add_security_headers
from app.utils.logger import info
from app.utils.sanitizer import sanitize_log_input

# Module-level limiter instance so blueprints can import it
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[Config.RATE_LIMIT_DEFAULT],
    storage_uri="memory://",
)


def create_app():
    """Application factory following MiroFish pattern."""
    app = Flask(__name__)

    # CORS setup - restrict to configured origins
    origins = [o.strip() for o in Config.ALLOWED_ORIGINS.split(",") if o.strip()]
    CORS(app, resources={r"/api/*": {"origins": origins}})

    # Initialize rate limiter
    limiter.init_app(app)

    # Register blueprints
    from app.api import validation_bp, memory_bp
    app.register_blueprint(validation_bp, url_prefix="/api/validation")
    app.register_blueprint(memory_bp, url_prefix="/api/memory")

    # Health check endpoint
    @app.route("/health")
    def health():
        return jsonify({"status": "ok", "service": "aivalidmarket-backend"})

    # Request logging middleware
    @app.before_request
    def log_request():
        sanitized_path = sanitize_log_input(request.path)
        info(f"{request.method} {sanitized_path}")

    # Security headers
    @app.after_request
    def apply_security_headers(response):
        return add_security_headers(response)

    return app
