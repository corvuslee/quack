"""Quack - DuckDuckGo search with browser impersonation."""

from .core import search, fetch, SearchError, NoResultsError, RequestError, FetchError
from .cli import main
from .utils import validate_query, clean_query, filter_results

__version__ = "0.1.0"
__all__ = [
    "search", 
    "fetch",
    "main",
    "SearchError", 
    "NoResultsError", 
    "RequestError",
    "FetchError",
    "validate_query",
    "clean_query", 
    "filter_results"
]