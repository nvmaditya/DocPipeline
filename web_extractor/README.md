# Search Pipeline

A modular, simple pipeline for searching Wikipedia, arXiv papers, and Project Gutenberg books with full content extraction for vector databases.

## Architecture

```
Query → Rewrite (optional LLM) → Search (Wikipedia + arXiv + Gutenberg) → Fetch URLs → Extract → Structure (optional LLM) → Cache → JSON
```

## Features

- **Modular design**: Each step is a separate module
- **LLM integration**: Optional query rewriting and content structuring
- **Caching**: File-based caching to avoid redundant searches
- **Error handling**: Graceful failures with retries
- **Simple interface**: Easy to use and extend

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Copy `.env.example` to `.env` and customize:

```bash
cp .env.example .env
```

### Optional: Enable LLM Features

To use LLM-based query rewriting and content structuring:

1. Install OpenAI SDK: `pip install openai`
2. Set `LLM_API_KEY` in `.env`
3. Set `USE_LLM_REWRITER=true` and/or `USE_LLM_STRUCTURER=true`

## Usage

### Run with example queries:

```bash
python main.py
```

### Search for a specific query:

```bash
python main.py "your search query here"
```

### Use in Python code:

```python
from pipeline import run_pipeline
import json

result = run_pipeline("machine learning", max_results=5)
print(json.dumps(result, indent=2))
```

### Direct module usage:

```python
from search import search
from fetcher import fetch_url
from extractor import extract_content

# Search
results = search("python web framework")

# Fetch content
url = results[0]["url"]
html = fetch_url(url)

# Extract
content = extract_content(html)
print(content)
```

## Modules

| Module | Purpose |
|--------|---------|
| `query_rewriter.py` | Optional LLM query enhancement |
| `search.py` | Multi-source search (Wikipedia, arXiv, Project Gutenberg) |
| `fetcher.py` | URL content fetching with Gutenberg support |
| `extractor.py` | HTML and text content extraction |
| `structurer.py` | Optional LLM content structuring |
| `cache.py` | Result caching |
| `pipeline.py` | Main orchestration |
| `config.py` | Configuration management |

## Output Format

```json
{
  "query": "original query",
  "rewritten_query": "optimized query",
  "timestamp": "2024-03-26T10:30:00",
  "total_results": 5,
  "results": [
    {
      "title": "Article Title",
      "url": "https://example.com",
      "snippet": "Search result snippet",
      "structured": {
        "content": "extracted content",
        "type": "text"
      }
    }
  ]
}
```

## Extending the Pipeline

Add custom steps by:

1. Creating a new module
2. Adding a method to `SearchPipeline`
3. Calling it in the `run()` method

Example:

```python
def translate_content(text: str, target_lang: str) -> str:
    # Translation logic
    return translated_text
```

## Caching

Cached results are stored in `./cache` with a default TTL of 1 hour.

- **Clear cache**: `cache.clear()`
- **Disable caching**: Set `CACHE_ENABLED=false` in `.env` or pass `use_cache=False` to `run_pipeline()`

## Performance Tips

1. Enable caching for repeated queries
2. Reduce `MAX_RESULTS` for faster searches
3. Disable LLM features if not needed
4. Adjust `TIMEOUT` based on network conditions

## License

MIT
