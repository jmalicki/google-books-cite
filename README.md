# google-books-cite

**⚠️ NOT AFFILIATED WITH GOOGLE**  
This is an independent, open-source LaTeX package created by researchers for researchers.  
It is not created, maintained, endorsed, or supported by Google LLC.

---

LaTeX package for creating citations with direct page-level links to Google Books.

## Motivation

When citing public domain works available on Google Books, it's helpful for readers to jump directly to the cited page. However, no existing LaTeX package provides this functionality. The standard approach requires manually constructing `\href` commands for each citation, which is tedious and error-prone.

This package automates the process: page numbers in citations become clickable links to the exact page in Google Books.

## Features

- ✅ **Clickable page numbers** in citations link directly to Google Books pages
- ✅ **Maintains classical citation format** for print compatibility
- ✅ **Graceful fallback** to regular citations when no Google Books ID is available
- ✅ **Works with BibLaTeX** and standard citation commands
- ✅ **Simple API** - just register Google Books IDs and use `\gbparencite` instead of `\parencite`

## Quick Start

See [WORKFLOW.md](WORKFLOW.md) for complete step-by-step guide.

**TL;DR:**
```bash
# 1. Add Google Books IDs to your bibliography
gbfind --augment references.bib

# 2. In your .tex files, use \gbparencite instead of \parencite
\gbparencite[p.~312]{CitationKey}

# 3. Compile with two-pass workflow
xelatex main.tex
biber main
gbfind --make-links main
xelatex main.tex
```

## Installation

### As a Git Submodule (Recommended)

```bash
git submodule add https://github.com/jmalicki/google-books-cite.git
cd google-books-cite/tools && uv pip install -e .
```

Then in your LaTeX document:
```latex
\usepackage{google-books-cite/google-books-cite}
```

### Manual Installation

1. Copy `google-books-cite.sty` to your project or local TeX tree
2. Install Python tool: `cd tools && pip install -e .`

## Usage

### 1. Register Google Books IDs

In your document preamble (before `\begin{document}`):

```latex
\usepackage{google-books-cite}

% Register Google Books IDs for your references
\SetGoogleBooksID{SchopenhauerWWR1969}{NbsVAAAAYAAJ}
\SetGoogleBooksID{KantGroundwork1996}{L9ATAAAAQAAJ}
\SetGoogleBooksID{NietzscheBGE1990}{7KwQAAAAYAAJ}
```

### 2. Use Enhanced Citation Commands

```latex
% Regular citation (no link):
\parencite[p.~312]{SchopenhauerWWR1969}
% Renders: (Schopenhauer, 1969, p. 312)

% Google Books citation (page number is clickable):
\gbparencite[p.~312]{SchopenhauerWWR1969}
% Renders: (Schopenhauer, 1969, p. 312)
% Links to: https://books.google.com/books?id=NbsVAAAAYAAJ&pg=PA312
```

### Available Commands

- `\gbparencite[p.~123]{key}` - Parenthetical citation with clickable page
- `\gbtextcite[p.~123]{key}` - Text citation with clickable page
- `\SetGoogleBooksID{key}{id}` - Register a Google Books ID

## Finding Google Books IDs

1. Search for your book on [Google Books](https://books.google.com/)
2. Open the book preview
3. Look at the URL: `https://books.google.com/books?id=BOOK_ID`
4. The `BOOK_ID` is what you need

Example: For Kant's Groundwork, the URL might be:
```
https://books.google.com/books?id=L9ATAAAAQAAJ
```
So the Google Books ID is `L9ATAAAAQAAJ`.

## Requirements

- LaTeX with LaTeX3 (`expl3`, `xparse`)
- `xstring` package (for page number extraction)
- `hyperref` package (for creating links)
- `biblatex` (for citation commands)

## How It Works

The package:
1. Stores Google Books IDs in a LaTeX3 data structure
2. When you use `\gbparencite`, it checks if a Google Books ID exists
3. If yes, extracts the page number and constructs a Google Books URL
4. Wraps the page number in an `\href` command
5. If no ID exists, falls back to regular `\parencite`

## Limitations

- Currently only supports arabic page numbers (PA prefix)
- Doesn't support roman numerals or preliminary pages yet
- Page ranges link to the first page only
- Assumes standard pagination format

## Roadmap

- [ ] Support for roman numeral pages (PR prefix)
- [ ] Support for preliminary pages (PP prefix)  
- [ ] Integration with BibTeX files (optional `googlebooksid` field)
- [ ] Configuration options (link color, style)
- [ ] Support for Internet Archive links as backup
- [ ] CTAN submission

## Research & Alternatives

We researched existing solutions and found:
- **No dedicated LaTeX package** for this functionality exists (as of 2025-10-14)
- **Manual approach**: Users manually construct `\href{URL}{text}` for each citation
- **Citation managers**: BibDesk, JabRef can store URLs but don't auto-generate page links
- **Google Scholar**: Exports BibTeX but doesn't include Google Books links

This package fills that gap.

## Contributing

Contributions welcome! Areas for improvement:
- Better page number parsing (handling more formats)
- Support for other digital book platforms (Internet Archive, HathiTrust)
- Integration with other citation styles beyond APA
- Test suite and examples

## License

MIT License - see LICENSE file

## Authors

- Joseph Malicki (concept and requirements)
- Claude/Cursor AI (initial implementation)

## Citation

If you use this package in academic work, please cite:

```bibtex
@software{google-books-cite,
  author = {Malicki, Joseph},
  title = {google-books-cite: LaTeX package for Google Books page-level citations},
  year = {2025},
  url = {https://github.com/jmalicki/google-books-cite}
}
```

