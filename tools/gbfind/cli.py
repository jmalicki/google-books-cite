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


def report_mode(bib_file: str) -> int:
    """
    Default mode - report what IDs can be found without modifying files.
    """
    print(f"Analyzing bibliography: {bib_file}")
    print("Searching Google Books (read-only, no changes will be made)\n")
    
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
    print("=" * 70)
    
    found = []
    ambiguous = []
    not_found = []
    
    for citation_key, author, title, year in entries:
        print(f"\n{citation_key}")
        print(f"  {author} - {title} ({year})")
        
        try:
            results = search_google_books(author, title, year)
        except RuntimeError as e:
            print(f"  ✗ Error: {e}")
            not_found.append((citation_key, f"API error: {e}"))
            continue
        
        if not results:
            print(f"  ✗ NOT FOUND - No Google Books results")
            not_found.append((citation_key, "No results from Google Books API"))
        elif len(results) == 1:
            best = results[0]
            status_parts = []
            if best['publicDomain']:
                status_parts.append('PUBLIC DOMAIN')
            if best['viewability'] == 'ALL_PAGES':
                status_parts.append('Full view')
            elif best['viewability'] == 'PARTIAL':
                status_parts.append('Partial view')
            else:
                status_parts.append('No preview')
            
            status = ' | '.join(status_parts)
            print(f"  ✓ FOUND: {best['title'][:60]}")
            print(f"    Google Books ID: {best['id']}")
            print(f"    Status: {status}")
            found.append((citation_key, best['id'], status))
        else:
            # Multiple results - ambiguous
            best = results[0]
            print(f"  ⚠ AMBIGUOUS - {len(results)} matches found")
            print(f"    Best match: {best['title'][:60]}")
            print(f"    Google Books ID: {best['id']}")
            print(f"    (Use interactive mode to review all matches)")
            ambiguous.append((citation_key, best['id'], len(results)))
    
    # Summary
    print("\n" + "=" * 70)
    print(f"\nSUMMARY:")
    print(f"  ✓ Found: {len(found)}")
    print(f"  ⚠ Ambiguous: {len(ambiguous)}")
    print(f"  ✗ Not found: {len(not_found)}")
    print(f"  Total: {len(entries)}")
    
    if found:
        print(f"\n✓ FOUND ({len(found)}):")
        for key, gid, status in found:
            print(f"  {key}: {gid} [{status}]")
    
    if ambiguous:
        print(f"\n⚠ AMBIGUOUS ({len(ambiguous)} - multiple matches):")
        for key, gid, count in ambiguous:
            print(f"  {key}: {gid} (best of {count} matches)")
        print("  Tip: Use interactive mode to review alternatives")
    
    if not_found:
        print(f"\n✗ NOT FOUND ({len(not_found)}):")
        for key, reason in not_found:
            print(f"  {key}: {reason}")
    
    # Next steps
    print("\n" + "=" * 70)
    print("NEXT STEPS:")
    print(f"  To add these IDs to your .bib file:")
    print(f"    gbfind --augment {bib_file}")
    print(f"  To preview changes first:")
    print(f"    gbfind --augment {bib_file} --dry-run")
    
    return 0


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


