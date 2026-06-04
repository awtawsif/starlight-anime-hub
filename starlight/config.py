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
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:151.0) Gecko/20100101 Firefox/151.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Sec-GPC': '1',
    'Connection': 'keep-alive',
    'Cookie': 'cf_clearance=M3.CnHQF7dPtHdLxtE1Q1G_vaYyWIDtZysZl.81tG7c-1780580417-1.2.1.1-opFMTwfo2LJwR2v5rVakWO68qX3kM3TN6QnFbg._szdlQTq8Vkd5wk1_awWvErLWNUueLcxTEEODcYhXkdHEAMOe3hLW5Htrtm_PlLzAFLlQxSVMeAMCg3UHOge0uvMYDDnS1RBYcNxDPWZqt46wBmSRQJu6PRa6So1iroSlFLr_hvjD0xM2kkKWyBNlxjR7i3AMm1yMpYY9jelKcOjWi97wHQvge0COcZtcj_mknTSJTiJDmHFjhPwseYXnlqfS5RxNIFqCS_h2gp71hWzUH7c.OgNGNwIThBT69ouUo.3ExK1QZEewV0fzZvsnWIWoemXf1xG.rfxPWqdAv1WFSU0_k9RkgRXr_C3SNhTrIJcTutMXiijYiX2Yi7K003CqSIeD._qdnQi.9i8SGMaNar3Ci9LzBlUT9l4H6JxsqLI; XSRF-TOKEN=eyJpdiI6Imo3Tnd4K3NwUmw5REx4bkVVNEF2Qmc9PSIsInZhbHVlIjoiY3YvMFJtb3RSV0FaV3BIcVFhbGtKMzU3V3lsdWs5TUd1dklqUnM5czluL00ySVgvYitZYkZnNHlYZGxvQWNYcTVla0QxV1dPRWZ4UU50U2x6M09OV2YrWTEwRnplZlROWXZwby9IWVdsUkhlSnZ5QmFRUmtVVis3Z0Z5VE9WNHoiLCJtYWMiOiI2MjUyZjlmY2Y5NmUxNTc0YzRmNzUwNDU1NjY0M2M2Y2RiNWQ5YmM3YzliNjNkNTllMTI4MmQzOWE0ZDZmY2EwIiwidGFnIjoiIn0%3D; animepahe_session=eyJpdiI6ImV2aGxpV3lzZENKTi9jNjlkb1czVFE9PSIsInZhbHVlIjoiMUtrdkM5K1VTbnV2bVJrYzdHNzczT2k1dlRycWhEM1hYaXN2ak1ISUxvSXlzQkhySHpidmgwVUpEVUhXSFJleG5DbWJhTjE0czVXQTJ2b0R6TFNjcFBLbWc1dW52QlhLQ2YzcVJnMzNwN2hnSVB6aU1RTFgvWGJxMTU5bkVxNmsiLCJtYWMiOiIwNjc4M2E2ODI0Y2U5YmVhMTcwODFlYjUyMTFlNzk4ODNhZjEzYzk4ZGQ3NmQyYTEwYTRjMjljMTJlMGViMWE1IiwidGFnIjoiIn0%3D; SERVERID=pong; latest=6402',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Priority': 'u=0, i',
    'TE': 'trailers'
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