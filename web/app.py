"""Flask web application — dashboard and WiFi configuration portal."""

import logging
from pathlib import Path

from flask import Flask

from src.platform_detect import IS_RASPBERRY_PI

logger = logging.getLogger(__name__)

_template_dir = Path(__file__).parent / "templates"
_static_dir = Path(__file__).parent / "static"


def create_app(app_state: dict) -> Flask:
    """
    Create and configure the Flask application.

    Args:
        app_state: Shared application state dict (read by API routes).
    """
    app = Flask(
        __name__,
        template_folder=str(_template_dir),
        static_folder=str(_static_dir),
    )
    app.config["APP_STATE"] = app_state
    app.config["IS_RASPBERRY_PI"] = IS_RASPBERRY_PI

    # Register routes
    from web.api.routes import api_bp
    from web.api.routes import register_page_routes

    app.register_blueprint(api_bp)
    register_page_routes(app)

    return app
