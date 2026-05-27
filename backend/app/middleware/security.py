from functools import wraps

from flask import jsonify, request

from app.config import Config


def require_api_key(f):
    """Decorator that checks X-API-Key header against Config.API_KEY.

    If API_KEY is empty/disabled, all requests pass through.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if not Config.API_KEY:
            return f(*args, **kwargs)
        api_key = request.headers.get("X-API-Key", "")
        if api_key != Config.API_KEY:
            return jsonify({"error": "Invalid or missing API key"}), 401
        return f(*args, **kwargs)
    return decorated


def add_security_headers(response):
    """Add security headers to the response."""
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["X-XSS-Protection"] = "0"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response
