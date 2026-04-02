"""URL fetching module."""

from typing import Dict, Optional, List
import requests
from config import TIMEOUT, MAX_RETRIES


class URLFetcher:
    """Fetches content from URLs."""
    
    def __init__(self, timeout: int = TIMEOUT, max_retries: int = MAX_RETRIES):
        self.timeout = timeout
        self.max_retries = max_retries
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    
    def fetch(self, url: str, result_data: Optional[Dict] = None) -> Optional[str]:
        """
        Fetch content from a single URL.
        
        Args:
            url: URL to fetch
            result_data: Optional dict with additional data (like download_url for Gutenberg books)
        
        Returns:
            HTML content or None if fetch failed
        """
        # Special handling for Project Gutenberg - use download_url if available
        if result_data and result_data.get("source") == "Project Gutenberg" and result_data.get("download_url"):
            try:
                response = requests.get(
                    result_data["download_url"],
                    headers=self.headers,
                    timeout=self.timeout
                )
                response.raise_for_status()
                print(f"[Fetcher] Successfully fetched Gutenberg book: {result_data.get('title', 'Unknown')}")
                return response.text
            except Exception as e:
                print(f"[Fetcher] Failed to fetch Gutenberg book: {e}")
                return None
        
        # Standard URL fetching for Wikipedia and arXiv
        for attempt in range(self.max_retries):
            try:
                response = requests.get(
                    url,
                    headers=self.headers,
                    timeout=self.timeout
                )
                response.raise_for_status()
                print(f"[Fetcher] Successfully fetched: {url}")
                return response.text
            
            except requests.RequestException as e:
                print(f"[Fetcher] Attempt {attempt + 1} failed for {url}: {e}")
                if attempt == self.max_retries - 1:
                    return None
        
        return None
    
    def fetch_multiple(self, urls: List[str], results_data: Optional[List[Dict]] = None) -> Dict[str, Optional[str]]:
        """Fetch content from multiple URLs."""
        results_map = {r.get("url"): r for r in (results_data or [])}
        fetched = {}
        for url in urls:
            result_data = results_map.get(url)
            fetched[url] = self.fetch(url, result_data)
        return fetched


def fetch_url(url: str) -> Optional[str]:
    """Convenience function to fetch a single URL."""
    fetcher = URLFetcher()
    return fetcher.fetch(url)


def fetch_urls(urls: List[str]) -> Dict[str, Optional[str]]:
    """Convenience function to fetch multiple URLs."""
    fetcher = URLFetcher()
    return fetcher.fetch_multiple(urls)
