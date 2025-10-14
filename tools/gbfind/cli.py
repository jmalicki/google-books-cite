"""Command-line interface for gbfind."""

import sys
import argparse
from typing import Optional

from .search import search_google_books, format_result
from .latex import generate_latex_command, generate_latex_file
from .bibtex import parse_bibtex_books, read_bibtex_file


def interactive_mode() -> int:
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
    
    try:
        results = search_google_books(author, title, year)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    
    if not results:
        print("No results found.")
        return 1
        
    print(f"Found {len(results)} result(s):\n")
    for i, result in enumerate(results, 1):
        print(format_result(result, i))
        
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


def batch_mode(bib_file: str, output_file: Optional[str] = None) -> int:
    """Batch process a BibTeX file."""
    print(f"Processing bibliography: {bib_file}")
    
    try:
        content = read_bibtex_file(bib_file)
    except FileNotFoundError:
        print(f"Error: File not found: {bib_file}", file=sys.stderr)
        return 1
        
    entries = parse_bibtex_books(content)
    
    if not entries:
        print("No book entries found in bibliography.", file=sys.stderr)
        return 1
        
    print(f"Found {len(entries)} book entries.\n")
    
    commands = []
    
    for citation_key, author, title, year in entries:
        print(f"Searching: {citation_key}")
        print(f"  {author} - {title} ({year})")
        
        try:
            results = search_google_books(author, title, year)
        except RuntimeError as e:
            print(f"  → Error: {e}")
            continue
        
        if results:
            best = results[0]
            google_books_id = best['id']
            
            status = "✓"
            if not best['publicDomain'] and best['viewability'] != 'ALL_PAGES':
                status = "⚠ Limited access"
                
            print(f"  → Found: {best['title'][:50]}... [{status}]")
            print(f"     Google Books ID: {google_books_id}")
            
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
            content = generate_latex_file(commands)
            with open(output_file, 'w') as f:
                f.write(content)
            print(f"\nCommands saved to: {output_file}")
    
    return 0


def main():
    """Main entry point."""
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Find Google Books IDs for bibliographic entries',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Interactive mode:
    gbfind
    
  Direct search:
    gbfind --author "Arthur Schopenhauer" --title "World as Will" --year 1969
    
  Batch process BibTeX file:
    gbfind --bib references.bib --output google-books-ids.tex
        """
    )
    
    parser.add_argument('--author', help='Author name')
    parser.add_argument('--title', help='Book title')
    parser.add_argument('--year', help='Publication year')
    parser.add_argument('--key', help='BibTeX citation key')
    parser.add_argument('--bib', help='Process entire .bib file')
    parser.add_argument('--augment', help='Augment .bib file with Google Books IDs (modifies file)')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without modifying files')
    parser.add_argument('--output', help='Output file for LaTeX commands')
    parser.add_argument('--version', action='version', version='gbfind 0.1.0')
    
    args = parser.parse_args()
    
    # Augment mode
    if args.augment:
        return augment_mode(args.augment, args.dry_run)
    
    # Batch mode
    if args.bib:
        return batch_mode(args.bib, args.output)
    
    # Direct search mode
    if args.author or args.title:
        try:
            results = search_google_books(args.author or '', args.title or '', args.year)
        except RuntimeError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
        
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


def augment_mode(bib_file: str, dry_run: bool = False) -> int:
    """Augment mode - add Google Books IDs to .bib file."""
    from .augment import augment_bibtex_file
    
    print(f"Augmenting bibliography: {bib_file}")
    print("This will add 'googlebooksid' and 'url' fields to entries.\n")
    
    try:
        content = read_bibtex_file(bib_file)
    except FileNotFoundError:
        print(f"Error: File not found: {bib_file}", file=sys.stderr)
        return 1
        
    entries = parse_bibtex_books(content)
    
    if not entries:
        print("No book entries found in bibliography.", file=sys.stderr)
        return 1
        
    print(f"Found {len(entries)} book entries.\n")
    
    updates = {}
    
    for citation_key, author, title, year in entries:
        print(f"Searching: {citation_key}")
        print(f"  {author} - {title} ({year})")
        
        try:
            results = search_google_books(author, title, year)
        except RuntimeError as e:
            print(f"  → Error: {e}")
            continue
        
        if results:
            best = results[0]
            google_books_id = best['id']
            
            status = "✓"
            if not best['publicDomain'] and best['viewability'] != 'ALL_PAGES':
                status = "⚠ Limited access"
                
            print(f"  → Found: {best['title'][:50]}... [{status}]")
            print(f"     Will add: googlebooksid = {{{google_books_id}}}")
            
            updates[citation_key] = google_books_id
        else:
            print(f"  → No results found")
            
        print()
    
    if not updates:
        print("No updates to apply.")
        return 0
    
    print("=" * 60)
    print(f"Ready to update {len(updates)} entries in {bib_file}")
    
    if dry_run:
        print("\n[DRY RUN] No changes made. Remove --dry-run to apply.")
        return 0
    
    # Confirm
    response = input("\nProceed? [y/N] ").strip().lower()
    if response != 'y':
        print("Aborted.")
        return 0
    
    # Apply updates
    updated_count = augment_bibtex_file(bib_file, updates, add_url=True, backup=True)
    
    print(f"\n✓ Updated {updated_count} entries")
    print(f"✓ Backup saved to {bib_file}.backup")
    print("\nYour .bib entries now include 'googlebooksid' and 'url' fields.")
    print("These will appear in your bibliography automatically with BibLaTeX.")
    
    return 0
