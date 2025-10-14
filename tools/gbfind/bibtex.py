"""BibTeX file parsing utilities."""

import re
from typing import List, Tuple


def parse_bibtex_books(content: str) -> List[Tuple[str, str, str, str]]:
    """
    Parse book entries from BibTeX content.
    
    Args:
        content: BibTeX file content
        
    Returns:
        List of tuples: (citation_key, author, title, year)
    """
    # Simple regex-based parser for @book entries
    # Matches: @book{key, author={...}, title={...}, year={...}}
    pattern = r'@book\{([^,]+),\s*author\s*=\s*\{([^}]+)\},.*?title\s*=\s*\{([^}]+)\}.*?year\s*=\s*\{?(\d{4})\}?'
    
    entries = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
    return entries


def read_bibtex_file(filepath: str) -> str:
    """Read BibTeX file content."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

