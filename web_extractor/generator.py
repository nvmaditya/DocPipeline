"""AI content generation module - generates comprehensive content from fetched data."""

from typing import Dict, Any, Optional
import os
from dotenv import load_dotenv

load_dotenv()

# Try to import OpenAI, fall back to basic generation if not available
try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False


class ContentGenerator:
    """Generates comprehensive AI content from fetched data."""
    
    def __init__(self):
        self.api_key = os.getenv("LLM_API_KEY")
        self.model = "gpt-3.5-turbo"
        self.has_api = HAS_OPENAI and self.api_key
        
        if self.has_api:
            self.client = OpenAI(api_key=self.api_key)
    
    def generate_content(self, query: str, results: list, target_words: int = 1000) -> str:
        """
        Generate comprehensive content from search results using AI.
        
        Args:
            query: The search query
            results: List of search result snippets/content
            target_words: Target word count (default 1000)
        
        Returns:
            Generated content as string
        """
        if not self.has_api:
            return self._generate_basic_content(query, results, target_words)
        
        try:
            # Extract content summaries from results
            summaries = []
            for i, result in enumerate(results[:3], 1):
                summaries.append(f"Source {i} ({result.get('source', 'Unknown')}): {result.get('snippet', '')[:300]}")
            
            sources_text = "\n".join(summaries)
            
            prompt = f"""Based on the following search results about "{query}", write a comprehensive and informative article of approximately {target_words} words.

Search Results:
{sources_text}

Please write:
1. An engaging introduction (2-3 paragraphs)
2. Key concepts and definitions (2-3 paragraphs)
3. Current applications or importance (2-3 paragraphs)
4. Interesting facts or examples (2-3 paragraphs)
5. Future perspectives or conclusions (1-2 paragraphs)

Make sure the content is:
- Informative and well-structured
- Written for a general educated audience
- Approximately {target_words} words
- Original synthesis, not just summaries
- Engaging and interesting to read

Generate a comprehensive article now:"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional technical writer and content generator. Create comprehensive, well-researched articles based on provided information."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=int(target_words * 1.3)  # Allow some buffer
            )
            
            generated_content = response.choices[0].message.content
            print(f"[Generator] Generated {len(generated_content.split())} words of AI content")
            return generated_content
        
        except Exception as e:
            print(f"[Generator] Error generating content: {e}")
            return self._generate_basic_content(query, results, target_words)
    
    def _generate_basic_content(self, query: str, results: list, target_words: int = 1000) -> str:
        """Generate basic content without AI (fallback)."""
        content = f"# Comprehensive Overview: {query}\n\n"
        content += f"## Introduction\n"
        content += f"This is a comprehensive overview of {query} based on multiple authoritative sources. "
        content += f"The following information has been synthesized from Wikipedia articles, academic research papers, and published books.\n\n"
        
        content += f"## Key Information\n\n"
        for i, result in enumerate(results, 1):
            source = result.get('source', 'Unknown')
            title = result.get('title', 'Untitled')
            snippet = result.get('snippet', '')[:200]
            content += f"### {i}. {title} ({source})\n"
            content += f"{snippet}...\n\n"
        
        content += f"## Summary\n"
        content += f"{query} is a significant topic that spans multiple domains including academic research, "
        content += f"encyclopedic knowledge, and published literature. Understanding {query} requires knowledge from "
        content += f"multiple perspectives as outlined above.\n\n"
        
        content += f"*Note: This is auto-generated content. For full details, please refer to the individual source documents.*"
        
        return content


def generate_content(query: str, results: list, target_words: int = 1000) -> str:
    """Convenience function for generating content."""
    generator = ContentGenerator()
    return generator.generate_content(query, results, target_words)
