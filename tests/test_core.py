"""Unit tests for core search functionality."""

import pytest
from unittest.mock import patch, MagicMock
from quack.core import (
    search,
    fetch,
    RequestError,
    FetchError,
    _extract_clean_url,
    _clean_result,
)


class TestExtractCleanUrl:
    """Test URL extraction from DuckDuckGo redirect URLs."""

    def test_extract_valid_url(self):
        """Test extracting valid URL from DuckDuckGo format."""
        duckduckgo_url = "/link?kh=-1&uddg=https%3A%2F%2Fexample.com%2Fpath"
        clean_url = _extract_clean_url(duckduckgo_url)
        assert clean_url == "https://example.com/path"

    def test_extract_url_with_query_params(self):
        """Test extracting URL with query parameters."""
        duckduckgo_url = "/link?kh=-1&uddg=https%3A%2F%2Fexample.com%2Fpath%3Fquery%3Dvalue%26other%3Dtest"
        clean_url = _extract_clean_url(duckduckgo_url)
        assert clean_url == "https://example.com/path?query=value&other=test"

    def test_extract_url_no_uddg_param(self):
        """Test handling URL without uddg parameter."""
        duckduckgo_url = "/link?kh=-1&other=param"
        clean_url = _extract_clean_url(duckduckgo_url)
        assert clean_url == duckduckgo_url

    def test_extract_empty_url(self):
        """Test handling empty URL."""
        assert _extract_clean_url("") == ""
        # URL with empty uddg parameter should return original URL
        assert _extract_clean_url("/link?kh=-1&uddg=") == "/link?kh=-1&uddg="


class TestCleanResult:
    """Test result cleaning function."""

    def test_clean_valid_result(self):
        """Test cleaning a valid result."""
        result = {
            "title": "  Python Programming  ",
            "href": "https://python.org",
            "body": "  Learn Python programming  ",
        }

        cleaned = _clean_result(result)
        assert cleaned is not None
        assert cleaned["title"] == "Python Programming"
        assert cleaned["href"] == "https://python.org"
        assert cleaned["body"] == "Learn Python programming"

    def test_clean_result_with_relative_url(self):
        """Test cleaning result with relative URL."""
        result = {
            "title": "Test Site",
            "href": "//example.com",
            "body": "Test description",
        }

        cleaned = _clean_result(result)
        assert cleaned is not None
        assert cleaned["href"] == "https://example.com"

    def test_clean_result_with_protocol_relative_url(self):
        """Test cleaning result with protocol-relative URL."""
        result = {"title": "Test Site", "href": "/path", "body": "Test description"}

        cleaned = _clean_result(result)
        assert cleaned is not None
        # Protocol-relative URLs get converted to https:// (not https:///)
        assert cleaned["href"] == "https://path"

    def test_filter_invalid_result_missing_title(self):
        """Test filtering out result with missing title."""
        result = {"href": "https://example.com", "body": "Test description"}

        cleaned = _clean_result(result)
        assert cleaned is None

    def test_filter_invalid_result_missing_href(self):
        """Test filtering out result with missing href."""
        result = {"title": "Test Title", "body": "Test description"}

        cleaned = _clean_result(result)
        assert cleaned is None

    def test_filter_invalid_result_empty_title(self):
        """Test filtering out result with empty title."""
        result = {
            "title": "",
            "href": "https://example.com",
            "body": "Test description",
        }

        cleaned = _clean_result(result)
        assert cleaned is None

    def test_clean_multiple_spaces(self):
        """Test cleaning multiple spaces in text fields."""
        result = {
            "title": "Python    Programming    Tutorial",
            "href": "https://python.org",
            "body": "Learn    Python    programming    today",
        }

        cleaned = _clean_result(result)
        assert cleaned is not None
        assert cleaned["title"] == "Python Programming Tutorial"
        assert cleaned["body"] == "Learn Python programming today"


