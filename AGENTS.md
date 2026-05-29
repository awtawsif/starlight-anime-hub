# Starlight Anime Hub — Agent Guide

## Stack
- **Backend**: Flask 3.1 (Python), Blueprint `main_bp` in `starlight/routes.py`
- **Frontend**: Tailwind CSS v4 (CLI, not PostCSS plugin)
- **No database** — all user state (bookmarks, watched episodes) is client-side `localStorage`
- **No test, lint, or typecheck setup** exists. Do not attempt to run any.
- **PWA**: service worker + manifest.json in `starlight/static/`

## Commands
```sh
npm run build:css     # Build Tailwind: starlight/static/css/style.css → tailwind.css
npm run watch:css     # Watch mode
python run.py         # Dev server (Flask debug)
gunicorn run:app      # Production (matching Procfile)
```

## Architecture
| File | Role |
|------|------|
| `run.py` | Entrypoint → `starlight/__init__.py:create_app()` |
| `starlight/routes.py` | All routes (7 HTML, 2 JSON API, 1 image proxy) |
| `starlight/api_handlers.py` | Scrapes `animepahe.pw` (API + BeautifulSoup) |
| `starlight/config.py` | Hardcoded cookies/headers for scraping target |
| `starlight/extensions.py` | `Flask-Caching` with `SimpleCache` (in-memory, volatile) |
| `starlight/static/js/main.js` | All client JS (bookmarks, watched, modals, PWA) |
| `starlight/templates/` | 10 Jinja2 templates |
| `starlight_cli/` | Terminal CLI (click + rich) — install via `pip install -e .` |
| `starlight_cli/cli.py` | All CLI commands: `search`, `airing`, `detail`, `episodes`, `watch`, `download`, `bookmarks`, `continue-watching` |
| `starlight_cli/kwik.py` | kwik.cx video URL extractor (decrypt JS obfuscation) |
| `starlight_cli/player.py` | mpv subprocess wrapper |
| `starlight_cli/state.py` | Persistent state via `~/.starlight/state.json` (bookmarks, watched, codes) |
| `setup.py` | Pip-installable entry point: `starlight=starlight_cli.cli:cli` |

## Short codes (CLI only)
Search/airing generates 4-6 char codes (`onpi` for One Piece, `moea` for Monster Eater).
Commands accept three identifier formats, resolved in order:
1. **Short code** — fastest, no API call, persisted in `~/.starlight/state.json`
2. **UUID** — backward compatible with the web app's session IDs
3. **Slug** — kebab-case title (`one-piece`, `frieren-beyond-journeys-end`), triggers search API + auto-pick if unique

Short codes are generated once and reused across sessions. Code format: first 2 chars of first 2 words, dedup with a number suffix (e.g. `onpi`, `onpi2`).

## Critical Gotchas

### Tailwind content paths are wrong
`tailwind.config.js` scans `./templates/` and `./static/js/` but the actual files are under `./starlight/templates/` and `./starlight/static/js/`. **No files are scanned** — the CSS output is whatever was last built manually.

### Entire app depends on animepahe.pw
Scraping breaks if the site changes HTML structure, or cookies in `config.py` expire. No offline fallback.

### Python version mismatch across environments
- `.python-version`: 3.13
- `vercel.json` (deploy): python3.9
- `runtime.txt` (Heroku): python-3.10

### Caching is in-memory
`SimpleCache` resets on every restart. `@cache.cached` timeouts: 300s (home), 3600s (details/episodes), 900s (downloads/proxy).

### No CI/CD config in repo
Deployment config exists in `Procfile` (Heroku, gunicorn) and `vercel.json` (Vercel, `@vercel/python`).
