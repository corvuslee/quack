"""Core DuckDuckGo search functionality with browser impersonation."""

import re
import time
from typing import List, Dict, Optional
from collections.abc import Mapping
from urllib.parse import urlencode, unquote

import primp
from selectolax.parser import HTMLParser


class SearchError(Exception):
    """Base exception for search-related errors."""

    pass


class NoResultsError(SearchError):
    """Exception raised when no search results are found."""

    pass


class RequestError(SearchError):
    """Exception raised when search request fails."""

    pass


class FetchError(SearchError):
    """Exception raised when fetch request fails."""

    pass


def search(
    query: str, max_results: int = 10, timeout: int = 30, max_retries: int = 3
) -> List[Dict[str, str]]:
    """
    Search DuckDuckGo and return results.

    Args:
        query: Search query string
        max_results: Maximum number of results to return (default: 10, max: 10)
        timeout: Request timeout in seconds (default: 30)
        max_retries: Maximum number of retry attempts (default: 3)

    Returns:
        List of dictionaries containing 'title', 'href', and 'body' for each result

    Raises:
        ValueError: If query is invalid or max_results is invalid (must be 1-10)
        RequestError: If search request fails after retries
        NoResultsError: If no search results are found
    """
    # Validate inputs
    if not query or not isinstance(query, str):
        raise ValueError("Query must be a non-empty string")

    if not isinstance(max_results, int) or max_results <= 0:
        raise ValueError("max_results must be a positive integer")

    if max_results > 10:
        raise ValueError("max_results cannot exceed 10")

    if not isinstance(max_retries, int) or max_retries < 0:
        raise ValueError("max_retries must be a non-negative integer")

    # Create browser session with primp - randomize browser config
    browser = primp.Client(impersonate="random", impersonate_os="random")

    # Construct DuckDuckGo search URL
    params = {
        "q": query,
        "kl": "uk-en",  # UK English
        "df": "",  # Any time (no date filtering)
    }

    search_url = f"https://html.duckduckgo.com/html/?{urlencode(params)}"

    # Retry logic
    for attempt in range(max_retries + 1):
        try:
            # Fetch search results with browser impersonation
            response = browser.get(search_url, timeout=timeout)
            response.raise_for_status()

            # Parse HTML content
            doc = HTMLParser(response.text)

            # Extract search results
            results = []
            result_elements = doc.css("div.result.web-result")

            for element in result_elements[:max_results]:
                try:
                    # Extract title and URL
                    title_element = element.css_first("a.result__a, a.result__url")
                    if title_element:
                        title = title_element.text(deep=True, separator=" ").strip()
                        href = title_element.attributes.get("href", "")

                        # Clean URL
                        if href and ("/link?" in href or "duckduckgo.com/l/" in href):
                            href = _extract_clean_url(href)

                        # Extract description
                        body_element = element.css_first("a.result__snippet")
                        body = (
                            body_element.text(deep=True, separator=" ").strip()
                            if body_element
                            else ""
                        )

                        # Clean and filter results
                        cleaned_result = _clean_result(
                            {"title": title, "href": href, "body": body}
                        )
                        if cleaned_result:
                            results.append(cleaned_result)

                except Exception:
                    # Skip individual result parsing errors
                    continue

            if not results:
                raise NoResultsError(f"No search results found for query: {query}")

            return results

        except Exception as e:
            if attempt < max_retries:
                # Exponential backoff: 1s, 2s, 4s capped at 10s
                wait_time = min((2**attempt) * 1.0, 10.0)
                time.sleep(wait_time)
                continue
            else:
                raise RequestError(
                    f"Search failed after {max_retries} retries: {str(e)}"
                )

    raise RequestError("Search failed: unreachable")


