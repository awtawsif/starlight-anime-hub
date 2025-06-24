import requests
from flask import Flask, request, render_template, jsonify, url_for
import logging
from bs4 import BeautifulSoup
import re

# Configure logging (minimal, or remove if not needed for production)
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

# Create a Flask application instance
app = Flask(__name__)

# --- API Configuration ---
# The base URL and headers for the animepahe API
API_BASE_URL = "https://animepahe.ru/api"
ANIME_PAGE_BASE_URL = "https://animepahe.ru/anime" # New base URL for detail pages
API_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'https://animepahe.ru/',
    'Cookie': '__ddgid_=U5s6Z9J3BF0pfdhM; __ddgmark_=BiGlRBjK0HMCPWLj; __ddg2_=IgFUmsxCz7Q4c66u; __ddg1_=Dxb4hS7Idd3Og4h75gA9; res=1080; aud=jpn; av1=0; latest=6114; __ddg8_=pOEMcyEFef8xzmDs; __ddg10_=1750607066; __ddg9_=103.204.209.15; XSRF-TOKEN=eyJpdiI6ImVhbG9vN0pFbCtrYSt1SVYyaEo1d1E9PSIsInZhbHVlIjoiOTdqUzQ4NmNHU0VaMkZEV29vd2ZIR0VoNWVaSkJKTTlTNW4rZ0dXaDVKYytQd3IzRHFpbnMvdlBqeTFlNzdXRHdkNnVPSzlNTHJRVHgvNzRZN2tHMjRhRDNtZkhBcjJBYUpiK010ZnhWV3JjLzZzMWFaZHQyWisyRHJYSmY3Z3UiLCJtYWMiOiI3ZmExYzUxMDIwYzhhYjkwZmEzNDlmY2FlMWI5ZGQ4NzdiZTU4YjRjZmM2MTRiNjUwNGVjNjk4ODlhYzQ4NjcyIiwidGFnIjoiIn0%3D; laravel_session=eyJpdiI6Ii9NOE4wOUZGaVpML3BlYzcwSTVRUXc9PSIsInZhbHVlIjoiZTJOOWhPaVNBc254Szk2K0pSejV5Q0VQNXFqM1ZwZEJtcUVQamdKb0liVzJZcFFjL1JKTVZ3TWJ0NkMyQzl3QXU4QzkwYjdyQnhnTDErcUpwSUZreWtJV2ZKREhGY2NNN0JNazIvZDcyVUFldDcraFMyb2kweEJyWmZDdThxcVgiLCJtYWMiOiI1ZGZiOWE0ODU4YjgyZTQwYmUxMjZjNzg0ZGM5YzcxOWM1ZmNhMmM1N2FhY2U1NjA5NDZhMDliNGZlNDc4MjE0IiwidGFnIjoiIn0%3D',
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

def _parse_related_anime_card(card_row_element):
    """
    Parses a BeautifulSoup element representing a single anime card (div with row mx-n1)
    from relations or recommendations sections.
    """
    anime_card_data = {
        'session_id': 'N/A',
        'title': 'N/A',
        'poster': "https://placehold.co/100x150/1a202c/ffffff?text=No+Img", # Default for small posters
        'type': 'N/A',
        'episodes_status': 'N/A',
        'season': 'N/A'
    }

    # Extract poster and main link
    img_link_container = card_row_element.find('div', class_='col-2')
    if img_link_container:
        img_tag = img_link_container.find('img')
        if img_tag:
            anime_card_data['poster'] = img_tag.get('data-src') or img_tag.get('src')
            if not anime_card_data['poster']:
                anime_card_data['poster'] = "https://placehold.co/100x150/1a202c/ffffff?text=No+Img"
        
        main_link_tag = img_link_container.find('a')
        if main_link_tag and main_link_tag.get('href'):
            session_match = re.search(r'/anime/([a-f0-9-]+)', main_link_tag.get('href'))
            if session_match:
                anime_card_data['session_id'] = session_match.group(1)

    # Extract title, type, episodes/status, and season from the info column
    info_col = card_row_element.find('div', class_='col-9')
    if info_col:
        # Title
        title_tag = info_col.find('h5')
        if title_tag and title_tag.find('a'):
            anime_card_data['title'] = title_tag.find('a').get('title') or title_tag.find('a').get_text(strip=True)
            # If session_id wasn't found from poster link, try from title link (more reliable perhaps)
            if anime_card_data['session_id'] == 'N/A' and title_tag.find('a').get('href'):
                 session_match = re.search(r'/anime/([a-f0-9-]+)', title_tag.find('a').get('href'))
                 if session_match:
                     anime_card_data['session_id'] = session_match.group(1)

        # Type, Episodes, Status
        strong_tag = info_col.find('strong')
        if strong_tag:
            type_link = strong_tag.find('a')
            if type_link:
                anime_card_data['type'] = type_link.get_text(strip=True)
            
            # Extract text after <strong>, before <br>
            episodes_status_text = ""
            current_sibling = strong_tag.next_sibling
            while current_sibling:
                if current_sibling.name == 'br':
                    break
                if isinstance(current_sibling, str):
                    episodes_status_text += current_sibling
                elif current_sibling.name == 'a': # In case type link is also within this flow
                    episodes_status_text += current_sibling.get_text(strip=True)
                current_sibling = current_sibling.next_sibling
            
            anime_card_data['episodes_status'] = re.sub(r'^-', '', episodes_status_text).strip() # Remove leading hyphen and strip

        # Season
        season_link = info_col.find('a', href=re.compile(r'/anime/season/'))
        if season_link:
            anime_card_data['season'] = season_link.get_text(strip=True)

    return anime_card_data


