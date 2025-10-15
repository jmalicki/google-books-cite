#!/bin/bash
# Test 4: Does \href create clickable links in PDF?

cat > test4.gblinks.tex << 'ENDLINKS'
\expandafter\gdef\csname gblink@Book@p.~42\endcsname{https://books.google.com/books?id=TEST123&pg=PA42}
ENDLINKS

cat > test4.tex << 'ENDTEX'
\documentclass{article}
\usepackage{hyperref}
\usepackage{xcolor}
\definecolor{gbcolor}{HTML}{008B8B}
\makeatletter

\input{test4.gblinks.tex}
\newcommand{\getgblink}[2]{\csname gblink@#1@#2\endcsname}

\makeatother
\begin{document}
Link: {\color{gbcolor}\href{\getgblink{Book}{p.~42}}{p. 42$^{\text{\tiny GB}}$}}
\end{document}
ENDTEX

xelatex -interaction=nonstopmode test4.tex >/dev/null 2>&1

# Check PDF contains the URL
if strings test4.pdf | grep -q "books.google.com.*TEST123"; then
  echo "✓ Test 4 PASS: PDF contains Google Books URL"
  strings test4.pdf | grep "books.google.com" | head -1
else
  echo "✗ Test 4 FAIL: URL not in PDF"
  exit 1
fi
