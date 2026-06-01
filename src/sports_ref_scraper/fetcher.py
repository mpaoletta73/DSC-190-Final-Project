"""HTTP fetching for sports-reference.com sites."""

from urllib.parse import urlparse

import requests

SUPPORTED_DOMAINS = [
    "baseball-reference.com",
    "basketball-reference.com",
    "pro-football-reference.com",
    "hockey-reference.com",
]

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def validate_url(url: str) -> None:
    """Raise ValueError if the URL is not from a supported sports-reference domain."""
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        raise ValueError(f"Invalid URL: {url!r}")
    domain = parsed.netloc.lower().removeprefix("www.")
    if not any(domain == d or domain.endswith("." + d) for d in SUPPORTED_DOMAINS):
        supported = ", ".join(SUPPORTED_DOMAINS)
        raise ValueError(
            f"Unsupported site '{domain}'. Supported domains: {supported}"
        )


def fetch_html(url: str) -> str:
    """Fetch and return the raw HTML for a sports-reference page."""
    validate_url(url)
    response = requests.get(url, headers=_HEADERS, timeout=30)
    response.raise_for_status()
    return response.text
