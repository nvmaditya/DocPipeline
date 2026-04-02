"""Multi-source search module: Wikipedia, arXiv papers, and Project Gutenberg books."""

from typing import List, Dict, Any
import requests
from config import MAX_RESULTS, MAX_RETRIES, TIMEOUT


class SearchEngine:
    """Multi-source search: Wikipedia articles, academic papers, and public domain books."""
    
    def __init__(self, max_results: int = MAX_RESULTS):
        self.max_results = max_results
        self.wikipedia_api = "https://en.wikipedia.org/w/api.php"
        self.arxiv_api = "http://export.arxiv.org/api/query"
        self.gutendex_api = "https://gutendex.com/books"
    
    def search_wikipedia(self, query: str) -> List[Dict[str, Any]]:
        """Search Wikipedia articles."""
        try:
            params = {
                "action": "query",
                "list": "search",
                "srsearch": query,
                "srwhat": "text",
                "srlimit": self.max_results // 3,
                "format": "json"
            }
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(self.wikipedia_api, params=params, headers=headers, timeout=TIMEOUT)
            response.raise_for_status()
            results = response.json().get("query", {}).get("search", [])
            
            formatted = []
            for r in results:
                formatted.append({
                    "source": "Wikipedia",
                    "title": r["title"],
                    "url": f"https://en.wikipedia.org/wiki/{r['title'].replace(' ', '_')}",
                    "snippet": r["snippet"],
                    "type": "article"
                })
            return formatted
        except Exception as e:
            print(f"[Search] Wikipedia error: {e}")
            return []
    
    def search_arxiv(self, query: str) -> List[Dict[str, Any]]:
        """Search arXiv for academic papers."""
        try:
            params = {
                "search_query": f"all:{query}",
                "start": 0,
                "max_results": self.max_results // 3,
                "sortBy": "relevance",
                "sortOrder": "descending"
            }
            response = requests.get(self.arxiv_api, params=params, timeout=TIMEOUT)
            response.raise_for_status()
            
            formatted = []
            import xml.etree.ElementTree as ET
            root = ET.fromstring(response.content)
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            
            for entry in root.findall("atom:entry", ns):
                title_elem = entry.find("atom:title", ns)
                summary_elem = entry.find("atom:summary", ns)
                id_elem = entry.find("atom:id", ns)
                
                if title_elem is not None and id_elem is not None:
                    arxiv_id = id_elem.text.split("/abs/")[-1]
                    formatted.append({
                        "source": "arXiv",
                        "title": title_elem.text.strip(),
                        "url": f"https://arxiv.org/abs/{arxiv_id}",
                        "snippet": (summary_elem.text.strip() if summary_elem is not None else "")[:500],
                        "type": "paper"
                    })
            return formatted
        except Exception as e:
            print(f"[Search] arXiv error: {e}")
            return []
    
    def search_gutenberg(self, query: str) -> List[Dict[str, Any]]:
        """Search Project Gutenberg for public domain books with full text."""
        try:
            params = {
                "search": query,
                "topic": query
            }
            response = requests.get(self.gutendex_api, params=params, timeout=TIMEOUT)
            response.raise_for_status()
            docs = response.json().get("results", [])
            
            formatted = []
            for doc in docs[:self.max_results // 3]:
                if "title" in doc:
                    # Get download URL for plain text
                    download_url = None
                    if "formats" in doc and "text/plain; charset=utf-8" in doc["formats"]:
                        download_url = doc["formats"]["text/plain; charset=utf-8"]
                    
                    formatted.append({
                        "source": "Project Gutenberg",
                        "title": doc.get("title", ""),
                        "url": f"https://www.gutenberg.org/ebooks/{doc.get('id', '')}",
                        "snippet": f"Author: {doc.get('author', 'Unknown')}",
                        "type": "book",
                        "download_url": download_url
                    })
            return formatted
        except Exception as e:
            print(f"[Search] Project Gutenberg error: {e}")
            return []
    
    def search(self, query: str) -> List[Dict[str, Any]]:
        """Search across all sources."""
        results = []
        
        # Fetch from all sources
        print(f"[Search] Searching Wikipedia for: {query}")
        results.extend(self.search_wikipedia(query))
        
        print(f"[Search] Searching arXiv for: {query}")
        results.extend(self.search_arxiv(query))
        
        print(f"[Search] Searching Project Gutenberg for: {query}")
        results.extend(self.search_gutenberg(query))
        
        print(f"[Search] Found {len(results)} total results from multiple sources")
        return results[:self.max_results]


def search(query: str, max_results: int = MAX_RESULTS) -> List[Dict[str, Any]]:
    """Convenience function for searching."""
    engine = SearchEngine(max_results=max_results)
    return engine.search(query)


def search(query: str, max_results: int = MAX_RESULTS) -> List[Dict[str, Any]]:
    """Convenience function for searching."""
    engine = SearchEngine(max_results=max_results)
    return engine.search(query)
