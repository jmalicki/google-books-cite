# Transparency in Digital Source Linking

## The Attribution Problem

When creating clickable links to digital sources, readers should understand:
1. **What** they're clicking (Google Books, Internet Archive, etc.)
2. **Why** it's not the authoritative source (convenience copy)
3. **Limitations** of the digital version (page numbers may differ, OCR errors, etc.)

## Our Approach

### Visual Indicators

We provide several options for indicating Google Books links:

#### Option 1: Subtle Superscript (Default)
```latex
(Schopenhauer, 1969, p. 312ᴳᴮ)
```
Small superscript "GB" indicates Google Books link.

#### Option 2: Bracketed Label
```latex
(Schopenhauer, 1969, p. 312 [GB])
```
More explicit but takes more space.

#### Option 3: Color Coding
```latex
% In preamble:
\hypersetup{
  citecolor=blue,      % Regular citations
  gbcolor=teal         % Google Books links in different color
}
```

#### Option 4: Tooltip (PDF only)
```latex
% Hover shows: "Link to Google Books digitized copy"
```

### Recommended: Combined Approach

**In text**: Subtle superscript
```latex
(Schopenhauer, 1969, p. 312ᴳᴮ)
```

**In first footnote**: Explanation
```latex
\footnote{Links marked with ᴳᴮ point to Google Books digitized copies. 
Page numbers reference the print edition cited in the bibliography. 
Digital versions are provided for convenience and may contain OCR errors or 
formatting differences from the authoritative print source.}
```

**In bibliography**: Full print citation (unchanged)
```
Schopenhauer, A. (1969). The World as Will and Representation (Vol. 1, 
  E. F. J. Payne, Trans.). Dover Publications.
```

## Implementation

### Configuration Options

```latex
% In document preamble:
\usepackage{google-books-cite}

% Choose indicator style:
\SetGBIndicator{superscript}  % Default: ᴳᴮ
\SetGBIndicator{brackets}     % [GB]
\SetGBIndicator{none}         % No indicator
\SetGBIndicator{custom}{🔗}   % Custom symbol

% Set link color:
\SetGBLinkColor{teal}         % Different from regular links
```

### Example Document

```latex
\documentclass{article}
\usepackage{google-books-cite}

% Configure Google Books indicators
\SetGBIndicator{superscript}
\SetGBLinkColor{DarkCyan}

\begin{document}

Digital copies of public domain works are linked for reader convenience.
Links marked with ᴳᴮ point to Google Books. Page numbers reference the 
print editions listed in the bibliography.\footnote{Google Books provides 
digitized copies of public domain works. These are secondary sources provided 
for convenience. Scholars should verify quotations against print editions 
when possible.}

% Citation with Google Books link
As \gbtextcite[p.~312]{SchopenhauerWWR1969} argues...
% Renders: As Schopenhauer (1969, p. 312ᴳᴮ) argues...
% Link is colored DarkCyan, distinct from regular citations

\printbibliography
\end{document}
```

## Best Practices

### DO:
✅ Make Google Books links visually distinct from citations to primary sources
✅ Explain the nature of digital links in a footnote or preface
✅ Keep full bibliographic information in the bibliography
✅ Use standard page numbers from the print edition
✅ Note when digital and print editions differ significantly

### DON'T:
❌ Replace proper citations with just Google Books links
❌ Suggest Google Books is the authoritative source
❌ Hide that links are to secondary digitizations
❌ Use links in place of proper bibliography entries

## Legal & Ethical Considerations

### Public Domain Works
- Safe to link for works published pre-1928 in US
- Google Books shows full previews
- Links enhance accessibility without copyright concerns

### Copyright Works
- Google Books shows limited previews only
- Links may break if preview access changes
- Consider alternative sources (publisher, DOI, library)

### Attribution
Always cite the original publication, not Google Books:

**Correct**:
```
Kant, I. (1785). Grundlegung zur Metaphysik der Sitten. 
  Riga: Johann Friedrich Hartknoch.
```

**Incorrect**:
```
Kant, I. (n.d.). Groundwork. Retrieved from Google Books.
```

## Comparison with Other Practices

### DOI Links (Journal Articles)
- DOIs point to publisher's authoritative version
- No need for special indicator - expected behavior
- Different from convenience copies

### arXiv Links (Preprints)
- Often explicitly marked as "[arXiv]" or "[preprint]"
- Good model for transparency
- We follow similar practice with "[GB]" or ᴳᴮ

### Internet Archive Links
- Similar to Google Books - convenience access
- Should also be marked distinctly
- Future: package could support `\iaparencite` for Internet Archive

## Accessibility Note

Visual indicators should also work for:
- Screen readers (use proper alt text)
- Printed versions (GB symbol prints clearly)
- Black & white printing (don't rely on color alone)

## Future Enhancements

- [ ] Automatic footnote generation explaining GB links
- [ ] Configurable disclaimer text
- [ ] Multi-source indicators (GB, IA, etc.)
- [ ] Export to different formats (HTML shows URL explicitly)
- [ ] QR codes for print versions

