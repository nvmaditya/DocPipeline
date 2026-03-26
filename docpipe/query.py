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
