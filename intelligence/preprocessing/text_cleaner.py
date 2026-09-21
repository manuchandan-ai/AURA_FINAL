"""Text preprocessing utilities."""

import re

def clean_text(text: str) -> str:
    """Basic text sanitization.
    
    - Removes extra whitespace
    - Lowercases text
    """
    if not text:
        return ""
    
    # Remove extra whitespace
    cleaned = re.sub(r'\s+', ' ', text).strip()
    return cleaned.lower()

def extract_urls(text: str) -> list:
    """Extract URLs from text."""
    if not text:
        return []
        
    url_pattern = re.compile(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+')
    return url_pattern.findall(text)

def tokenize(text: str) -> list:
    """Simple tokenization (split by word boundaries).
    
    Later stages will replace this with NLTK/Spacy.
    """
    if not text:
        return []
        
    # Keep alphanumeric characters
    words = re.findall(r'\b\w+\b', text.lower())
    return words
