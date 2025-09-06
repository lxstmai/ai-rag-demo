"""
Text processing utilities
"""
import re
from typing import List


def clean_text(text: str) -> str:
    """
    Очищает текст от лишних символов и форматирования
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
    Разбивает текст на чанки с перекрытием
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
    Извлекает заголовок из HTML контента
    """
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        title_tag = soup.find('title')
        if title_tag:
            return title_tag.get_text().strip()
    except Exception:
        pass
    
    return "Без заголовка"


def extract_text_from_html(html_content: str) -> str:
    """
    Извлекает чистый текст из HTML контента
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
    Проверяет валидность URL
    """
    import re
    pattern = re.compile(
        r'^https?://'  # http:// или https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # домен
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
        r'(?::\d+)?'  # порт
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return pattern.match(url) is not None
