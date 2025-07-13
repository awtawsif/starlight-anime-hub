# ✨ Starlight Anime Hub ✨

## 🚀 Introduction

Starlight Anime Hub is a sleek and intuitive web application designed for anime enthusiasts to effortlessly discover, explore, and access their favorite anime. Leveraging the AnimePahe API and intelligent web scraping, it provides a seamless experience for searching anime, viewing detailed information, browsing currently airing titles, and even finding direct download links for episodes.

Built with Flask for a robust backend and a dynamic frontend powered by Tailwind CSS and vanilla JavaScript, Starlight Anime Hub offers a responsive and visually appealing interface across all devices.

## 🌟 Features

*   **Anime Search:** Quickly find any anime by title with a powerful search functionality.
*   **Detailed Anime Pages:** Dive deep into anime details including synopsis, genre, type, status, related anime, and recommendations.
*   **Currently Airing Anime:** Stay up-to-date with the latest episodes of ongoing series, complete with pagination for easy browsing.
*   **Episode Listings & Downloads:** Browse episodes for any anime and retrieve direct download links for convenient offline viewing.
*   **Client-Side Bookmarking:** Save your favorite anime directly in your browser's local storage for quick access.
*   **Responsive Design:** Enjoy a consistent and optimized experience on desktops, tablets, and mobile devices, thanks to Tailwind CSS.
*   **Dynamic Modals:** Interactive modals for episode options and download links enhance user experience.
*   **Image Proxying:** Securely loads external images through the backend to bypass CORS restrictions.
*   **Clean & Modern UI:** A dark-themed interface with smooth animations and intuitive navigation.

## 🛠️ Technologies Used

### Backend
*   **Python 3.x**
*   **Flask:** Web framework for building the application's routes and logic.
*   **Requests:** For making HTTP requests to external APIs and web scraping.
*   **BeautifulSoup4 & LXML:** Powerful libraries for parsing HTML content and extracting data.
*   **Gunicorn:** WSGI HTTP Server for deploying the Flask application.

### Frontend
*   **HTML5:** Structure of the web pages.
*   **Tailwind CSS:** A utility-first CSS framework for rapid UI development and responsive design.
*   **Vanilla JavaScript:** For interactive elements, API calls, and client-side logic (e.g., bookmarking, modals).

## ⚙️ Getting Started

Follow these instructions to get a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

Before you begin, ensure you have the following installed:

*   **Python 3.8+**
*   **pip** (Python package installer)
*   **Node.js & npm** (Node Package Manager) - Required for Tailwind CSS build process.

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/starlight-anime-hub.git
    cd starlight-anime-hub
    ```

2.  **Set up Python Backend:**

    a. Create a virtual environment (recommended):
    ```bash
    python3 -m venv .venv
    ```

    b. Activate the virtual environment:
    *   On macOS/Linux:
        ```bash
        source .venv/bin/activate
        ```
    *   On Windows:
        ```bash
        .venv\Scripts\activate
        ```

    c. Install Python dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up Frontend (Tailwind CSS):**

    a. Install Node.js dependencies:
    ```bash
    npm install
    ```

    b. Build the production CSS (this will generate `static/css/tailwind.css`):
    ```bash
    npm run build:css
    ```
    *   For development, you can use `npm run watch:css` to automatically recompile CSS on changes.

### Running the Application

1.  **Ensure your Python virtual environment is activated.**
2.  **Start the Flask application:**
    ```bash
    gunicorn app:app
    ```
    (For local development, you can also run `python app.py` but `gunicorn` is recommended for production-like testing.)

3.  **Access the application:**
    Open your web browser and navigate to `http://127.0.0.1:8000` (or the address Gunicorn specifies).

## 🌐 Live Demo

Experience Starlight Anime Hub live at: [https://starlight-anime-hub.vercel.app/](https://starlight-anime-hub.vercel.app/)

## 💡 Usage

*   **Search:** Use the search bar in the navigation to find anime by title.
*   **Browse Airing Anime:** The homepage displays currently airing anime. Use the pagination at the bottom to navigate through pages.
*   **View Details:** Click on any anime card to view its detailed page, including synopsis, cast, and related titles.
*   **Episode Selection & Download:** From an anime's detail page or the airing anime cards, click on an episode to see options to view details or download.
*   **Bookmarks:** Click the star icon on anime cards to bookmark them. Access your bookmarks from the navigation bar.

## 📂 Project Structure

```
starlight-anime-hub/
├── api_handlers.py       # Handles all external API interactions and web scraping logic.
├── app.py                # Main Flask application entry point.
├── config.py             # Configuration settings for API URLs and headers.
├── Procfile              # For Heroku deployment (specifies how to run the app).
├── requirements.txt      # Python dependencies.
├── routes.py             # Defines all Flask routes and their corresponding logic.
├── runtime.txt           # Specifies Python runtime for deployment.
├── tailwind.config.js    # Tailwind CSS configuration, including content purging paths.
├── package.json          # Node.js dependencies and Tailwind build scripts.
├── static/               # Static assets (CSS, JS, images).
│   ├── css/
│   │   ├── style.css     # Custom CSS and Tailwind imports.
│   │   └── tailwind.css  # Compiled Tailwind CSS (generated by npm run build:css).
│   ├── img/
│   └── js/               # Frontend JavaScript files.
│       ├── bookmark_manager.js # Manages client-side bookmarks.
│       ├── episode_selection.js # Handles episode selection and download modal logic.
│       ├── index.js      # Main frontend logic, including modal orchestration.
│       └── navbar.js     # Navbar functionality (mobile toggle, hide on scroll).
└── templates/            # Jinja2 HTML templates.
    ├── anime_details_page.html
    ├── bookmarks.html
    ├── episode_selection.html
    ├── index.html
    └── navbar.html
```

## 🤝 Contributing

Contributions are welcome! If you have suggestions for improvements or new features, please open an issue or submit a pull request.

## 📄 License

This project is licensed under the MIT License - see the `LICENSE` file for details (if you have one, otherwise specify your chosen license).

## 🙏 Acknowledgements

*   [AnimePahe](https://animepahe.ru/) for the API and data.
*   [Flask](https://flask.palletsprojects.com/)
*   [Tailwind CSS](https://tailwindcss.com/)
*   [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
*   [Requests](https://requests.readthedocs.io/en/latest/)
