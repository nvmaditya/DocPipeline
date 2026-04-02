"""Entry point for the DDG search pipeline."""

import json
import sys
import io
import os
from datetime import datetime
from pathlib import Path

# Set UTF-8 encoding for output on Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from pipeline import run_pipeline
from cache import cache


def create_output_structure(query: str) -> Path:
    """Create output folder structure for the query."""
    # Sanitize query name for folder
    safe_query = "".join(c for c in query if c.isalnum() or c in (' ', '-', '_')).rstrip()
    safe_query = safe_query.replace(' ', '_')[:50]  # Limit length
    
    # Create outputs/query_name/ folder
    output_dir = Path("outputs") / safe_query
    output_dir.mkdir(parents=True, exist_ok=True)
    
    return output_dir


def save_results(result: dict, output_dir: Path) -> None:
    """Save results in multiple formats."""
    
    # 1. Save full JSON (for vector DB, metadata)
    json_file = output_dir / "results.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"[Output] Saved JSON: {json_file}")
    
    # 2. Save AI-generated comprehensive content
    if "ai_generated_summary" in result:
        ai_file = output_dir / "ai_generated_content.txt"
        with open(ai_file, 'w', encoding='utf-8') as f:
            f.write(f"Topic: {result['query']}\n")
            f.write(f"Generated: {result['timestamp']}\n")
            f.write(f"Sources used: {result['total_results']}\n")
            f.write("="*80 + "\n\n")
            f.write(result["ai_generated_summary"])
        print(f"[Output] Saved AI content: {ai_file}")
    
    # 3. Save readable summary (TXT)
    txt_file = output_dir / "summary.txt"
    with open(txt_file, 'w', encoding='utf-8') as f:
        f.write(f"Query: {result['query']}\n")
        f.write(f"Rewritten Query: {result.get('rewritten_query', result['query'])}\n")
        f.write(f"Timestamp: {result['timestamp']}\n")
        f.write(f"Total Results: {result['total_results']}\n")
        f.write("="*80 + "\n\n")
        
        for i, item in enumerate(result['results'], 1):
            f.write(f"\n{'='*80}\n")
            f.write(f"Result #{i}\n")
            f.write(f"{'='*80}\n")
            f.write(f"Title: {item['title']}\n")
            f.write(f"Source: {item['source']}\n")
            f.write(f"Type: {item['type']}\n")
            f.write(f"URL: {item['url']}\n")
            f.write(f"Snippet: {item['snippet']}\n")
            f.write(f"\n--- Content ({len(item.get('content', ''))} chars) ---\n")
            f.write(item.get('content', 'No content available') + "\n")
    print(f"[Output] Saved summary: {txt_file}")
    
    # 4. Save individual documents as separate files
    for i, item in enumerate(result['results'], 1):
        # Create filename from title
        safe_title = "".join(c for c in item['title'] if c.isalnum() or c in ('-', '_'))[:40]
        doc_file = output_dir / f"doc_{i}_{safe_title}.txt"
        
        with open(doc_file, 'w', encoding='utf-8') as f:
            f.write(f"Title: {item['title']}\n")
            f.write(f"Source: {item['source']} | Type: {item['type']}\n")
            f.write(f"URL: {item['url']}\n")
            f.write(f"Timestamp: {result['timestamp']}\n")
            f.write("="*80 + "\n\n")
            f.write(item.get('content', 'No content available'))
        print(f"[Output] Saved document: {doc_file}")
    
    # 5. Create a metadata file
    metadata_file = output_dir / "metadata.txt"
    with open(metadata_file, 'w', encoding='utf-8') as f:
        f.write(f"Query: {result['query']}\n")
        f.write(f"Timestamp: {result['timestamp']}\n")
        f.write(f"Total Results: {result['total_results']}\n")
        f.write(f"Sources:\n")
        sources = {}
        for item in result['results']:
            source = item['source']
            sources[source] = sources.get(source, 0) + 1
        for source, count in sorted(sources.items()):
            f.write(f"  - {source}: {count}\n")
        f.write(f"\nAI Generated Content: {'Yes' if 'ai_generated_summary' in result else 'No'}\n")
    print(f"[Output] Saved metadata: {metadata_file}")


def print_result(result: dict) -> None:
    """Pretty print the result to console."""
    print("\n" + "="*80)
    print("RESULT")
    print("="*80)
    print(json.dumps(result, indent=2, ensure_ascii=True))
    print("="*80 + "\n")


def main():
    """Main entry point."""
    # Use command-line arguments or default example queries
    if len(sys.argv) > 1:
        # If user provided query as argument, use it
        queries = sys.argv[1:]
    else:
        # Default example queries
        queries = [
            "Python machine learning libraries",
            "How to learn web development",
        ]
    
    # Run pipeline for each query
    for query in queries:
        try:
            print(f"\n[Pipeline] Processing query: {query}")
            result = run_pipeline(query, max_results=5, use_cache=True)
            
            # Create output structure and save results
            output_dir = create_output_structure(query)
            print(f"[Output] Directory created: {output_dir}\n")
            save_results(result, output_dir)
            
            # Also print to console
            print_result(result)
        
        except Exception as e:
            print(f"Error processing query '{query}': {e}")
            import traceback
            traceback.print_exc()


def search_single(query: str, max_results: int = 5) -> dict:
    """Search for a single query and return result."""
    return run_pipeline(query, max_results=max_results, use_cache=True)


if __name__ == "__main__":
    main()
