"""3-stage hybrid topic extraction engine.

Stage 1: Extract TOC from PDF metadata (free, fast, accurate)
Stage 2: LLM classification fallback via Ollama (only if Stage 1 fails)
Stage 3: Assign chunks to topics via cosine similarity (reuses existing vectors)
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np


@dataclass
class Topic:
    topic_id: int
    name: str
    chunk_ids: list[int] = field(default_factory=list)

    @property
    def chunk_count(self) -> int:
        return len(self.chunk_ids)


# ---------------------------------------------------------------------------
#  Stage 1 — PDF TOC extraction via PyMuPDF
# ---------------------------------------------------------------------------

def extract_toc_from_pdf(source_file: str) -> list[str]:
    """Extract topic/chapter names from PDF bookmark tree."""
    path = Path(source_file)
    if path.suffix.lower() != ".pdf":
        return []

    try:
        import fitz
    except ImportError:
        return []

    try:
        doc = fitz.open(str(path))
        toc = doc.get_toc()  # list of [level, title, page]
        doc.close()
    except Exception:
        return []

    if not toc:
        return []

    # Take top-level (level 1) or level 2 entries as topics
    # Filter out generic entries like "Table of Contents", "Index", etc.
    skip_patterns = re.compile(
        r"^(table\s+of\s+contents|index|bibliography|references|appendix|glossary|preface|foreword|acknowledgements?)$",
        re.IGNORECASE,
    )

    topics: list[str] = []
    
    # Try grouping by level to find a good depth
    from collections import defaultdict
    level_counts = defaultdict(int)
    for level, title, _ in toc:
        # Avoid counting generic titles
        if not skip_patterns.match(title.strip()):
            level_counts[level] += 1
            
    # We want a level that gives us a reasonable number of topics (e.g., 5 to 50)
    # If a book has very few items overall, just take basically everything up to level 3.
    target_levels = set()
    total_valid = sum(level_counts.values())
    
    if total_valid < 10:
        # Too few items, take all levels up to 3
        target_levels = {1, 2, 3}
    else:
        # Assume the level with the most items <= 30 is the 'chapter' level
        best_level = 1
        max_valid = 0
        for lvl in sorted(level_counts.keys()):
            count = level_counts[lvl]
            if 4 <= count <= 50 and count > max_valid:
                best_level = lvl
                max_valid = count
        
        # If we failed to find a prime chapter level, fallback to Min Level + 1
        if max_valid == 0:
            min_level = min(level_counts.keys())
            target_levels = {min_level, min_level + 1}
        else:
            # We also include any parent levels to be safe
            target_levels = set(range(1, best_level + 1))

    for level, title, _page in toc:
        if level not in target_levels and level > 3:
            continue  # Skip deeply nested sub-sections
        title = title.strip()
        if not title or skip_patterns.match(title):
            continue
        # Normalize chapter numbering: "Chapter 1: Solid State" → "Solid State"
        clean = re.sub(r"^((chapter|unit|section|part|module)\s*[\d.IVX]+\s*[-:]?\s*)", "", title, flags=re.IGNORECASE).strip()
        if clean and len(clean) > 2 and clean not in topics:
            topics.append(clean)

    return topics


# ---------------------------------------------------------------------------
#  Stage 2 — LLM classification fallback (Ollama phi3)
# ---------------------------------------------------------------------------

def classify_topics_with_llm(
    sample_chunks: list[str],
    llm_model: str = "llama-3.1-8b-instant",
    llm_backend: str = "groq",
    api_key: str = "",
) -> list[str]:
    """Send sampled chunks to an LLM to infer topic names."""
    if not sample_chunks:
        return ["General"]

    numbered = "\n".join(f"[{i+1}] {chunk[:300]}" for i, chunk in enumerate(sample_chunks))

    prompt = (
        "Below are sample text chunks from a book. "
        "Identify at least 8 to 15 distinct, specific topics or subject areas covered in these chunks. "
        "Avoid broad generic topics. Be specific based on the text. "
        "Return ONLY a JSON array of short topic name strings, nothing else.\n\n"
        f"Chunks:\n{numbered}\n\n"
        "JSON array of topic names:"
    )

    content = ""
    try:
        if llm_backend == "groq":
            content = _classify_with_groq(prompt, llm_model, api_key)
        elif llm_backend == "gemini":
            content = _classify_with_gemini(prompt, llm_model, api_key)
        else:
            content = _classify_with_ollama(prompt, llm_model)
    except Exception:
        return ["General"]

    if content:
        match = re.search(r"\[.*\]", content, re.DOTALL)
        if match:
            topics = json.loads(match.group())
            if isinstance(topics, list) and all(isinstance(t, str) for t in topics):
                return [t.strip() for t in topics if t.strip()]

    return ["General"]


def _classify_with_groq(prompt: str, model: str, api_key: str) -> str:
    """Use Groq API (OpenAI-compatible) for topic classification."""
    from openai import OpenAI
    client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You extract topic names from text. Reply with valid JSON only."},
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content or ""


def _classify_with_gemini(prompt: str, model: str, api_key: str) -> str:
    """Use Gemini API for topic classification."""
    from google import genai
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config={
            "system_instruction": "You extract topic names from text. Reply with valid JSON only.",
        },
    )
    return response.text or ""


def _classify_with_ollama(prompt: str, model: str) -> str:
    """Use Ollama for topic classification."""
    import ollama
    result = ollama.chat(
        model=model,
        messages=[
            {"role": "system", "content": "You extract topic names from text. Reply with valid JSON only."},
            {"role": "user", "content": prompt},
        ],
    )
    return result.get("message", {}).get("content", "")


# ---------------------------------------------------------------------------
#  Stage 3 — Assign chunks to topics via cosine similarity
# ---------------------------------------------------------------------------

def assign_chunks_to_topics(
    topic_names: list[str],
    chunk_ids: list[int],
    chunk_texts: list[str],
    embed_fn,
) -> list[Topic]:
    """Embed topic names, compare against chunk texts, assign closest topic."""
    if not topic_names or not chunk_ids:
        return []

    # If only one topic, assign everything to it
    if len(topic_names) == 1:
        return [Topic(topic_id=0, name=topic_names[0], chunk_ids=list(chunk_ids))]

    # Embed topic names and chunk texts
    topic_vecs = np.asarray(embed_fn(topic_names), dtype=np.float32)
    chunk_vecs = np.asarray(embed_fn(chunk_texts), dtype=np.float32)

    # Normalize for cosine similarity
    topic_norms = np.linalg.norm(topic_vecs, axis=1, keepdims=True)
    topic_norms[topic_norms == 0] = 1.0
    topic_vecs = topic_vecs / topic_norms

    chunk_norms = np.linalg.norm(chunk_vecs, axis=1, keepdims=True)
    chunk_norms[chunk_norms == 0] = 1.0
    chunk_vecs = chunk_vecs / chunk_norms

    # Cosine similarity matrix: (num_chunks, num_topics)
    similarity = chunk_vecs @ topic_vecs.T
    assignments = np.argmax(similarity, axis=1)

    # Build Topic objects
    topics: list[Topic] = []
    for tid, name in enumerate(topic_names):
        assigned_chunk_ids = [
            chunk_ids[i] for i in range(len(chunk_ids)) if assignments[i] == tid
        ]
        topics.append(Topic(topic_id=tid, name=name, chunk_ids=assigned_chunk_ids))

    return topics


# ---------------------------------------------------------------------------
#  Orchestrator — runs all 3 stages
# ---------------------------------------------------------------------------

def extract_topics(
    source_file: str,
    chunk_ids: list[int],
    chunk_texts: list[str],
    embed_fn,
    llm_model: str = "llama-3.1-8b-instant",
    llm_backend: str = "groq",
    api_key: str = "",
) -> list[Topic]:
    """Run the full 3-stage topic extraction pipeline.

    Args:
        source_file: Path to the original book file (PDF, TXT, etc.)
        chunk_ids: List of chunk IDs from the SQLite store
        chunk_texts: Corresponding chunk texts
        embed_fn: Callable that takes list[str] and returns embeddings array
        llm_model: Model name for Stage 2 fallback
        llm_backend: LLM backend to use ("groq", "gemini", or "ollama")
        api_key: API key for the LLM backend
    """
    # --- Stage 1: PDF TOC ---
    topic_names = extract_toc_from_pdf(source_file)

    # --- Stage 2: LLM fallback ---
    if not topic_names:
        # Sample ~20 chunks spread evenly across the book
        n = len(chunk_texts)
        if n <= 20:
            sample = chunk_texts
        else:
            step = n // 20
            sample = [chunk_texts[i] for i in range(0, n, step)][:20]
        topic_names = classify_topics_with_llm(
            sample,
            llm_model=llm_model,
            llm_backend=llm_backend,
            api_key=api_key,
        )

    # --- Stage 3: Semantic assignment ---
    return assign_chunks_to_topics(topic_names, chunk_ids, chunk_texts, embed_fn)
