"""
config.py
---------
This module contains configuration settings for the Anime API, HTTP headers, and website metadata.
"""

# Base URL for the animepahe API
API_BASE_URL = "https://animepahe.ru/api"

# Base URL for anime detail pages (for scraping)
ANIME_PAGE_BASE_URL = "https://animepahe.ru/anime"

# Default HTTP headers to use for API requests and web scraping
# These headers mimic a typical web browser request to avoid bot detection
API_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'https://animepahe.ru/',
    'Cookie': '__ddg8_=YJOG0vO34DB3UbwT; __ddg10_=1752381610; __ddg9_=103.109.59.228; __ddgid_=2hXmxDnC41E10u3d; __ddgmark_=N92cqg6NvQTrMSTB; __ddg2_=FZF2QUR1OoUtn6W5; __ddg1_=jDF17M15htxHLqIAwo7P; res=1080; aud=jpn; av1=0; ddg_last_challenge=1752342417847; latest=6035; XSRF-TOKEN=eyJpdiI6IlBsd1M3emV1b3RoMTl4OTdvUTRhYUE9PSIsInZhbHVlIjoiUEtKa3NGb3hrOG1rNWx5QTlRR3NvMTI5YVkzMnRSaU1hbzZTSEwvQ29DUi9PVDJmaFhaMnh5c2hlT2xUbDFLWkIwVzRndFk2emhDeVBQeTVYWXBQaGtxVTBHT1YxNEszRkZhWXMvTFVWT1lnU296TUNJZitqUTM4d0QwY25ZOTciLCJtYWMiOiJmOWI2NTIyYzUyYTgyM2Q5MmZhZTUwMDRlNzJhZDFhOGQ2MmEwYTExYWJjNWIzODIxMmQ5NDEwNjRmYzM3ZWNmIiwidGFnIjoiIn0%3D; laravel_session=eyJpdiI6IjdDcVB3eGNWYVZyTWpyY3IzYlpLaFE9PSIsInZhbHVlIjoiZjFscWJRQmJWV0ZReHdMd1UzNEkzR2tqSVlSSnJ3Rlk5OWptKzF3bnVCTVpKd2p3TGVHSzlzMGdMMDNmVnQ0WDRVeDRLcGdta2lUM2JlWUtWbVlqZGFnRFI3dXBpUW9MZjNJTG84ejN5RHNZcnVjMDN6NkJFZnVISExIbHBUSnoiLCJtYWMiOiJlM2E3ZDNmNDA1YWU2NmU1ODRkMjQwODNmMzE3MzI4ZGY4NWI4MDMyZjNmMGIyYmU5NTQ3YmI2YWZjNzllYzA3IiwidGFnIjoiIn0%3D',
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