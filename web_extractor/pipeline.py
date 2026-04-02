"""Main pipeline orchestrator."""

import json
from typing import List, Dict, Any
from datetime import datetime

from query_rewriter import rewrite_query
from search import search
from fetcher import fetch_urls, URLFetcher
from extractor import extract_content
from structurer import structure_content
from cache import cache
from generator import generate_content


class SearchPipeline:
    """Complete search pipeline from query to structured JSON results."""
    
    def __init__(self, use_cache: bool = True):
        self.use_cache = use_cache
    
    def _error_result(self, query: str, error_message: str) -> Dict[str, Any]:
        """Create error result."""
        return {
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "error": error_message,
            "total_results": 0,
            "results": []
        }
    
    def run(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """
        Run complete pipeline.
        
        Args:
            query: Search query
            max_results: Maximum number of results to process
        
        Returns:
            Structured JSON result
        """
        # Step 1: Check cache
        print(f"\n[Pipeline] Starting for query: {query}")
        cached = cache.get(query) if self.use_cache else None
        if cached:
            print("[Pipeline] Using cached result")
            return cached
        
        # Step 2: Rewrite query (optional)
        print("[Pipeline] Step 1/7: Rewriting query...")
        rewritten_query = rewrite_query(query)
        
        # Step 3: Search
        print("[Pipeline] Step 2/7: Searching with DuckDuckGo...")
        search_results = search(rewritten_query, max_results=max_results)
        
        if not search_results:
            result = self._error_result(query, "No search results found")
            return result
        
        # Step 4: Fetch URLs
        print("[Pipeline] Step 3/7: Fetching URLs...")
        urls = [r["url"] for r in search_results]
        fetcher = URLFetcher()
        fetched_content = {}
        for url in urls:
            result = next((r for r in search_results if r["url"] == url), None)
            fetched_content[url] = fetcher.fetch(url, result)
        
        # Step 5: Extract content
        print("[Pipeline] Step 4/7: Extracting content...")
        extracted_results = []
        for result in search_results:
            url = result["url"]
            html_content = fetched_content.get(url)
            
            if html_content:
                # Extract more content for vector DB (5000 chars)
                extracted_text = extract_content(html_content, max_chars=5000)
                extracted_results.append({
                    "title": result["title"],
                    "url": url,
                    "snippet": result["snippet"],
                    "source": result.get("source", "Unknown"),
                    "content_type": result.get("type", "text"),
                    "content": extracted_text
                })
        
        # Step 6: Structure with LLM
        print("[Pipeline] Step 5/7: Structuring content...")
        structured_items = []
        for item in extracted_results:
            structured = structure_content(item["content"], query)
            structured_items.append({
                "title": item["title"],
                "url": item["url"],
                "source": item["source"],
                "type": item["content_type"],
                "snippet": item["snippet"],
                "content": item["content"],
                "structured": structured
            })
        
        # Step 7: Build result
        print("[Pipeline] Step 6/7: Building final result...")
        result = {
            "query": query,
            "rewritten_query": rewritten_query,
            "timestamp": datetime.now().isoformat(),
            "total_results": len(structured_items),
            "results": structured_items
        }
        
        # Step 8: Generate AI content synthesis
        print("[Pipeline] Step 7/7: Generating AI-synthesized content...")
        ai_generated_content = generate_content(query, structured_items, target_words=1000)
        result["ai_generated_summary"] = ai_generated_content
        
        # Step 9: Cache result
        print("[Pipeline] Step 8/9: Caching result...")
        if self.use_cache:
            cache.set(query, result)
        
        print("[Pipeline] Complete!\n")
        return result


def run_pipeline(query: str, max_results: int = 5, use_cache: bool = True) -> Dict[str, Any]:
    """Convenience function to run pipeline."""
    pipeline = SearchPipeline(use_cache=use_cache)
    return pipeline.run(query, max_results)
