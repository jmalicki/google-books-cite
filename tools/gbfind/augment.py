"""Augment BibTeX files with Google Books metadata."""

import re
from typing import Dict, List


def augment_bibtex_entry(
    entry_text: str,
    google_books_id: str,
    add_url: bool = True
) -> str:
    """
    Add Google Books ID and URL to a BibTeX entry.
    
    Args:
        entry_text: Original BibTeX entry text
        google_books_id: Google Books ID to add
        add_url: Whether to also add the URL field
        
    Returns:
        Modified BibTeX entry with new fields
    """
    # Find the closing brace
    lines = entry_text.rstrip().rstrip('}').split('\n')
    
    # Add fields before the closing brace
    new_fields = []
    
    # Add googlebooksid field
    new_fields.append(f"  googlebooksid = {{{google_books_id}}},")
    
    # Add url field if requested
    if add_url:
        url = f"https://books.google.com/books?id={google_books_id}"
        new_fields.append(f"  url           = {{{url}}},")
    
    # Reconstruct entry
    result = '\n'.join(lines)
    if result.rstrip().endswith(','):
        result = result.rstrip()
    else:
        result = result.rstrip() + ','
    
    result += '\n' + '\n'.join(new_fields)
    result += '\n}\n'
    
    return result


def find_entry_in_content(content: str, citation_key: str) -> tuple[int, int, str]:
    """
    Find a BibTeX entry in content by citation key.
    
    Returns:
        (start_pos, end_pos, entry_text)
    """
    # Find @book{key,
    pattern = rf'(@book\{{{re.escape(citation_key)},.*?^\}})'
    match = re.search(pattern, content, re.MULTILINE | re.DOTALL | re.IGNORECASE)
    
    if not match:
        raise ValueError(f"Entry not found: {citation_key}")
    
    return match.start(), match.end(), match.group(1)


def augment_bibtex_file(
    filepath: str,
    updates: Dict[str, str],
    add_url: bool = True,
    backup: bool = True
) -> int:
    """
    Augment a BibTeX file with Google Books IDs.
    
    Args:
        filepath: Path to .bib file
        updates: Dict of {citation_key: google_books_id}
        add_url: Whether to add URL fields
        backup: Whether to create .bib.backup file
        
    Returns:
        Number of entries updated
    """
    # Read file
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Backup if requested
    if backup:
        with open(filepath + '.backup', 'w', encoding='utf-8') as f:
            f.write(content)
    
    # Apply updates
    updated_count = 0
    for citation_key, google_books_id in updates.items():
        try:
            start, end, entry = find_entry_in_content(content, citation_key)
            
            # Check if already has googlebooksid
            if 'googlebooksid' in entry.lower():
                print(f"  ⚠ {citation_key}: Already has googlebooksid, skipping")
                continue
            
            # Augment entry
            new_entry = augment_bibtex_entry(entry, google_books_id, add_url)
            
            # Replace in content
            content = content[:start] + new_entry + content[end:]
            updated_count += 1
            
        except ValueError as e:
            print(f"  ✗ {citation_key}: {e}")
    
    # Write updated content
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return updated_count

