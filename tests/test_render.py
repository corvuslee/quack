"""Unit tests for render functionality."""

import pytest
from pathlib import Path


class TestRenderFunction:
    """Test render function with SeleniumBase UC Mode."""

    @pytest.fixture
    def js_test_file(self):
        """Get the path to the JS test page."""
        fixtures_dir = Path(__file__).parent / "fixtures"
        return fixtures_dir / "js_test.html"

    def test_render_executes_javascript(self, js_test_file):
        """Test that render() executes JavaScript and returns modified content."""
        try:
            from quack.render import render

            # Use file:// URL
            url = f"file://{js_test_file.absolute()}"
            
            # Render the page
            content = render(url, wait_time=2)

            # Verify JavaScript was executed
            assert "JavaScript executed successfully!" in content
            assert "This content was modified by JavaScript!" in content

            # Verify original content is NOT present
            assert "JavaScript NOT executed" not in content
            assert "This content is static" not in content

        except ImportError as e:
            pytest.skip(f"SeleniumBase not installed: {e}")

    def test_render_validates_url(self):
        """Test that render() validates URL parameter."""
        try:
            from quack.render import render

            # Test empty URL
            with pytest.raises(ValueError, match="URL must be a non-empty string"):
                render("")

            # Test None URL
            with pytest.raises(ValueError, match="URL must be a non-empty string"):
                render(None)

            # Test non-string URL
            with pytest.raises(ValueError, match="URL must be a non-empty string"):
                render(123)

            # Test URL without http/https/file prefix
            with pytest.raises(ValueError, match="URL must start with"):
                render("example.com")

        except ImportError as e:
            pytest.skip(f"SeleniumBase not installed: {e}")
