"""
Text processing utilities
"""
import re
from typing import List


def clean_text(text: str) -> str:
    """
    Cleans text of extra characters and formatting
    """
    if not text:
        return ""
    
    # Remove multiple spaces and line breaks
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters but keep punctuation
    text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)]', '', text)
    
    return text.strip()


def chunk_text(text: str, chunk_size: int = 300, overlap: int = 50) -> List[str]:
    """
    Splits text into chunks with overlap
    """
    if not text:
        return []
    
    words = text.split()
    if len(words) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk = ' '.join(words[start:end])
        chunks.append(chunk)
        
        if end == len(words):
            break
            
        start = end - overlap
    
    return chunks


def extract_title_from_html(html_content: str) -> str:
    """
    Extracts the title from HTML content
    """
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        title_tag = soup.find('title')
        if title_tag:
            return title_tag.get_text().strip()
    except Exception:
        pass
    
    return "No Title"


def extract_text_from_html(html_content: str) -> str:
    """
    Extracts clean text from HTML content
    """
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove scripts, styles and other unnecessary elements
        for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
            element.decompose()
        
        # Get text
        text = soup.get_text(separator=' ', strip=True)
        return clean_text(text)
    except Exception:
        return ""


def is_valid_url(url: str) -> bool:
    """
    Checks if a URL is valid
    """
    import re
    pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
        r'(?::\d+)?'  # port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return pattern.match(url) is not None
    
