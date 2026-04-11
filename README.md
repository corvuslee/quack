# Quack 🦆

![CI](https://github.com/corvuslee/quack/actions/workflows/ci.yml/badge.svg)

A Python and CLI tool for searching DuckDuckGo with browser impersonation. Designed for LLM agents and developers who need programmatic access to DuckDuckGo search results.

## Features

- ✅ **Browser Impersonation**: Uses `primp` library to mimic real browser behavior
- ✅ **Simple API**: Easy-to-use Python interface and CLI
- ✅ **JSON Output**: Structured results for programmatic use
- ✅ **Minimal Dependencies**: Only requires `primp`, `selectolax`, and `html2text`

## Installation

```bash
uv tool install git+https://github.com/corvuslee/quack.git
```

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
```

---

*Quack is not affiliated with DuckDuckGo. Use responsibly and respect search engine terms of service.*
