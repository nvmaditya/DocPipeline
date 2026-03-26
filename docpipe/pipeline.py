from __future__ import annotations

import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from .chunkers import RecursiveChunker, SemanticChunker
from .cleaner import clean_text
from .embedder import Embedder
from .extractors import ExtractorRouter
from .query import join_ranked_results
from .store import FaissStore, SQLiteStore


class Pipeline:
    def __init__(self, config: str = "config.yaml") -> None:
        cfg = self._load_config(config)
        self.config = cfg

        extraction_cfg = cfg.get("extraction", {})
        chunk_cfg = cfg.get("chunking", {})
        embedding_cfg = cfg.get("embedding", {})
        faiss_cfg = cfg.get("faiss", {})
        store_cfg = cfg.get("store", {})

        self.router = ExtractorRouter(
            scanned_threshold=int(extraction_cfg.get("scanned_threshold", 50)),
            ocr_engine=str(extraction_cfg.get("ocr_engine", "none")),
            ocr_language=str(extraction_cfg.get("ocr_language", "eng")),
        )
        self.embedder = Embedder(
            model_name=str(embedding_cfg.get("model", "BAAI/bge-large-en-v1.5")),
            batch_size=int(embedding_cfg.get("batch_size", 32)),
            device=str(embedding_cfg.get("device", "cpu")),
            normalize=bool(embedding_cfg.get("normalize", True)),
        )

        chunk_size = int(chunk_cfg.get("chunk_size", 512))
        chunk_overlap = int(chunk_cfg.get("chunk_overlap", 64))
        strategy = str(chunk_cfg.get("strategy", "recursive")).lower()
        if strategy == "semantic":
            self.chunker = SemanticChunker(
                embedding_fn=self.embedder.encode,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                similarity_threshold=float(chunk_cfg.get("semantic_threshold", 0.5)),
            )
        else:
            self.chunker = RecursiveChunker(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
            )

        self.sqlite = SQLiteStore(str(store_cfg.get("sqlite_path", "store/metadata.db")))
        self.faiss = FaissStore(
            str(store_cfg.get("faiss_path", "store/faiss.index")),
            index_type=str(faiss_cfg.get("index_type", "flat")),
            hnsw_m=int(faiss_cfg.get("hnsw_m", 32)),
            hnsw_ef_construction=int(faiss_cfg.get("hnsw_ef_construction", 200)),
            hnsw_ef_search=int(faiss_cfg.get("hnsw_ef_search", 64)),
        )

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        with open(config_path, "r", encoding="utf-8") as handle:
            return yaml.safe_load(handle) or {}

    def ingest(self, path: str) -> int:
        p = Path(path)
        files = [p] if p.is_file() else [f for f in p.rglob("*") if f.is_file()]
        ingested = 0
        for file_path in files:
            try:
                if self._ingest_file(str(file_path)):
                    ingested += 1
            except ValueError:
                # Ignore unsupported formats in directory ingestion.
                continue
        return ingested

    def _ingest_file(self, file_path: str) -> bool:
        extractor = self.router.route(file_path)
        records = extractor.extract(file_path)
        cleaned_records = []
        for record in records:
            cleaned = clean_text(record.get("text", ""))
            if cleaned:
                rec = dict(record)
                rec["text"] = cleaned
                cleaned_records.append(rec)

        if not cleaned_records:
            return False

        path_obj = Path(file_path)
        doc_meta = {
            "doc_id": str(uuid.uuid4()),
            "file_path": str(path_obj.resolve()),
            "file_name": path_obj.name,
            "file_type": path_obj.suffix.lower().lstrip("."),
            "ingested_at": datetime.now(timezone.utc).isoformat(),
            "metadata": {},
        }

        chunks = self.chunker.chunk(cleaned_records, doc_meta)
        if not chunks:
            return False

        start_chunk_id = self.sqlite.next_chunk_id()
        if start_chunk_id != self.faiss.count():
            raise RuntimeError("FAISS and SQLite are out of sync. Repair store before ingesting.")

        embeddings = self.embedder.encode([c["chunk_text"] for c in chunks])
        self.faiss.add_vectors(embeddings)
        self.sqlite.add_document(doc_meta, total_chunks=len(chunks))
        self.sqlite.add_chunks(chunks, start_chunk_id=start_chunk_id)
        self.faiss.save()
        return True

    def search(self, query: str, top_k: Optional[int] = None) -> List[Dict[str, Any]]:
        query_cfg = self.config.get("query", {})
        k = int(top_k or query_cfg.get("top_k", 5))
        threshold = float(query_cfg.get("score_threshold", 0.0))

        vec = self.embedder.encode([query])[0]
        hits = self.faiss.search(vec, k)
        ids = [chunk_id for chunk_id, _ in hits]
        rows = self.sqlite.get_chunks_by_ids(ids)
        return join_ranked_results(hits, rows, score_threshold=threshold)

    def stats(self) -> Dict[str, int]:
        return self.sqlite.stats()

    def close(self) -> None:
        self.sqlite.close()
