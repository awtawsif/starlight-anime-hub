import re

import requests

CHARACTER_MAP = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ+/"

KWIK_PARAMS_RE = re.compile(r'\("(\w+)",\d+,"(\w+)",(\d+),(\d+),\d+\)')
KWIK_D_URL_RE = re.compile(r'action="([^"]+)"')
KWIK_TOKEN_RE = re.compile(r'value="([^"]+)"')


def _get_string(content: str, s1: int, s2: int) -> str:
    slice_2 = CHARACTER_MAP[:s2]
    acc = 0
    for n, i in enumerate(content[::-1]):
        acc += int(i if i.isdigit() else 0) * s1 ** n
    k = ""
    while acc > 0:
        k = slice_2[int(acc % s2)] + k
        acc = (acc - (acc % s2)) // s2
    return k or "0"


def _decrypt(full_string: str, key: str, v1: int, v2: int) -> str:
    v1, v2 = int(v1), int(v2)
    r = ""
    i = 0
    while i < len(full_string):
        s = ""
        while full_string[i] != key[v2]:
            s += full_string[i]
            i += 1
        for j in range(len(key)):
            s = s.replace(key[j], str(j))
        r += chr(int(_get_string(s, v2, 10)) - v1)
        i += 1
    return r


def extract_video_url(kwik_url: str) -> str:
    session = requests.Session()

    resp = session.get(kwik_url, headers={"Referer": "https://kwik.cx/"})
    resp.raise_for_status()

    match = KWIK_PARAMS_RE.search(resp.text)
    if not match:
        raise ValueError("Could not find kwik decryption parameters")

    full_string, key, v1, v2 = match.group(1, 2, 3, 4)
    decrypted = _decrypt(full_string, key, v1, v2)

    d_url_match = KWIK_D_URL_RE.search(decrypted)
    token_match = KWIK_TOKEN_RE.search(decrypted)
    if not d_url_match or not token_match:
        raise ValueError("Could not find download URL or token in decrypted HTML")

    d_url = d_url_match.group(1)
    token = token_match.group(1)

    while True:
        post = session.post(
            d_url,
            data={"_token": token},
            headers={"Referer": str(resp.url)},
            allow_redirects=False,
        )
        if post.status_code == 302:
            return post.headers["Location"]
        if post.status_code != 419:
            raise ValueError(
                f"Unexpected status from kwik POST: {post.status_code}"
            )
