"""Adapter that bridges FastAPI services to the live docpipe pipeline."""

from __future__ import annotations

import copy
from dataclasses import dataclass
from pathlib import Path
import re
import uuid
from typing import Any

import yaml

from docpipe.pipeline import Pipeline


@dataclass
class AdapterDocument:
    doc_id: str
    user_id: str
    file_name: str
    file_size_bytes: int
    ingested_at: str
    file_type: str
    file_path: str


class PipelineAdapter:
    def __init__(
        self,
        base_config_path: str = "config.yaml",
        store_root: str = "store/backend_users",
        community_store_root: str = "store/community_books",
        embedding_backend_override: str | None = None,
        embedding_model_override: str | None = None,
        embedding_github_token_env_override: str | None = None,
    ) -> None:
        self.base_config_path = base_config_path
        self.store_root = Path(store_root)
        self.store_root.mkdir(parents=True, exist_ok=True)
        self.community_store_root = Path(community_store_root)
        self.community_store_root.mkdir(parents=True, exist_ok=True)
        self._base_config = self._load_base_config(base_config_path)
        self._apply_embedding_overrides(
            backend_override=embedding_backend_override,
            model_override=embedding_model_override,
            github_token_env_override=embedding_github_token_env_override,
        )
        self._pipelines: dict[str, Pipeline] = {}
        self._community_pipelines: dict[str, Pipeline] = {}

    def _load_base_config(self, config_path: str) -> dict[str, Any]:
        with open(config_path, "r", encoding="utf-8") as handle:
            return yaml.safe_load(handle) or {}

    def _apply_embedding_overrides(
        self,
        backend_override: str | None,
        model_override: str | None,
        github_token_env_override: str | None,
    ) -> None:
        if (
            backend_override is None
            and model_override is None
            and github_token_env_override is None
        ):
            return

        embedding_cfg = self._base_config.setdefault("embedding", {})

        if backend_override is not None:
            backend_value = backend_override.strip().lower()
            if backend_value not in {"local", "github"}:
                raise ValueError("embedding backend override must be one of: local, github")
            embedding_cfg["backend"] = backend_value

        if model_override is not None:
            model_value = model_override.strip()
            if not model_value:
                raise ValueError("embedding model override must not be empty")
            embedding_cfg["model"] = model_value

        if github_token_env_override is not None:
            token_env_value = github_token_env_override.strip()
            if not token_env_value:
                raise ValueError("embedding github token env override must not be empty")
            embedding_cfg["github_token_env"] = token_env_value

    def _user_dir(self, user_id: str) -> Path:
        path = self.store_root / user_id
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _user_config_path(self, user_id: str) -> Path:
        user_dir = self._user_dir(user_id)
        config_path = user_dir / "config.backend.yaml"
        if config_path.exists():
            return config_path

        cfg = copy.deepcopy(self._base_config)
        store_cfg = cfg.setdefault("store", {})
        store_cfg["faiss_path"] = str((user_dir / "faiss.index").as_posix())
        store_cfg["sqlite_path"] = str((user_dir / "metadata.db").as_posix())

        with open(config_path, "w", encoding="utf-8") as handle:
            yaml.safe_dump(cfg, handle, sort_keys=False)
        return config_path

    def _pipeline_for_user(self, user_id: str) -> Pipeline:
        pipe = self._pipelines.get(user_id)
        if pipe is not None:
            return pipe

        config_path = self._user_config_path(user_id)
        pipe = Pipeline(config=str(config_path))
        self._pipelines[user_id] = pipe
        return pipe

    def _normalize_database_id(self, database_id: str) -> str:
        normalized = re.sub(r"[^a-z0-9_-]+", "-", database_id.strip().lower())
        normalized = normalized.strip("-")
        if not normalized:
            raise ValueError("database_id must contain at least one alphanumeric character")
        return normalized

    def _community_db_dir(self, database_id: str) -> Path:
        safe_id = self._normalize_database_id(database_id)
        path = self.community_store_root / safe_id
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _community_config_path(self, database_id: str) -> Path:
        db_dir = self._community_db_dir(database_id)
        
        # Check if index builder already exported the accurate config
        book_config_path = db_dir / "config.book.yaml"
        if book_config_path.exists():
            return book_config_path
            
        config_path = db_dir / "config.community.yaml"
        if config_path.exists():
            return config_path

        cfg = copy.deepcopy(self._base_config)
        store_cfg = cfg.setdefault("store", {})
        store_cfg["faiss_path"] = str((db_dir / "faiss.index").as_posix())
        store_cfg["sqlite_path"] = str((db_dir / "metadata.db").as_posix())

        with open(config_path, "w", encoding="utf-8") as handle:
            yaml.safe_dump(cfg, handle, sort_keys=False)
        return config_path

    def _pipeline_for_community(self, database_id: str) -> Pipeline:
        safe_id = self._normalize_database_id(database_id)
        pipe = self._community_pipelines.get(safe_id)
        if pipe is not None:
            return pipe

        config_path = self._community_config_path(safe_id)
        pipe = Pipeline(config=str(config_path))
        self._community_pipelines[safe_id] = pipe
        return pipe

    def bootstrap_community_database(self, database_id: str, source_file: str) -> dict[str, Any]:
        safe_id = self._normalize_database_id(database_id)
        source_path = Path(source_file).resolve()
        if not source_path.is_file():
            raise ValueError(f"source file does not exist: {source_file}")

        pipe = self._pipeline_for_community(safe_id)
        existing = pipe.sqlite.get_document_by_file_path(str(source_path))
        if existing is None:
            ingested = pipe.ingest(str(source_path))
            if ingested < 1:
                raise ValueError(f"community ingestion failed for: {source_file}")

        stats = pipe.stats()
        return {
            "database_id": safe_id,
            "source_file": str(source_path),
            "documents": int(stats["documents"]),
            "chunks": int(stats["chunks"]),
            "faiss_path": pipe.faiss.index_path,
            "sqlite_path": pipe.sqlite.db_path,
        }

    def community_semantic_search(self, database_id: str, query: str, top_k: int) -> list[dict[str, Any]]:
        pipe = self._pipeline_for_community(database_id)
        return pipe.search(query, top_k=top_k)

    def _upload_path(self, user_id: str, file_name: str) -> Path:
        uploads_dir = self._user_dir(user_id) / "uploads"
        uploads_dir.mkdir(parents=True, exist_ok=True)
        safe_name = Path(file_name).name or "unnamed"
        unique_name = f"{uuid.uuid4()}_{safe_name}"
        return uploads_dir / unique_name

    def add_document(self, user_id: str, file_name: str, payload: bytes) -> AdapterDocument:
        target_path = self._upload_path(user_id, file_name)
        target_path.write_bytes(payload)

        pipe = self._pipeline_for_user(user_id)
        ingested = pipe.ingest(str(target_path))
        if ingested < 1:
            raise ValueError("document ingestion failed")

        row = pipe.sqlite.get_document_by_file_path(str(target_path.resolve()))
        if row is None:
            raise RuntimeError("ingested document metadata not found")

        return AdapterDocument(
            doc_id=str(row["doc_id"]),
            user_id=user_id,
            file_name=str(row["file_name"]),
            file_size_bytes=len(payload),
            ingested_at=str(row["ingested_at"]),
            file_type=str(row["file_type"]),
            file_path=str(row["file_path"]),
        )

    def list_documents(self, user_id: str) -> list[AdapterDocument]:
        pipe = self._pipeline_for_user(user_id)
        rows = pipe.sqlite.list_documents()
        docs: list[AdapterDocument] = []
        for row in rows:
            file_path = str(row.get("file_path", ""))
            file_size = Path(file_path).stat().st_size if file_path and Path(file_path).exists() else 0
            docs.append(
                AdapterDocument(
                    doc_id=str(row["doc_id"]),
                    user_id=user_id,
                    file_name=str(row["file_name"]),
                    file_size_bytes=file_size,
                    ingested_at=str(row["ingested_at"]),
                    file_type=str(row["file_type"]),
                    file_path=file_path,
                )
            )
        return docs

    def get_document(self, user_id: str, doc_id: str) -> AdapterDocument | None:
        pipe = self._pipeline_for_user(user_id)
        row = pipe.sqlite.get_document(doc_id)
        if row is None:
            return None
        file_path = str(row.get("file_path", ""))
        file_size = Path(file_path).stat().st_size if file_path and Path(file_path).exists() else 0
        return AdapterDocument(
            doc_id=str(row["doc_id"]),
            user_id=user_id,
            file_name=str(row["file_name"]),
            file_size_bytes=file_size,
            ingested_at=str(row["ingested_at"]),
            file_type=str(row["file_type"]),
            file_path=file_path,
        )

    def delete_document(self, user_id: str, doc_id: str) -> bool:
        pipe = self._pipeline_for_user(user_id)
        return pipe.sqlite.mark_document_deleted(doc_id)

    def semantic_search(
        self,
        user_id: str,
        query: str,
        top_k: int,
        database_id: str | None = None,
    ) -> list[dict[str, Any]]:
        pipe = self._pipeline_for_community(database_id) if database_id else self._pipeline_for_user(user_id)
        return pipe.search(query, top_k=top_k)

    def ask(
        self,
        user_id: str,
        query: str,
        top_k: int,
        database_id: str | None = None,
    ) -> dict[str, Any]:
        pipe = self._pipeline_for_community(database_id) if database_id else self._pipeline_for_user(user_id)
        
        # Override old community DB configs with current global LLM settings
        # so users edit ONE config.yaml file for their LLM choice.
        pipe.config["query"] = self._base_config.get("query", {})
        
        return pipe.ask(question=query, top_k=top_k)

    def get_community_topics(self, database_id: str, source_file: str) -> list[dict[str, Any]]:
        """Return cached topics or run the 3-stage extraction pipeline."""
        from docpipe.topic_extractor import extract_topics

        pipe = self._pipeline_for_community(database_id)

        # Check cache first
        cached = pipe.sqlite.get_topics()
        if cached:
            return cached

        # Gather all chunks from this database
        all_chunks = pipe.sqlite.get_all_chunks()
        if not all_chunks:
            return []

        chunk_ids = [c["chunk_id"] for c in all_chunks]
        chunk_texts = [c["chunk_text"] for c in all_chunks]

        # Get llm_model from config
        query_cfg = self._base_config.get("query", {})
        llm_model = str(query_cfg.get("llm_model", "phi3"))

        # Run 3-stage extraction
        topics = extract_topics(
            source_file=source_file,
            chunk_ids=chunk_ids,
            chunk_texts=chunk_texts,
            embed_fn=pipe.embedder.encode,
            llm_model=llm_model,
        )

        # Persist to SQLite
        topic_dicts = [
            {"topic_id": t.topic_id, "name": t.name, "chunk_ids": t.chunk_ids}
            for t in topics
        ]
        pipe.sqlite.save_topics(topic_dicts)

        return pipe.sqlite.get_topics()

    def close(self) -> None:
        for pipeline in self._pipelines.values():
            pipeline.close()
        for pipeline in self._community_pipelines.values():
            pipeline.close()
        self._pipelines.clear()
        self._community_pipelines.clear()
