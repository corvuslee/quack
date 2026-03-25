"""Quack - DuckDuckGo search with browser impersonation."""

from .core import search, SearchError, NoResultsError, RequestError
from .cli import main
from .utils import validate_query, clean_query, filter_results

__version__ = "0.1.0"
__all__ = [
    "search", 
    "main",
    "SearchError", 
    "NoResultsError", 
    "RequestError",
    "validate_query",
    "clean_query", 
    "filter_results"
]