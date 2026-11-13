"""Quack - DuckDuckGo search with browser impersonation."""

from importlib.metadata import version as get_version

from .cli import main
from .core import (
    ChallengeError,
    FetchError,
    FetchRequestError,
    LibraryError,
    NoResultsError,
    SearchError,
    SearchRequestError,
    fetch,
    search,
)
from .utils import clean_query, filter_results, validate_query

# Optional render import
try:
    from .render import RenderError as RenderError
    from .render import render as render

    _render_available = True
except ImportError:
    _render_available = False

__version__ = get_version("quack")
__all__ = [
    "ChallengeError",
    "FetchError",
    "FetchRequestError",
    "LibraryError",
    "NoResultsError",
    "SearchError",
    "SearchRequestError",
    "clean_query",
    "fetch",
    "filter_results",
    "main",
    "search",
    "validate_query",
]

# Add render to exports if available
if _render_available:
    __all__.extend(["RenderError", "render"])
