"""Content extraction module."""

from typing import Optional
from bs4 import BeautifulSoup
import re


class ContentExtractor:
    """Extracts meaningful content from HTML."""
    
    def __init__(self):
        self.parser = "html.parser"
    
    def extract(self, html: str, max_chars: int = 2000) -> str:
        """
        Extract main content from HTML.
        
        Args:
            html: HTML content
            max_chars: Maximum characters to extract
        
        Returns:
            Extracted text content
        """
        try:
            soup = BeautifulSoup(html, self.parser)
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer"]):
                script.decompose()
            
            # Get text
            text = soup.get_text()
            
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = " ".join(chunk for chunk in chunks if chunk)
            
            # Limit characters
            return text[:max_chars]
        
        except Exception as e:
            print(f"[Extractor] Error: {e}")
            return ""
    
    def extract_paragraphs(self, html: str, max_paragraphs: int = 5) -> list[str]:
        """
        Extract main paragraphs from HTML.
        
        Returns:
            List of paragraph texts
        """
        try:
            soup = BeautifulSoup(html, self.parser)
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer"]):
                script.decompose()
            
            # Get paragraphs
            paragraphs = soup.find_all("p")
            texts = [p.get_text().strip() for p in paragraphs if p.get_text().strip()]
            
            return texts[:max_paragraphs]
        
        except Exception as e:
            print(f"[Extractor] Error: {e}")
            return []


def extract_content(html: str, max_chars: int = 2000) -> str:
    """Convenience function to extract content."""
    extractor = ContentExtractor()
    return extractor.extract(html, max_chars)


def extract_paragraphs(html: str, max_paragraphs: int = 5) -> list[str]:
    """Convenience function to extract paragraphs."""
    extractor = ContentExtractor()
    return extractor.extract_paragraphs(html, max_paragraphs)
