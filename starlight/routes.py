"""
routes.py
~~~~~~~~~
This module defines the Flask routes for the Starlight Anime Hub application.
It uses functions from api_handlers to fetch and process data.
"""

from flask import Blueprint, request, render_template, jsonify, url_for, current_app
from .extensions import cache
from .api_handlers import (
    fetch_anime_search_results,
    fetch_anime_details,
    fetch_episode_list,
    fetch_episode_download_links,
    proxy_image_content,
    fetch_airing_anime, # Import the new function
    fetch_final_download_link, # Import the new function
    fetch_batch_download_links,
    fetch_available_resolutions_and_sources,
    fetch_common_resolutions_and_sources,
    fetch_single_episode_download_link
)
import logging
import asyncio

# Create a Blueprint for your routes
main_bp = Blueprint('main', __name__)


# Configure logging for this module
logger = logging.getLogger(__name__)

@main_bp.route('/', methods=['GET'])
@cache.cached(timeout=300, query_string=True)
def home_page():
    """
    Handles displaying the home page with the latest airing anime.
    """
    error_message = None
    airing_anime = []
    airing_pagination = {}
    
    # Get current page for airing anime from query parameters, default to 1
    page = request.args.get('page', 1, type=int)

    airing_anime, airing_pagination, error_message = fetch_airing_anime(page)
    # Generate next/prev page URLs for airing pagination
    cp = airing_pagination.get('current_page', 1)
    lp = airing_pagination.get('last_page', 1)
    if cp < lp:
        airing_pagination['next_page_url'] = url_for('main.home_page', page=cp + 1)
    if cp > 1:
        airing_pagination['prev_page_url'] = url_for('main.home_page', page=cp - 1)

    return render_template(
        'index.html', 
        error_message=error_message,
        airing_anime=airing_anime,         # Pass airing anime data
        airing_pagination=airing_pagination # Pass airing pagination data
    )

@main_bp.route('/search', methods=['POST'])
def search():
    """
    Handles processing API search requests and displays the results on a separate page.
    """
    results = []
    search_query = ""
    error_message = None
    
    query = request.form.get('query', '').strip()
    search_query = query

    if query:
        results, error_message = fetch_anime_search_results(query)
    
    return render_template(
        'search_results.html', 
        results=results, 
        search_query=search_query,
        error_message=error_message
    )

@main_bp.route('/anime/<string:anime_session_id>', methods=['GET'])
@cache.cached(timeout=3600)
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
    if anime_details.get('title') == 'N/A' and anime_title != 'N/A':
        anime_details['title'] = anime_title

    return render_template(
        'anime_details_page.html', 
        anime_session_id=anime_session_id, 
        anime_details=anime_details,
        error_message=error_message
    )

@main_bp.route('/episodes/<string:anime_session_id>', methods=['GET'])
@cache.cached(timeout=3600, query_string=True)
def episode_selection_page(anime_session_id):
    """
    Fetches and displays episodes for a given anime session ID with pagination.
    This route is now specifically for episode listing.
    """
    # Get anime_title from query parameters, defaulting to a generic title if not found
    anime_title = request.args.get('anime_title', "Anime Episodes") 
    
    # Get current page from query parameters, default to 1
    page = request.args.get('page', 1, type=int)
    
    # Get sort order from query parameters, default to 'episode_asc'
    sort_order = request.args.get('sort', 'episode_asc')

    # Fetch episodes and pagination data using the handler
    episodes, pagination_data, error_message = fetch_episode_list(anime_session_id, page, sort_order)
    
    # Generate next/prev page URLs for the template
    # Make sure to pass anime_title and sort_order to ensure continuity in navigation
    cp = pagination_data.get('current_page', 1)
    lp = pagination_data.get('last_page', 1)
    
    pagination_data['next_page_url'] = None
    pagination_data['prev_page_url'] = None

    if cp < lp:
        pagination_data['next_page_url'] = url_for('main.episode_selection_page', anime_session_id=anime_session_id, anime_title=anime_title, page=cp + 1, sort=sort_order)
    if cp > 1:
        pagination_data['prev_page_url'] = url_for('main.episode_selection_page', anime_session_id=anime_session_id, anime_title=anime_title, page=cp - 1, sort=sort_order)

    return render_template(
        'episode_selection.html', 
        anime_session_id=anime_session_id, 
        episodes=episodes, 
        error_message=error_message,
        anime_title=anime_title, # Pass the fetched or default anime_title
        pagination=pagination_data, # Pass pagination data to the template
        current_sort_order=sort_order # Pass current sort order to the template
    )

