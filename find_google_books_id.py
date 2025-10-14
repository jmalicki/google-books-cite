#!/usr/bin/env python3
"""
Find Google Books IDs for bibliographic entries.
Usage: ./find_google_books_id.py "Author Name" "Book Title" [year]
"""

import sys
import urllib.parse
import urllib.request
import json
import argparse
from typing import Optional, List, Dict


def search_google_books(author: str, title: str, year: Optional[str] = None) -> List[Dict]:
    """
    Search Google Books API for a work.
    
    Args:
        author: Author name
        title: Book title
        year: Optional publication year
        
    Returns:
        List of matching books with metadata
    """
    # Construct search query
    query_parts = []
    if author:
        query_parts.append(f'inauthor:"{author}"')
    if title:
        query_parts.append(f'intitle:"{title}"')
    
    query = ' '.join(query_parts)
    
    # Build API URL
    base_url = "https://www.googleapis.com/books/v1/volumes"
    params = {
        'q': query,
        'maxResults': 10,
        'printType': 'books',
        'langRestrict': 'en'  # Prioritize English editions
    }
    
    url = f"{base_url}?{urllib.parse.urlencode(params)}"
    
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())
            
        if 'items' not in data:
            return []
            
        results = []
        for item in data['items']:
            volume_info = item.get('volumeInfo', {})
            access_info = item.get('accessInfo', {})
            
            # Extract relevant information
            result = {
                'id': item.get('id', ''),
                'title': volume_info.get('title', ''),
                'authors': volume_info.get('authors', []),
                'publishedDate': volume_info.get('publishedDate', ''),
                'viewability': access_info.get('viewability', 'NO_PAGES'),
                'publicDomain': access_info.get('publicDomain', False),
                'webReaderLink': volume_info.get('canonicalVolumeLink', ''),
                'pageCount': volume_info.get('pageCount', 0)
            }
            
            # Filter by year if provided
            if year:
                pub_year = result['publishedDate'][:4] if result['publishedDate'] else ''
                if pub_year and abs(int(pub_year) - int(year)) > 5:
                    continue  # Skip if year is too different
                    
            results.append(result)
            
        return results
        
    except Exception as e:
        print(f"Error searching Google Books: {e}", file=sys.stderr)
        return []


def format_result(result: Dict, index: int) -> str:
    """Format a search result for display."""
    authors = ', '.join(result['authors']) if result['authors'] else 'Unknown'
    status = []
    
    if result['publicDomain']:
        status.append('PUBLIC DOMAIN')
    
    viewability = result['viewability']
    if viewability == 'ALL_PAGES':
        status.append('Full view')
    elif viewability == 'PARTIAL':
        status.append('Partial view')
    elif viewability == 'NO_PAGES':
        status.append('No preview')
        
    status_str = ' | '.join(status) if status else 'Limited access'
    
    return f"""
[{index}] {result['title']}
    Authors: {authors}
    Date: {result['publishedDate']}
    Pages: {result['pageCount']}
    Status: {status_str}
    ID: {result['id']}
    URL: {result['webReaderLink']}
"""


def generate_latex_command(citation_key: str, google_books_id: str) -> str:
    """Generate LaTeX command to register the Google Books ID."""
    return f"\\SetGoogleBooksID{{{citation_key}}}{{{google_books_id}}}"


def interactive_mode():
    """Interactive mode for finding Google Books IDs."""
    print("=== Google Books ID Finder ===")
    print("Find Google Books IDs for your bibliography entries.\n")
    
    author = input("Author name: ").strip()
    title = input("Book title: ").strip()
    year = input("Publication year (optional): ").strip() or None
    
    if not author and not title:
        print("Error: Must provide at least author or title.", file=sys.stderr)
        return 1
        
    print(f"\nSearching for: {author} - {title}" + (f" ({year})" if year else ""))
    print("-" * 60)
    
    results = search_google_books(author, title, year)
    
    if not results:
        print("No results found.")
        return 1
        
    print(f"Found {len(results)} result(s):\n")
    for i, result in enumerate(results, 1):
        print(format_result(result, i))
        
    # Ask user to select
    print("-" * 60)
    choice = input(f"\nSelect result [1-{len(results)}] or 'q' to quit: ").strip()
    
    if choice.lower() == 'q':
        return 0
        
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(results):
            selected = results[idx]
            print(f"\nSelected: {selected['title']}")
            print(f"Google Books ID: {selected['id']}")
            
            # Ask for citation key
            citation_key = input("\nBibTeX citation key (e.g., Kant1785): ").strip()
            if citation_key:
                cmd = generate_latex_command(citation_key, selected['id'])
                print(f"\nLaTeX command:")
                print(f"  {cmd}")
                print("\nAdd this to your document preamble (before \\begin{{document}}).")
            
            return 0
        else:
            print("Invalid selection.", file=sys.stderr)
            return 1
    except ValueError:
        print("Invalid input.", file=sys.stderr)
        return 1


