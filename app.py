import requests
from flask import Flask, request, render_template

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
    'Cookie': '__ddgid_=U5s6Z9J3BF0pfdhM; __ddgmark_=BiGlRBjK0HMCPWLj; __ddg2_=IgFUmsxCz7Q4c6zu; __ddg1_=Dxb4hS7Idd3Og4h75gA9; res=1080; aud=jpn; av1=0; latest=6114; __ddg8_=pOEMgyEFef8xzmDs; __ddg10_=1750607066; __ddg9_=103.204.209.15; XSRF-TOKEN=eyJpdiI6ImVhbG9vN0pFbCtrYSt1SVYyaEo1d1E9PSIsInZhbHVlIjoiOTdqUzQ4NmNHU0VaMkZEV29vd2ZIR0VoNWVaSkJKTTlTNW4rZ0dXaDVKYytQd3IzRHFpbnMvdmBqeTFlNzdXRHdkNnVPSzlNTHJRVHgvNzRZN2tHMjRhRDNtZkhBcjJBYUpiK010ZnhWV3JjLzZzMWFaZHQyWisyRHJYSmY3Z3UiLCJtYWMiOiI3ZmExYzUxMDIwYzhhYjkwZmEzNDlmY2FlMWI5ZGQ4NzdiZTU4YjRjZmM2MTRiNjUwNGVjNjk4ODlhYzQ4NjcyIiwidGFnIjoiIn0%3D; laravel_session=eyJpdiI6Ii9NOE4wOUZGaVpML3BlYzcwSTVRUXc9PSIsInZhbHVlIjoiZTJOOWhPaVNBc254Szk2K0pSejV5Q0VQNXFqM1ZwZEJtcUVQamdKb0liVzJZcFFjL1JKTVZ3TWJ0NkMyQzl3QXU4QzkwYjdyQnhnTDErcUpwSUZreWtJV2ZKREhGY2NNN0JNazIvZDcyVUFldDcraFMyb2kweEJyWmZDdThxcVgiLCJtYWMiOiI1ZGZiOWE0ODU4YjgyZTQwYmUxMjZjNzg0ZGM5YzcxOWM1ZmNhMmM1N2FhY2U1NjA5NDZhMDliNGZlNDc4MjE0IiwidGFnIjoiIn0%3D',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin'
}

# --- Flask Route ---
@app.route('/', methods=['GET', 'POST'])
def search_page():
    """
    Handles displaying the page and processing API search requests.
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
                error_message = f"Could not connect to the API. Please try again later. ({e})"
            except Exception as e:
                # Handle other potential errors (e.g., JSON parsing)
                error_message = f"An unexpected error occurred: {e}"

    # Render the HTML template with the provided data
    return render_template(
        'index.html', 
        results=results, 
        search_query=search_query,
        search_performed=search_performed,
        error_message=error_message
    )

# --- Run the Application ---
if __name__ == '__main__':
    # The app should be run using the 'flask' command in the terminal.
    # Example:
    # export FLASK_APP=app.py
    # export FLASK_ENV=development
    # flask run
    app.run(debug=True)
