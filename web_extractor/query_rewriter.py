"""Query rewriting module for LLM-based query enhancement."""

import os
from typing import Optional
from config import USE_LLM_REWRITER, LLM_API_KEY, LLM_MODEL


class QueryRewriter:
    """Rewrites queries using LLM (optional)."""
    
    def __init__(self, use_llm: bool = USE_LLM_REWRITER):
        self.use_llm = use_llm
        self.api_key = LLM_API_KEY
        self.model = LLM_MODEL
    
    def rewrite(self, query: str) -> str:
        """
        Rewrite query for better search results.
        If LLM is disabled, returns original query.
        """
        if not self.use_llm:
            return query
        
        try:
            # Example: Using OpenAI API
            import openai
            openai.api_key = self.api_key
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a search query optimization expert. "
                                 "Rewrite the user's query to be more effective for web search."
                    },
                    {
                        "role": "user",
                        "content": f"Rewrite this query for better search results: {query}"
                    }
                ],
                temperature=0.3,
                max_tokens=100
            )
            
            rewritten = response.choices[0].message.content.strip()
            print(f"[QueryRewriter] Original: {query}")
            print(f"[QueryRewriter] Rewritten: {rewritten}")
            return rewritten
            
        except ImportError:
            print("[QueryRewriter] OpenAI not installed, using original query")
            return query
        except Exception as e:
            print(f"[QueryRewriter] Error: {e}, using original query")
            return query


def rewrite_query(query: str) -> str:
    """Convenience function to rewrite query."""
    rewriter = QueryRewriter()
    return rewriter.rewrite(query)
