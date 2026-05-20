from flask import Flask, jsonify, request
from flask_cors import CORS
from app.utils.logger import info


def create_app():
    """Application factory following MiroFish pattern."""
    app = Flask(__name__)

    # CORS setup
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Register blueprints
    from app.api import validation_bp
    app.register_blueprint(validation_bp, url_prefix="/api/validation")

    # Health check endpoint
    @app.route("/health")
    def health():
        return jsonify({"status": "ok", "service": "aivalidmarket-backend"})

    # Request logging middleware
    @app.before_request
    def log_request():
        info(f"{request.method} {request.path}")

    return app
