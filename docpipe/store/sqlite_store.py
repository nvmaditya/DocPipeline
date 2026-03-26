from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional


class SQLiteStore:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self) -> None:
        cursor = self.conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS documents (
                doc_id TEXT PRIMARY KEY,
                file_path TEXT NOT NULL,
                file_name TEXT NOT NULL,
                file_type TEXT NOT NULL,
                ingested_at TEXT NOT NULL,
                total_chunks INTEGER,
                metadata TEXT
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS chunks (
                chunk_id INTEGER PRIMARY KEY,
                doc_id TEXT NOT NULL REFERENCES documents(doc_id),
                chunk_index INTEGER NOT NULL,
                page_number INTEGER,
                char_start INTEGER,
                char_end INTEGER,
                chunk_text TEXT NOT NULL,
                heading_context TEXT,
                UNIQUE(doc_id, chunk_index)
            )
            """
        )
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_chunks_doc_id ON chunks(doc_id)")
        self.conn.commit()

    def add_document(self, doc_meta: Dict[str, Any], total_chunks: int) -> None:
        self.conn.execute(
            """
            INSERT OR REPLACE INTO documents
            (doc_id, file_path, file_name, file_type, ingested_at, total_chunks, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                doc_meta["doc_id"],
                doc_meta["file_path"],
                doc_meta["file_name"],
                doc_meta["file_type"],
                doc_meta["ingested_at"],
                total_chunks,
                json.dumps(doc_meta.get("metadata", {})),
            ),
        )
        self.conn.commit()

    def next_chunk_id(self) -> int:
        row = self.conn.execute("SELECT COALESCE(MAX(chunk_id), -1) AS max_id FROM chunks").fetchone()
        return int(row["max_id"]) + 1

    def add_chunks(self, chunks: List[Dict[str, Any]], start_chunk_id: int) -> List[int]:
        ids: List[int] = []
        for offset, chunk in enumerate(chunks):
            chunk_id = start_chunk_id + offset
            ids.append(chunk_id)
            self.conn.execute(
                """
                INSERT INTO chunks
                (chunk_id, doc_id, chunk_index, page_number, char_start, char_end, chunk_text, heading_context)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    chunk_id,
                    chunk["doc_id"],
                    chunk["chunk_index"],
                    chunk.get("page_number"),
                    chunk.get("char_start"),
                    chunk.get("char_end"),
                    chunk["chunk_text"],
                    chunk.get("heading_context"),
                ),
            )
        self.conn.commit()
        return ids

    def get_chunks_by_ids(self, chunk_ids: List[int]) -> Dict[int, Dict[str, Any]]:
        if not chunk_ids:
            return {}
        placeholders = ",".join("?" for _ in chunk_ids)
        rows = self.conn.execute(
            f"""
            SELECT c.*, d.file_name, d.file_path, d.file_type
            FROM chunks c
            JOIN documents d ON d.doc_id = c.doc_id
            WHERE c.chunk_id IN ({placeholders})
            """,
            chunk_ids,
        ).fetchall()
        return {int(row["chunk_id"]): dict(row) for row in rows}

    def stats(self) -> Dict[str, int]:
        doc_count = self.conn.execute("SELECT COUNT(*) AS c FROM documents").fetchone()["c"]
        chunk_count = self.conn.execute("SELECT COUNT(*) AS c FROM chunks").fetchone()["c"]
        return {"documents": int(doc_count), "chunks": int(chunk_count)}

    def close(self) -> None:
        self.conn.close()
