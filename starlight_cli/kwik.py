import re
import time
import logging

from curl_cffi import requests
from starlight_cli import state

logger = logging.getLogger(__name__)
_kwik_session = None


def _get_session():
    global _kwik_session
    if _kwik_session is None:
        _kwik_session = requests.Session()
    return _kwik_session


DEAN_PACKER_RE = re.compile(
    r"return p}\('((?:\\'|[^'])*)',(\d+),(\d+),'([^']*)'\.split\('\|'\)"
)
HLS_URL_RE = re.compile(r"(https?://[^\"']+\.m3u8)")


def _e_func(c_val, a):
    res = ""
    while c_val >= a:
        c_mod = c_val % a
        if c_mod > 35:
            res = chr(c_mod + 29) + res
        elif c_mod > 9:
            res = chr(c_mod + 87) + res
        else:
            res = str(c_mod) + res
        c_val //= a
    if c_val > 35:
        res = chr(c_val + 29) + res
    elif c_val > 9:
        res = chr(c_val + 87) + res
    else:
        res = str(c_val) + res
    return res


def __unpack(p, a, c, k, d):
    a = max(a, 2)

    while c > 0:
        c -= 1
        val = k[c] if c < len(k) and k[c] else _e_func(c, a)
        d[_e_func(c, a)] = val

    return re.sub(r"\b\w+\b", lambda m: d.get(m.group(0), m.group(0)), p)


def extract_hls_url(kwik_url: str) -> str:
    cached = state.get_kwik_cache().get(kwik_url)
    if cached and cached.get("expires", 0) > time.time():
        return cached["hls_url"]

    headers = {
        "Referer": "https://animepahe.pw/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
    }
    resp = _get_session().get(kwik_url, headers=headers, timeout=15)
    resp.raise_for_status()

    raw_m3u8 = HLS_URL_RE.search(resp.text)
    if raw_m3u8:
        hls_url = raw_m3u8.group(1)
        state.set_kwik_cache_entry(kwik_url, hls_url)
        return hls_url

    for match in DEAN_PACKER_RE.finditer(resp.text):
        p_val = match.group(1).replace("\\'", "'")
        a_val = int(match.group(2))
        c_val = int(match.group(3))
        k_val = match.group(4).split("|")

        unpacked = __unpack(p_val, a_val, c_val, k_val, {})
        m3u8_match = HLS_URL_RE.search(unpacked)
        if m3u8_match:
            hls_url = m3u8_match.group(1)
            state.set_kwik_cache_entry(kwik_url, hls_url)
            return hls_url

    logger.warning("No .m3u8 found in kwik page (first 2000 chars): %s", resp.text[:2000])
    raise ValueError(f"Could not find .m3u8 URL in kwik embed page: {kwik_url}")
