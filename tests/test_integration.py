"""Integration tests for Quack - tests actual DuckDuckGo searches."""

from quack import search


class TestIntegration:
    """Integration tests that make actual DuckDuckGo API calls."""

    def test_actual_search_basic_functionality(self):
        """Test basic search functionality returns results with correct structure."""
        results = search("quantum computing entanglement protocols")

        # Should return results
        assert len(results) > 0

        # Validate result structure
        for result in results:
            assert "href" in result
            assert "title" in result
            assert "body" in result

            # URLs should be clean, not DuckDuckGo redirect URLs
            assert "duckduckgo.com/l/" not in result["href"], (
                f"URL not cleaned: {result['href']}"
            )
            assert "uddg=" not in result["href"], f"URL not cleaned: {result['href']}"
