"""Google Books API search functionality."""

import json
import urllib.parse
import urllib.request
from typing import Optional, List, Dict


def search_google_books(
    author: str = "",
    title: str = "",
    year: Optional[str] = None,
    max_results: int = 10
) -> List[Dict]:
    """
    Search Google Books API for a work.
    
    Args:
        author: Author name
        title: Book title  
        year: Optional publication year for filtering
        max_results: Maximum number of results to return
        
    Returns:
        List of matching books with metadata
    """
    if not author and not title:
        return []
        
    # Construct search query
    query_parts = []
    if author:
        query_parts.append(f'inauthor:"{author}"')
    if title:
        query_parts.append(f'intitle:"{title}"')
    
    query = ' '.join(query_parts)
    
    # Build API URL
    base_url = "https://www.googleapis.com/books/v1/volumes"
    params = {
        'q': query,
        'maxResults': max_results,
        'printType': 'books',
        'langRestrict': 'en'
    }
    
    url = f"{base_url}?{urllib.parse.urlencode(params)}"
    
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())
            
        if 'items' not in data:
            return []
            
        results = []
        for item in data['items']:
            volume_info = item.get('volumeInfo', {})
            access_info = item.get('accessInfo', {})
            
            result = {
                'id': item.get('id', ''),
                'title': volume_info.get('title', ''),
                'authors': volume_info.get('authors', []),
                'publishedDate': volume_info.get('publishedDate', ''),
                'viewability': access_info.get('viewability', 'NO_PAGES'),
                'publicDomain': access_info.get('publicDomain', False),
                'webReaderLink': volume_info.get('canonicalVolumeLink', ''),
                'pageCount': volume_info.get('pageCount', 0)
            }
            
            # Filter by year if provided
            if year:
                pub_year = result['publishedDate'][:4] if result['publishedDate'] else ''
                if pub_year and abs(int(pub_year) - int(year)) > 5:
                    continue
                    
            results.append(result)
            
        return results
        
    except Exception as e:
        raise RuntimeError(f"Error searching Google Books: {e}")


def format_result(result: Dict, index: int) -> str:
    """Format a search result for display."""
    authors = ', '.join(result['authors']) if result['authors'] else 'Unknown'
    status = []
    
    if result['publicDomain']:
        status.append('PUBLIC DOMAIN')
    
    viewability = result['viewability']
    if viewability == 'ALL_PAGES':
        status.append('Full view')
    elif viewability == 'PARTIAL':
        status.append('Partial view')
    elif viewability == 'NO_PAGES':
        status.append('No preview')
        
    status_str = ' | '.join(status) if status else 'Limited access'
    
    return f"""
[{index}] {result['title']}
    Authors: {authors}
    Date: {result['publishedDate']}
    Pages: {result['pageCount']}
    Status: {status_str}
    Google Books ID: {result['id']}
    URL: {result['webReaderLink']}
"""

