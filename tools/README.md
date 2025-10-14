# gbfind - Google Books ID Finder

Command-line tool to find Google Books IDs and augment BibTeX files.

## Installation

### Using uv (Recommended)

```bash
cd tools
uv pip install -e .
```

### Using pip

```bash
cd tools
pip install -e .
```

## Usage

After installation, the `gbfind` command is available globally.

### Augment Mode (Recommended) 🌟

**Automatically add Google Books IDs to your .bib file:**

```bash
# Dry run (preview changes)
gbfind --augment references.bib --dry-run

# Apply changes
gbfind --augment references.bib
```

This will:
1. Search Google Books for each `@book` entry
2. Add `googlebooksid = {ABC123}` field
3. Add `url = {https://books.google.com/books?id=ABC123}` field
4. Create `.backup` file before modifying
5. Prompt for confirmation

**Example result:**
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

The Google Books ID and URL will now appear in your bibliography automatically!

### Interactive Mode

```bash
gbfind
```

### Direct Search

```bash
gbfind --author "Arthur Schopenhauer" --title "World as Will" --year 1969 --key SchopenhauerWWR1969
```

### Batch Mode (Generate Commands)

```bash
gbfind --bib references.bib --output google-books-ids.tex
```

Generates `\SetGoogleBooksID` commands (legacy approach).

## Comparison: Augment vs Batch

| Feature | Augment Mode | Batch Mode |
|---------|--------------|------------|
| Modifies .bib | ✅ Yes | ❌ No |
| Data location | In bibliography | Separate file |
| Updates needed | Once | Every change |
| Works with tools | ✅ Yes | ⚠️ Custom only |
| Recommended | ✅ **Yes** | ❌ Legacy |

## Features

- 🔍 Search Google Books API by author, title, and year
- 📝 **Augment .bib files** with Google Books metadata
- ✅ Validates public domain status and viewability
- 🛡️ Creates backups before modifying files
- 🎯 Dry-run mode to preview changes
- 📦 No external dependencies for basic features

## Development

```bash
# Install with dev dependencies
uv pip install -e ".[dev]"

# Run tests
pytest

# Format code
black gbfind/
ruff check gbfind/
```

## See Also

- Main package documentation: [../README.md](../README.md)
- Detailed usage guide: [../TOOLS.md](../TOOLS.md)