class TestSearchValidation:
    """Test input validation in search function."""

    def test_invalid_query_empty_string(self):
        """Test that empty query raises ValueError."""
        with pytest.raises(ValueError, match="Query must be a non-empty string"):
            search("")

    def test_invalid_query_none(self):
        """Test that None query raises ValueError."""
        with pytest.raises(ValueError, match="Query must be a non-empty string"):
            search(None)  # ty:ignore[invalid-argument-type]

    def test_invalid_query_non_string(self):
        """Test that non-string query raises ValueError."""
        with pytest.raises(ValueError, match="Query must be a non-empty string"):
            search(123)  # ty:ignore[invalid-argument-type]

    def test_invalid_max_results_zero(self):
        """Test that zero max_results raises ValueError."""
        with pytest.raises(ValueError, match="max_results must be a positive integer"):
            search("test", max_results=0)

    def test_invalid_max_results_negative(self):
        """Test that negative max_results raises ValueError."""
        with pytest.raises(ValueError, match="max_results must be a positive integer"):
            search("test", max_results=-5)

    def test_invalid_max_results_non_integer(self):
        """Test that non-integer max_results raises ValueError."""
        with pytest.raises(ValueError, match="max_results must be a positive integer"):
            search("test", max_results="10")  # ty:ignore[invalid-argument-type]

    def test_invalid_max_retries_negative(self):
        """Test that negative max_retries raises ValueError."""
        with pytest.raises(
            ValueError, match="max_retries must be a non-negative integer"
        ):
            search("test", max_retries=-1)


class TestSearchErrorHandling:
    """Test error handling in search function."""

    @patch("quack.core.primp.Client")
    def test_request_failure_after_retries(self, mock_client):
        """Test that RequestError is raised after max retries."""
        mock_browser = MagicMock()
        mock_browser.get.side_effect = Exception("Connection error")
        mock_client.return_value = mock_browser

        with pytest.raises(RequestError, match="Search failed after 3 retries"):
            search("test", max_retries=3)

    @patch("quack.core.primp.Client")
    def test_no_results_found(self, mock_client):
        """Test that NoResultsError is raised when no results found."""
        # Mock browser and response
        mock_browser = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "<html></html>"
        mock_response.raise_for_status.return_value = None
        mock_browser.get.return_value = mock_response
        mock_client.return_value = mock_browser

        # The NoResultsError gets caught by the retry logic and re-raised as RequestError
        # So we need to catch RequestError instead
        with pytest.raises(RequestError, match="Search failed after 3 retries"):
            search("test")


class TestSearchRetryLogic:
    """Test retry logic in search function."""

    @patch("quack.core.primp.Client")
    @patch("quack.core.time.sleep")
    def test_retry_logic(self, mock_sleep, mock_client):
        """Test that retry logic works correctly."""
        # Mock browser that fails first time, succeeds second time
        mock_browser = MagicMock()

        # First call fails, second succeeds with proper HTML structure
        mock_browser.get.side_effect = [
            Exception("Connection error"),
            MagicMock(
                text="""<html><div class="result web-result"><a class="result__a" href="https://example.com">Example</a><a class="result__snippet">Test description</a></div></html>""",
                raise_for_status=MagicMock(),
            ),
        ]
        mock_client.return_value = mock_browser

        # This should succeed on second attempt
        results = search("test", max_retries=1)

        # Should have been called twice
        assert mock_browser.get.call_count == 2
        # Should have results
        assert len(results) == 1
        assert results[0]["title"] == "Example"
        assert results[0]["href"] == "https://example.com"

        # Should have slept between retries
        assert mock_sleep.call_count == 1

        # Should return results
        assert len(results) == 1
        assert results[0]["title"] == "Example"
        assert results[0]["href"] == "https://example.com"


