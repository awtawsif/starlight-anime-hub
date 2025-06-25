"""
routes.py
~~~~~~~~~
This module defines the Flask routes for the Starlight Anime Hub application.
It uses functions from api_handlers to fetch and process data.
"""

from flask import Blueprint, request, render_template, jsonify, url_for, current_app
from api_handlers import ( # Changed from .api_handlers to api_handlers
    fetch_anime_search_results,
    fetch_anime_details,
    fetch_episode_list,
    fetch_episode_download_links,
    proxy_image_content
)
import logging

# Create a Blueprint for your routes
main_bp = Blueprint('main', __name__)

# Configure logging for this module
logger = logging.getLogger(__name__)

@main_bp.route('/', methods=['GET', 'POST'])
def search_page():
    """
    Handles displaying the search page and processing API search requests.
    """
    results = []
    search_query = ""
    search_performed = False
    error_message = None

    if request.method == 'POST':
        search_performed = True
        query = request.form.get('query', '').strip()
        search_query = query

        if query:
            results, error_message = fetch_anime_search_results(query)

    return render_template(
        'index.html',
        results=results,
        search_query=search_query,
        search_performed=search_performed,
        error_message=error_message
    )

@main_bp.route('/anime/<string:anime_session_id>', methods=['GET'])
def anime_detail(anime_session_id):
    """
    Fetches and displays full details for a given anime session ID by scraping
    the animepahe.ru/anime/{anime_session_id} page.
    The anime title is passed from the search page for reliability.
    """
    # Get anime_title from query parameters, using it as the primary title
    anime_title = request.args.get('anime_title', 'N/A')

    # Fetch details using the handler
    anime_details, error_message = fetch_anime_details(anime_session_id)

    # Override title if it's 'N/A' from the fetch and we have it from query
    if anime_details['title'] == 'N/A' and anime_title != 'N/A':
        anime_details['title'] = anime_title

    return render_template(
        'anime_details_page.html',
        anime_session_id=anime_session_id,
        anime_details=anime_details,
        error_message=error_message
    )

@main_bp.route('/episodes/<string:anime_session_id>', methods=['GET'])
def episode_selection_page(anime_session_id):
    """
    Fetches and displays episodes for a given anime session ID with pagination.
    This route is now specifically for episode listing.
    """
    # Get anime_title from query parameters, defaulting to a generic title if not found
    anime_title = request.args.get('anime_title', "Anime Episodes")

    # Get current page from query parameters, default to 1
    page = request.args.get('page', 1, type=int)

    # Fetch episodes and pagination data using the handler
    episodes, pagination_data, error_message = fetch_episode_list(anime_session_id, page)

    # Generate next/prev page URLs for the template
    # Make sure to pass anime_title to ensure continuity in navigation
    cp = pagination_data['current_page']
    lp = pagination_data['last_page']

    if cp < lp:
        pagination_data['next_page_url'] = url_for('main.episode_selection_page', anime_session_id=anime_session_id, anime_title=anime_title, page=cp + 1)
    if cp > 1:
        pagination_data['prev_page_url'] = url_for('main.episode_selection_page', anime_session_id=anime_session_id, anime_title=anime_title, page=cp - 1)

    return render_template(
        'episode_selection.html',
        anime_session_id=anime_session_id,
        episodes=episodes,
        error_message=error_message,
        anime_title=anime_title,
        pagination=pagination_data
    )

@main_bp.route('/api/episode-downloads/<string:anime_session_id>/<string:episode_session_id>', methods=['GET'])
def get_episode_downloads(anime_session_id, episode_session_id):
    """
    Fetches download links for a specific episode using the API handler.
    """
    downloads, error_message = fetch_episode_download_links(anime_session_id, episode_session_id)

    if error_message:
        return jsonify({'error': error_message}), 500
    return jsonify({'downloads': downloads})

@main_bp.route('/proxy-image')
def proxy_image():
    """
    Proxies images from the animepahe.ru domain to bypass CORS restrictions.
    The image URL is passed as a query parameter.
    """
    image_url = request.args.get('url')
    if not image_url:
        return "Image URL not provided", 400

    content, mimetype = proxy_image_content(image_url)

    if content is None:
        return "Error loading image", 500

    return current_app.response_class(content, mimetype=mimetype)
