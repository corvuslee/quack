"""Integration tests for Quack - tests actual DuckDuckGo searches."""
from quack import search


class TestIntegration:
    """Integration tests that make actual DuckDuckGo API calls."""

    def test_actual_search_basic_functionality(self):
        """Test basic search functionality returns results with correct structure."""
        results = search("Python programming")
        
        # Should return results
        assert len(results) > 0
        
        # Validate result structure
        for result in results:
            assert 'href' in result
            assert 'title' in result
            assert 'body' in result

    def test_actual_search_max_results(self):
        """Test max_results parameter works correctly."""
        results = search("test query", max_results=3)
        assert len(results) <= 3

    def test_actual_search_query_types(self):
        """Test different types of search queries."""
        # Regular query
        results1 = search("Python documentation")
        assert len(results1) > 0
        
        # Query with special characters
        results2 = search("Python 3.12+ features")
        assert len(results2) > 0
        
        # Unicode query
        results3 = search("Python 编程")
        assert len(results3) > 0
