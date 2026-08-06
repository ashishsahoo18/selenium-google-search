"""Search engine URL construction."""
from urllib.parse import quote_plus

ENGINES = {
    "Google": "https://www.google.com/search?q={query}",
    "Bing": "https://www.bing.com/search?q={query}",
    "DuckDuckGo": "https://duckduckgo.com/?q={query}",
    "Yahoo": "https://search.yahoo.com/search?p={query}",
    "YouTube": "https://www.youtube.com/results?search_query={query}",
    "Wikipedia": "https://en.wikipedia.org/w/index.php?search={query}",
    "GitHub": "https://github.com/search?q={query}",
    "Stack Overflow": "https://stackoverflow.com/search?q={query}",
}


def search_url(engine: str, query: str) -> str:
    """Return an encoded URL for a supported search engine."""
    return ENGINES[engine].format(query=quote_plus(query))
