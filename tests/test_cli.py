"""Unit tests for CLI functionality."""

import pytest
from unittest.mock import patch
from quack.cli import main, _print_text_results
from quack.core import SearchError, NoResultsError, RequestError
import sys


class TestCLIArgumentParsing:
    """Test CLI argument parsing."""
    
    @patch('quack.cli.search')
    def test_basic_search(self, mock_search, capsys):
        """Test basic search with default arguments."""
        mock_search.return_value = [
            {"title": "Test Result", "href": "https://example.com", "body": "Test description"}
        ]
        
        # Simulate command line arguments
        test_args = ["test query"]
        with patch.object(sys, 'argv', ['quack'] + test_args):
            main()
        
        # Verify search was called with correct parameters
        mock_search.assert_called_once_with("test query", max_results=10, timeout=30)
    
    @patch('quack.cli.search')
    def test_search_with_max_results(self, mock_search):
        """Test search with custom max results."""
        mock_search.return_value = []
        
        test_args = ["test query", "--max", "5"]
        with patch.object(sys, 'argv', ['quack'] + test_args):
            main()
        
        mock_search.assert_called_once_with("test query", max_results=5, timeout=30)
    
    @patch('quack.cli.search')
    def test_search_with_json_output(self, mock_search, capsys):
        """Test search with JSON output."""
        mock_search.return_value = [
            {"title": "Test Result", "href": "https://example.com", "body": "Test description"}
        ]
        
        test_args = ["test query", "--json"]
        with patch.object(sys, 'argv', ['quack'] + test_args):
            main()
        
        # Verify JSON output
        captured = capsys.readouterr()
        assert "Test Result" in captured.out
        assert "https://example.com" in captured.out
    
    @patch('quack.cli.search')
    def test_search_with_timeout(self, mock_search):
        """Test search with custom timeout."""
        mock_search.return_value = []
        
        test_args = ["test query", "--timeout", "60"]
        with patch.object(sys, 'argv', ['quack'] + test_args):
            main()
        
        mock_search.assert_called_once_with("test query", max_results=10, timeout=60)


class TestCLIErrorHandling:
    """Test CLI error handling."""
    
    @patch('quack.cli.search')
    def test_handle_value_error(self, mock_search, capsys):
        """Test handling of ValueError."""
        mock_search.side_effect = ValueError("Invalid query")
        
        test_args = ["invalid query"]
        with patch.object(sys, 'argv', ['quack'] + test_args):
            with pytest.raises(SystemExit) as exc_info:
                main()
        
        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "Invalid input: Invalid query" in captured.err
    
    @patch('quack.cli.search')
    def test_handle_no_results_error(self, mock_search, capsys):
        """Test handling of NoResultsError."""
        mock_search.side_effect = NoResultsError("No results found for query: test")
        
        test_args = ["test"]
        with patch.object(sys, 'argv', ['quack'] + test_args):
            with pytest.raises(SystemExit) as exc_info:
                main()
        
        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "No results found: No results found for query: test" in captured.err
    
    @patch('quack.cli.search')
    def test_handle_request_error(self, mock_search, capsys):
        """Test handling of RequestError."""
        mock_search.side_effect = RequestError("Connection failed")
        
        test_args = ["test"]
        with patch.object(sys, 'argv', ['quack'] + test_args):
            with pytest.raises(SystemExit) as exc_info:
                main()
        
        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "Search request failed: Connection failed" in captured.err
    
    @patch('quack.cli.search')
    def test_handle_generic_search_error(self, mock_search, capsys):
        """Test handling of generic SearchError."""
        mock_search.side_effect = SearchError("Generic search error")
        
        test_args = ["test"]
        with patch.object(sys, 'argv', ['quack'] + test_args):
            with pytest.raises(SystemExit) as exc_info:
                main()
        
        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "Search error: Generic search error" in captured.err
    
    @patch('quack.cli.search')
    def test_handle_unexpected_error(self, mock_search, capsys):
        """Test handling of unexpected errors."""
        mock_search.side_effect = RuntimeError("Unexpected error")
        
        test_args = ["test"]
        with patch.object(sys, 'argv', ['quack'] + test_args):
            with pytest.raises(SystemExit) as exc_info:
                main()
        
        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "Unexpected error: Unexpected error" in captured.err


class TestPrintTextResults:
    """Test text output formatting."""
    
    def test_print_text_results(self, capsys):
        """Test printing results in text format."""
        results = [
            {
                "title": "Python Programming",
                "href": "https://python.org",
                "body": "Learn Python programming language"
            },
            {
                "title": "DuckDuckGo Search",
                "href": "https://duckduckgo.com",
                "body": "Privacy-focused search engine"
            }
        ]
        
        _print_text_results(results)
        
        captured = capsys.readouterr()
        output = captured.out
        
        # Check that results are printed in expected format
        assert "1. Python Programming" in output
        assert "https://python.org" in output
        assert "Learn Python programming language" in output
        assert "2. DuckDuckGo Search" in output
        assert "https://duckduckgo.com" in output
        assert "Privacy-focused search engine" in output
    
    def test_print_results_with_empty_body(self, capsys):
        """Test printing results with empty body."""
        results = [
            {
                "title": "Test Site",
                "href": "https://example.com",
                "body": ""
            }
        ]
        
        _print_text_results(results)
        
        captured = capsys.readouterr()
        output = captured.out
        
        assert "1. Test Site" in output
        assert "https://example.com" in output
        # Empty body should not be printed
        assert output.count("https://example.com") == 1


class TestCLIHelpAndVersion:
    """Test CLI help and version functionality."""
    
    def test_version_flag(self, capsys):
        """Test version flag."""
        test_args = ["--version"]
        with patch.object(sys, 'argv', ['quack'] + test_args):
            with pytest.raises(SystemExit) as exc_info:
                main()
        
        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert "quack" in captured.out
        assert "0.1.0" in captured.out
    
    def test_help_flag(self, capsys):
        """Test help flag."""
        test_args = ["--help"]
        with patch.object(sys, 'argv', ['quack'] + test_args):
            with pytest.raises(SystemExit) as exc_info:
                main()
        
        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert "Quack - DuckDuckGo search with browser impersonation" in captured.out
        assert "positional arguments:" in captured.out
        assert "options:" in captured.out  # argparse shows "options:" not "optional arguments:"