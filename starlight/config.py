"""
config.py
---------
This module contains configuration settings for the Anime API, HTTP headers, and website metadata.
"""

# Base URL for the animepahe API
API_BASE_URL = "https://animepahe.pw/api"

# Base URL for anime detail pages (for scraping)
ANIME_PAGE_BASE_URL = "https://animepahe.pw/anime"

# Default HTTP headers to use for API requests and web scraping
# These headers mimic a typical web browser request to avoid bot detection
API_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'https://animepahe.pw/',
    'Cookie': '__ddg1_=YUhBIBrskG3DbXfMe7ZH; __ddgid_=hIJ8lS0aeWgM3Jlx; __ddgmark_=IPZS5KPogrKD15mV; ann-fakesite=0; res=1080; aud=jpn; av1=0; __ddg2_=z5tlCvKDwcz72UHy; latest=6713; ddg_last_challenge=1775485035452; __ddg8_=URNinrdLmCF6HaSH; __ddg10_=1775647159; __ddg9_=43.245.120.209; XSRF-TOKEN=eyJpdiI6InE0bU9zZlNaNEJEWm91R2VpU1djbkE9PSIsInZhbHVlIjoiR3VXZll6dVNOUDFhMHlBRWdFaXBsRTE3Y2F2RFd0MEx4Nzl5ZzBQbkRiQzhVbXVYMTBwTWhOOUE3TndQSFZqWEVtVS9iR2w2SlFaU1d4WVVwOFI3RUE1ZDRmU1Y1TDM3b1ZmV2RFL2tVdHJ1Mm5BQnNLVHV1cDIxS0NncHJtK3MiLCJtYWMiOiJlNTUxYmEwN2IzNmFlNmQ2MzAwYWU3MjM0MDEzMmRlZDI2Y2MyOTEyNDYwMTZlZWUzMjAxYTJmZDVlYzkyYzIxIiwidGFnIjoiIn0%3D; laravel_session=eyJpdiI6ImI4YktRYVk4ZTV3T2kxdzh5YURPT2c9PSIsInZhbHVlIjoieGZ3LzhYdWdhWi84ZStwSG1uOGpBWDdTaFd2akRmaXlvMkdNcUhkZmI4Qy9ZS2d1TkNrR2FvYVk5ZlQ4b09tRmtqbFFxZy9WQVJ0c0s5d00xcGtpdXFDUzJwL1gvVzVCOGZvVHA3aERESS9HdVJUZ3AvVW1UZWhOcUZUVlFoWWUiLCJtYWMiOiJkNzhlMWI4ZmZjOTU5OWM4OTg1OWYwZmJkYjZhNDAzNDQwOTQ0ZGUyNzZhZTBiNjZiZTBjZWU4ZjRhYmQ3OGQ3IiwidGFnIjoiIn0%3D',
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
WEBSITE_DESCRIPTION = "Your ultimate destination for anime streaming and information. Create constellations of your favorite anime, resume your trajectory, and stay updated with ongoing transmissions."
WEBSITE_IMAGE = "/static/img/favicon.ico"  # Path to a default social sharing image
WEBSITE_KEYWORDS = "anime, watch anime, anime streaming, anime hub, latest anime, download anime, download anime for free, free anime downloading, constellations, resume trajectory, ongoing transmissions"