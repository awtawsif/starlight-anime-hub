"""
api_handlers.py
~~~~~~~~~~~~~~~
This module encapsulates all logic for interacting with the external AnimePahe API
and scraping data from its web pages. It includes functions for searching,
fetching anime details, retrieving episode lists, and extracting download links.
"""

import requests
import re
from bs4 import BeautifulSoup
import logging
from .config import API_BASE_URL, ANIME_PAGE_BASE_URL, API_HEADERS, REDIRECT_HEADERS

# Configure logging for this module
logger = logging.getLogger(__name__)

def _parse_related_anime_card(card_row_element):
    """
    Parses a BeautifulSoup element representing a single anime card (div with row mx-n1)
    from relations or recommendations sections.

    Args:
        card_row_element (bs4.element.Tag): The BeautifulSoup tag corresponding
                                            to an anime card.

    Returns:
        dict: A dictionary containing parsed anime card data.
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
            # Prioritize data-src, then src. Provide fallback.
            anime_card_data['poster'] = img_tag.get('data-src') or img_tag.get('src')
            if not anime_card_data['poster']:
                anime_card_data['poster'] = "https://placehold.co/100x150/1a202c/ffffff?text=No+Img"
        
        main_link_tag = img_link_container.find('a')
        if main_link_tag and main_link_tag.get('href'):
            # Extract session_id from the URL
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
            
            # Remove leading hyphen and strip whitespace
            anime_card_data['episodes_status'] = re.sub(r'^-', '', episodes_status_text).strip()

        # Season
        season_link = info_col.find('a', href=re.compile(r'/anime/season/'))
        if season_link:
            anime_card_data['season'] = season_link.get_text(strip=True)

    return anime_card_data

def fetch_anime_search_results(query):
    """
    Fetches anime search results from the AnimePahe API.

    Args:
        query (str): The search query for anime.

    Returns:
        tuple: A tuple containing a list of search results (dict) and an error message (str).
               Returns ([], error_message) on failure, (results, None) on success.
    """
    results = []
    error_message = None
    try:
        params = {'m': 'search', 'q': query}
        response = requests.get(API_BASE_URL, params=params, headers=API_HEADERS, timeout=10)
        response.raise_for_status()
        json_data = response.json()
        results = json_data.get('data', [])
    except requests.exceptions.RequestException as e:
        logger.error(f"API Request Error during search for '{query}': {e}")
        error_message = f"Could not connect to the anime search service. Please try again later. ({e})"
    except Exception as e:
        logger.error(f"Unexpected Error during search for '{query}': {e}")
        error_message = f"An unexpected error occurred during search: {e}"
    return results, error_message

def fetch_anime_details(anime_session_id):
    """
    Fetches and parses full details for a given anime session ID by scraping
    the animepahe.si/anime/{anime_session_id} page.

    Args:
        anime_session_id (str): The unique session ID for the anime.

    Returns:
        tuple: A tuple containing a dictionary of anime details and an error message.
               Returns ({}, error_message) on failure, (anime_details, None) on success.
    """
    detail_url = f"{ANIME_PAGE_BASE_URL}/{anime_session_id}"
    anime_details = {
        'title': 'N/A', 'synopsis': 'No synopsis available.',
        'poster': "https://placehold.co/300x450/1a202c/ffffff?text=No+Image+Available&font=inter",
        'synonyms': 'N/A', 'japanese': 'N/A', 'type': 'N/A', 'episodes': 'N/A',
        'status': 'N/A', 'duration': 'N/A', 'aired': 'N/A', 'season': 'N/A',
        'studio': 'N/A', 'theme': 'N/A', 'demographic': 'N/A', 'genre': 'N/A',
        'relations': [], 'recommendations': []
    }
    error_message = None

    try:
        response = requests.get(detail_url, headers=API_HEADERS, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml') 

        # Extract Synopsis
        synopsis_tag = soup.find('div', class_='anime-synopsis')
        anime_details['synopsis'] = synopsis_tag.get_text(strip=True) if synopsis_tag else 'No synopsis available.'

        # Extract Poster
        poster_div = soup.find('div', class_='anime-poster')
        if poster_div:
            poster_img_tag = poster_div.find('img')
            if poster_img_tag:
                anime_details['poster'] = poster_img_tag.get('data-src') or poster_img_tag.get('src')
            if not anime_details['poster']:
                 anime_details['poster'] = "https://placehold.co/300x450/1a202c/ffffff?text=No+Image+Available&font=inter"
        else:
            anime_details['poster'] = "https://placehold.co/300x450/1a202c/ffffff?text=No+Image+Available&font=inter"

        # Extract other details from the anime-info list
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
                    temp_p_tag = BeautifulSoup(str(p_tag), 'lxml').find('p') 
                    temp_strong_tag = temp_p_tag.find('strong')
                    if temp_strong_tag:
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

        # Supplement episode count via API if missing or unreliable
        if anime_details.get('episodes', 'N/A') in ('N/A', '', None):
            try:
                episode_api_url = f"{API_BASE_URL}?m=release&id={anime_session_id}&sort=episode_desc&page=1"
                response = requests.get(episode_api_url, headers=API_HEADERS, timeout=10)
                response.raise_for_status()
                json_data = response.json()
                episodes_total = json_data.get('total')
                if episodes_total:
                    anime_details['episodes'] = str(episodes_total)
            except Exception as e:
                logger.warning(f"Could not fetch episode total from API for {anime_session_id}: {e}")

        # Extract Relations
        relations_div = soup.find('div', class_='tab-content anime-relation row')
        if relations_div:
            relation_type_sections = relations_div.find_all('div', class_=re.compile(r'col-12 col-sm-6'))
            for section in relation_type_sections:
                relation_type_tag = section.find('h4')
                relation_type = relation_type_tag.find('span').get_text(strip=True) if relation_type_tag and relation_type_tag.find('span') else 'Unknown'
                
                anime_cards = section.find_all('div', class_='row mx-n1')
                for card_soup_element in anime_cards:
                    parsed_card = _parse_related_anime_card(card_soup_element)
                    parsed_card['relation_type_label'] = relation_type
                    anime_details['relations'].append(parsed_card)

        # Extract Recommendations
        recommendations_div = soup.find('div', class_='tab-content anime-recommendation row')
        if recommendations_div:
            recommendation_cards_containers = recommendations_div.find_all('div', class_=re.compile(r'col-12 col-sm-6'))
            for container in recommendation_cards_containers:
                anime_card_element = container.find('div', class_='row mx-n1')
                if anime_card_element:
                    parsed_card = _parse_related_anime_card(anime_card_element)
                    anime_details['recommendations'].append(parsed_card)

        # Ensure all expected keys are present
        default_keys = ['synonyms', 'japanese', 'type', 'episodes', 'status', 'duration', 'aired', 'season', 'studio', 'theme', 'demographic', 'genre'] 
        for k in default_keys:
            if k not in anime_details:
                anime_details[k] = 'N/A'
        
    except requests.exceptions.RequestException as e:
        logger.error(f"API Request Error fetching anime details ({detail_url}): {e}")
        error_message = f"Could not fetch anime details. Please check your connection or try again later. ({e})"
    except Exception as e:
        logger.error(f"An unexpected error occurred while parsing anime details ({detail_url}): {e}")
        error_message = f"An unexpected error occurred while fetching anime details: {e}"

    return anime_details, error_message

def fetch_episode_list(anime_session_id, page, sort_order='episode_asc'):
    """
    Fetches a paginated list of episodes for a given anime session ID from the API.

    Args:
        anime_session_id (str): The unique session ID for the anime.
        page (int): The page number of episodes to fetch.
        sort_order (str): The order to sort episodes ('episode_asc' or 'episode_desc').

    Returns:
        tuple: A tuple containing a list of episodes, pagination data, and an error message.
               Returns ([], {}, error_message) on failure, (episodes, pagination_data, None) on success.
    """
    episodes = []
    error_message = None
    pagination_data = {
        'total': 0, 'per_page': 0, 'current_page': page,
        'last_page': 1, 'next_page_url': None, 'prev_page_url': None
    }

    try:
        params = {
            'm': 'release', 'id': anime_session_id,
            'sort': sort_order, 'page': page
        }
        response = requests.get(API_BASE_URL, params=params, headers=API_HEADERS, timeout=10)
        response.raise_for_status()
        json_data = response.json()
        
        episodes = json_data.get('data', [])
        
        pagination_data['total'] = json_data.get('total', 0)
        pagination_data['per_page'] = json_data.get('per_page', 0)
        pagination_data['current_page'] = json_data.get('current_page', page)
        pagination_data['last_page'] = json_data.get('last_page', 1)
        
    except requests.exceptions.RequestException as e:
        logger.error(f"API Request Error for episodes (ID: {anime_session_id}, page: {page}): {e}")
        error_message = f"Could not fetch episode data. Please try again later. ({e})"
    except Exception as e:
        logger.error(f"Unexpected Error fetching episodes (ID: {anime_session_id}): {e}")
        error_message = f"An unexpected error occurred while fetching episodes: {e}"

    return episodes, pagination_data, error_message

def fetch_episode_download_links(anime_session_id, episode_session_id):
    """
    Fetches the animepahe.si play page for a specific episode,
    parses it to find initial download links, then follows those links
    to extract the real kwik.si download URLs from embedded JavaScript.

    Args:
        anime_session_id (str): The session ID of the anime.
        episode_session_id (str): The session ID of the specific episode.

    Returns:
        tuple: A tuple containing a list of download links (dict) and an error message.
               Returns ([], error_message) on failure, (download_links, None) on success.
    """
    play_url = f"https://animepahe.si/play/{anime_session_id}/{episode_session_id}"
    final_downloads = []
    error_message = None
    
    try:
        # 1. Fetch the animepahe.si play page HTML
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
                text = link_tag.get_text(strip=True)
                
                if initial_href:
                    try:
                        # 2. Fetch the redirect page (e.g., pahe.win/cvhun)
                        redirect_headers = REDIRECT_HEADERS.copy()
                        redirect_headers['Referer'] = play_url # Indicate where the request is coming from
                        
                        response_redirect_page = requests.get(initial_href, headers=redirect_headers, timeout=15)
                        response_redirect_page.raise_for_status()
                        soup_redirect_page = BeautifulSoup(response_redirect_page.text, 'html.parser')

                        # 3. Find the script containing the real download link
                        script_tags = soup_redirect_page.find_all('script', type='text/javascript')
                        
                        found_kwik_link = None
                        if script_tags:
                            target_script = script_tags[0]
                            script_content = target_script.string

                            if script_content and 'kwik.si' in script_content:
                                # Regex to find https://kwik.si/f/ followed by alphanumeric characters
                                match = re.search(r'https:\/\/kwik\.si\/f\/[a-zA-Z0-9]+', script_content)
                                if match:
                                    found_kwik_link = match.group(0)
                                    
                        if found_kwik_link:
                            final_downloads.append({'text': text, 'href': found_kwik_link})
                    except requests.exceptions.RequestException as e:
                        logger.error(f"Error fetching redirect page {initial_href}: {e}")
                    except Exception as e:
                        logger.error(f"Error parsing redirect page {initial_href}: {e}")
        else:
            logger.warning(f"Download div not found on play page for {play_url}")

    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching play page for downloads ({play_url}): {e}")
        error_message = 'Could not fetch initial download data due to a network issue.'
    except Exception as e:
        logger.error(f"An unexpected error occurred parsing initial downloads ({play_url}): {e}")
        error_message = 'An unexpected error occurred while parsing initial downloads.'

    return final_downloads, error_message

def proxy_image_content(image_url):
    """
    Proxies images from the animepahe.si domain to bypass CORS restrictions.

    Args:
        image_url (str): The URL of the image to proxy.

    Returns:
        tuple: A tuple containing image content (bytes) and MIME type (str) on success,
               or (None, None) on failure.
    """
    if not image_url:
        return None, None

    try:
        response = requests.get(image_url, headers=API_HEADERS, stream=True, timeout=10)
        response.raise_for_status()
        mimetype = response.headers.get('Content-Type', 'application/octet-stream')
        return response.content, mimetype
    except requests.exceptions.RequestException as e:
        logger.error(f"Error loading image from {image_url}: {e}")
        return None, None
    except Exception as e:
        logger.error(f"An unexpected error occurred while proxying image {image_url}: {e}")
        return None, None

def fetch_airing_anime(page):
    """
    Fetches the list of currently airing anime from the API.

    Args:
        page (int): The page number of airing anime to fetch.

    Returns:
        tuple: A tuple containing a list of airing anime, pagination data, and an error message.
               Returns ([], {}, error_message) on failure, (airing_anime, pagination_data, None) on success.
    """
    airing_anime = []
    error_message = None
    pagination_data = {
        'total': 0, 'per_page': 0, 'current_page': page,
        'last_page': 1, 'next_page_url': None, 'prev_page_url': None
    }
    try:
        params = {'m': 'airing', 'page': page}
        response = requests.get(API_BASE_URL, params=params, headers=API_HEADERS, timeout=10)
        response.raise_for_status()
        json_data = response.json()

        airing_anime = json_data.get('data', [])

        pagination_data['total'] = json_data.get('total', 0)
        pagination_data['per_page'] = json_data.get('per_page', 0)
        pagination_data['current_page'] = json_data.get('current_page', page)
        pagination_data['last_page'] = json_data.get('last_page', 1)

    except requests.exceptions.RequestException as e:
        logger.error(f"API Request Error fetching airing anime (page: {page}): {e}")
        error_message = f"Could not fetch airing anime. Please try again later. ({e})"
    except Exception as e:
        logger.error(f"Unexpected Error fetching airing anime (page: {page}): {e}")
        error_message = f"An unexpected error occurred while fetching airing anime: {e}"

    return airing_anime, pagination_data, error_message
