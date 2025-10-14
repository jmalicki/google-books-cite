# gbfind - Google Books ID Finder

Command-line tool to find and report Google Books IDs for BibTeX files.

## Installation

```bash
cd tools
uv pip install -e .
```

## Quick Start

```bash
# 1. Analyze your bibliography (safe, read-only)
gbfind paper/everyone.bib

# 2. Review the report (shows: found, ambiguous, not found)

# 3. Add IDs to your .bib file
gbfind --augment paper/everyone.bib
```

## Modes

### Report Mode (Default) 🔍

**Safe and informational** - analyzes without modifying files:

```bash
gbfind references.bib
```

Output:
```
Analyzing bibliography: references.bib
Searching Google Books (read-only, no changes will be made)

Found 59 book entries.
======================================================================

SchopenhauerWWR1969
  Arthur Schopenhauer - The World as Will and Representation (1969)
  ✓ FOUND: The World as Will and Representation, Vol. 1
    Google Books ID: NbsVAAAAYAAJ
    Status: PUBLIC DOMAIN | Full view

KantGroundwork1996
  Immanuel Kant - Groundwork of the Metaphysics of Morals (1996)
  ⚠ AMBIGUOUS - 3 matches found
    Best match: Groundwork for the Metaphysics of Morals
    Google Books ID: L9ATAAAAQAAJ
    (Use interactive mode to review all matches)

ModernWork2020
  John Smith - Recent Philosophy (2020)
  ✗ NOT FOUND - No Google Books results

======================================================================
SUMMARY:
  ✓ Found: 45
  ⚠ Ambiguous: 10
  ✗ Not found: 4
  Total: 59

✓ FOUND (45):
  SchopenhauerWWR1969: NbsVAAAAYAAJ [PUBLIC DOMAIN | Full view]
  ...

⚠ AMBIGUOUS (10 - multiple matches):
  KantGroundwork1996: L9ATAAAAQAAJ (best of 3 matches)
  ...

✗ NOT FOUND (4):
  ModernWork2020: No results from Google Books API
  ...

======================================================================
NEXT STEPS:
  To add these IDs to your .bib file:
    gbfind --augment references.bib
  To preview changes first:
    gbfind --augment references.bib --dry-run
```

### Augment Mode 📝

**Modifies your .bib file** to add Google Books metadata:

```bash
# Preview changes
gbfind --augment references.bib --dry-run

# Apply changes (prompts for confirmation)
gbfind --augment references.bib
```

This adds `googlebooksid` and `url` fields to your bibliography entries:

```bibtex
@book{SchopenhauerWWR1969,
  author        = {Arthur Schopenhauer},
  year          = {1969},
  title         = {The World as Will and Representation},
  publisher     = {Dover},
  googlebooksid = {NbsVAAAAYAAJ},
  url           = {https://books.google.com/books?id=NbsVAAAAYAAJ},
}
```

Safety features:
- ✅ Creates `.backup` file before modifying
- ✅ Prompts for confirmation
- ✅ Skips entries that already have `googlebooksid`
- ✅ `--dry-run` flag to preview

### Interactive Mode 🎯

Search for individual books:

```bash
gbfind --interactive
# or just:
gbfind
```

Guided prompts for author, title, year, and citation key.

### Direct Search

```bash
gbfind --author "Arthur Schopenhauer" --title "World as Will" --year 1969
```

### Commands Mode (Legacy)

Generate `\SetGoogleBooksID` commands instead of modifying .bib:

```bash
gbfind --commands references.bib --output google-books-ids.tex
```

## Workflow

**Recommended workflow:**

1. **Analyze** (read-only):
   ```bash
   gbfind paper/everyone.bib > analysis.txt
   ```

2. **Review** the report:
   - Check ambiguous entries (multiple matches)
   - Note not-found entries
   
3. **Resolve ambiguities** using interactive mode:
   ```bash
   gbfind --interactive
   # Search for ambiguous entries one by one
   ```

4. **Augment** the bibliography:
   ```bash
   gbfind --augment paper/everyone.bib --dry-run  # Preview
   gbfind --augment paper/everyone.bib            # Apply
   ```

5. **Use in LaTeX**:
   - URLs appear in bibliography automatically
   - Use `\gbparencite` for clickable page numbers

## Requirements

- Python 3.8+
- No external dependencies (uses stdlib only)

## See Also

- LaTeX package documentation: [../README.md](../README.md)
- Detailed tool guide: [../TOOLS.md](../TOOLS.md)
