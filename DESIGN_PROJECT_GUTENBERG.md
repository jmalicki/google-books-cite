# Project Gutenberg Integration Design

## Overview

Extend the `google-books-cite` package (which conveniently abbreviates as "gb") to also support Project Gutenberg links. The same `gb` prefix serves both **G**oogle **B**ooks and Project **G**uten**b**erg.

## Requirements

### 1. Bibliography Links
- Bibliography entries should link to the main Project Gutenberg book page
- Example: `https://www.gutenberg.org/ebooks/1234`

### 2. Inline Citation Links
- Inline citations with page references should link to specific sections/chapters if possible
- Challenge: Project Gutenberg doesn't use page numbers (texts are reflowable)
- Need to map print page numbers to PG sections/anchors

### 3. User Interface
- Should be similar to `\gbparencite` for consistency
- May need optional parameter to specify source (GB vs PG)

## Project Gutenberg URL Structure

### Book Pages
```
https://www.gutenberg.org/ebooks/[ID]
```

Example: Heart of Darkness is `https://www.gutenberg.org/ebooks/219`

### Reading Interface Options

1. **HTML "Read Now"**:
   ```
   https://www.gutenberg.org/cache/epub/[ID]/pg[ID]-images.html
   ```
   - Single-page HTML with chapter anchors
   - Anchors typically: `#chap01`, `#chap02`, etc.
   - Or sometimes `#link2H_4_0001` style IDs

2. **Chapter-based HTML**:
   ```
   https://www.gutenberg.org/files/[ID]/[ID]-h/[ID]-h.htm
   ```
   - Then navigate to chapter files

3. **Plain Text**:
   ```
   https://www.gutenberg.org/files/[ID]/[ID]-0.txt
   ```
   - No linking capability

## Challenges

### Challenge 1: Page Number → Section Mapping

Project Gutenberg texts don't have page numbers. Possible approaches:

**Option A: Chapter-Only Links**
- User specifies chapter/section number instead of page
- Syntax: `\gbparencite[chap=3]{key}` or `\gbparencite[§3]{key}`
- Pro: Feasible, works with PG's anchor structure
- Con: Different from page-based citations

**Option B: Approximate Mapping**
- Build a lookup table: print page → PG chapter
- Requires manual curation per work
- Pro: Keeps standard citation format
- Con: Maintenance intensive, inexact

**Option C: Percentage-Based**
- Calculate percentage through book from page number
- Link to approximate location in HTML
- Pro: Automatic
- Con: Very imprecise, may not work with anchors

**Option D: No Section Links**
- Bibliography links to book
- Inline citations don't link (or link to book start)
- Pro: Simple, safe
- Con: Less useful than Google Books page links

### Challenge 2: Finding PG IDs

Unlike Google Books API, Project Gutenberg doesn't have a search API. Options:

**Option A: Manual Entry**
- User provides PG ID in `.bib` file
- Tool verifies it exists
- Pro: Accurate
- Con: Manual work

**Option B: Scrape Catalog**
- Parse PG catalog files (they publish RDF/XML feeds)
- Match by author/title
- Pro: Automated
- Con: Parsing complexity, rate limiting concerns

**Option C: Hybrid**
- Tool suggests based on author/title search of catalog
- User confirms
- Pro: Balance of automation and accuracy
- Con: More complex workflow

### Challenge 3: Which Source for Which Work?

Many works are in both Google Books and Project Gutenberg:
- GB: Better for modern scholarship, specific editions, page fidelity
- PG: Better for classic public domain works, full free access

How to choose? Options:

**Option A: User Specifies**
```latex
\gbparencite[p.~47, source=gb]{Augustine}  % Google Books
\gbparencite[chap=3, source=pg]{Augustine}  % Project Gutenberg
```

**Option B: Automatic by Field**
- If `.bib` has `googlebooksid`, use GB
- If `.bib` has `gutenbergid`, use PG
- If both, prefer GB for page-specific, PG for chapter-level?

**Option C: Separate Commands**
```latex
\gbparencite[p.~47]{Augustine}    % Google Books
\pgparencite[chap=3]{Augustine}   % Project Gutenberg
```

## Proposed Design

### Phase 1: Basic Support (Minimum Viable)

1. **BibTeX Field**: Add `gutenbergid = {219}` to entries
2. **Bibliography Links**: If `gutenbergid` present, make title link to `https://www.gutenberg.org/ebooks/[ID]`
3. **Inline Citations**: 
   - For now, `\pgparencite[chap=3]{key}` links to book start + `#chap03` anchor
   - Syntax: `\pgparencite[§3]{key}` or `\pgparencite[chap=3]{key}`
4. **Verification**: `gbfind --verify` checks PG IDs resolve (simple HTTP check)

### Phase 2: Enhanced Section Linking

1. **Mapping File**: Optional `[key].pgmap` files that map pages to chapters
   ```
   # Augustine-Confessions.pgmap
   p1-20: chap01
   p21-45: chap02
   ```
2. **Smart Linking**: If `.pgmap` exists, `\gbparencite[p.~47]{key}` can use page→chapter map
3. **Fallback**: Without `.pgmap`, falls back to chapter-only or book start

### Phase 3: Unified Interface

1. **Single Command**: `\gbparencite` auto-detects source
   - Uses GB if `googlebooksid` present
   - Uses PG if `gutenbergid` present
   - Prefers GB if both (better page fidelity)
2. **Override**: `\gbparencite[p.~47, source=pg]{key}` forces PG

## Questions for User

1. **For inline citations with page numbers and PG IDs**: Should we:
   - Link to book start (safe but less useful)?
   - Link to chapter based on manual mapping (accurate but requires work)?
   - Attempt percentage-based guess (automatic but imprecise)?

2. **For finding PG IDs**: Should we:
   - Require manual entry (slow but accurate)?
   - Build automated search (faster but needs catalog scraping)?
   - Hybrid with suggestions and confirmation?

3. **User interface preference**:
   - Separate commands (`\gbparencite` vs `\pgparencite`)?
   - Unified command with auto-detection?
   - Optional source parameter?

4. **For works in both GB and PG**: Which to prefer by default?

## Implementation Notes

- PG texts are public domain (mostly pre-1928 works)
- Good candidates from our bib: Augustine, Aquinas, Schopenhauer, Nietzsche, Kant, Kierkegaard, Dostoevsky
- Modern works (Sartre, Beauvoir, Camus, Foucault, etc.) won't be in PG
- Could have hybrid: classics → PG, modern → GB

## Next Steps

1. Get user feedback on design questions
2. Add `pgid` field support to `.bib` parser
3. Implement basic PG linking (bibliography only)
4. Add verification for PG IDs
5. Decide on section/chapter linking strategy
6. Implement chosen approach
7. Update documentation

## Naming Consideration

The `gb` abbreviation working for both **G**oogle **B**ooks and Project **G**uten**b**erg is serendipitous and worth highlighting in documentation. This allows:
- `\gbparencite` to work for both sources
- `gbfind` tool to search/manage both
- Unified visual indicator (superscript GB) to signal "digitized copy available"

