"""
run.py
~~~~~~
This is the main entry point for running the Starlight Anime Hub application.
"""

from starlight import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