# New API endpoint to fetch episodes as JSON
@main_bp.route('/api/anime-episodes/<string:anime_session_id>', methods=['GET'])
@cache.cached(timeout=3600, query_string=True)
def get_anime_episodes_json(anime_session_id):
    """
    Fetches a list of episodes for a given anime session ID and returns it as JSON.
    If 'page' is provided, returns a paginated list. Otherwise, returns all episodes.
    """
    page_param = request.args.get('page', type=int)

    if page_param:
        # Original paginated behavior
        episodes, pagination_data, error_message = fetch_episode_list(anime_session_id, page_param)
        if error_message:
            return jsonify({'error': error_message}), 500
        return jsonify({'episodes': episodes, 'pagination': pagination_data})

    else:
        # Fetch all episodes
        all_episodes = []
        current_page = 1
        while True:
            episodes, pagination_data, error_message = fetch_episode_list(anime_session_id, current_page)
            if error_message:
                return jsonify({'error': error_message}), 500
            
            all_episodes.extend(episodes)
            
            if pagination_data.get('current_page') >= pagination_data.get('last_page'):
                break
            current_page += 1
        
        return jsonify({'episodes': all_episodes})


@main_bp.route('/api/episode-downloads/<string:anime_session_id>/<string:episode_session_id>', methods=['GET'])
@cache.cached(timeout=900)
def get_episode_downloads(anime_session_id, episode_session_id):
    """
    Fetches download links for a specific episode using the API handler.
    """
    downloads, error_message = fetch_episode_download_links(anime_session_id, episode_session_id)
    
    if error_message:
        return jsonify({'error': error_message}), 500
    return jsonify({'downloads': downloads})

@main_bp.route('/api/get-final-download', methods=['POST'])
def get_final_download():
    """
    Receives a single kwik.si URL and uses the Streamline API to get the final direct download link.
    """
    data = request.get_json()
    kwik_si_url = data.get('url')

    if not kwik_si_url:
        return jsonify({'error': 'No URL provided.'}), 400

    final_link, error_message = fetch_final_download_link(kwik_si_url)

    if error_message:
        return jsonify({'error': error_message}), 500
    if not final_link:
        return jsonify({'error': 'Could not retrieve final download link.'}), 500
    
    return jsonify({'final_download': final_link})

@main_bp.route('/proxy-image')
@cache.cached(timeout=900, query_string=True)
def proxy_image():
    """
    Proxies images from the animepahe.ru domain to bypass CORS restrictions,
    with browser-side caching enabled.
    The image URL is passed as a query parameter.
    """
    image_url = request.args.get('url')
    if not image_url:
        return "Image URL not provided", 400

    content, mimetype = proxy_image_content(image_url)

    if content is None:
        return "Error loading image", 500
    
    # Create a response object
    response = current_app.response_class(content, mimetype=mimetype)
    
    # Set browser caching headers (cache for 1 day)
    response.headers['Cache-Control'] = 'public, max-age=86400'
    
    return response

@main_bp.route('/blackhole')
def blackhole_page():
    """
    Renders the blackhole page.
    """
    return render_template('blackhole.html')

@main_bp.route('/bookmarks')
def bookmarks_page():
    """
    Renders the constellations page. Bookmarks are loaded client-side from localStorage.
    """
    return render_template('bookmarks.html')

