from __future__ import annotations

from typing import Any, Dict, List


def join_ranked_results(search_hits, chunk_map: Dict[int, Dict[str, Any]], score_threshold: float = 0.0) -> List[Dict[str, Any]]:
    ranked: List[Dict[str, Any]] = []
    for chunk_id, score in search_hits:
        if score < score_threshold:
            continue
        row = chunk_map.get(chunk_id)
        if not row:
            continue
        ranked.append(
            {
                "score": score,
                "chunk_id": chunk_id,
                "doc_id": row["doc_id"],
                "file_name": row["file_name"],
                "file_path": row["file_path"],
                "file_type": row["file_type"],
                "page_number": row["page_number"],
                "chunk_index": row["chunk_index"],
                "chunk_text": row["chunk_text"],
                "heading_context": row["heading_context"],
            }
        )
    return ranked


def build_rag_prompt(question: str, ranked_chunks: List[Dict[str, Any]]) -> str:
    context_blocks: List[str] = []
    for idx, chunk in enumerate(ranked_chunks, start=1):
        source = f"{chunk['file_name']}|page={chunk.get('page_number')}|chunk={chunk['chunk_id']}"
        context_blocks.append(f"[{idx}] SOURCE={source}\n{chunk['chunk_text']}")

    context_text = "\n\n".join(context_blocks)
    return (
        f"""You are VectorLearn, an intelligent document assistant. Your role is to provide accurate, well-reasoned answers strictly grounded in the provided context.

        ## Instructions
        - Answer ONLY using information from the provided context below.
        - If the context does not contain enough information to answer the question, respond with: "I don't have enough information in the uploaded documents to answer this."
        - Do NOT speculate, hallucinate, or use outside knowledge.
        - Be concise but complete — avoid unnecessary filler.
        - When multiple sources contribute to an answer, synthesize them coherently.
        - Cite every factual claim using inline source markers like [1], [2], etc., corresponding to the context chunks below.
        - If the question is ambiguous, answer the most reasonable interpretation and note any assumptions.

        ## Question
        {question}

        ## Context
        {context_text}

        ## Response Format
        - Lead with a direct answer to the question.
        - Follow with supporting detail where needed.
        - End citations inline (e.g., "The mitochondria is the powerhouse of the cell [1].").
        - If no relevant context exists, clearly state the limitation.
        """
    )


def collect_sources(ranked_chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen = set()
    sources: List[Dict[str, Any]] = []
    for chunk in ranked_chunks:
        key = (chunk["file_name"], chunk.get("page_number"), chunk["chunk_id"])
        if key in seen:
            continue
        seen.add(key)
        sources.append(
            {
                "file_name": chunk["file_name"],
                "file_path": chunk["file_path"],
                "page_number": chunk.get("page_number"),
                "chunk_id": chunk["chunk_id"],
                "score": chunk["score"],
            }
        )
    return sources
