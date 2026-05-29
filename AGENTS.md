# Starlight Anime Hub — Agent Guide

## Stack
- **Backend**: Python CLI (click + rich), scrapes `animepahe.pw`
- **No database** — all state is `~/.starlight/state.json`
- **No test, lint, or typecheck setup** exists. Do not attempt to run any.

## Commands
```sh
pip install -e .         # Install the `starlight` CLI
starlight --help
starlight search "One Piece"
starlight watch onpi     # requires mpv
```

## Architecture
| File | Role |
|------|------|
| `starlight_cli/cli.py` | All CLI commands: `search`, `airing`, `detail`, `episodes`, `watch`, `download`, `bookmarks`, `continue-watching` |
| `starlight_cli/api.py` | Scrapes `animepahe.pw` (API + BeautifulSoup) |
| `starlight_cli/config.py` | Hardcoded cookies/headers for scraping target |
| `starlight_cli/kwik.py` | kwik.cx video URL extractor (decrypt JS obfuscation) |
| `starlight_cli/player.py` | mpv subprocess wrapper |
| `starlight_cli/state.py` | Persistent state via `~/.starlight/state.json` (bookmarks, watched, codes) |
| `setup.py` | Pip-installable entry point: `starlight=starlight_cli.cli:cli` |

## Short codes
Search/airing generates 4-6 char codes (`onpi` for One Piece, `moea` for Monster Eater).
Commands accept three identifier formats, resolved in order:
1. **Short code** — fastest, no API call, persisted in `~/.starlight/state.json`
2. **UUID** — backward compatible with the web app's session IDs
3. **Slug** — kebab-case title (`one-piece`, `frieren-beyond-journeys-end`), triggers search API + auto-pick if unique

Short codes are generated once and reused across sessions. Code format: first 2 chars of first 2 words, dedup with a number suffix (e.g. `onpi`, `onpi2`).

## Critical Gotchas

### Entire app depends on animepahe.pw
Scraping breaks if the site changes HTML structure, or cookies in `config.py` expire. No offline fallback.

### kwik.cx obfuscation changes
The `kwik.py` decrypt algorithm may break if kwik.cx changes their JS obfuscation. The reference implementation is in `anime-dl/anime-downloader`.

### Short codes are local
Codes in `~/.starlight/state.json` are local to this machine. No sync or sharing.