def batch_mode(bib_file: str, output_file: Optional[str] = None) -> int:
    """Batch mode - generate LaTeX commands (legacy)."""
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
            content = generate_latex_file(commands)
            with open(output_file, 'w') as f:
                f.write(content)
            print(f"\nCommands saved to: {output_file}")
    
    return 0


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Find Google Books IDs for bibliographic entries',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Report mode (safe, default):
    gbfind references.bib
    
  Augment .bib file (adds googlebooksid fields):
    gbfind --augment references.bib
    
  Dry run (preview changes):
    gbfind --augment references.bib --dry-run
    
  Interactive mode:
    gbfind --interactive
    
  Generate LaTeX commands (legacy):
    gbfind --commands references.bib --output google-books-ids.tex
        """
    )
    
    parser.add_argument('bibfile', nargs='?', help='BibTeX file to analyze')
    parser.add_argument('--augment', action='store_true', 
                       help='Modify .bib file to add Google Books IDs (requires confirmation)')
    parser.add_argument('--make-links', metavar='JOBNAME', help='Generate .gblinks.tex from .gbaux file (e.g., paper/main)')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Preview changes without modifying files (use with --augment)')
    parser.add_argument('--commands', action='store_true',
                       help='Generate \\SetGoogleBooksID commands (legacy mode)')
    parser.add_argument('--output', help='Output file for LaTeX commands (use with --commands)')
    parser.add_argument('--interactive', action='store_true',
                       help='Interactive mode for single book lookup')
    parser.add_argument('--author', help='Author name (for direct search)')
    parser.add_argument('--title', help='Book title (for direct search)')
    parser.add_argument('--year', help='Publication year (for direct search)')
    parser.add_argument('--key', help='BibTeX citation key (for direct search)')
    parser.add_argument('--version', action='version', version='gbfind 0.1.0')
    
    args = parser.parse_args()
    
    # Link generation mode (highest priority - doesn't need bibfile)
    if args.make_links:
        return linkgen_mode(args.make_links, None)
    
    # Interactive mode
    if args.interactive or (not args.bibfile and not args.author and not args.title):
        return interactive_mode()
    
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
    
    # Requires bibfile for remaining modes
    if not args.bibfile:
        parser.print_help()
        return 1
    
    # Augment mode (modifies file)
    if args.augment:
        return augment_mode(args.bibfile, args.dry_run)
    
    # Commands mode (legacy - generates LaTeX commands)
    if args.commands:
        return batch_mode(args.bibfile, args.output)
    
    # Default: Report mode (safe, informational)
    return report_mode(args.bibfile)


if __name__ == '__main__':
    sys.exit(main())


def linkgen_mode(jobname: str, bib_file: Optional[str] = None) -> int:
    """Generate .gblinks.tex from .gbaux file."""
    from .linkgen import generate_links_file
    
    gbaux_file = f"{jobname}.gbaux"
    output_file = f"{jobname}.gblinks.tex"
    
    # Find .bib file
    if not bib_file:
        # Look for .bib in same directory
        import os
        dirname = os.path.dirname(jobname) or '.'
        bib_files = [f for f in os.listdir(dirname) if f.endswith('.bib')]
        if not bib_files:
            print(f"Error: No .bib file found. Specify with --bib", file=sys.stderr)
            return 1
        bib_file = os.path.join(dirname, bib_files[0])
        print(f"Using bibliography: {bib_file}")
    
    try:
        count = generate_links_file(gbaux_file, bib_file, output_file)
        print(f"\n✓ Generated {count} Google Books links")
        print(f"✓ Output: {output_file}")
        print("\nRun LaTeX again to include the links.")
        return 0
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        print(f"\nMake sure to run LaTeX first to generate {gbaux_file}", file=sys.stderr)
        return 1


def linkgen_mode(jobname: str, bib_file: Optional[str] = None) -> int:
    """Generate .gblinks.tex from .gbaux file."""
    from .linkgen import generate_links_file
    import os
    
    gbaux_file = f"{jobname}.gbaux"
    output_file = f"{jobname}.gblinks.tex"
    
    # Find .bib file if not specified
    if not bib_file:
        dirname = os.path.dirname(jobname) or '.'
        bib_files = [f for f in os.listdir(dirname) if f.endswith('.bib')]
        if not bib_files:
            print(f"Error: No .bib file found. Specify with --bib", file=sys.stderr)
            return 1
        bib_file = os.path.join(dirname, bib_files[0])
        print(f"Using bibliography: {bib_file}")
    
    try:
        count = generate_links_file(gbaux_file, bib_file, output_file)
        print(f"\n✓ Generated {count} Google Books links")
        print(f"✓ Output: {output_file}")
        print("\nRun LaTeX again to include the links.")
        return 0
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        print(f"\nMake sure to run LaTeX first to generate {gbaux_file}", file=sys.stderr)
        return 1
