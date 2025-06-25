"""
app.py
~~~~~~
This is the main application file for the Starlight Anime Hub.
It initializes the Flask application, configures logging, and registers
the blueprints containing the application's routes.
"""

from flask import Flask, url_for
import logging
from routes import main_bp # Import the blueprint from your new routes.py

# Configure logging (minimal, or remove if not needed for production)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Create a Flask application instance
app = Flask(__name__)

# Register the blueprint containing your routes
app.register_blueprint(main_bp)

# --- Run the Application ---
if __name__ == '__main__':
    # For local development only. In production, use Gunicorn or another WSGI server.
    app.run(debug=True)