# New route for the "Continue Watching" page
@main_bp.route('/continue-watching')
def continue_watching_page():
    """
    Renders the resume trajectory page. Unwatched episodes for bookmarked anime
    are loaded client-side from localStorage and API calls.
    """
    return render_template('continue_watching.html')

@main_bp.route('/api/blackhole/prepare-download', methods=['POST'])
async def prepare_blackhole_download():
    """
    Prepares a batch download for a given anime.
    """
    data = request.get_json()
    anime_session_id = data.get('anime_session_id')
    resolution = data.get('resolution')
    source = data.get('source')
    episodes = data.get('episodes', [])

    logger.info(f"Received blackhole download request for anime {anime_session_id} with {len(episodes)} episodes.")
    logger.debug(f"Request details: Resolution='{resolution}', Source='{source}'")

    if not all([anime_session_id, resolution, source, episodes]):
        logger.warning("Blackhole request missing required parameters.")
        return jsonify({'error': 'Missing required parameters.'}), 400

    final_links, error_message = await fetch_batch_download_links(
        anime_session_id, resolution, source, episodes
    )

    if error_message:
        logger.error(f"Error during batch download link fetching for {anime_session_id}: {error_message}")
        return jsonify({'error': error_message}), 500

    logger.info(f"Successfully prepared {len(final_links)} download links for anime {anime_session_id}.")
    return jsonify({'download_links': final_links})

@main_bp.route('/api/anime-resolutions/<string:anime_session_id>', methods=['GET'])
@cache.cached(timeout=3600)
def get_anime_resolutions(anime_session_id):
    """
    Fetches available resolutions and sources for a given anime by sampling
    a few episodes.
    """
    resolutions, sources, error = fetch_available_resolutions_and_sources(anime_session_id)
    if error:
        return jsonify({'error': error}), 500
    
    return jsonify({
        'resolutions': resolutions,
        'sources': sources
    })

@main_bp.route('/api/blackhole/fetch-options', methods=['POST'])
def fetch_blackhole_options():
    """
    Fetches common resolutions and sources for a given list of episodes.
    """
    data = request.get_json()
    anime_session_id = data.get('anime_session_id')
    episodes = data.get('episodes', [])
    
    logger.info(f"Fetching blackhole options for anime {anime_session_id} with {len(episodes)} episodes.")

    if not anime_session_id or not episodes:
        logger.warning("Fetch-options request missing anime_session_id or episodes.")
        return jsonify({'error': 'Missing anime_session_id or episodes.'}), 400

    resolutions, sources, error = fetch_common_resolutions_and_sources(anime_session_id, episodes)

    if error:
        logger.error(f"Error fetching common resolutions/sources for {anime_session_id}: {error}")
        return jsonify({'error': error}), 500
    
    logger.info(f"Returning {len(resolutions)} common resolutions and {len(sources)} common sources for {anime_session_id}.")
    response = jsonify({
        'resolutions': resolutions,
        'sources': sources
    })
    return response

@main_bp.route('/api/blackhole/fetch-single-link', methods=['POST'])
async def fetch_single_link():
    """
    Fetches a download link for a single episode.
    """
    data = request.get_json()
    anime_session_id = data.get('anime_session_id')
    resolution = data.get('resolution')
    source = data.get('source')
    episode = data.get('episode')

    logger.debug(f"Received single link request for anime {anime_session_id}, episode {episode.get('number') if episode else 'N/A'}.")

    if not all([anime_session_id, resolution, source, episode]):
        logger.warning("Single link request missing required parameters.")
        return jsonify({'error': 'Missing required parameters.'}), 400

    link_data, error_message = await fetch_single_episode_download_link(
        anime_session_id, resolution, source, episode
    )

    if error_message:
        logger.error(f"Error fetching single link for episode {episode.get('number', 'N/A')}: {error_message}")
        return jsonify({'error': error_message}), 500

    return jsonify({'download_link': link_data})