def batch_mode(bib_file: str, output_file: Optional[str] = None):
    """
    Batch process a BibTeX file to find Google Books IDs.
    
    Args:
        bib_file: Path to .bib file
        output_file: Optional output file for LaTeX commands
    """
    import re
    
    print(f"Processing bibliography: {bib_file}")
    
    try:
        with open(bib_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File not found: {bib_file}", file=sys.stderr)
        return 1
        
    # Parse BibTeX entries (simple regex-based parser)
    entry_pattern = r'@book\{([^,]+),\s*author\s*=\s*\{([^}]+)\},.*?title\s*=\s*\{([^}]+)\}.*?year\s*=\s*\{?(\d{4})\}?'
    entries = re.findall(entry_pattern, content, re.DOTALL | re.IGNORECASE)
    
    if not entries:
        print("No book entries found in bibliography.", file=sys.stderr)
        return 1
        
    print(f"Found {len(entries)} book entries.\n")
    
    commands = []
    
    for citation_key, author, title, year in entries:
        print(f"Searching: {citation_key}")
        print(f"  {author} - {title} ({year})")
        
        results = search_google_books(author, title, year)
        
        if results:
            # Take the first (best) match
            best = results[0]
            google_books_id = best['id']
            
            # Check if it's a good match
            status = "✓"
            if not best['publicDomain'] and best['viewability'] != 'ALL_PAGES':
                status = "⚠ Limited access"
                
            print(f"  → Found: {best['title'][:50]}... [{status}]")
            print(f"     ID: {google_books_id}")
            
            cmd = generate_latex_command(citation_key, google_books_id)
            commands.append(cmd)
        else:
            print(f"  → No results found")
            
        print()
        
    if commands:
        print("=" * 60)
        print("LaTeX commands for your preamble:\n")
        for cmd in commands:
            print(cmd)
            
        if output_file:
            with open(output_file, 'w') as f:
                f.write("% Google Books IDs\n")
                f.write("% Add these to your document preamble\n\n")
                for cmd in commands:
                    f.write(cmd + '\n')
            print(f"\nCommands saved to: {output_file}")
    
    return 0


def main():
    parser = argparse.ArgumentParser(
        description='Find Google Books IDs for bibliographic entries',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Interactive mode:
    %(prog)s
    
  Direct search:
    %(prog)s --author "Arthur Schopenhauer" --title "World as Will" --year 1969
    
  Batch process BibTeX file:
    %(prog)s --bib references.bib --output google-books-ids.tex
        """
    )
    
    parser.add_argument('--author', help='Author name')
    parser.add_argument('--title', help='Book title')
    parser.add_argument('--year', help='Publication year')
    parser.add_argument('--key', help='BibTeX citation key')
    parser.add_argument('--bib', help='Process entire .bib file')
    parser.add_argument('--output', help='Output file for LaTeX commands')
    
    args = parser.parse_args()
    
    # Batch mode
    if args.bib:
        return batch_mode(args.bib, args.output)
    
    # Direct search mode
    if args.author or args.title:
        results = search_google_books(args.author or '', args.title or '', args.year)
        
        if not results:
            print("No results found.", file=sys.stderr)
            return 1
            
        for i, result in enumerate(results, 1):
            print(format_result(result, i))
            
        if args.key and results:
            cmd = generate_latex_command(args.key, results[0]['id'])
            print(f"\nLaTeX command:\n  {cmd}")
            
        return 0
    
    # Interactive mode (default)
    return interactive_mode()


if __name__ == '__main__':
    sys.exit(main())

