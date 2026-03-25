"""Command-line interface for Quack."""

import argparse
import json
import sys
from typing import List, Dict

from .core import search, SearchError, NoResultsError, RequestError

# Import version directly to avoid circular import
from importlib.metadata import version as get_version
__version__ = get_version("quack")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Quack - DuckDuckGo search with browser impersonation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  quack "python programming"            # Basic search
  quack "python programming" --max 5    # Limit to 5 results
  quack "python programming" --json     # JSON output
        """
    )
    
    parser.add_argument(
        "query",
        nargs="+",
        help="Search query"
    )
    
    parser.add_argument(
        "--max", "--max-results",
        type=int,
        default=10,
        help="Maximum number of results to return (default: 10)"
    )
    
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )
    
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Request timeout in seconds (default: 30)"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="Show version and exit"
    )
    
    args = parser.parse_args()
    
    # Combine query arguments into single string
    query = " ".join(args.query)
    
    try:
        # Perform search
        results = search(query, max_results=args.max, timeout=args.timeout)
        
        # Output results
        if args.json:
            print(json.dumps(results, indent=2, ensure_ascii=False))
        else:
            _print_text_results(results)
            
    except ValueError as e:
        print(f"Invalid input: {str(e)}", file=sys.stderr)
        sys.exit(1)
    except NoResultsError as e:
        print(f"No results found: {str(e)}", file=sys.stderr)
        sys.exit(1)
    except RequestError as e:
        print(f"Search request failed: {str(e)}", file=sys.stderr)
        sys.exit(1)
    except SearchError as e:
        print(f"Search error: {str(e)}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {str(e)}", file=sys.stderr)
        sys.exit(1)


def _print_text_results(results: List[Dict[str, str]]):
    """Print results in human-readable text format."""
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['title']}")
        print(f"   {result['href']}")
        if result['body']:
            print(f"   {result['body']}")
        print()


if __name__ == "__main__":
    main()