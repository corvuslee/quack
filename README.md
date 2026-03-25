# Quack 🦆

A lightweight Python tool for searching DuckDuckGo with browser impersonation. Designed for LLM agents and developers who need programmatic access to DuckDuckGo search results.

## Features

- ✅ **Browser Impersonation**: Uses `primp` library to mimic real browser behavior
- ✅ **Simple API**: Easy-to-use Python interface and CLI
- ✅ **JSON Output**: Structured results for programmatic use
- ✅ **Minimal Dependencies**: Only requires `primp` and `lxml`

## Installation

```bash
# Using uv (recommended)
uv tool install .
```

## Usage

### Python API

```python
from quack import search

results = search("python programming", max_results=5)
for result in results:
    print(f"{result['title']}: {result['href']}")
```

### Command Line

```bash
# Basic search
quack "python programming"

# With options
quack "python programming" --max 5 --json
```

## Example Output

```json
[
  {
    "title": "Python.org",
    "href": "https://www.python.org",
    "body": "The official home of the Python Programming Language."
  },
  {
    "title": "Python Documentation",
    "href": "https://docs.python.org/3",
    "body": "Official Python 3 documentation."
  }
]
```

## License

MIT

---

*Quack is not affiliated with DuckDuckGo. Use responsibly and respect search engine terms of service.*
