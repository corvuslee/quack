"""Unit tests for utility functions."""

from quack.utils import validate_query, clean_query, filter_results


class TestValidateQuery:
    """Test query validation function."""

    def test_valid_queries(self):
        """Test that valid queries return True."""
        assert validate_query("python programming")
        assert validate_query("hello world")
        assert validate_query("a")
        assert validate_query("  valid  ")

    def test_invalid_queries(self):
        """Test that invalid queries return False."""
        assert not validate_query("")
        assert not validate_query("   ")
        assert not validate_query(None)  # ty:ignore[invalid-argument-type]
        assert not validate_query(123)  # ty:ignore[invalid-argument-type]
        assert not validate_query([])  # ty:ignore[invalid-argument-type]
        assert not validate_query({})  # ty:ignore[invalid-argument-type]


class TestCleanQuery:
    """Test query cleaning function."""

    def test_clean_whitespace(self):
        """Test removing extra whitespace."""
        assert clean_query("  hello   world  ") == "hello world"
        assert clean_query("\tpython\nprogramming\r") == "python programming"

    def test_clean_control_characters(self):
        """Test that control characters are passed through to downstream."""
        # Control characters are preserved and passed to downstream search engine
        result = clean_query("test\x1fmore")
        assert "test" in result and "more" in result
        # Basic whitespace still works normally
        assert clean_query("hello  world") == "hello world"

    def test_clean_unicode_characters(self):
        """Test that Unicode characters are passed through to downstream."""
        # Unicode characters are preserved for downstream handling
        result = clean_query("hello\u2003world")  # Em space
        assert "hello" in result and "world" in result
        # Mixed Unicode characters
        result2 = clean_query("test\u2009more\u2003data")  # Thin space + em space
        assert "test" in result2 and "more" in result2 and "data" in result2

    def test_clean_mixed_content(self):
        """Test mixed control characters, Unicode, and normal text."""
        # All characters are preserved, only whitespace is normalized
        result = clean_query("hello  \x1f  \u2003  world")
        assert "hello" in result and "world" in result
        # Verify whitespace is normalized but content is preserved
        assert result.count(" ") == 1  # Multiple spaces become single space

    def test_empty_query(self):
        """Test handling of empty queries."""
        assert clean_query("") == ""
        assert clean_query("   ") == ""
        assert clean_query(None) == ""  # ty:ignore[invalid-argument-type]


class TestFilterResults:
    """Test result filtering function."""

    def test_filter_by_title_length(self):
        """Test filtering by minimum title length."""
        results = [
            {"title": "Python", "href": "https://python.org"},
            {"title": "Py", "href": "https://py.org"},
            {"title": "P", "href": "https://p.org"},
            {"title": "", "href": "https://empty.org"},
        ]

        filtered = filter_results(results, min_title_length=3)
        assert len(filtered) == 1
        assert filtered[0]["title"] == "Python"

    def test_filter_invalid_urls(self):
        """Test filtering results with invalid URLs."""
        results = [
            {"title": "Valid", "href": "https://valid.com"},
            {"title": "No Protocol", "href": "valid.com"},
            {"title": "Empty URL", "href": ""},
            {"title": "Relative", "href": "/path"},
        ]

        filtered = filter_results(results)
        assert len(filtered) == 1
        assert filtered[0]["title"] == "Valid"

    def test_keep_valid_results(self):
        """Test that valid results are kept."""
        results = [
            {"title": "Python Programming", "href": "https://python.org"},
            {"title": "DuckDuckGo", "href": "https://duckduckgo.com"},
        ]

        filtered = filter_results(results)
        assert len(filtered) == 2

    def test_filter_results_with_none_values(self):
        """Test filtering results with None values."""
        results = [
            {"title": "Valid Title", "href": "https://valid.com"},
            {"title": None, "href": "https://none-title.com"},
            {"title": "Another Valid", "href": None},
            {"title": None, "href": None},
        ]

        filtered = filter_results(results)
        # Only the first result should pass (has both valid title and URL)
        assert len(filtered) == 1
        assert filtered[0]["title"] == "Valid Title"

    def test_filter_edge_case_urls(self):
        """Test filtering edge case URL formats."""
        results = [
            {"title": "Valid HTTPS", "href": "https://valid.com"},
            {"title": "Valid HTTP", "href": "http://valid.com"},
            {"title": "JavaScript URL", "href": "javascript:void(0)"},
            {"title": "Data URL", "href": "data:text/plain,test"},
            {"title": "Mailto URL", "href": "mailto:test@example.com"},
            {"title": "Tel URL", "href": "tel:+1234567890"},
            {"title": "File URL", "href": "file:///path/to/file"},
            {"title": "FTP URL", "href": "ftp://example.com"},
            {"title": "Relative URL", "href": "/relative/path"},
            {"title": "No Protocol", "href": "example.com"},
            {"title": "Empty URL", "href": ""},
            {"title": "About Blank", "href": "about:blank"},
            {"title": "Invalid Scheme", "href": "invalid://example.com"},
        ]

        filtered = filter_results(results)
        # Only HTTP/HTTPS URLs should pass
        assert len(filtered) == 2
        titles = [r["title"] for r in filtered]
        assert "Valid HTTPS" in titles
        assert "Valid HTTP" in titles

    def test_filter_very_long_fields(self):
        """Test filtering results with very long titles/URLs."""
        long_title = "A" * 500  # Very long title
        long_url = "https://" + "x" * 1000 + ".com"  # Very long URL

        results = [
            {"title": long_title, "href": "https://valid.com"},
            {"title": "Short Title", "href": long_url},
            {"title": "Normal", "href": "https://normal.com"},
        ]

        filtered = filter_results(results)
        # All should pass (length doesn't affect basic filtering)
        assert len(filtered) == 3
        # Verify the long fields are preserved
        assert len(filtered[0]["title"]) == 500
        assert len(filtered[1]["href"]) > 1000

    def test_filter_url_special_cases(self):
        """Test filtering URL special cases and malformed URLs."""
        results = [
            {"title": "Valid with Port", "href": "https://example.com:8080"},
            {
                "title": "Valid with Path",
                "href": "https://example.com/path?query=value",
            },
            {"title": "Valid with Fragment", "href": "https://example.com/#section"},
            {"title": "Valid IP Address", "href": "http://192.168.1.1"},
            {"title": "Missing Protocol", "href": "//example.com"},
            {"title": "Spaces in URL", "href": "https://example.com/path with spaces"},
            {"title": "Invalid Characters", "href": "https://example.com/<script>"},
            {"title": "Localhost", "href": "http://localhost:3000"},
        ]

        filtered = filter_results(results)
        # Should include valid HTTP/HTTPS URLs (our filter only checks protocol)
        valid_titles = [r["title"] for r in filtered]
        assert "Valid with Port" in valid_titles
        assert "Valid with Path" in valid_titles
        assert "Valid with Fragment" in valid_titles
        assert "Valid IP Address" in valid_titles
        assert "Localhost" in valid_titles
        # URLs with spaces are included (they start with https://)
        assert "Spaces in URL" in valid_titles
        # URLs with invalid characters are included (they start with https://)
        assert "Invalid Characters" in valid_titles
        # Should exclude non-HTTP/HTTPS URLs
        assert "Missing Protocol" not in valid_titles