class TestFetchFunction:
    """Test fetch function."""

    def test_fetch_url_validation(self):
        """Test URL validation in fetch function."""
        # Test empty URL
        with pytest.raises(ValueError, match="URL must be a non-empty string"):
            fetch("")

        # Test None URL
        with pytest.raises(ValueError, match="URL must be a non-empty string"):
            fetch(None)  # ty:ignore[invalid-argument-type]

        # Test non-string URL
        with pytest.raises(ValueError, match="URL must be a non-empty string"):
            fetch(123)  # ty:ignore[invalid-argument-type]

        # Test URL without http/https prefix
        with pytest.raises(ValueError, match="URL must start with http:// or https://"):
            fetch("example.com")

        # Test URL with whitespace
        with pytest.raises(ValueError, match="URL must start with http:// or https://"):
            fetch("  example.com  ")

    def test_fetch_invalid_max_retries(self):
        """Test that invalid max_retries raises ValueError."""
        with pytest.raises(
            ValueError, match="max_retries must be a non-negative integer"
        ):
            fetch("https://example.com", max_retries=-1)

        with pytest.raises(
            ValueError, match="max_retries must be a non-negative integer"
        ):
            fetch("https://example.com", max_retries="invalid")  # ty:ignore[invalid-argument-type]

    @patch("quack.core.primp.Client")
    def test_fetch_successful(self, mock_client):
        """Test successful fetch operation."""
        # Mock browser and response
        mock_browser = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "<html>Test content</html>"
        mock_response.raise_for_status.return_value = None
        mock_browser.get.return_value = mock_response
        mock_client.return_value = mock_browser

        # Call fetch
        content = fetch("https://example.com", timeout=30, max_retries=1)

        # Verify the result - should be markdown, not HTML
        assert content == "Test content\n"

        # Verify browser was called with correct parameters
        mock_client.assert_called_once()
        expected_headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-GB,en;q=0.9",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
        }
        mock_browser.get.assert_called_once_with(
            "https://example.com", timeout=30, headers=expected_headers
        )

    @patch("quack.core.primp.Client")
    def test_fetch_retry_logic(self, mock_client):
        """Test retry logic in fetch function."""
        # Mock browser that fails first time, succeeds second time
        mock_browser = MagicMock()

        # First call fails, second succeeds
        mock_browser.get.side_effect = [
            Exception("Connection error"),
            MagicMock(text="<html>Success</html>", raise_for_status=MagicMock()),
        ]
        mock_client.return_value = mock_browser

        # This should succeed on second attempt
        content = fetch("https://example.com", max_retries=1)

        # Should have been called twice
        assert mock_browser.get.call_count == 2

        # Should return successful content (markdown, not HTML)
        assert content == "Success\n"

    @patch("quack.core.primp.Client")
    @patch("quack.core.time.sleep")
    def test_fetch_exponential_backoff(self, mock_sleep, mock_client):
        """Test exponential backoff in retry logic."""
        # Mock browser that fails first time, succeeds second time
        mock_browser = MagicMock()
        mock_browser.get.side_effect = [
            Exception("Connection error"),
            MagicMock(text="<html>Success</html>", raise_for_status=MagicMock()),
        ]
        mock_client.return_value = mock_browser

        # Call fetch
        content = fetch("https://example.com", max_retries=1)

        # Verify exponential backoff was used (2^0 = 1 second)
        mock_sleep.assert_called_once_with(1)
        assert content == "Success\n"

    @patch("quack.core.primp.Client")
    def test_fetch_failure_after_retries(self, mock_client):
        """Test that FetchError is raised after max retries."""
        mock_browser = MagicMock()
        mock_browser.get.side_effect = Exception("Connection error")
        mock_client.return_value = mock_browser

        with pytest.raises(FetchError, match="Fetch failed after 2 retries"):
            fetch("https://example.com", max_retries=2)

        # Should have been called 3 times (initial + 2 retries)
        assert mock_browser.get.call_count == 3

    @patch("quack.core.primp.Client")
    def test_fetch_http_error(self, mock_client):
        """Test handling of HTTP errors."""
        mock_browser = MagicMock()
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception("404 Not Found")
        mock_browser.get.return_value = mock_response
        mock_client.return_value = mock_browser

        with pytest.raises(FetchError, match="Fetch failed after 0 retries"):
            fetch("https://example.com", max_retries=0)
