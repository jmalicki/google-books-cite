# Research: Google Books Citation Linking in LaTeX

## Problem Statement

Academic papers often cite classic works available in Google Books. Readers benefit when they can click directly to the cited page rather than searching through the book. However, this requires manually constructing URLs for each citation.

**Research Question**: Does an existing LaTeX package automate page-level linking to Google Books?

## Literature Review (2025-10-14)

### Search Queries Conducted
1. "biblatex Google Books page links citation LaTeX package"
2. "biblatex clickable page numbers inline citations hyperref"
3. "LaTeX biblatex-ext biblatex-philosophy page links"

### Findings

**No existing package found.** The LaTeX community currently uses:

1. **Manual `\href` approach** (most common):
   ```latex
   \href{https://books.google.com/books?id=BOOK_ID&pg=PA123}{Author (Year, p. 123)}
   ```
   **Problems**: Tedious, error-prone, doesn't integrate with BibTeX/BibLaTeX

2. **Citation managers** (BibDesk, JabRef):
   - Can store URLs in bibliography entries
   - Don't auto-generate page-specific links
   - URL appears in bibliography, not as clickable page numbers

3. **Google Scholar BibTeX export**:
   - Exports standard BibTeX format
   - Doesn't include Google Books links
   - No page-level information

### Relevant LaTeX Packages Examined

- **hyperref**: Provides `\href` but no citation integration
- **biblatex**: Extensible citation system but no Google Books support
- **biblatex-ext**: Extended styles, no digital linking
- **biblatex-philosophy**: Philosophy-specific formats, no page linking
- **doi**: Links DOIs but not book pages

## Technical Approaches Considered

### Approach 1: Custom Citation Commands ⭐ (Chosen)

**Pros**:
- Clean separation of concerns
- Easy to understand and debug
- Graceful fallback
- User controls when to use linking vs. regular citations

**Cons**:
- Requires using `\gbparencite` instead of `\parencite`
- Doesn't automatically apply to all citations

**Implementation**:
```latex
\NewDocumentCommand{\gbparencite}{o m}{
  % Check for Google Books ID
  % Extract page number
  % Construct URL
  % Wrap in \href
}
```

### Approach 2: BibLaTeX Format Override

Override `\parencite` to automatically detect Google Books IDs and add links.

**Pros**:
- Seamless - all citations automatically enhanced
- No need for special commands

**Cons**:
- Complex to implement correctly
- Risk of breaking existing citations
- Harder to debug
- May conflict with citation styles

**Verdict**: Too complex for initial version, consider for v2.0

### Approach 3: BibTeX Field

Add `googlebooksid` field to `.bib` entries, have BibLaTeX format it automatically.

**Pros**:
- Data stored with bibliography entry
- Could work with any citation style

**Cons**:
- Requires BibLaTeX format modifications
- Still need custom cite commands or format hooks
- More invasive

**Verdict**: Could be combined with Approach 1 as enhancement

## Google Books URL Structure

### Base URL
```
https://books.google.com/books?id=BOOK_ID
```

### Page-Specific URL
```
https://books.google.com/books?id=BOOK_ID&pg=PREFIX123
```

### Page Prefixes
- `PA` - Arabic page numbers (most common)
- `PR` - Roman numeral pages (prefaces, etc.)
- `PP` - Preliminary pages  
- `PT` - Table pages

### Examples
```
&pg=PA312    # Page 312
&pg=PRxiv    # Page xiv (roman numerals)
&pg=PP1      # Preliminary page 1
```

## Implementation Challenges

### 1. Page Number Extraction

Citations use various formats:
- `p.~123` (single page)
- `pp.~123-125` (range)
- `pp.~123--125` (range with en-dash)
- `123` (bare number)

**Solution**: Use `xstring` package to parse and extract first page number.

### 2. Page Prefix Detection

Need to determine if page is arabic, roman, or preliminary.

**Solution for v1.0**: Assume arabic (`PA`), add prefix detection in future version.

### 3. Google Books ID Storage

Where to store the mapping from citation keys to Google Books IDs?

**Options**:
- LaTeX3 property lists (chosen - flexible and fast)
- BibTeX fields (future enhancement)
- External database file (over-engineered)

### 4. Fallback Behavior

What happens when no Google Books ID is registered?

**Solution**: Use regular `\parencite` - zero breaking changes.

## Testing Strategy

### Phase 1: Proof of Concept
- [x] Create basic `\gbparencite` command
- [x] Test with 3 books from different eras
- [ ] Verify links work in PDF readers (Evince, Adobe, Preview)

### Phase 2: Robustness
- [ ] Test various page number formats
- [ ] Test with page ranges
- [ ] Test missing Google Books IDs
- [ ] Test with different citation styles (APA, Chicago, MLA)

### Phase 3: Integration
- [ ] Add as submodule to apocalypse-now-essay
- [ ] Convert several citations to use new commands
- [ ] Verify bibliography still formats correctly

## Future Enhancements

1. **Auto-detect page type** (arabic vs. roman)
2. **BibTeX field integration** (`googlebooksid` field)
3. **Internet Archive support** (backup when Google Books unavailable)
4. **Configuration options**:
   - Link color
   - Disable for print version
   - Preferred digital source priority
5. **Multiple platform support**:
   - HathiTrust
   - Project Gutenberg
   - Internet Archive
6. **Smart fallback**:
   - Try multiple sources
   - Generate QR codes for print versions

## Related Work

### Similar Projects in Other Contexts

- **Zotero/Mendeley**: Desktop apps with Google Books integration
- **Better BibTeX**: Enhanced BibTeX export for Zotero (doesn't do page linking)
- **DOI linking**: Established for journal articles, but books lack DOI
- **arXiv linking**: Similar concept for preprints

### Why This Is Novel

No tool bridges the gap between:
1. LaTeX's powerful citation system
2. Google Books' public domain repository
3. Page-level precision

This package is the first to automate this workflow.

## Conclusion

Creating `google-books-cite` package fills a real gap in the LaTeX ecosystem. The custom command approach provides immediate value with minimal risk, while leaving room for future enhancements through BibLaTeX integration.

## References

- LaTeX3 documentation: <https://ctan.org/pkg/l3kernel>
- BibLaTeX manual: <https://ctan.org/pkg/biblatex>
- Google Books API: <https://developers.google.com/books>
- xstring package: <https://ctan.org/pkg/xstring>

