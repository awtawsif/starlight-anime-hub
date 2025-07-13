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

    // --- Utility Functions ---

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

            // Only proceed if the click was not on a bookmark button within the card
            if (event.target.closest('.bookmark-icon')) {
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
        });


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
