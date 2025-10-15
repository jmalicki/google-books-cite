"""Verify Google Books IDs and links."""

import urllib.request
import urllib.error
import time
from typing import Dict, Optional


def normalize_string(s: str) -> str:
    """Normalize a string for fuzzy comparison."""
    import re
    # Remove punctuation, lowercase, strip whitespace
    s = re.sub(r'[^\w\s]', '', s.lower())
    # Collapse multiple spaces
    s = re.sub(r'\s+', ' ', s)
    return s.strip()


def fuzzy_match(str1: str, str2: str, threshold: float = 0.6) -> bool:
    """
    Check if two strings are similar enough.
    
    Args:
        str1, str2: Strings to compare
        threshold: Similarity threshold (0.0-1.0)
        
    Returns:
        True if strings are similar enough
    """
    norm1 = normalize_string(str1)
    norm2 = normalize_string(str2)
    
    # Simple containment check
    if norm1 in norm2 or norm2 in norm1:
        return True
    
    # Word overlap check
    words1 = set(norm1.split())
    words2 = set(norm2.split())
    
    if not words1 or not words2:
        return False
    
    overlap = len(words1 & words2)
    similarity = overlap / min(len(words1), len(words2))
    
    return similarity >= threshold


def verify_google_books_id(
    book_id: str, 
    expected_author: Optional[str] = None,
    expected_title: Optional[str] = None,
    expected_year: Optional[str] = None,
    retry_delay: float = 0.5
) -> Dict[str, any]:
    """
    Verify that a Google Books ID resolves to a valid book and optionally check if it matches expected metadata.
    
    Args:
        book_id: Google Books ID to verify
        expected_author: Expected author name (for matching)
        expected_title: Expected title (for matching)
        expected_year: Expected publication year (for matching)
        retry_delay: Delay between requests (be polite to API)
        
    Returns:
        Dictionary with verification results:
        - 'valid': bool (ID exists)
        - 'matches': bool (metadata matches expected values)
        - 'title': str (actual title)
        - 'authors': list (actual authors)
        - 'year': str (actual year)
        - 'match_details': dict (what matched/didn't match)
        - 'error': str (if invalid)
        - 'url': str (the checked URL)
    """
    # Use the API to verify the ID
    api_url = f"https://www.googleapis.com/books/v1/volumes/{book_id}"
    
    time.sleep(retry_delay)  # Rate limiting
    
    try:
        with urllib.request.urlopen(api_url, timeout=10) as response:
            import json
            data = json.loads(response.read().decode())
            
            volume_info = data.get('volumeInfo', {})
            title = volume_info.get('title', 'Unknown')
            authors = volume_info.get('authors', [])
            published_date = volume_info.get('publishedDate', '')
            year = published_date[:4] if published_date else ''
            
            # Check if metadata matches expected values
            matches = True
            match_details = {}
            
            if expected_author:
                author_match = any(fuzzy_match(expected_author, author) for author in authors)
                match_details['author'] = author_match
                if not author_match:
                    matches = False
            
            if expected_title:
                title_match = fuzzy_match(expected_title, title)
                match_details['title'] = title_match
                if not title_match:
                    matches = False
            
            if expected_year:
                year_match = year and abs(int(year) - int(expected_year)) <= 3
                match_details['year'] = year_match
                if not year_match:
                    matches = False
            
            return {
                'valid': True,
                'matches': matches,
                'title': title,
                'authors': authors,
                'year': year,
                'match_details': match_details,
                'url': f"https://books.google.com/books?id={book_id}",
                'error': None
            }
            
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return {
                'valid': False,
                'title': None,
                'authors': None,
                'url': f"https://books.google.com/books?id={book_id}",
                'error': 'ID not found (404)'
            }
        else:
            return {
                'valid': False,
                'title': None,
                'authors': None,
                'url': f"https://books.google.com/books?id={book_id}",
                'error': f'HTTP error {e.code}'
            }
    except Exception as e:
        return {
            'valid': False,
            'title': None,
            'authors': None,
            'url': f"https://books.google.com/books?id={book_id}",
            'error': str(e)
        }


def verify_page_link(book_id: str, page_number: str, retry_delay: float = 0.5) -> Dict[str, any]:
    """
    Verify that a Google Books ID + page number resolves.
    
    Note: This checks if the book exists, but Google Books may not have
    the specific page available. We can't easily verify page-level access
    without making the actual request.
    
    Args:
        book_id: Google Books ID
        page_number: Page number (just the number, e.g., "47")
        retry_delay: Delay between requests
        
    Returns:
        Dictionary with verification results
    """
    # First verify the book ID exists
    book_result = verify_google_books_id(book_id, retry_delay)
    
    if not book_result['valid']:
        return book_result
    
    # Add page-specific URL
    page_url = f"https://books.google.com/books?id={book_id}&pg=PA{page_number}"
    
    return {
        'valid': True,
        'title': book_result['title'],
        'authors': book_result['authors'],
        'url': page_url,
        'error': None,
        'note': 'Book exists; page-level access depends on preview availability'
    }

