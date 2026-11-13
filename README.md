# Quack 🦆

![CI](https://github.com/corvuslee/quack/actions/workflows/ci.yml/badge.svg)

A Python and CLI tool for searching DuckDuckGo and fetching webpages with browser impersonation. Designed for LLM agents and developers who need programmatic access to web search and fetch.

Support Python 3.11 - 3.14.

## Features

- **Browser Impersonation**: Uses `primp` library to mimic real browser behavior
- **API**: Python interface and CLI
- **Minimal Dependencies**: Core requires only `primp`, `beautifulsoup4`, and `html2text`
- (Optional) **JavaScript Rendering**: Render JavaScript pages with SeleniumBase UC Mode (much heavier dependencies)

## Platforms

Quack's core feature is pure Python. It would run on any platforms that [`primp` supports](https://pypi.org/project/primp/#files). Tested on MacOS (arm64), Linux (x86-64, x86-32).

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
# Search
from quack import search

results = search("python programming", max_results=5)

# Fetch webpage content
from quack import fetch

content = fetch("https://www.python.org")

# Render JavaScript pages (requires [render] extra)
from quack import render

content = render("https://www.python.org")
```

### Command Line

```bash
# Search with JSON output
quack search "python programming" --json

# Fetch webpage content
quack fetch "https://www.python.org"

# Render pages with javascript
quack render "https://www.python.org"
```
---

*Quack is not affiliated with DuckDuckGo. Use responsibly and respect search engine terms of service.*
