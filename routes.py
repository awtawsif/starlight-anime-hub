# starlight-anime-hub/routes.py

from flask import request, render_template, jsonify, url_for, current_app
from api_handlers import (
    fetch_anime_search_results,
    fetch_anime_details,
    fetch_episode_list,
    fetch_episode_download_links,
    proxy_image_content,
    fetch_airing_anime
)
import logging
# Import the blueprint instance defined in the local __init__.py
from . import anime_bp

# Configure logging for this module
logger = logging.getLogger(__name__)

# All routes are now registered with 'anime_bp'
@anime_bp.route('/', methods=['GET', 'POST'])
def search_page():
    """
    Handles displaying the search page and processing API search requests,
    or displays the airing anime list if no search is performed.
    """
    results = []
    search_query = ""
    search_performed = False
    error_message = None
    airing_anime = []
    airing_pagination = {}
    
    # Get current page for airing anime from query parameters, default to 1
    page = request.args.get('page', 1, type=int)

    if request.method == 'POST':
        search_performed = True
        query = request.form.get('query', '').strip()
        search_query = query

        if query:
            results, error_message = fetch_anime_search_results(query)
        else:
            # If a POST request with an empty query, treat as no search and show airing
            search_performed = False
            airing_anime, airing_pagination, error_message = fetch_airing_anime(page)
            # Generate next/prev page URLs for airing pagination
            cp = airing_pagination.get('current_page', 1)
            lp = airing_pagination.get('last_page', 1)
            if cp < lp:
                # Use 'starlight_anime' blueprint name for url_for
                airing_pagination['next_page_url'] = url_for('starlight_anime.search_page', page=cp + 1)
            if cp > 1:
                # Use 'starlight_anime' blueprint name for url_for
                airing_pagination['prev_page_url'] = url_for('starlight_anime.search_page', page=cp - 1)


    else: # GET request (initial load or pagination for airing anime)
        airing_anime, airing_pagination, error_message = fetch_airing_anime(page)
        # Generate next/prev page URLs for airing pagination
        cp = airing_pagination.get('current_page', 1)
        lp = airing_pagination.get('last_page', 1)
        if cp < lp:
            # Use 'starlight_anime' blueprint name for url_for
            airing_pagination['next_page_url'] = url_for('starlight_anime.search_page', page=cp + 1)
        if cp > 1:
            # Use 'starlight_anime' blueprint name for url_for
            airing_pagination['prev_page_url'] = url_for('starlight_anime.search_page', page=cp - 1)


    # Render template from the blueprint's template folder (starlight-anime-hub/templates/)
    return render_template(
        'index.html', # No nested path needed here because template_folder is 'templates'
        results=results, 
        search_query=search_query,
        search_performed=search_performed,
        error_message=error_message,
        airing_anime=airing_anime,
        airing_pagination=airing_pagination
    )

@anime_bp.route('/anime/<string:anime_session_id>', methods=['GET'])
def anime_detail(anime_session_id):
    """
    Fetches and displays full details for a given anime session ID by scraping
    the animepahe.ru/anime/{anime_session_id} page.
    The anime title is passed from the search page for reliability.
    """
    anime_title = request.args.get('anime_title', 'N/A')
    
    anime_details, error_message = fetch_anime_details(anime_session_id)
    
    if anime_details.get('title') == 'N/A' and anime_title != 'N/A':
        anime_details['title'] = anime_title

    # Render template from the blueprint's template folder
    return render_template(
        'anime_details_page.html', # No nested path needed
        anime_session_id=anime_session_id, 
        anime_details=anime_details,
        error_message=error_message
    )

@anime_bp.route('/episodes/<string:anime_session_id>', methods=['GET'])
def episode_selection_page(anime_session_id):
    """
    Fetches and displays episodes for a given anime session ID with pagination.
    This route is now specifically for episode listing.
    """
    anime_title = request.args.get('anime_title', "Anime Episodes") 
    page = request.args.get('page', 1, type=int)

    episodes, pagination_data, error_message = fetch_episode_list(anime_session_id, page)
    
    cp = pagination_data.get('current_page', 1)
    lp = pagination_data.get('last_page', 1)
    
    pagination_data['next_page_url'] = None
    pagination_data['prev_page_url'] = None

    if cp < lp:
        # Use 'starlight_anime' blueprint name for url_for
        pagination_data['next_page_url'] = url_for('starlight_anime.episode_selection_page', anime_session_id=anime_session_id, anime_title=anime_title, page=cp + 1)
    if cp > 1:
        # Use 'starlight_anime' blueprint name for url_for
        pagination_data['prev_page_url'] = url_for('starlight_anime.episode_selection_page', anime_session_id=anime_session_id, anime_title=anime_title, page=cp - 1)

    # Render template from the blueprint's template folder
    return render_template(
        'episode_selection.html', # No nested path needed
        anime_session_id=anime_session_id, 
        episodes=episodes, 
        error_message=error_message,
        anime_title=anime_title,
        pagination=pagination_data
    )

@anime_bp.route('/api/episode-downloads/<string:anime_session_id>/<string:episode_session_id>', methods=['GET'])
def get_episode_downloads(anime_session_id, episode_session_id):
    """
    Fetches download links for a specific episode using the API handler.
    """
    downloads, error_message = fetch_episode_download_links(anime_session_id, episode_session_id)
    
    if error_message:
        return jsonify({'error': error_message}), 500
    return jsonify({'downloads': downloads})

@anime_bp.route('/proxy-image')
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

@anime_bp.route('/bookmarks')
def bookmarks_page():
    """
    Renders the bookmarks page. Bookmarks are loaded client-side from localStorage.
    """
    # Render template from the blueprint's template folder
    return render_template('bookmarks.html') # No nested path needed
