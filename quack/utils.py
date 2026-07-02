"""Utility functions for Quack."""

import re
from typing import List, Dict, Optional
from collections.abc import Mapping, Sequence


def validate_query(query: str) -> bool:
    """
    Validate search query.

    Args:
        query: Search query string

    Returns:
        True if query is valid, False otherwise
    """
    return bool(query) and isinstance(query, str) and len(query.strip()) > 0


def clean_query(query: str) -> str:
    """
    Clean search query by removing extra whitespace and special characters.

    Args:
        query: Search query string

    Returns:
        Cleaned query string
    """
    if not query:
        return ""

    # Minimal cleaning: just normalize whitespace and strip
    # Let downstream handle all other characters
    query = query.strip()
    query = re.sub(r"\s+", " ", query)

    return query


def filter_results(
    results: Sequence[Mapping[str, Optional[str]]], min_title_length: int = 3
) -> List[Dict[str, str]]:
    """
    Filter search results based on quality criteria.

    Args:
        results: List of search results
        min_title_length: Minimum title length to consider valid (default: 3)

    Returns:
        Filtered list of results
    """
    filtered = []
    for result in results:
        # Filter out results with very short titles (handle None safely)
        title = result.get("title", "")
        if title is None:
            continue
        if len(title.strip()) < min_title_length:
            continue

        # Filter out results with invalid URLs (handle None safely)
        href = result.get("href", "")
        if href is None or not (
            href.startswith("http://") or href.startswith("https://")
        ):
            continue

        filtered.append(
            {"title": title, "href": href, "body": result.get("body") or ""}
        )

    return filtered
