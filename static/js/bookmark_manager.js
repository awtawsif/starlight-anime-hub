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
        bookmarkIcon.classList.remove('text-yellow-400'); // Remove filled style
        bookmarkIcon.classList.add('text-gray-400', 'hover:text-yellow-300'); // Add outline style
        bookmarkIcon.innerHTML = `<svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.545 4.757a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.545 4.757c.3.921-.755 1.683-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.565-1.838-.197-1.538-1.118l1.545-4.757a1 1 0 00-.363-1.118L2.92 8.72c-.783-.57-.38-1.81.588-1.81h4.915a1 1 0 00.95-.69l1.545-4.757z"></path></svg>`;
        bookmarkIcon.title = "Add to Bookmarks";
    } else {
        addBookmark(animeData);
        bookmarkIcon.classList.remove('text-gray-400', 'hover:text-yellow-300'); // Remove outline style
        bookmarkIcon.classList.add('text-yellow-400'); // Add filled style
        bookmarkIcon.innerHTML = `<svg class="h-6 w-6" fill="currentColor" viewBox="0 0 20 20"><path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.683-1.538 1.118l-2.8-2.034a1 1 0 00-1.176 0l-2.8 2.034c-.783.565-1.838-.197-1.538-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.92 8.72c-.783-.57-.38-1.81.588-1.81h3.462a1 1 0 00.95-.69l1.07-3.292z"></path></svg>`;
        bookmarkIcon.title = "Remove from Bookmarks";
    }
}

/**
 * Renders the initial bookmark status of an icon based on whether the anime is bookmarked.
 * This should be called on page load for each bookmarkable element.
 *
 * @param {HTMLElement} bookmarkIcon The HTML element (e.g., SVG or its parent button) that serves as the bookmark icon.
 * @param {string} sessionId The unique session ID of the anime.
 */
function renderBookmarkStatus(bookmarkIcon, sessionId) {
    if (isBookmarked(sessionId)) {
        bookmarkIcon.classList.remove('text-gray-400', 'hover:text-yellow-300');
        bookmarkIcon.classList.add('text-yellow-400');
        bookmarkIcon.innerHTML = `<svg class="h-6 w-6" fill="currentColor" viewBox="0 0 20 20"><path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.683-1.538 1.118l-2.8-2.034a1 1 0 00-1.176 0l-2.8 2.034c-.783.565-1.838-.197-1.538-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.92 8.72c-.783-.57-.38-1.81.588-1.81h3.462a1 1 0 00.95-.69l1.07-3.292z"></path></svg>`;
        bookmarkIcon.title = "Remove from Bookmarks";
    } else {
        bookmarkIcon.classList.remove('text-yellow-400');
        bookmarkIcon.classList.add('text-gray-400', 'hover:text-yellow-300');
        bookmarkIcon.innerHTML = `<svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.545 4.757a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.545 4.757c.3.921-.755 1.683-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.565-1.838-.197-1.538-1.118l1.545-4.757a1 1 0 00-.363-1.118L2.92 8.72c-.783-.57-.38-1.81.588-1.81h4.915a1 1 0 00.95-.69l1.545-4.757z"></path></svg>`;
        bookmarkIcon.title = "Add to Bookmarks";
    }
}
