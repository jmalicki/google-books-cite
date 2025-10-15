"""Verify Google Books IDs and links."""

import urllib.request
import urllib.error
import time
from typing import Dict, Optional


def verify_google_books_id(book_id: str, retry_delay: float = 0.5) -> Dict[str, any]:
    """
    Verify that a Google Books ID resolves to a valid book.
    
    Args:
        book_id: Google Books ID to verify
        retry_delay: Delay between requests (be polite to API)
        
    Returns:
        Dictionary with verification results:
        - 'valid': bool
        - 'title': str (if found)
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
            
            return {
                'valid': True,
                'title': title,
                'authors': authors,
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

