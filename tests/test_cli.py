"""Unit tests for CLI functionality."""

import pytest
import unittest
from unittest.mock import patch
from quack.cli import main, _print_text_results
from quack.core import SearchError, NoResultsError, RequestError, FetchError
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
        test_args = ["search", "test query"]
        with patch.object(sys, 'argv', ['quack'] + test_args):
            main()
        
        # Verify search was called with correct parameters
        mock_search.assert_called_once_with("test query", max_results=10, timeout=30)
    
    @patch('quack.cli.search')
    def test_search_with_max_results(self, mock_search):
        """Test search with custom max results."""
        mock_search.return_value = []
        
        test_args = ["search", "test query", "--max", "5"]
        with patch.object(sys, 'argv', ['quack'] + test_args):
            main()
        
        mock_search.assert_called_once_with("test query", max_results=5, timeout=30)
    
    @patch('quack.cli.search')
    def test_search_with_json_output(self, mock_search, capsys):
        """Test search with JSON output."""
        mock_search.return_value = [
            {"title": "Test Result", "href": "https://example.com", "body": "Test description"}
        ]
        
        test_args = ["search", "test query", "--json"]
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
        
        test_args = ["search", "test query", "--timeout", "60"]
        with patch.object(sys, 'argv', ['quack'] + test_args):
            main()
        
        mock_search.assert_called_once_with("test query", max_results=10, timeout=60)


class TestCLIErrorHandling:
    """Test CLI error handling."""
    
    @patch('quack.cli.search')
    def test_handle_value_error(self, mock_search, capsys):
        """Test handling of ValueError."""
        mock_search.side_effect = ValueError("Invalid query")
        
        test_args = ["search", "invalid query"]
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
        
        test_args = ["search", "test"]
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
        
        test_args = ["search", "test"]
        with patch.object(sys, 'argv', ['quack'] + test_args):
            with pytest.raises(SystemExit) as exc_info:
                main()
        
        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "Request failed: Connection failed" in captured.err
    
    @patch('quack.cli.search')
    def test_handle_generic_search_error(self, mock_search, capsys):
        """Test handling of generic SearchError."""
        mock_search.side_effect = SearchError("Generic search error")
        
        test_args = ["search", "test"]
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
        
        test_args = ["search", "test"]
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


class TestCLIFetchFunctionality:
    """Test CLI fetch command functionality."""

    @patch('quack.cli.fetch')
    def test_basic_fetch(self, mock_fetch, capsys):
        """Test basic fetch with default arguments."""
        mock_fetch.return_value = "Test content\n"
        
        # Simulate command line arguments
        test_args = ["fetch", "https://example.com"]
        with patch.object(sys, 'argv', ['quack'] + test_args):
            main()
        
        # Verify fetch was called with correct parameters
        mock_fetch.assert_called_once_with("https://example.com", timeout=30)
        
        # Verify output
        captured = capsys.readouterr()
        assert "Test content" in captured.out

    @patch('quack.cli.fetch')
    def test_fetch_with_timeout(self, mock_fetch, capsys):
        """Test fetch with custom timeout."""
        mock_fetch.return_value = "Test content\n"
        
        test_args = ["fetch", "https://example.com", "--timeout", "60"]
        with patch.object(sys, 'argv', ['quack'] + test_args):
            main()
        
        mock_fetch.assert_called_once_with("https://example.com", timeout=60)

    @patch('quack.cli.fetch')
    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    def test_fetch_with_output_file(self, mock_open, mock_fetch, capsys):
        """Test fetch with output file."""
        mock_fetch.return_value = "Test content\n"
        
        test_args = ["fetch", "https://example.com", "--output", "test.html"]
        with patch.object(sys, 'argv', ['quack'] + test_args):
            main()
        
        # Verify fetch was called
        mock_fetch.assert_called_once_with("https://example.com", timeout=30)
        
        # Verify file was written
        mock_open.assert_called_once_with('test.html', 'w', encoding='utf-8')
        handle = mock_open()
        handle.write.assert_called_once_with("Test content\n")
        
        # Verify console output
        captured = capsys.readouterr()
        assert "Content saved to test.html" in captured.out

    @patch('quack.cli.fetch')
    def test_fetch_handle_value_error(self, mock_fetch, capsys):
        """Test handling of ValueError in fetch."""
        mock_fetch.side_effect = ValueError("Invalid URL")
        
        test_args = ["fetch", "invalid-url"]
        with patch.object(sys, 'argv', ['quack'] + test_args):
            with pytest.raises(SystemExit) as exc_info:
                main()
        
        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "Invalid input: Invalid URL" in captured.err

    @patch('quack.cli.fetch')
    def test_fetch_handle_fetch_error(self, mock_fetch, capsys):
        """Test handling of FetchError."""
        mock_fetch.side_effect = FetchError("Connection failed")
        
        test_args = ["fetch", "https://example.com"]
        with patch.object(sys, 'argv', ['quack'] + test_args):
            with pytest.raises(SystemExit) as exc_info:
                main()
        
        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "Fetch error: Connection failed" in captured.err

    @patch('quack.cli.fetch')
    def test_fetch_handle_request_error(self, mock_fetch, capsys):
        """Test handling of RequestError in fetch."""
        mock_fetch.side_effect = RequestError("Request timeout")
        
        test_args = ["fetch", "https://example.com"]
        with patch.object(sys, 'argv', ['quack'] + test_args):
            with pytest.raises(SystemExit) as exc_info:
                main()
        
        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "Request failed: Request timeout" in captured.err