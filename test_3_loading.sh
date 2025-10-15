#!/bin/bash
# Test 3: Does LaTeX load and use .gblinks.tex correctly?

cat > test3.gblinks.tex << 'ENDLINKS'
\expandafter\gdef\csname gblink@TestBook@p.~312\endcsname{http://example.com/page312}
ENDLINKS

cat > test3.tex << 'ENDTEX'
\documentclass{article}
\usepackage{hyperref}
\makeatletter

\input{test3.gblinks.tex}

\newcommand{\getgblink}[2]{\csname gblink@#1@#2\endcsname}
\newcommand{\ifgblink}[2]{%
  \ifcsname gblink@#1@#2\endcsname
    \expandafter\@firstoftwo
  \else
    \expandafter\@secondoftwo
  \fi
}

\makeatother
\begin{document}
Test: \ifgblink{TestBook}{p.~312}{
  Link found: [\getgblink{TestBook}{p.~312}]
}{
  Link NOT found
}
\end{document}
ENDTEX

xelatex -interaction=nonstopmode test3.tex >/dev/null 2>&1

if grep -q "Link found.*example.com/page312" <(pdftotext test3.pdf -); then
  echo "✓ Test 3 PASS: Links loaded and retrieved correctly"
else
  echo "✗ Test 3 FAIL: Links not retrieved"
  pdftotext test3.pdf -
  exit 1
fi
