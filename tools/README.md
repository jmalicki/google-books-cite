# gbfind - Google Books ID Finder

Command-line tool to find Google Books IDs for LaTeX citations.

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

After installation, the `gbfind` command is available globally:

### Interactive Mode
```bash
gbfind
```

### Direct Search
```bash
gbfind --author "Arthur Schopenhauer" --title "World as Will" --year 1969 --key SchopenhauerWWR1969
```

### Batch Mode (Process .bib file)
```bash
gbfind --bib ../paper/everyone.bib --output google-books-ids.tex
```

## Features

- 🔍 Search Google Books API by author, title, and year
- 📚 Batch process entire BibTeX files
- ✅ Validates public domain status and viewability
- 🎯 Generates ready-to-use LaTeX commands
- 🚀 Zero external dependencies (uses stdlib only for basic features)
- 📦 Proper Python package with uv support

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
- Usage guide: [../TOOLS.md](../TOOLS.md)

