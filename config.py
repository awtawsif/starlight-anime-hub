"""
config.py
---------
This module contains configuration settings for the Anime API, HTTP headers, and website metadata.
"""

# Base URL for the animepahe API
API_BASE_URL = "https://animepahe.si/api"

# Base URL for anime detail pages (for scraping)
ANIME_PAGE_BASE_URL = "https://animepahe.si/anime"

# Default HTTP headers to use for API requests and web scraping
# These headers mimic a typical web browser request to avoid bot detection
API_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'https://animepahe.si/',
    'Cookie': '__ddgid_=iYWMAyRO4hf0okA6; __ddgmark_=RvCt0bqM4WqP1OmM; __ddg2_=IzuBL5o0aS1rhi2E; __ddg1_=ubd4cco9B88CLjKbptZd; ddg_last_challenge=1757580029138; latest=6266; __ddg8_=11tvp4DVa25P4RK3; __ddg10_=1757588181; __ddg9_=103.109.59.228; XSRF-TOKEN=eyJpdiI6InZyUitJQzhrVFN6U0JXSC9HK2JhcFE9PSIsInZhbHVlIjoiTDZnbzJ2NjVMWTY4TDhLaGxSdlcrTUxuSFc5RXVHcjJGTWU4UFlhd3hWLzdlVE1JVDJYTVdZdUZQb1BTTXpBRVlrTWsxbTJ0RXpmKzhRazUwUDZpNWFRVU04OXYrN3oyRTF2TURmTHQ1cTdObXJDeTJVM05mZXFuOThNbEM0ekYiLCJtYWMiOiIwM2NlOGI3Y2IxY2FkZTc2ZGExYjM4YzIwYjRlZDY0YjM4ZDYyZDA5MjdiYjQxYzU4ZDk2YTI3OWRhN2M3OGYyIiwidGFnIjoiIn0%3D; laravel_session=eyJpdiI6InYyVjM3QmQ0UEx1THNxN0NUNDFwc2c9PSIsInZhbHVlIjoiMjJRWTVhS1d6SitkeG1aay94MTJXQy9KQXd5KzZBSUI5UWJTelpNczFWR29VY2VPZkt6eHZHcTdZWjJJSUxIL0hjazltSWlHWXE4VnFHV1RWTjJBekgva3h3empLbWdGUVhqcHl6eE9ISU9Rekc2UER5QVBDODhIaHhzWXFCVWwiLCJtYWMiOiJkYzY4YTg1NDdhMjQzNzRlMmViNTQ0MDkwMjRiODg4NmYzNWVjZTZmZWE1MTAxOTliMDU5YjUzZWRlZTEwYWRkIiwidGFnIjoiIn0%3D',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin'
}

# User-Agent for fetching redirect pages (can be different to mimic a generic browser more closely)
REDIRECT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36',
}

# Website Metadata
WEBSITE_TITLE = "Starlight Anime Hub"
WEBSITE_DESCRIPTION = "Your ultimate destination for anime streaming and information."
WEBSITE_IMAGE = "/static/img/favicon.ico"  # Path to a default social sharing image
WEBSITE_KEYWORDS = "anime, watch anime, anime streaming, anime hub, latest anime, download anime, download anime for free, free anime downloading"