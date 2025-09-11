"""
starlight/__init__.py
~~~~~~~~~~~~~~~~~~~
This file contains the application factory for the Starlight Anime Hub.
"""

from flask import Flask, request
import logging
from .routes import main_bp
from .extensions import cache
from . import config

def create_app():
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__)

    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Configure Cache
    app.config["CACHE_TYPE"] = "SimpleCache"
    app.config["CACHE_DEFAULT_TIMEOUT"] = 300
    cache.init_app(app)

    # Register the blueprint
    app.register_blueprint(main_bp)

    @app.context_processor
    def inject_config():
        return dict(config=config, request=request)

    return app
