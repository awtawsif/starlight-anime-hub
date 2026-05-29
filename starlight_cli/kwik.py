import re

from curl_cffi import requests

kwik_session = requests.Session()

DEAN_PACKER_RE = re.compile(
    r"return p}\('((?:\\'|[^'])*)',(\d+),(\d+),'([^']*)'\.split\('\|'\)"
)
HLS_URL_RE = re.compile(r"(https?://[^\"']+\.m3u8)")


def __unpack(p, a, c, k, d):
    def e_func(c_val):
        res = ""
        if c_val >= a:
            res = e_func(int(c_val / a))
        c_mod = c_val % a
        if c_mod > 35:
            res += chr(c_mod + 29)
        elif c_mod > 9:
            res += chr(c_mod + 87)
        else:
            res += str(c_mod)
        return res

    while c > 0:
        c -= 1
        val = k[c] if c < len(k) and k[c] else e_func(c)
        d[e_func(c)] = val

    return re.sub(r"\b\w+\b", lambda m: d.get(m.group(0), m.group(0)), p)


def extract_hls_url(kwik_url: str) -> str:
    headers = {
        "Referer": "https://animepahe.pw/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
    }
    resp = kwik_session.get(kwik_url, headers=headers, timeout=15)
    resp.raise_for_status()

    for match in DEAN_PACKER_RE.finditer(resp.text):
        p_val = match.group(1).replace("\\'", "'")
        a_val = int(match.group(2))
        c_val = int(match.group(3))
        k_val = match.group(4).split("|")

        unpacked = __unpack(p_val, a_val, c_val, k_val, {})
        m3u8_match = HLS_URL_RE.search(unpacked)
        if m3u8_match:
            return m3u8_match.group(1)

    raise ValueError("Could not find .m3u8 URL in kwik embed page")