# --- Flask Route for Anime Details Page ---
@app.route('/anime/<string:anime_session_id>', methods=['GET'])
def anime_detail(anime_session_id):
    """
    Fetches and displays full details for a given anime session ID by scraping
    the animepahe.ru/anime/{anime_session_id} page.
    The anime title is now passed from the search page for reliability.
    """
    detail_url = f"{ANIME_PAGE_BASE_URL}/{anime_session_id}"
    anime_details = {
        'title': 'N/A',
        'synopsis': 'No synopsis available.',
        'poster': "https://placehold.co/300x450/1a202c/ffffff?text=No+Image+Available&font=inter",
        'synonyms': 'N/A', 
        'japanese': 'N/A', 
        'type': 'N/A', 
        'episodes': 'N/A', 
        'status': 'N/A', 
        'duration': 'N/A', 
        'aired': 'N/A', 
        'season': 'N/A', 
        'studio': 'N/A', 
        'theme': 'N/A', 
        'demographic': 'N/A', 
        'genre': 'N/A',
        'relations': [], # New: To store related anime (sequel, prequel, summary etc.)
        'recommendations': [] # New: To store recommended anime
    }
    error_message = None

    # Get anime_title from query parameters, using it as the primary title
    # Flask automatically URL-decodes query parameters, so no manual decoding is needed.
    anime_details['title'] = request.args.get('anime_title', 'N/A')

    try:
        # Only keep info log for fetching details (optional, can be removed if not needed)
        # app.logger.info(f"Fetching anime details from: {detail_url}")
        response = requests.get(detail_url, headers=API_HEADERS, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml') 

        # Extract Synopsis (from anime-synopsis)
        synopsis_tag = soup.find('div', class_='anime-synopsis')
        anime_details['synopsis'] = synopsis_tag.get_text(strip=True) if synopsis_tag else 'No synopsis available.'

        # Extract Poster (from anime-poster)
        poster_div = soup.find('div', class_='anime-poster')
        if poster_div:
            poster_img_tag = poster_div.find('img')
            if poster_img_tag:
                anime_details['poster'] = poster_img_tag.get('data-src') or poster_img_tag.get('src')
            
            if not anime_details['poster']:
                 anime_details['poster'] = "https://placehold.co/300x450/1a202c/ffffff?text=No+Image+Available&font=inter"
        else:
            anime_details['poster'] = "https://placehold.co/300x450/1a202c/ffffff?text=No+Image+Available&font=inter"

        # Extract other details from the anime-info list (col-sm-4 anime-info)
        info_column = soup.find('div', class_='col-sm-4 anime-info')
        if info_column:
            for p_tag in info_column.find_all('p', recursive=False):
                if 'external-links' in p_tag.get('class', []):
                    continue
                
                strong_tag = p_tag.find('strong')
                if not strong_tag:
                    continue 

                key_text_parts = []
                for content in strong_tag.contents:
                    if isinstance(content, str):
                        key_text_parts.append(content.strip())
                    elif content.name == 'a': 
                        pass 
                key_raw = "".join(key_text_parts).strip()
                key = key_raw.replace(':', '').strip().lower()
                
                value = 'N/A' 

                a_tag_inside_strong = strong_tag.find('a')
                if a_tag_inside_strong:
                    value = a_tag_inside_strong.get_text(strip=True)
                else:
                    # Create a copy of the p_tag before modifying it for robust parsing
                    temp_p_tag = BeautifulSoup(str(p_tag), 'lxml').find('p') 
                    temp_strong_tag = temp_p_tag.find('strong')
                    if temp_strong_tag: # Ensure strong tag exists in temp copy
                        temp_strong_tag.extract() 
                    value = temp_p_tag.get_text(strip=True)
                    value = re.sub(r'\s+', ' ', value).strip() 

                anime_details[key] = value if value else 'N/A'
            
            genre_div = info_column.find('div', class_='anime-genre')
            if genre_div:
                genres = [a.get_text(strip=True) for a in genre_div.find_all('a')]
                anime_details['genre'] = ', '.join(genres) if genres else 'N/A'
            else:
                anime_details['genre'] = 'N/A'

        # --- Extract Relations ---
        relations_div = soup.find('div', class_='tab-content anime-relation row')
        if relations_div:
            # Find all individual relation sections (e.g., Sequel, Summary)
            # The structure for a relation type section is col-12 col-sm-6
            relation_type_sections = relations_div.find_all('div', class_=re.compile(r'col-12 col-sm-6'))
            for section in relation_type_sections:
                relation_type_tag = section.find('h4')
                relation_type = relation_type_tag.find('span').get_text(strip=True) if relation_type_tag and relation_type_tag.find('span') else 'Unknown'
                
                # Find all individual anime cards within this relation type section
                # Each anime card is a 'div' with class 'row mx-n1'
                anime_cards = section.find_all('div', class_='row mx-n1')
                for card_soup_element in anime_cards:
                    parsed_card = _parse_related_anime_card(card_soup_element)
                    parsed_card['relation_type_label'] = relation_type # Add relation type to the card data
                    anime_details['relations'].append(parsed_card)


        # --- Extract Recommendations ---
        recommendations_div = soup.find('div', class_='tab-content anime-recommendation row')
        if recommendations_div:
            # Recommendations are also individual anime cards (div with class 'row mx-n1')
            # directly under the main recommendations_div (inside col-12 col-sm-6 mb-3 elements)
            recommendation_cards_containers = recommendations_div.find_all('div', class_=re.compile(r'col-12 col-sm-6'))
            for container in recommendation_cards_containers:
                anime_card_element = container.find('div', class_='row mx-n1')
                if anime_card_element:
                    parsed_card = _parse_related_anime_card(anime_card_element)
                    anime_details['recommendations'].append(parsed_card)


        # Ensure all expected keys are present in anime_details dictionary for template consistency
        default_keys = ['synonyms', 'japanese', 'type', 'episodes', 'status', 'duration', 'aired', 'season', 'studio', 'theme', 'demographic', 'genre'] 
        for k in default_keys:
            if k not in anime_details:
                anime_details[k] = 'N/A'
        

    except requests.exceptions.RequestException as e:
        app.logger.error(f"API Request Error fetching anime details ({detail_url}): {e}")
        error_message = f"Could not fetch anime details. Please try again later. ({e})"
    except Exception as e:
        app.logger.error(f"An unexpected error occurred while parsing anime details ({detail_url}): {e}")
        error_message = f"An unexpected error occurred: {e}"

    return render_template(
        'anime_details_page.html', 
        anime_session_id=anime_session_id, 
        anime_details=anime_details,
        error_message=error_message
    )


# --- Flask Route for Anime Episode Selection ---
@app.route('/episodes/<string:anime_session_id>', methods=['GET'])
def episode_selection_page(anime_session_id):
    """
    Fetches and displays episodes for a given anime session ID with pagination.
    This route is now specifically for episode listing.
    """
    episodes = []
    error_message = None
    # Get anime_title from query parameters, defaulting to a generic title if not found
    anime_title = request.args.get('anime_title', "Anime Episodes") 
    
    # Get current page from query parameters, default to 1
    page = request.args.get('page', 1, type=int)

    pagination_data = {
        'total': 0,
        'per_page': 0,
        'current_page': page,
        'last_page': 1,
        'next_page_url': None,
        'prev_page_url': None
    }

    try:
        # Fetch episode data for the given anime_session_id
        params = {
            'm': 'release',
            'id': anime_session_id,
            'sort': 'episode_asc',
            'page': page
        }
        response = requests.get(API_BASE_URL, params=params, headers=API_HEADERS, timeout=10)
        response.raise_for_status()
        json_data = response.json()
        
        # The 'release' API returns episodes within a 'data' key.
        episodes = json_data.get('data', [])
        
        # Update pagination data from the API response
        pagination_data['total'] = json_data.get('total', 0)
        pagination_data['per_page'] = json_data.get('per_page', 0)
        pagination_data['current_page'] = json_data.get('current_page', page)
        pagination_data['last_page'] = json_data.get('last_page', 1)
        
        # Generate next/prev page URLs for the template
        # Make sure to pass anime_title to ensure continuity in navigation
        cp = pagination_data['current_page']
        lp = pagination_data['last_page']
        if cp < lp:
            pagination_data['next_page_url'] = url_for('episode_selection_page', anime_session_id=anime_session_id, anime_title=anime_title, page=cp + 1)
        if cp > 1:
            pagination_data['prev_page_url'] = url_for('episode_selection_page', anime_session_id=anime_session_id, anime_title=anime_title, page=cp - 1)

    except requests.exceptions.RequestException as e:
        app.logger.error(f"API Request Error for episodes (ID: {anime_session_id}, page: {page}): {e}")
        error_message = f"Could not fetch episode data. Please try again later. ({e})"
    except Exception as e:
        app.logger.error(f"Unexpected Error fetching episodes (ID: {anime_session_id}): {e}")
        error_message = f"An unexpected error occurred: {e}"

    return render_template(
        'episode_selection.html', 
        anime_session_id=anime_session_id, 
        episodes=episodes, 
        error_message=error_message,
        anime_title=anime_title, # Pass the fetched or default anime_title
        pagination=pagination_data # Pass pagination data to the template
    )

# --- Flask Route for Episode Download Links ---
@app.route('/api/episode-downloads/<string:anime_session_id>/<string:episode_session_id>', methods=['GET'])
def get_episode_downloads(anime_session_id, episode_session_id):
    """
    Fetches the animepahe.ru play page for a specific episode,
    parses it to find initial download links, then follows those links
    to extract the real kwik.si download URLs from embedded JavaScript.
    """
    play_url = f"https://animepahe.ru/play/{anime_session_id}/{episode_session_id}"
    final_downloads = []
    
    try:
        # 1. Fetch the animepahe.ru play page HTML
        response_play_page = requests.get(play_url, headers=API_HEADERS, timeout=15)
        response_play_page.raise_for_status()

        soup_play_page = BeautifulSoup(response_play_page.text, 'html.parser')

        # Find the div with id="pickDownload"
        download_div = soup_play_page.find('div', id='pickDownload')

        if download_div:
            # Find all initial download links (e.g., pahe.win links)
            initial_links = download_div.find_all('a', class_='dropdown-item')
            
            for link_tag in initial_links:
                initial_href = link_tag.get('href')
                text = link_tag.get_text(strip=True) # e.g., "df68 · 360p (46MB) BD"
                
                if initial_href:
                    # Remove info log for fetching redirect page
                    try:
                        # 2. Fetch the redirect page (e.g., pahe.win/cvhun)
                        # Use a new User-Agent that might be more generally accepted by redirection services
                        redirect_headers = {
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36',
                            'Referer': play_url # Indicate where the request is coming from
                        }
                        response_redirect_page = requests.get(initial_href, headers=redirect_headers, timeout=15)
                        response_redirect_page.raise_for_status()
                        soup_redirect_page = BeautifulSoup(response_redirect_page.text, 'html.parser')

                        # 3. Find the script containing the real download link
                        # As per user feedback, target the first script tag more directly
                        script_tags = soup_redirect_page.find_all('script', type='text/javascript')
                        
                        found_kwik_link = None
                        if script_tags:
                            target_script = script_tags[0] # Assume the first script tag
                            script_content = target_script.string

                            if script_content and 'kwik.si' in script_content:
                                # Regex to find https://kwik.si/f/ followed by alphanumeric characters
                                match = re.search(r'https:\/\/kwik\.si\/f\/[a-zA-Z0-9]+', script_content)
                                if match:
                                    found_kwik_link = match.group(0)
                                    
                        if found_kwik_link:
                            final_downloads.append({'text': text, 'href': found_kwik_link})
                    except requests.exceptions.RequestException as e:
                        app.logger.error(f"Error fetching redirect page {initial_href}: {e}")
                    except Exception as e:
                        app.logger.error(f"Error parsing redirect page {initial_href}: {e}")
                # Remove warning log for empty href
            # Remove info log for found download links
        # Remove warning log for missing download div
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error fetching play page for downloads ({play_url}): {e}")
        return jsonify({'error': 'Could not fetch initial download data. Network issue.'}), 500
    except Exception as e:
        app.logger.error(f"An unexpected error occurred parsing initial downloads ({play_url}): {e}")
        return jsonify({'error': 'An unexpected error occurred while parsing initial downloads.'}), 500

    return jsonify({'downloads': final_downloads})


# --- Flask Route for Image Proxying ---
@app.route('/proxy-image')
def proxy_image():
    """
    Proxies images from the animepahe.ru domain to bypass CORS restrictions.
    The image URL is passed as a query parameter.
    """
    image_url = request.args.get('url')
    if not image_url:
        return "Image URL not provided", 400

    try:
        # Fetch the image using requests.
        response = requests.get(image_url, headers=API_HEADERS, stream=True, timeout=10)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)

        # Get the content type from the response headers. If not present, default to octet-stream.
        mimetype = response.headers.get('Content-Type', 'application/octet-stream')
        
        # Return the image content with the correct MIME type
        return response.content, 200, {'Content-Type': mimetype}

    except requests.exceptions.RequestException:
        return "Error loading image", 500
    except Exception:
        return "An unexpected error occurred while proxying image", 500

# --- Run the Application ---
if __name__ == '__main__':
    # For local development only. In production, use Gunicorn or another WSGI server.
    app.run(debug=True)
