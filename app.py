import requests
from flask import Flask, request, render_template, send_file
import urllib.parse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Create a Flask application instance
app = Flask(__name__)

# --- API Configuration ---
# The base URL and headers for the animepahe API
API_BASE_URL = "https://animepahe.ru/api"
API_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'https://animepahe.ru/',
    'Cookie': '__ddgid_=U5s6Z9J3BF0pfdhM; __ddgmark_=BiGlRBjK0HMCPWLj; __ddg2_=IgFUmsxCz7Q4c66u; __ddg1_=Dxb4hS7Idd3Og4h75gA9; res=1080; aud=jpn; av1=0; latest=6114; __ddg8_=pOEMgyEFef8xzmDs; __ddg10_=1750607066; __ddg9_=103.204.209.15; XSRF-TOKEN=eyJpdiI6ImVhbG9vN0pFbCtrYSt1SVYyaEo1d1E9PSIsInZhbHVlIjoiOTdqUzQ4NmNHU0VaMkZEV29vd2ZIR0VoNWVaSkJKTTlTNW4rZ0dXaDVKYytQd3IzRHFpbnMvdlBqeTFlNzdXRHdkNnVPSzlNTHJRVHgvNzRZN2tHMjRhRDNtZkhBcjJBYUpiK010ZnhWV3JjLzZzMWFaZHQyWisyRHJYSmY3Z3UiLCJtYWMiOiI3ZmExYzUxMDIwYzhhYjkwZmEzNDlmY2FlMWI5ZGQ4NzdiZTU4YjRjZmM2MTRiNjUwNGVjNjk4ODlhYzQ4NjcyIiwidGFnIjoiIn0%3D; laravel_session=eyJpdiI6Ii9NOE4wOUZGaVpML3BlYzcwSTVRUXc9PSIsInYmFsdWUiOiJZTjJOOWhPaVNBc254Szk2K0pSejV5Q0VQNXFqM1ZwZEJtcUVQamdKb0liVzJZcFFjL1JKTVZ3TWJ0NkMyQzl3QXU4QzkwYjdyQnhnTDErcUpwSUZreWtJV2ZKREhGY2NNN0JNazIvZDcyVUFldDcraFMyb2kweEJyWmZDdThxcVgiLCJtYWMiOiI1ZGZiOWE0ODU4YjgyZTQwYmUxMjZjNzg0ZGM5YzcxOWM1ZmNhMmM1N2FhY2U1NjA5NDZhMDliNGZlNDc4MjE0IiwidGFnIjoiIn0%3D',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin'
}

# --- Flask Route for Anime Search ---
@app.route('/', methods=['GET', 'POST'])
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
            try:
                # Set up the parameters for the API request
                params = {'m': 'search', 'q': query}
                
                # Make the GET request to the API
                response = requests.get(API_BASE_URL, params=params, headers=API_HEADERS, timeout=10)
                
                # Raise an exception for bad status codes (4xx or 5xx)
                response.raise_for_status()
                
                # Parse the JSON response
                json_data = response.json()
                
                # The search results are in the 'data' key
                results = json_data.get('data', [])

            except requests.exceptions.RequestException as e:
                # Handle network errors (timeout, connection error, etc.)
                app.logger.error(f"API Request Error: {e}")
                error_message = f"Could not connect to the API. Please try again later. ({e})"
            except Exception as e:
                # Handle other potential errors (e.g., JSON parsing)
                app.logger.error(f"Unexpected Error during search: {e}")
                error_message = f"An unexpected error occurred: {e}"

    # Render the HTML template with the provided data
    return render_template(
        'index.html', 
        results=results, 
        search_query=search_query,
        search_performed=search_performed,
        error_message=error_message
    )

# --- Flask Route for Anime Episode Selection ---
@app.route('/anime/<string:anime_session_id>', methods=['GET'])
def anime_detail(anime_session_id):
    """
    Fetches and displays episodes for a given anime session ID.
    """
    episodes = []
    error_message = None
    anime_title = "Anime Episodes" # Default title, can be updated if more info is passed

    try:
        # Fetch episode data for the given anime_session_id
        params = {
            'm': 'release',
            'id': anime_session_id,
            'sort': 'episode_asc',
            'page': 1 # Fetching only the first page of episodes for now
        }
        app.logger.info(f"Fetching episodes for session ID: {anime_session_id}")
        response = requests.get(API_BASE_URL, params=params, headers=API_HEADERS, timeout=10)
        response.raise_for_status()
        json_data = response.json()
        
        # --- DEBUGGING LOGS ---
        app.logger.info(f"Raw JSON data from release API for {anime_session_id}: {json_data}")

        # CORRECTED: The 'release' API returns episodes within a 'data' key.
        episodes = json_data.get('data', [])
        
        # The API usually returns episodes sorted, but we can sort explicitly if needed
        # Example if sorting by 'episode' number is crucial and not guaranteed by API:
        # episodes.sort(key=lambda x: x.get('episode', 0))

        app.logger.info(f"Processed episodes for {anime_session_id}: {episodes}")
        # --- END DEBUGGING LOGS ---

        # If there are episodes, we can try to infer a title from the API response
        # or, ideally, pass the anime title from the search results to this function
        # if you want a more specific title than just the session ID.
        if episodes:
            anime_title = f"Episodes for Anime ID: {anime_session_id}" 
            # If you passed anime_title from the search, you'd use that here instead.

    except requests.exceptions.RequestException as e:
        app.logger.error(f"API Request Error for episodes (ID: {anime_session_id}): {e}")
        error_message = f"Could not fetch episode data. Please try again later. ({e})"
    except Exception as e:
        app.logger.error(f"Unexpected Error fetching episodes (ID: {anime_session_id}): {e}")
        error_message = f"An unexpected error occurred: {e}"

    return render_template(
        'episode_selection.html', 
        anime_session_id=anime_session_id, 
        episodes=episodes, 
        error_message=error_message,
        anime_title=anime_title # Pass the title to the template
    )


# --- Flask Route for Image Proxying ---
@app.route('/proxy-image')
def proxy_image():
    """
    Proxies images from the animepahe.ru domain to bypass CORS restrictions.
    The image URL is passed as a query parameter.
    """
    image_url = request.args.get('url')
    if not image_url:
        app.logger.warning("Attempted to proxy image without a URL.")
        return "Image URL not provided", 400

    try:
        # Fetch the image using requests.
        response = requests.get(image_url, headers=API_HEADERS, stream=True, timeout=10)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)

        # Get the content type from the response headers. If not present, default to octet-stream.
        mimetype = response.headers.get('Content-Type', 'application/octet-stream')
        
        # Return the image content with the correct MIME type
        return response.content, 200, {'Content-Type': mimetype}

    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error proxying image {image_url}: {e}")
        return "Error loading image", 500
    except Exception as e:
        app.logger.error(f"An unexpected error occurred while proxying image {image_url}: {e}")
        return "An unexpected error occurred while proxying image", 500

# --- Run the Application ---
if __name__ == '__main__':
    # The app should be run using the 'flask' command in the terminal.
    # Example:
    # export FLASK_APP=app.py
    # export FLASK_ENV=development
    # flask run
    app.run(debug=True)
