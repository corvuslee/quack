# Quack 🦆

![CI](https://github.com/corvuslee/quack/actions/workflows/ci.yml/badge.svg)

A Python and CLI tool for searching DuckDuckGo with browser impersonation. Designed for LLM agents and developers who need programmatic access to DuckDuckGo search results.

## Features

- ✅ **Browser Impersonation**: Uses `primp` library to mimic real browser behavior
- ✅ **Simple API**: Easy-to-use Python interface and CLI
- ✅ **JSON Output**: Structured results for programmatic use
- ✅ **Minimal Dependencies**: Core requires only `primp`, `selectolax`, and `html2text`
- ✅ (Optional) **JavaScript Rendering**: Render JavaScript pages with SeleniumBase UC Mode (much heavier dependencies)

## Installation

### Core (minimal dependencies)

```bash
uv tool install git+https://github.com/corvuslee/quack.git
```

### With JavaScript rendering support

```bash
uv tool install "git+https://github.com/corvuslee/quack.git[render]"
```

> **Note**: The `render` extra installs `seleniumbase` and its dependencies (including Chrome/ChromeDriver). This is optional and only needed for rendering JavaScript-heavy pages.

## Usage

### Python API

```python
from quack import search, fetch

# Search
results = search("python programming", max_results=5)
for result in results:
    print(f"{result['title']}: {result['href']}")

# Fetch webpage content
content = fetch("https://www.python.org")
print(content[:500])  # Print first 500 characters
```

### Command Line

```bash
# Basic search (for human)
quack search "python programming"

# Get JSON output (for machine)
quack search "python programming" --json

# Fetch webpage content
quack fetch "https://www.python.org"

# Render pages with javascript
quack render "https://www.python.org"
```

---

*Quack is not affiliated with DuckDuckGo. Use responsibly and respect search engine terms of service.*
