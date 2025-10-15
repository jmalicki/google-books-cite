#!/bin/bash
# Test 1: Does LaTeX generate .gbaux correctly?

cat > test1.tex << 'ENDTEX'
\documentclass{article}
\usepackage{./google-books-cite}
\begin{document}
\gbparencite[p.~312]{TestKey}
\gbparencite[pp.~45-67]{OtherKey}
\end{document}
ENDTEX

xelatex -interaction=nonstopmode test1.tex >/dev/null 2>&1

if [ -f test1.gbaux ]; then
  echo "✓ Test 1 PASS: .gbaux file created"
  echo "Contents:"
  cat test1.gbaux
else
  echo "✗ Test 1 FAIL: .gbaux not created"
  exit 1
fi
