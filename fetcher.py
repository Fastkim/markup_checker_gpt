import requests

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    "Connection": "keep-alive",
}

def fetch_html(url: str) -> str:
    session = requests.Session()
    res = session.get(url, headers=DEFAULT_HEADERS, timeout=15, allow_redirects=True)
    res.raise_for_status()
    # 인코딩이 애매할 때 대비
    if not res.encoding:
        res.encoding = res.apparent_encoding
    return res.text