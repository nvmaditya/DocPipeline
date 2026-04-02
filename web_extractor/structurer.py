"""LLM-based content structuring module."""

import json
from typing import Dict, Any, Optional
from config import USE_LLM_STRUCTURER, LLM_API_KEY, LLM_MODEL


class ContentStructurer:
    """Structures extracted content using LLM (optional)."""
    
    def __init__(self, use_llm: bool = USE_LLM_STRUCTURER):
        self.use_llm = use_llm
        self.api_key = LLM_API_KEY
        self.model = LLM_MODEL
    
    def structure(self, content: str, query: str) -> Dict[str, Any]:
        """
        Structure content using LLM.
        If LLM is disabled, returns simple structure.
        
        Args:
            content: Content to structure
            query: Original query
        
        Returns:
            Structured data as dictionary
        """
        basic_structure = {
            "query": query,
            "content": content[:500],  # Summary
            "type": "text"
        }
        
        if not self.use_llm:
            return basic_structure
        
        try:
            import openai
            openai.api_key = self.api_key
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a data extraction expert. "
                                 "Extract key information and return valid JSON."
                    },
                    {
                        "role": "user",
                        "content": f"Extract key information from this content about '{query}':\n\n{content}"
                    }
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # Try to parse as JSON
            try:
                structured = json.loads(response_text)
            except json.JSONDecodeError:
                structured = basic_structure
                structured["ai_summary"] = response_text
            
            print(f"[Structurer] Structured content for query: {query}")
            return structured
        
        except ImportError:
            print("[Structurer] OpenAI not installed, using basic structure")
            return basic_structure
        except Exception as e:
            print(f"[Structurer] Error: {e}, using basic structure")
            return basic_structure


def structure_content(content: str, query: str) -> Dict[str, Any]:
    """Convenience function to structure content."""
    structurer = ContentStructurer()
    return structurer.structure(content, query)
