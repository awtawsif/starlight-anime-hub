# starlight-anime-hub/__init__.py

from flask import Blueprint

# Define the blueprint for the Starlight Anime Hub.
# The name 'starlight_anime' will be used in url_for calls (e.g., 'starlight_anime.search_page').
# template_folder='templates' tells Flask to look for templates in the 'templates'
# directory relative to THIS __init__.py file (i.e., starlight-anime-hub/templates/).
# static_folder='static' similarly points to starlight-anime-hub/static/.
anime_bp = Blueprint('starlight_anime', __name__,
                    template_folder='templates',
                    static_folder='static')

# Import routes to associate them with this blueprint.
# This ensures that when 'anime_bp' is registered by the main hub,
# all its routes (defined in routes.py, which is in the same directory)
# are also registered.
from . import routes
