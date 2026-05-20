import sys
from pathlib import Path

# Add the backend directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app import create_app
from app.config import Config
from app.utils.logger import info, error


def main():
    """Start the Flask application."""
    try:
        Config.validate()
    except ValueError as e:
        error(f"Configuration error: {e}")
        sys.exit(1)

    app = create_app()
    info("Starting AiValidMarket backend server...")
    app.run(host="0.0.0.0", port=5001, debug=Config.DEBUG, threaded=True)


if __name__ == "__main__":
    main()
