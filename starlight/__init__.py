"""
starlight/__init__.py
~~~~~~~~~~~~~~~~~~~
This file contains the application factory for the Starlight Anime Hub.
"""

from flask import Flask, request
import logging
import os
from .routes import main_bp
from .extensions import cache
from . import config

def create_app():
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__)

    # Configure logging - use DEBUG level if DEBUG env var is set
    log_level = logging.DEBUG if os.environ.get('DEBUG', '').lower() in ('1', 'true', 'yes') else logging.INFO
    logging.basicConfig(level=log_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    app.logger.setLevel(log_level)

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