def _extract_clean_url(duckduckgo_url: str) -> str:
    """
    Extract clean URL from DuckDuckGo redirect URL.

    Args:
        duckduckgo_url: DuckDuckGo redirect URL

    Returns:
        Clean URL
    """
    # Extract URL from DuckDuckGo redirect format
    # Example: /link?kh=-1&uddg=https%3A%2F%2Fexample.com
    match = re.search(r"uddg=([^&]+)", duckduckgo_url)
    if match:
        return unquote(match.group(1))

    return duckduckgo_url


def _clean_whitespace(text: Optional[str]) -> str:
    """Clean whitespace in text - strip and normalize spaces."""
    if not text:
        return ""
    text = text.strip()
    return re.sub(r"\s+", " ", text)


def _clean_result(result: Mapping[str, Optional[str]]) -> Optional[Dict[str, str]]:
    """
    Clean and filter search results.

    Args:
        result: Raw search result dictionary

    Returns:
        Cleaned result dictionary or None if result should be filtered out
    """
    # Filter out empty or invalid results
    if not result.get("title") or not result.get("href"):
        return None

    # Clean title
    title = _clean_whitespace(result["title"])

    # Clean URL - ensure it's a valid HTTP/HTTPS URL
    href = (result["href"] or "").strip()
    if not href.startswith(("http://", "https://")):
        # Make relative URLs absolute
        href = f"https://{href.lstrip('/')}"

    # Clean body text
    body = _clean_whitespace(result["body"])

    return {"title": title, "href": href, "body": body}


def _html_to_markdown(html_content: str) -> str:
    """
    Convert HTML content to Markdown using html2text.

    Args:
        html_content: HTML content as string

    Returns:
        Markdown content as string
    """
    import html2text

    # Create html2text converter with reasonable defaults
    converter = html2text.HTML2Text()
    converter.body_width = 0  # Don't wrap lines
    converter.ignore_links = False  # Keep links
    converter.ignore_images = False  # Keep images
    converter.ignore_emphasis = False  # Keep emphasis

    # Convert HTML to Markdown
    markdown_content = converter.handle(html_content)

    return markdown_content


def fetch(
    url: str, timeout: int = 30, max_retries: int = 3, http2_only: bool = True
) -> str:
    """
    Fetch webpage content from a URL and convert to Markdown.

    Args:
        url: URL to fetch
        timeout: Request timeout in seconds (default: 30)
        max_retries: Maximum number of retry attempts (default: 3)
        http2_only: Force HTTP/2 only (default: True)

    Returns:
        Webpage content as Markdown string

    Raises:
        ValueError: If URL is invalid
        RequestError: If fetch request fails after retries
        FetchError: If content cannot be retrieved
    """
    # Validate URL
    if not url or not isinstance(url, str):
        raise ValueError("URL must be a non-empty string")

    url = url.strip()
    if not (url.startswith("http://") or url.startswith("https://")):
        raise ValueError("URL must start with http:// or https://")

    if not isinstance(max_retries, int) or max_retries < 0:
        raise ValueError("max_retries must be a non-negative integer")

    # Create browser session with primp - use Safari on macOS
    browser = primp.Client(
        impersonate="safari",
        impersonate_os="macos",
        http2_only=http2_only,
    )

    # Realistic headers to appear as legitimate browser navigation
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-GB,en;q=0.9",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
    }

    # Retry logic
    for attempt in range(max_retries + 1):
        try:
            # Fetch webpage with browser impersonation
            response = browser.get(url, timeout=timeout, headers=headers)
            response.raise_for_status()

            # Convert HTML to Markdown using html2text
            html_content = response.text
            markdown_content = _html_to_markdown(html_content)

            return markdown_content

        except Exception as e:
            if attempt < max_retries:
                # Exponential backoff: 1s, 2s, 4s capped at 10s
                wait_time = min((2**attempt) * 1.0, 10.0)
                time.sleep(wait_time)
                continue
            else:
                raise FetchError(f"Fetch failed after {max_retries} retries: {str(e)}")

    raise FetchError("Fetch failed: unreachable")
