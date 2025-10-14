# Tools: Finding Google Books IDs

## find_google_books_id.py

Python script to automatically find Google Books IDs for your bibliography.

### Requirements

- Python 3.6+
- No external dependencies (uses stdlib only)

### Usage Modes

#### 1. Interactive Mode (Easiest)

```bash
./find_google_books_id.py
```

You'll be prompted for:
- Author name
- Book title  
- Publication year (optional)
- Citation key

The script will search Google Books, show results, and generate the LaTeX command.

**Example session:**
```
=== Google Books ID Finder ===
Author name: Arthur Schopenhauer
Book title: World as Will and Representation
Publication year (optional): 1969

Searching for: Arthur Schopenhauer - World as Will and Representation (1969)
------------------------------------------------------------
Found 3 result(s):

[1] The World as Will and Representation, Vol. 1
    Authors: Arthur Schopenhauer
    Date: 1969
    Pages: 534
    Status: PUBLIC DOMAIN | Full view
    ID: NbsVAAAAYAAJ
    URL: https://books.google.com/books?id=NbsVAAAAYAAJ

[2] The World as Will and Representation
    Authors: Arthur Schopenhauer
    Date: 2012
    Pages: 480
    Status: Partial view
    ID: xyz123abc
    URL: https://books.google.com/books?id=xyz123abc

Select result [1-2] or 'q' to quit: 1

Selected: The World as Will and Representation, Vol. 1
Google Books ID: NbsVAAAAYAAJ

BibTeX citation key (e.g., Kant1785): SchopenhauerWWR1969

LaTeX command:
  \SetGoogleBooksID{SchopenhauerWWR1969}{NbsVAAAAYAAJ}

Add this to your document preamble (before \begin{document}).
```

#### 2. Direct Search Mode

Search directly from command line:

```bash
./find_google_books_id.py \
  --author "Immanuel Kant" \
  --title "Groundwork" \
  --year "1785" \
  --key "Kant1785"
```

#### 3. Batch Mode (Process entire .bib file)

Automatically find IDs for all books in your bibliography:

```bash
./find_google_books_id.py --bib references.bib --output google-books-ids.tex
```

This will:
1. Parse your `.bib` file
2. Search Google Books for each `@book` entry
3. Generate `\SetGoogleBooksID` commands
4. Save to output file

**Example output file:**
```latex
% Google Books IDs
% Add these to your document preamble

\SetGoogleBooksID{SchopenhauerWWR1969}{NbsVAAAAYAAJ}
\SetGoogleBooksID{KantGroundwork1996}{L9ATAAAAQAAJ}
\SetGoogleBooksID{NietzscheBGE1990}{7KwQAAAAYAAJ}
```

Then in your LaTeX document:
```latex
\usepackage{google-books-cite}
\input{google-books-ids.tex}  % Load all IDs at once
```

### Understanding Results

#### Viewability Status

- **PUBLIC DOMAIN | Full view**: Best option! All pages available.
- **Partial view**: Some pages available (copyrighted works).
- **No preview**: No pages available online.

#### Tips for Best Results

1. **Use original publication year** if searching for classic works
2. **Check multiple results** - different editions may have different page numbers
3. **Verify page numbers** - click the URL to check the edition matches your citation
4. **Public domain works** (pre-1928) usually have full view

### Verifying Results

After getting a Google Books ID, verify it works:

1. Visit: `https://books.google.com/books?id=YOUR_ID`
2. Navigate to a page you cite (e.g., page 312)
3. Check the URL: should be `...&pg=PA312`
4. Verify the page content matches your print citation

### Troubleshooting

**No results found:**
- Try with just author or just title
- Remove subtitles
- Try variant spellings
- Check if it's in Google Books at all (not everything is)

**Wrong edition:**
- Check publication year carefully
- Look at page count (should match your edition)
- Translator name can help identify editions

**Limited access:**
- Public domain works (pre-1928) usually have full access
- Copyrighted works may have restricted preview
- Consider using entry without Google Books ID for copyrighted works

### Integration Workflow

**Recommended workflow:**

1. Write your paper with regular `\parencite` citations
2. Compile and verify all citations work correctly
3. Run batch mode on your `.bib` file:
   ```bash
   ./find_google_books_id.py --bib paper/everyone.bib --output paper/google-books-ids.tex
   ```
4. Review the generated IDs (check status messages)
5. Add to your document:
   ```latex
   \usepackage{google-books-cite}
   \input{google-books-ids.tex}
   ```
6. Replace `\parencite` with `\gbparencite` for works with IDs
7. Add `\gbdisclaimer` footnote on first use
8. Recompile and test links

### API Limits

The Google Books API has usage limits:
- 1000 queries per day for free
- If you hit limits, wait 24 hours or get an API key

To use your own API key:
```bash
export GOOGLE_BOOKS_API_KEY="your_key_here"
./find_google_books_id.py --bib references.bib
```

(Script will automatically use the API key if set)

### Advanced: Filtering Results

Edit the script to customize filtering:

```python
# Line ~65: Filter by viewability
if result['viewability'] not in ['ALL_PAGES', 'PARTIAL']:
    continue  # Skip no-preview books

# Line ~72: Stricter year matching  
if abs(int(pub_year) - int(year)) > 2:  # Within 2 years instead of 5
    continue
```

### Contributing

Found a bug or want to improve the tool? PRs welcome!

Ideas for enhancements:
- Support for other entry types (@incollection, @inbook)
- Fuzzy matching for titles
- Cache results to avoid re-searching
- Export to CSV for bulk review
- Integration with Zotero/JabRef

