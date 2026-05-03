"""Render webpage content using SeleniumBase UC Mode for JavaScript execution."""

from .core import _html_to_markdown


class RenderError(Exception):
    """Exception raised when render request fails."""

    pass


def render(
    url: str,
    wait_time: int = 2,
) -> str:
    """
    Render webpage content using SeleniumBase UC Mode.

    This function executes JavaScript and bypasses bot detection using
    SeleniumBase's UC Mode (Undetected-Chromedriver Mode).

    Args:
        url: URL to render (http://, https://, or file://)
        wait_time: Additional wait time after page load for JS execution (default: 2)

    Returns:
        Webpage content as Markdown string

    Raises:
        ValueError: If URL is invalid
        RenderError: If rendering fails
    """
    # Validate URL
    if not url or not isinstance(url, str):
        raise ValueError("URL must be a non-empty string")

    url = url.strip()
    if not (
        url.startswith("http://")
        or url.startswith("https://")
        or url.startswith("file://")
    ):
        raise ValueError("URL must start with http://, https://, or file://")

    try:
        from seleniumbase import SB
    except ImportError:
        raise RenderError(
            "Error: Render command requires SeleniumBase.\n"
            "Install the optional [render] dependencies\n"
        )

    try:
        # Use SeleniumBase UC Mode with incognito for clean sessions
        with SB(
            uc=True,
            headless2=True,  # UC Mode headless variant
            incognito=True,  # Clean session without temp profile management
            locale="en-GB",
        ) as sb:
            # Open URL with UC Mode (uses default reconnect_time for anti-bot bypass)
            sb.uc_open_with_reconnect(url)

            # Wait for JavaScript to execute
            sb.sleep(wait_time)

            # Handle CAPTCHAs if present (optional, won't fail if not found)
            try:
                sb.uc_gui_click_captcha()
            except Exception:
                # CAPTCHA handling is optional
                pass

            # Get rendered HTML
            html_content = sb.get_page_source()

            # Convert to markdown
            markdown_content = _html_to_markdown(html_content)

            return markdown_content

    except Exception as e:
        raise RenderError(f"Render failed: {str(e)}")
