/**
 * main.js
 *
 * This script consolidates and refactors the functionality from:
 * - navbar.js
 * - index.js
 * - episode_selection.js (relevant parts for modal handling)
 * - bookmark_manager.js
 *
 * It aims to provide a cleaner, more organized, and efficient client-side experience
 * by centralizing event listeners, managing modals, and handling bookmark logic.
 */

(function() {
    // --- Constants ---
    const BOOKMARK_STORAGE_KEY = 'starlightAnimeBookmarks';
    const WATCHED_EPISODES_STORAGE_KEY = 'starlightWatchedEpisodes'; // New storage key for watched episodes
    const ITEMS_PER_PAGE_CONTINUE_WATCHING = 30; // Number of unwatched episodes to show per page

    // --- DOM Element References (Cached for performance) ---
    const navbar = document.getElementById('navbar');
    const menuToggle = document.getElementById('menu-toggle');
    const navLinks = document.getElementById('nav-links');

    const episodeOptionsModal = document.getElementById('episodeOptionsModal');
    const episodeOptionsModalTitle = document.getElementById('episodeOptionsModalTitle');
    const viewDetailsBtn = document.getElementById('viewDetailsBtn');
    const downloadEpisodeBtn = document.getElementById('downloadEpisodeBtn');
    const closeEpisodeOptionsModalBtn = episodeOptionsModal ? episodeOptionsModal.querySelector('button') : null;

    const downloadModal = document.getElementById('downloadModal');
    const downloadModalTitle = document.getElementById('downloadModalTitle');
    const downloadLinksContainer = document.getElementById('downloadLinks');
    const loadingMessage = document.getElementById('loadingMessage');
    const noLinksFoundMessage = document.getElementById('noLinksFound');
    const errorMessage = document.getElementById('errorMessage');
    const closeDownloadModalBtn = downloadModal ? downloadModal.querySelector('button') : null;

    // --- Global state for Continue Watching pagination ---
    let allUnwatchedEpisodes = []; // Stores all unwatched episodes after initial fetch
    let currentContinueWatchingPage = 1;

    // --- Utility Functions for Bookmarks ---

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
            return [];
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
     * @param {Object} animeData An object containing anime details.
     */
    function addBookmark(animeData) {
        let bookmarks = getBookmarkData();
        // Safeguard: Ensure poster is a string, even if null/undefined from dataset
        animeData.poster = animeData.poster || '';
        if (!isBookmarked(animeData.session_id)) {
            bookmarks.push(animeData);
            saveBookmarkData(bookmarks);
            console.log(`Bookmark added: ${animeData.title}, Poster saved: ${animeData.poster}`);
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
     * Renders the initial bookmark status of an icon based on whether the anime is bookmarked.
     * @param {HTMLElement} bookmarkIcon The HTML element that serves as the bookmark icon.
     * @param {string} sessionId The unique session ID of the anime.
     */
    function renderBookmarkStatus(bookmarkIcon, sessionId) {
        if (isBookmarked(sessionId)) {
            bookmarkIcon.classList.remove('text-gray-400', 'hover:text-green-300');
            bookmarkIcon.classList.add('text-green-400');
            bookmarkIcon.innerHTML = `<svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 12H4"></path></svg>`;
            bookmarkIcon.title = "Remove from Bookmarks";
        } else {
            bookmarkIcon.classList.remove('text-green-400');
            bookmarkIcon.classList.add('text-gray-400', 'hover:text-green-300');
            bookmarkIcon.innerHTML = `<svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path></svg>`;
            bookmarkIcon.title = "Add to Bookmarks";
        }
    }

    /**
     * Toggles the bookmark status of an anime and updates the UI element.
     * @param {HTMLElement} bookmarkElement The HTML element (button) that was clicked.
     * @param {Object} animeData An object containing anime details.
     */
    function toggleBookmark(bookmarkElement, animeData) {
        const sessionId = animeData.session_id;

        if (isBookmarked(sessionId)) {
            removeBookmark(sessionId);
        } else {
            addBookmark(animeData);
        }
        renderBookmarkStatus(bookmarkElement, sessionId); // Use bookmarkElement directly
    }

    // --- New Utility Functions for Episode Tracking ---

    /**
     * Retrieves all watched episodes data from localStorage.
     * @returns {Object} An object where keys are animeSessionIds and values are arrays of watched episodeSessionIds.
     * Returns an empty object if no data is found or if storage fails.
     */
    function getWatchedEpisodesData() {
        try {
            const storedData = localStorage.getItem(WATCHED_EPISODES_STORAGE_KEY);
            return storedData ? JSON.parse(storedData) : {};
        } catch (error) {
            console.error("Error retrieving watched episodes data from localStorage:", error);
            return {};
        }
    }

    /**
     * Saves the current watched episodes data to localStorage.
     * @param {Object} data The object containing watched episodes data to save.
     */
    function saveWatchedEpisodesData(data) {
        try {
            localStorage.setItem(WATCHED_EPISODES_STORAGE_KEY, JSON.stringify(data));
        } catch (error) {
            console.error("Error saving watched episodes data to localStorage:", error);
        }
    }

    /**
     * Checks if a specific episode of an anime is marked as watched.
     * @param {string} animeSessionId The session ID of the anime.
     * @param {string} episodeSessionId The session ID of the episode.
     * @returns {boolean} True if the episode is watched, false otherwise.
     */
    function isEpisodeWatched(animeSessionId, episodeSessionId) {
        const watchedData = getWatchedEpisodesData();
        return watchedData[animeSessionId] && watchedData[animeSessionId].includes(episodeSessionId);
    }

    /**
     * Marks an episode as watched or unwatched and updates the UI.
     * @param {HTMLElement} watchedIcon The HTML element that serves as the watched icon.
     * @param {string} animeSessionId The session ID of the anime.
     * @param {string} episodeSessionId The session ID of the episode.
     */
    function toggleEpisodeWatched(watchedIcon, animeSessionId, episodeSessionId) {
        let watchedData = getWatchedEpisodesData();
        
        if (!watchedData[animeSessionId]) {
            watchedData[animeSessionId] = [];
        }

        const isCurrentlyWatched = watchedData[animeSessionId].includes(episodeSessionId);

        if (isCurrentlyWatched) {
            // Mark as unwatched
            watchedData[animeSessionId] = watchedData[animeSessionId].filter(id => id !== episodeSessionId);
            console.log(`Episode ${episodeSessionId} of anime ${animeSessionId} marked as UNWATCHED.`);
        } else {
            // Mark as watched
            watchedData[animeSessionId].push(episodeSessionId);
            console.log(`Episode ${episodeSessionId} of anime ${animeSessionId} marked as WATCHED.`);
        }

        saveWatchedEpisodesData(watchedData);
        renderEpisodeWatchedStatus(watchedIcon, animeSessionId, episodeSessionId);
        
        // If on the continue watching page, re-render the list to remove the watched episode
        if (document.getElementById('continue-watching-list')) {
            renderContinueWatchingPage(currentContinueWatchingPage); // Re-render current page
        }
    }

    /**
     * Renders the visual status of an episode's watched icon.
     * @param {HTMLElement} watchedIcon The HTML element that serves as the watched icon.
     * @param {string} animeSessionId The session ID of the anime.
     * @param {string} episodeSessionId The session ID of the episode.
     */
    function renderEpisodeWatchedStatus(watchedIcon, animeSessionId, episodeSessionId) {
        if (isEpisodeWatched(animeSessionId, episodeSessionId)) {
            watchedIcon.classList.remove('text-gray-400', 'hover:text-green-300');
            watchedIcon.classList.add('text-green-400');
            watchedIcon.innerHTML = `<svg class="h-6 w-6" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path></svg>`;
            watchedIcon.title = "Mark as Unwatched";
            // Add a class to the parent card for styling
            watchedIcon.closest('.episode-card')?.classList.add('watched-episode');
        } else {
            watchedIcon.classList.remove('text-green-400');
            watchedIcon.classList.add('text-gray-400', 'hover:text-green-300');
            watchedIcon.innerHTML = `<svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>`;
            watchedIcon.title = "Mark as Watched";
            // Remove the class from the parent card
            watchedIcon.closest('.episode-card')?.classList.remove('watched-episode');
        }
    }

    /**
     * Marks all episodes of a specific anime as watched.
     * @param {string} animeSessionId The session ID of the anime.
     */
    async function markAllEpisodesWatchedForAnime(animeSessionId) {
        let watchedData = getWatchedEpisodesData();
        if (!watchedData[animeSessionId]) {
            watchedData[animeSessionId] = [];
        }

        try {
            let currentPage = 1;
            let lastPage = 1;
            let allEpisodes = [];

            do {
                const response = await fetch(`/api/anime-episodes/${animeSessionId}?page=${currentPage}`);
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const data = await response.json();
                if (data.error) {
                    throw new Error(data.error);
                }
                allEpisodes = allEpisodes.concat(data.episodes || []);
                lastPage = data.pagination.last_page || 1;
                currentPage++;
            } while (currentPage <= lastPage);

            const episodeSessionsToMark = allEpisodes.map(ep => ep.session);
            // Add only new episodes to watched list, avoid duplicates
            watchedData[animeSessionId] = Array.from(new Set([...watchedData[animeSessionId], ...episodeSessionsToMark]));
            saveWatchedEpisodesData(watchedData);
            console.log(`All episodes for anime ${animeSessionId} marked as WATCHED.`);

            // Update UI for all episode cards on the current page
            document.querySelectorAll('.episode-card[data-anime-session-id="' + animeSessionId + '"] .watched-icon').forEach(iconElement => {
                renderEpisodeWatchedStatus(iconElement, animeSessionId, iconElement.dataset.episodeSessionId);
            });
            // If on continue watching page, refresh it
            if (document.getElementById('continue-watching-list')) {
                renderContinueWatchingPage(currentContinueWatchingPage);
            }

        } catch (error) {
            console.error(`Error marking all episodes watched for anime ${animeSessionId}:`, error);
            // Provide user feedback, e.g., a temporary message on the UI
            alert("Failed to mark all episodes as watched. Please try again later.");
        }
    }

    /**
     * Unmarks all episodes of a specific anime as watched.
     * @param {string} animeSessionId The session ID of the anime.
     */
    function unmarkAllEpisodesWatchedForAnime(animeSessionId) {
        let watchedData = getWatchedEpisodesData();
        if (watchedData[animeSessionId]) {
            watchedData[animeSessionId] = []; // Clear the array for this anime
            saveWatchedEpisodesData(watchedData);
            console.log(`All episodes for anime ${animeSessionId} marked as UNWATCHED.`);

            // Update UI for all episode cards on the current page
            document.querySelectorAll('.episode-card[data-anime-session-id="' + animeSessionId + '"] .watched-icon').forEach(iconElement => {
                renderEpisodeWatchedStatus(iconElement, animeSessionId, iconElement.dataset.episodeSessionId);
            });
            // If on continue watching page, refresh it
            if (document.getElementById('continue-watching-list')) {
                renderContinueWatchingPage(currentContinueWatchingPage);
            }
        }
    }


    // --- Navbar Logic ---
    let lastScrollTop = 0;
    const navbarHeight = navbar ? navbar.offsetHeight : 0;

    function handleNavbarScroll() {
        let currentScroll = window.scrollY || document.documentElement.scrollTop;
        if (currentScroll > lastScrollTop && currentScroll > navbarHeight) {
            navbar.classList.add('-translate-y-full', 'opacity-0');
        } else if (currentScroll < lastScrollTop || currentScroll <= 0) {
            navbar.classList.remove('-translate-y-full', 'opacity-0');
        }
        lastScrollTop = currentScroll <= 0 ? 0 : currentScroll;
    }

    function handleMenuToggle() {
        if (navLinks) {
            navLinks.classList.toggle('hidden');
            navLinks.classList.toggle('flex');
        }
    }

    function handleResize() {
        if (navLinks && window.innerWidth >= 1024) {
            navLinks.classList.remove('hidden', 'flex');
            navLinks.style.display = ''; // Reset display style
        } else if (navLinks && !navLinks.classList.contains('flex')) {
            navLinks.classList.add('hidden');
        }
    }


    // --- Modal Logic ---

    /**
     * Opens a given modal element.
     * @param {HTMLElement} modalElement The modal div to open.
     */
    function openModal(modalElement) {
        if (modalElement) {
            modalElement.classList.remove('hidden');
            // A small timeout to ensure the browser registers the 'hidden' removal
            // before 'active' is added, allowing CSS transition to apply.
            setTimeout(() => {
                modalElement.classList.add('active');
            }, 10);
        }
    }

    /**
     * Closes a given modal element.
     * @param {HTMLElement} modalElement The modal div to close.
     */
    function closeModal(modalElement) {
        if (modalElement) {
            modalElement.classList.remove('active');
            // A small timeout to allow CSS transition to complete before hiding.
            setTimeout(() => {
                modalElement.classList.add('hidden');
            }, 100); // This duration should match the CSS transition duration for opacity/visibility
        }
    }

    /**
     * Handles opening the Episode Options Modal from an anime card click.
     * Uses event delegation on the document for efficiency.
     * @param {Event} event The click event.
     */
    function handleEpisodeCardClick(event) {
        const clickedElement = event.target.closest('.anime-card[data-anime-session-id], .episode-card[data-anime-session-id]');

        if (clickedElement) {
            const animeSessionId = clickedElement.dataset.animeSessionId;
            const animeTitle = clickedElement.dataset.animeTitle;
            const episodeSessionId = clickedElement.dataset.episodeSessionId;
            const episodeNumber = clickedElement.dataset.episodeNumber;

            // Only proceed if the click was not on a bookmark or watched button within the card
            if (event.target.closest('.bookmark-icon') || event.target.closest('.watched-icon')) {
                return;
            }

            if (!animeSessionId || !animeTitle || !episodeSessionId || !episodeNumber) {
                console.error("Missing data for episode options. Cannot open modal.", {
                    animeSessionId, animeTitle, episodeSessionId, episodeNumber
                });
                return;
            }

            // If the episode options modal exists, show it. Otherwise, directly show the downloads.
            if (episodeOptionsModal) {
                episodeOptionsModalTitle.textContent = animeTitle + ' - Episode ' + episodeNumber;
                viewDetailsBtn.href = `/anime/${animeSessionId}?anime_title=${encodeURIComponent(animeTitle)}`;
                downloadEpisodeBtn.onclick = function() {
                    closeModal(episodeOptionsModal);
                    showDownloads(animeSessionId, episodeSessionId, 'Episode ' + episodeNumber);
                };
                openModal(episodeOptionsModal);
            } else {
                showDownloads(animeSessionId, episodeSessionId, 'Episode ' + episodeNumber);
            }
        }
    }

    /**
     * Fetches and displays download links in the Download Modal.
     * @param {string} animeSessionId The session ID of the anime.
     * @param {string} episodeSessionId The session ID of the specific episode.
     * @param {string} episodeTitle A display title for the episode.
     */
    async function showDownloads(animeSessionId, episodeSessionId, episodeTitle) {
        const modalTitleElement = downloadModalTitle || document.getElementById('modalTitle');
        if (!downloadModal || !modalTitleElement || !downloadLinksContainer || !loadingMessage || !noLinksFoundMessage || !errorMessage) {
            console.error("Download modal elements not found.");
            return;
        }

        modalTitleElement.textContent = episodeTitle + ' - Download Options';
        loadingMessage.classList.remove('hidden');
        noLinksFoundMessage.classList.add('hidden');
        errorMessage.classList.add('hidden');
        downloadLinksContainer.innerHTML = '';
        downloadLinksContainer.appendChild(loadingMessage);

        openModal(downloadModal);

        try {
            const response = await fetch(`/api/episode-downloads/${animeSessionId}/${episodeSessionId}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();

            loadingMessage.classList.add('hidden');
            if (data.downloads && data.downloads.length > 0) {
                data.downloads.forEach(link => {
                    const a = document.createElement('a');
                    a.href = link.href;
                    a.textContent = link.text;
                    a.target = '_blank';
                    a.rel = 'noopener noreferrer';
                    a.className = 'block px-5 py-3 bg-blue-600 text-white font-semibold rounded-lg text-center hover:bg-blue-700 transition-colors duration-100 shadow-md btn-primary';
                    downloadLinksContainer.appendChild(a);
                });
            } else {
                noLinksFoundMessage.classList.remove('hidden');
            }
        } catch (error) {
            console.error('Error fetching download links:', error);
            loadingMessage.classList.add('hidden');
            errorMessage.textContent = 'Failed to load download links. Please check your connection or try again later.';
            errorMessage.classList.remove('hidden');
        }
    }

    /**
     * Renders an individual anime card for the bookmarks page.
     * This function is now part of main.js to be used by renderBookmarksPage.
     * @param {Object} anime The anime data to render.
     * @returns {string} The HTML string for the anime card.
     */
    function renderBookmarkCard(anime) {
        // Construct proxy image URL relative to Flask's static folder
        // Corrected: Use '/static/proxy-image' to match Flask route
        const proxyImageUrl = `/proxy-image?url=${encodeURIComponent(anime.poster || '')}`; // Safeguard for empty poster
        // Construct detail page URL using placeholder for Flask's url_for
        const detailPageUrl = `/anime/${anime.session_id}?anime_title=${encodeURIComponent(anime.title)}`;

        return `
            <a href="${detailPageUrl}"
               class="anime-card block bg-black border-2 border-green-400 rounded-none shadow-none overflow-hidden
                      transform hover:scale-100 hover:shadow-none hover:border-green-400 group relative flex flex-col h-full">

                <!-- Image container -->
                <div class="relative w-full aspect-[2/3] overflow-hidden flex-shrink-0">
                    <img
                        src="${proxyImageUrl}"
                        alt="Poster for ${anime.title}"
                        class="absolute inset-0 w-full h-full object-cover rounded-none border-b-2 border-green-400 shadow-none group-hover:scale-100 group-hover:brightness-100"
                        onerror="this.onerror=null;this.src='https://placehold.co/300x450/1a202c/ffffff?text=No+Image+Available&font=inter'; console.error('Image failed to load:', this.src);"
                        loading="lazy"
                    >
                    <!-- Bookmark Icon -->
                    <button
                        class="bookmark-icon absolute top-3 left-3 z-20 p-2 rounded-none bg-black border-2 border-green-400 text-green-400 hover:text-green-300 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 focus:ring-offset-black"
                        title="Add to Bookmarks"
                        data-session-id="${anime.session_id}"
                        data-anime-title="${anime.title.replace(/"/g, '&quot;')}"
                        data-poster="${anime.poster ? anime.poster.replace(/"/g, '&quot;') : ''}"
                        data-type="${anime.type.replace(/"/g, '&quot;')}"
                        data-year="${anime.year || 'N/A'}"
                    >
                        <!-- SVG for initial state (will be updated by renderBookmarkStatus) -->
                        <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
                        </svg>
                    </button>
                </div>

                <!-- Text content -->
                <div class="p-4 text-center bg-black flex-grow relative z-0">
                    <h3 class="font-extrabold text-green-400 text-lg mb-1 truncate" title="${anime.title}">${anime.title}</h3>
                    <p class="text-sm text-green-300 font-medium">${anime.type} &middot; ${anime.year || 'N/A'}</p>
                </div>
            </a>
        `;
    }

    /**
     * Renders the bookmarks page content.
     * This function is specifically for the bookmarks.html page.
     */
    function renderBookmarksPage() {
        const bookmarkListContainer = document.getElementById('bookmark-list');
        const noBookmarksMessage = document.getElementById('no-bookmarks-message');

        if (!bookmarkListContainer || !noBookmarksMessage) {
            // Not on the bookmarks page, or elements not found
            return;
        }

        const bookmarks = getBookmarkData();
        if (bookmarks.length > 0) {
            bookmarkListContainer.innerHTML = bookmarks.map(anime => renderBookmarkCard(anime)).join('');
            noBookmarksMessage.classList.add('hidden');

            // After rendering, ensure the bookmark icons reflect their current status
            bookmarkListContainer.querySelectorAll('.bookmark-icon').forEach(iconElement => {
                const sessionId = iconElement.dataset.sessionId;
                if (sessionId) {
                    renderBookmarkStatus(iconElement, sessionId);
                }
            });
        } else {
            bookmarkListContainer.innerHTML = ''; // Clear any previous content
            noBookmarksMessage.classList.remove('hidden');
        }
    }

    /**
     * Renders an individual episode card for the "Continue Watching" page.
     * @param {Object} episode The episode data.
     * @param {Object} animeData The parent anime data (for title, session_id).
     * @returns {string} The HTML string for the episode card.
     */
    function renderEpisodeCardForTracking(episode, animeData) {
        const proxyImageUrl = `/proxy-image?url=${encodeURIComponent(episode.snapshot || '')}`;
        const detailPageUrl = `/anime/${animeData.session_id}?anime_title=${encodeURIComponent(animeData.title)}`;

        // Determine if the episode is watched to apply initial styling
        const isWatched = isEpisodeWatched(animeData.session_id, episode.session);
        const watchedClass = isWatched ? 'watched-episode' : '';
        const watchedIconSvg = isWatched 
            ? `<svg class="h-6 w-6" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path></svg>`
            : `<svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>`;
        const watchedIconTitle = isWatched ? "Mark as Unwatched" : "Mark as Watched";

        return `
            <div class="episode-card group block cursor-pointer relative ${watchedClass}"
               data-anime-session-id="${animeData.session_id}"
               data-anime-title="${animeData.title.replace(/"/g, '&quot;')}"
               data-episode-session-id="${episode.session}"
               data-episode-number="${episode.episode}"
            > 
                <!-- Watched Icon -->
                <button
                    class="watched-icon absolute top-3 right-3 z-20 rounded-full text-gray-400 hover:text-green-300"
                    title="${watchedIconTitle}"
                    data-anime-session-id="${animeData.session_id}"
                    data-episode-session-id="${episode.session}"
                >
                    ${watchedIconSvg}
                </button>

                <!-- Image container - wrapped in an anchor for main click behavior -->
                <a href="javascript:void(0);" 
                   class="block w-full h-full"
                   data-anime-session-id="${animeData.session_id}"
                   data-anime-title="${animeData.title.replace(/"/g, '&quot;')}"
                   data-episode-session-id="${episode.session}"
                   data-episode-number="${episode.episode}"
                >
                    <div class="relative w-full aspect-video overflow-hidden flex-shrink-0">
                        <img 
                            src="${proxyImageUrl}" 
                            alt="Snapshot for Episode ${episode.episode}" 
                            class="absolute inset-0 w-full h-full object-cover border-b-2 border-green-400"
                            onerror="this.onerror=null;this.src='https://placehold.co/300x168/000000/00ff00?text=No+Snapshot+Available&font=vt323';"
                            loading="lazy"
                        >
                    </div>
                    <!-- Text content -->
                    <div class="p-4 text-center bg-black">
                        <h3 class="font-bold text-green-400 text-lg mb-1 truncate" title="${animeData.title} - Episode ${episode.episode}">${animeData.title} - Ep ${episode.episode}</h3>
                        ${episode.title ? `<p class="text-sm text-green-300 truncate" title="${episode.title}">${episode.title}</p>` : ''}
                        <p class="text-xs text-gray-400 mt-1">${episode.duration}</p>
                    </div>
                </a>
            </div>
        `;
    }

    /**
     * Renders the pagination controls for the "Continue Watching" page.
     * @param {number} totalItems The total number of unwatched episodes.
     * @param {number} currentPage The current page number.
     * @param {number} itemsPerPage The number of items per page.
     */
    function renderContinueWatchingPagination(totalItems, currentPage, itemsPerPage) {
        const paginationContainer = document.getElementById('continue-watching-pagination');
        if (!paginationContainer) return;

        const totalPages = Math.ceil(totalItems / itemsPerPage);
        paginationContainer.innerHTML = ''; // Clear previous pagination
        
        if (totalPages <= 1) {
            paginationContainer.classList.add('hidden');
            return;
        }

        paginationContainer.classList.remove('hidden');

        // Page numbers
        const numVisiblePages = 4; // Max number of page buttons to show
        let startPage = Math.max(1, currentPage - Math.floor(numVisiblePages / 2));
        let endPage = Math.min(totalPages, startPage + numVisiblePages - 1);

        // Adjust startPage if endPage is constrained
        if (endPage - startPage + 1 < numVisiblePages) {
            startPage = Math.max(1, endPage - numVisiblePages + 1);
        }

        if (startPage > 1) {
            const firstPageBtn = document.createElement('button');
            firstPageBtn.textContent = '1';
            firstPageBtn.className = `mb-2 px-5 py-3 bg-black border-2 border-green-400 text-green-400 font-semibold`;
            firstPageBtn.onclick = () => {
                currentContinueWatchingPage = 1;
                renderContinueWatchingPage(currentContinueWatchingPage);
                window.scrollTo({ top: 0, behavior: 'smooth' });
            };
            paginationContainer.appendChild(firstPageBtn);
            if (startPage > 2) {
                const ellipsis = document.createElement('span');
                ellipsis.textContent = '...';
                ellipsis.className = 'mb-2 px-4 py-2 text-gray-500';
                paginationContainer.appendChild(ellipsis);
            }
        }

        for (let i = startPage; i <= endPage; i++) {
            const pageButton = document.createElement('button');
            pageButton.textContent = i;
            pageButton.className = `mb-2 px-5 py-3 ${i === currentPage ? 'bg-green-500 text-black font-bold' : 'bg-black border-2 border-green-400 text-green-400 font-semibold'}`;
            pageButton.onclick = () => {
                currentContinueWatchingPage = i;
                renderContinueWatchingPage(currentContinueWatchingPage);
                window.scrollTo({ top: 0, behavior: 'smooth' });
            };
            paginationContainer.appendChild(pageButton);
        }

        if (endPage < totalPages) {
            if (endPage < totalPages - 1) {
                const ellipsis = document.createElement('span');
                ellipsis.textContent = '...';
                ellipsis.className = 'mb-2 px-4 py-2 text-gray-500';
                paginationContainer.appendChild(ellipsis);
            }
            const lastPageBtn = document.createElement('button');
            lastPageBtn.textContent = totalPages;
            lastPageBtn.className = `mb-2 px-5 py-3 bg-black border-2 border-green-400 text-green-400 font-semibold`;
            lastPageBtn.onclick = () => {
                currentContinueWatchingPage = totalPages;
                renderContinueWatchingPage(currentContinueWatchingPage);
                window.scrollTo({ top: 0, behavior: 'smooth' });
            };
            paginationContainer.appendChild(lastPageBtn);
        }
    }


    /**
     * Renders the "Continue Watching" page content.
     * Fetches unwatched episodes for bookmarked anime, handling pagination.
     * @param {number} page The current page number to render. Defaults to 1.
     */
    async function renderContinueWatchingPage(page = 1) {
        currentContinueWatchingPage = page; // Update global page state
        const continueWatchingListContainer = document.getElementById('continue-watching-list');
        const loadingMessageDiv = document.getElementById('loading-unwatched-message');
        const noUnwatchedMessageDiv = document.getElementById('no-unwatched-message');
        const errorMessageDiv = document.getElementById('continue-watching-error-message');
        const errorTextSpan = document.getElementById('continue-watching-error-text');
        const paginationContainer = document.getElementById('continue-watching-pagination');


        if (!continueWatchingListContainer || !loadingMessageDiv || !noUnwatchedMessageDiv || !errorMessageDiv || !errorTextSpan || !paginationContainer) {
            return;
        }

        // Show loading, hide others
        loadingMessageDiv.classList.remove('hidden');
        noUnwatchedMessageDiv.classList.add('hidden');
        errorMessageDiv.classList.add('hidden');
        paginationContainer.classList.add('hidden'); // Hide pagination during loading
        continueWatchingListContainer.innerHTML = ''; // Clear previous content

        const bookmarks = getBookmarkData();
        const watchedEpisodes = getWatchedEpisodesData();
        
        // Fetch all unwatched episodes only once if not already fetched
        if (allUnwatchedEpisodes.length === 0 || page === 1) { // Re-fetch on first load or if list is empty
            let tempAllUnwatched = [];
            let hasFetchError = false; // Track errors during fetching

            if (bookmarks.length === 0) {
                loadingMessageDiv.classList.add('hidden');
                noUnwatchedMessageDiv.classList.remove('hidden');
                noUnwatchedMessageDiv.querySelector('p:first-of-type').textContent = "No anime bookmarked yet!";
                noUnwatchedMessageDiv.querySelector('p:last-of-type').textContent = "Bookmark some anime to start tracking your progress.";
                return;
            }

            for (const anime of bookmarks) {
                let currentPageForAnime = 1;
                let lastPageForAnime = 1;
                let allEpisodesForThisAnime = [];

                try {
                    do {
                        const response = await fetch(`/api/anime-episodes/${anime.session_id}?page=${currentPageForAnime}`);
                        if (!response.ok) {
                            throw new Error(`HTTP error! status: ${response.status}`);
                        }
                        const data = await response.json();

                        if (data.error) {
                            throw new Error(data.error);
                        }

                        allEpisodesForThisAnime = allEpisodesForThisAnime.concat(data.episodes || []);
                        lastPageForAnime = data.pagination.last_page || 1;
                        currentPageForAnime++;

                    } while (currentPageForAnime <= lastPageForAnime);

                    const watchedForThisAnime = watchedEpisodes[anime.session_id] || [];

                    const unwatchedForThisAnime = allEpisodesForThisAnime.filter(episode => 
                        !watchedForThisAnime.includes(episode.session)
                    );

                    unwatchedForThisAnime.forEach(episode => {
                        tempAllUnwatched.push({
                            episodeData: episode,
                            animeData: anime 
                        });
                    });

                } catch (error) {
                    console.error(`Error fetching all episodes for bookmarked anime ${anime.title} (${anime.session_id}):`, error);
                    hasFetchError = true;
                    // Only show one error message for the first error encountered, or append if multiple
                    if (errorTextSpan.textContent === '') {
                        errorTextSpan.textContent = `Could not load all episodes for "${anime.title}". Please try again later.`;
                    } else {
                        errorTextSpan.textContent += ` Also, failed for "${anime.title}".`;
                    }
                    errorMessageDiv.classList.remove('hidden');
                }
            }
            allUnwatchedEpisodes = tempAllUnwatched; // Store the full list
            if (hasFetchError) {
                errorMessageDiv.classList.remove('hidden');
            }
        }

        loadingMessageDiv.classList.add('hidden'); 

        if (allUnwatchedEpisodes.length > 0) {
            // Sort the full list before pagination
            allUnwatchedEpisodes.sort((a, b) => {
                const animeTitleA = a.animeData.title.toLowerCase();
                const animeTitleB = b.animeData.title.toLowerCase();
                if (animeTitleA < animeTitleB) return -1;
                if (animeTitleA > animeTitleB) return 1;
                
                const episodeNumA = parseInt(a.episodeData.episode, 10);
                const episodeNumB = parseInt(b.episodeData.episode, 10);
                return episodeNumA - episodeNumB;
            });

            // Apply pagination to the sorted list
            const startIndex = (page - 1) * ITEMS_PER_PAGE_CONTINUE_WATCHING;
            const endIndex = startIndex + ITEMS_PER_PAGE_CONTINUE_WATCHING;
            const episodesToRender = allUnwatchedEpisodes.slice(startIndex, endIndex);

            continueWatchingListContainer.innerHTML = episodesToRender.map(item => 
                renderEpisodeCardForTracking(item.episodeData, item.animeData)
            ).join('');

            // Re-initialize watched status for newly rendered cards
            continueWatchingListContainer.querySelectorAll('.watched-icon').forEach(iconElement => {
                const animeSessionId = iconElement.dataset.animeSessionId;
                const episodeSessionId = iconElement.dataset.episodeSessionId;
                if (animeSessionId && episodeSessionId) {
                    renderEpisodeWatchedStatus(iconElement, animeSessionId, episodeSessionId);
                }
            });

            renderContinueWatchingPagination(allUnwatchedEpisodes.length, currentContinueWatchingPage, ITEMS_PER_PAGE_CONTINUE_WATCHING);

        } else if (!hasError) {
            noUnwatchedMessageDiv.classList.remove('hidden');
            noUnwatchedMessageDiv.querySelector('p:first-of-type').textContent = "You're all caught up!";
            noUnwatchedMessageDiv.querySelector('p:last-of-type').textContent = "No unwatched episodes from your bookmarked anime.";
        }
    }


    // --- Initialization ---
    document.addEventListener('DOMContentLoaded', () => {
        // Register Service Worker
        if ('serviceWorker' in navigator) {
            window.addEventListener('load', () => {
                navigator.serviceWorker.register('/static/js/service-worker.js')
                    .then(registration => {
                        console.log('Service Worker registered with scope:', registration.scope);
                    })
                    .catch(error => {
                        console.error('Service Worker registration failed:', error);
                    });
            });
        }

        // Initialize navbar scroll behavior
        if (navbar) {
            window.addEventListener('scroll', handleNavbarScroll);
        }

        // Initialize mobile menu toggle
        if (menuToggle) {
            menuToggle.addEventListener('click', handleMenuToggle);
        }

        // Initialize window resize listener for navbar
        window.addEventListener('resize', handleResize);
        handleResize(); // Call once on load to set initial state

        // Initialize bookmark status for all existing bookmark icons on the page
        // This runs on all pages to ensure icons are correct on initial load
        document.querySelectorAll('.bookmark-icon').forEach(iconElement => {
            const sessionId = iconElement.dataset.sessionId;
            if (sessionId) {
                renderBookmarkStatus(iconElement, sessionId);
            }
        });

        // Initialize watched status for all existing watched icons on the page (episode_selection.html)
        document.querySelectorAll('.watched-icon').forEach(iconElement => {
            const animeSessionId = iconElement.dataset.animeSessionId;
            const episodeSessionId = iconElement.dataset.episodeSessionId;
            if (animeSessionId && episodeSessionId) {
                renderEpisodeWatchedStatus(iconElement, animeSessionId, episodeSessionId);
            }
        });


        // Event delegation for bookmark toggling (for dynamically added elements)
        document.addEventListener('click', (event) => {
            const bookmarkBtn = event.target.closest('.bookmark-icon');
            if (bookmarkBtn) {
                // Prevent the parent card's click handler from firing
                event.stopPropagation();
                event.preventDefault(); // Prevent default button behavior (e.g., form submission)

                // Extract anime data from the button's dataset or parent card's dataset
                const animeData = {
                    session_id: bookmarkBtn.dataset.sessionId,
                    title: bookmarkBtn.dataset.animeTitle || bookmarkBtn.closest('.anime-card')?.querySelector('h3')?.title || 'Unknown Title',
                    poster: bookmarkBtn.dataset.poster || bookmarkBtn.closest('.anime-card')?.querySelector('img')?.src || '',
                    type: bookmarkBtn.dataset.type || bookmarkBtn.closest('.anime-card')?.querySelector('p.text-blue-300')?.textContent.split(' ')[0] || 'Unknown Type',
                    // Extract year from data-aired if present, otherwise try data-year, then infer from text
                    year: (() => {
                        const airedDate = bookmarkBtn.dataset.aired;
                        if (airedDate) {
                            const match = airedDate.match(/\d{4}/);
                            return match ? match[0] : 'N/A';
                        }
                        return bookmarkBtn.dataset.year || bookmarkBtn.closest('.anime-card')?.querySelector('p.text-blue-300')?.textContent.split(' ')[2] || 'N/A';
                    })()
                };
                toggleBookmark(bookmarkBtn, animeData); // Pass the actual button element
            }

            // Event delegation for watched episode toggling
            const watchedBtn = event.target.closest('.watched-icon');
            if (watchedBtn) {
                event.stopPropagation();
                event.preventDefault();

                const animeSessionId = watchedBtn.dataset.animeSessionId;
                const episodeSessionId = watchedBtn.dataset.episodeSessionId;
                
                if (animeSessionId && episodeSessionId) {
                    toggleEpisodeWatched(watchedBtn, animeSessionId, episodeSessionId);
                } else {
                    console.error("Missing data for watched episode toggle.");
                }
            }
        });

        // Event listener for "Mark All Watched" button
        const markAllWatchedBtn = document.getElementById('markAllWatchedBtn');
        if (markAllWatchedBtn) {
            markAllWatchedBtn.addEventListener('click', () => {
                const animeSessionId = markAllWatchedBtn.dataset.animeSessionId;
                if (animeSessionId) {
                    markAllEpisodesWatchedForAnime(animeSessionId);
                } else {
                    console.error("Anime session ID not found for 'Mark All Watched' button.");
                }
            });
        }

        // Event listener for "Unmark All Watched" button
        const unmarkAllWatchedBtn = document.getElementById('unmarkAllWatchedBtn');
        if (unmarkAllWatchedBtn) {
            unmarkAllWatchedBtn.addEventListener('click', () => {
                const animeSessionId = markAllWatchedBtn.dataset.animeSessionId; // Use the same data-anime-session-id
                if (animeSessionId) {
                    unmarkAllEpisodesWatchedForAnime(animeSessionId);
                } else {
                    console.error("Anime session ID not found for 'Unmark All Watched' button.");
                }
            });
        }


        // Event delegation for opening episode options modal (for dynamically added elements)
        // This targets the main anime/episode cards on index.html and episode_selection.html
        document.addEventListener('click', handleEpisodeCardClick);

        // Close Episode Options Modal
        if (closeEpisodeOptionsModalBtn) {
            closeEpisodeOptionsModalBtn.addEventListener('click', () => closeModal(episodeOptionsModal));
        }
        if (episodeOptionsModal) {
            episodeOptionsModal.addEventListener('click', (event) => {
                if (event.target === episodeOptionsModal) {
                    closeModal(episodeOptionsModal);
                }
            });
        }

        // Close Download Links Modal
        if (closeDownloadModalBtn) {
            closeDownloadModalBtn.addEventListener('click', () => closeModal(downloadModal));
        }
        if (downloadModal) {
            downloadModal.addEventListener('click', (event) => {
                if (event.target === downloadModal) {
                    closeModal(downloadModal);
                }
            });
        }

        // --- Page-specific Initialization ---
        // For bookmarks.html
        if (document.getElementById('bookmark-list')) {
            renderBookmarksPage();
        }
        // For episode_selection.html (to apply watched status on load)
        if (document.querySelector('.episode-card')) {
            document.querySelectorAll('.episode-card').forEach(card => {
                const watchedIcon = card.querySelector('.watched-icon');
                const animeSessionId = card.dataset.animeSessionId;
                const episodeSessionId = card.dataset.episodeSessionId;
                if (watchedIcon && animeSessionId && episodeSessionId) {
                    renderEpisodeWatchedStatus(watchedIcon, animeSessionId, episodeSessionId);
                }
            });
        }
        // For continue_watching.html
        if (document.getElementById('continue-watching-list')) {
            renderContinueWatchingPage(currentContinueWatchingPage);
        }
    });

    // Expose functions to global scope if needed by inline scripts (e.g., toggleText)
    window.toggleBookmark = toggleBookmark;
    window.showDownloads = showDownloads; // For episode_selection.html direct calls
    window.closeModal = (modalId) => { // Generic closeModal for direct HTML calls
        const modalElement = document.getElementById(modalId);
        if (modalElement) {
            closeModal(modalElement);
        }
    };
    window.showEpisodeOptionsFromCard = handleEpisodeCardClick; // For index.html direct calls
})();
