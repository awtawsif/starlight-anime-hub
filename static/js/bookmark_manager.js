// bookmark_manager.js

/**
 * Manages anime bookmarks using the browser's localStorage.
 * Bookmarks are stored as an array of objects, each representing an anime.
 */

const BOOKMARK_STORAGE_KEY = 'starlightAnimeBookmarks';

/**
 * Retrieves all bookmarked anime data from localStorage.
 * @returns {Array<Object>} An array of bookmarked anime objects. Returns an empty array if no bookmarks are found or if storage fails.
 */
function getBookmarkData() {
    try {
        const storedData = localStorage.getItem(BOOKMARK_STORAGE_KEY);
        return storedData ? JSON.parse(storedData) : [];
    } catch (error) {
        console.error("Error retrieving bookmark data from localStorage:", error);
        return []; // Return empty array on error
    }
}

/**
 * Saves the current array of bookmarked anime data to localStorage.
 * @param {Array<Object>} data The array of anime objects to save.
 */
function saveBookmarkData(data) {
    try {
        localStorage.setItem(BOOKMARK_STORAGE_KEY, JSON.stringify(data));
    } catch (error) {
        console.error("Error saving bookmark data to localStorage:", error);
        // Optionally, inform the user if storage is full or restricted
    }
}

/**
 * Checks if an anime is currently bookmarked.
 * @param {string} sessionId The unique session ID of the anime.
 * @returns {boolean} True if the anime is bookmarked, false otherwise.
 */
function isBookmarked(sessionId) {
    const bookmarks = getBookmarkData();
    return bookmarks.some(anime => anime.session_id === sessionId);
}

/**
 * Adds an anime to the bookmarks. Prevents adding duplicates.
 * @param {Object} animeData An object containing anime details (e.g., session_id, title, poster, type, year).
 */
function addBookmark(animeData) {
    let bookmarks = getBookmarkData();
    if (!isBookmarked(animeData.session_id)) {
        bookmarks.push(animeData);
        saveBookmarkData(bookmarks);
        console.log(`Bookmark added: ${animeData.title}`);
    } else {
        console.log(`Anime '${animeData.title}' is already bookmarked.`);
    }
}

/**
 * Removes an anime from the bookmarks based on its session ID.
 * @param {string} sessionId The unique session ID of the anime to remove.
 */
function removeBookmark(sessionId) {
    let bookmarks = getBookmarkData();
    const initialLength = bookmarks.length;
    bookmarks = bookmarks.filter(anime => anime.session_id !== sessionId);
    if (bookmarks.length < initialLength) {
        saveBookmarkData(bookmarks);
        console.log(`Bookmark removed for session ID: ${sessionId}`);
    } else {
        console.log(`Anime with session ID '${sessionId}' was not found in bookmarks.`);
    }
}

/**
 * Toggles the bookmark status of an anime and updates the UI element.
 * This function is intended to be called directly from an HTML element's onclick event.
 *
 * @param {Event} event The click event object.
 * @param {Object} animeData An object containing anime details required for bookmarking.
 * Expected properties:
 * - session_id: The unique session ID of the anime.
 * - title: The title of the anime.
 * - poster: URL to the anime's poster image.
 * - type: Type of anime (e.g., TV, Movie).
 * - year (optional): The release year of the anime (for search/airing).
 */
function toggleBookmark(event, animeData) {
    event.stopPropagation(); // Prevent card click event if nested
    event.preventDefault(); // Prevent default link behavior if applicable

    const bookmarkIcon = event.currentTarget; // The element that was clicked (the SVG or its parent button)
    const sessionId = animeData.session_id;

    if (isBookmarked(sessionId)) {
        removeBookmark(sessionId);
        bookmarkIcon.classList.remove('text-green-400'); // Remove filled style
        bookmarkIcon.classList.add('text-gray-400', 'hover:text-green-300'); // Add outline style
        bookmarkIcon.innerHTML = `<svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path></svg>`;
        bookmarkIcon.title = "Add to Bookmarks";
    } else {
        addBookmark(animeData);
        bookmarkIcon.classList.remove('text-gray-400', 'hover:text-green-300'); // Remove outline style
        bookmarkIcon.classList.add('text-green-400'); // Add filled style
        bookmarkIcon.innerHTML = `<svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 12H4"></path></svg>`;
        bookmarkIcon.title = "Remove from Bookmarks";
    
