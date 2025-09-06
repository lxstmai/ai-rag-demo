"""
Website indexer for RAG system
"""
import requests
import time
from typing import List, Optional, Tuple
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

from utils.config import CHUNK_SIZE, CHUNK_OVERLAP
from utils.text_processing import (
    extract_text_from_html, 
    extract_title_from_html, 
    chunk_text,
    is_valid_url
)


class WebsiteIndexer:
    """
    Class for website indexing and vector representation creation
    """
    
    def __init__(self, embedding_model, chroma_collection):
        self.embedding_model = embedding_model
        self.chroma_collection = chroma_collection
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.visited_urls = set()
    
    def index_website(self, base_url: str, max_pages: int = 10) -> dict:
        """
        Indexes website starting from base URL
        
        Args:
            base_url: Base website URL
            max_pages: Maximum number of pages to index
            
        Returns:
            dict: Indexing result
        """
        if not is_valid_url(base_url):
            return {"error": "Invalid URL"}
        
        print(f"🚀 Starting website indexing: {base_url}")
        
        # Collect URLs for indexing
        urls_to_index = self._collect_urls(base_url, max_pages)
        
        if not urls_to_index:
            return {"error": "Failed to collect URLs for indexing"}
        
        print(f"📄 Found .* pages for indexing")
        
        # Index each page
        indexed_count = 0
        errors = []
        
        for i, url in enumerate(urls_to_index, 1):
            print(f"📝 Indexing page {i}/{len(urls_to_index)}: {url}")
            
            try:
                success = self._index_single_page(url)
                if success:
                    indexed_count += 1
                else:
                    errors.append(f"Indexing error: {url}")
                
                # Small pause between requests
                time.sleep(0.5)
                
            except Exception as e:
                error_msg = f"Error during indexing {url}: {str(e)}"
                print(f"❌ {error_msg}")
                errors.append(error_msg)
        
        result = {
            "total_urls": len(urls_to_index),
            "indexed_count": indexed_count,
            "errors": errors,
            "success": indexed_count > 0
        }
        
        print(f"✅ Indexing completed: {indexed_count}/{len(urls_to_index)} pages")
        return result
    
    def _collect_urls(self, base_url: str, max_pages: int) -> List[str]:
        """
        Collects URLs for indexing
        """
        urls = {base_url}
        visited = set()
        
        try:
            # Try to get sitemap
            sitemap_urls = self._get_sitemap_urls(base_url)
            if sitemap_urls:
                urls.update(sitemap_urls[:max_pages])
                return list(urls)[:max_pages]
        except Exception:
            pass
        
        # If sitemap unavailable, use link crawling
        return self._crawl_links(base_url, max_pages)
    
    def _get_sitemap_urls(self, base_url: str) -> Optional[List[str]]:
        """
        Tries to get URLs from sitemap.xml
        """
        try:
            sitemap_url = urljoin(base_url, "/sitemap.xml")
            response = requests.get(sitemap_url, timeout=10, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, "lxml-xml")
            urls = []
            
            for url_elem in soup.find_all("url"):
                loc_elem = url_elem.find("loc")
                if loc_elem:
                    url = loc_elem.get_text().strip()
                    if is_valid_url(url):
                        urls.append(url)
            
            return urls if urls else None
            
        except Exception:
            return None
    
    def _crawl_links(self, base_url: str, max_pages: int) -> List[str]:
        """
        Crawls site and collects internal links
        """
        urls_to_visit = {base_url}
        visited = set()
        base_domain = urlparse(base_url).netloc
        
        while urls_to_visit and len(visited) < max_pages:
            current_url = urls_to_visit.pop()
            
            if current_url in visited:
                continue
                
            visited.add(current_url)
            
            try:
                response = requests.get(current_url, timeout=10, headers=self.headers)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Search for links on the same domain
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    if not href or href.startswith(('#', 'tel:', 'mailto:', 'javascript:')):
                        continue
                    
                    full_url = urljoin(current_url, href)
                    parsed_url = urlparse(full_url)
                    
                    if parsed_url.netloc == base_domain:
                        clean_url = full_url.split('#')[0].rstrip('/')
                        if clean_url not in visited and clean_url not in urls_to_visit:
                            urls_to_visit.add(clean_url)
                
            except Exception:
                continue
        
        return list(visited)
    
    def _index_single_page(self, url: str) -> bool:
        """
        Indexes one page
        """
        try:
            response = requests.get(url, timeout=15, headers=self.headers)
            response.raise_for_status()
            
            # Extract text and title
            html_content = response.text
            title = extract_title_from_html(html_content)
            text_content = extract_text_from_html(html_content)
            
            if not text_content or len(text_content) < 50:
                return False
            
            # Split into chunks
            chunks = chunk_text(text_content, CHUNK_SIZE, CHUNK_OVERLAP)
            
            if not chunks:
                return False
            
            # Create embeddings
            embeddings = self.embedding_model.encode(chunks, normalize_embeddings=True)
            
            # Prepare metadata
            metadatas = []
            ids = []
            
            for i, chunk in enumerate(chunks):
                metadatas.append({
                    "url": url,
                    "title": title,
                    "chunk_index": i,
                    "total_chunks": len(chunks)
                })
                ids.append(f"{url}_{i}")
            
            # Add to vector database
            self.chroma_collection.add(
                embeddings=[emb.tolist() for emb in embeddings],
                documents=chunks,
                metadatas=metadatas,
                ids=ids
            )
            
            return True
            
        except Exception as e:
            print(f"Error during indexing {url}: {e}")
            return False
    
    def get_indexed_urls(self) -> List[str]:
        """
        Returns list of indexed URLs
        """
        try:
            results = self.chroma_collection.get(include=['metadatas'])
            urls = set()
            for metadata in results['metadatas']:
                if 'url' in metadata:
                    urls.add(metadata['url'])
            return list(urls)
        except Exception:
            return []
    
    def get_collection_stats(self) -> dict:
        """
        Returns collection statistics
        """
        try:
            count = self.chroma_collection.count()
            return {
                "total_chunks": count,
                "indexed_urls": len(self.get_indexed_urls())
            }
        except Exception:
            return {"total_chunks": 0, "indexed_urls": 0}
