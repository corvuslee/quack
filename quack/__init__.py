"""Quack - DuckDuckGo search with browser impersonation."""

from .core import search, fetch, SearchError, NoResultsError, RequestError, FetchError
from .cli import main
from .utils import validate_query, clean_query, filter_results

# Optional render import
try:
    from .render import render, RenderError  # noqa: F401
    _render_available = True
except ImportError:
    _render_available = False

__version__ = "0.2.0"
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
    "filter_results",
]

# Add render to exports if available
if _render_available:
    __all__.extend(["render", "RenderError"])
