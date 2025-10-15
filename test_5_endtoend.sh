#!/bin/bash
# Test 5: Complete end-to-end workflow

echo "=== Test 5: End-to-End Workflow ==="

# Setup
cat > test5.bib << 'ENDBIB'
@book{Schopenhauer1969,
  author = {Arthur Schopenhauer},
  title = {The World as Will},
  year = {1969},
  googlebooksid = {NbsVAAAAYAAJ},
}
ENDBIB

cat > test5.tex << 'ENDTEX'
\documentclass{article}
\usepackage{hyperref}
\usepackage{./google-books-cite}
\usepackage[backend=biber]{biblatex}
\addbibresource{test5.bib}
\begin{document}
Test citation: \gbparencite[p.~312]{Schopenhauer1969}
\end{document}
ENDTEX

# Step 1: First LaTeX pass
echo "Step 1: First LaTeX pass (generate .gbaux)..."
xelatex -interaction=nonstopmode test5.tex >/dev/null 2>&1
[ -f test5.gbaux ] && echo "  ✓ .gbaux created" || (echo "  ✗ FAIL"; exit 1)

# Step 2: Generate links
echo "Step 2: Generate links..."
python3 << 'EOPY'
import sys
sys.path.insert(0, 'tools')
from gbfind.linkgen import generate_links_file
count = generate_links_file('test5.gbaux', 'test5.bib', 'test5.gblinks.tex')
print(f"  ✓ Generated {count} links")
EOPY
[ -f test5.gblinks.tex ] && echo "  ✓ .gblinks.tex created" || (echo "  ✗ FAIL"; exit 1)

# Step 3: Second LaTeX pass
echo "Step 3: Second LaTeX pass (with links)..."
xelatex -interaction=nonstopmode test5.tex >/dev/null 2>&1
[ -f test5.pdf ] && echo "  ✓ PDF created" || (echo "  ✗ FAIL"; exit 1)

# Step 4: Verify PDF
echo "Step 4: Verify PDF contains links..."
if strings test5.pdf | grep -q "NbsVAAAAYAAJ"; then
  echo "  ✓ Google Books ID in PDF"
  if strings test5.pdf | grep -q "pg=PA312\|pg=PA31"; then
    echo "  ✓ Page parameter in PDF"
    echo ""
    echo "✅ Test 5 PASS: Complete workflow successful!"
    echo "   PDF should have clickable link to Google Books page 312"
  else
    echo "  ⚠ Page parameter missing"
  fi
else
  echo "  ✗ FAIL: Google Books URL not in PDF"
  exit 1
fi
