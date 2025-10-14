"""
gbfind - Find Google Books IDs for LaTeX citations.
"""

__version__ = "0.1.0"

from .search import search_google_books
from .latex import generate_latex_command

__all__ = ["search_google_books", "generate_latex_command"]

