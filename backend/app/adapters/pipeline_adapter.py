"""Adapter that bridges FastAPI services to the live docpipe pipeline."""

from __future__ import annotations

import copy
from dataclasses import dataclass
from pathlib import Path
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
    ) -> None:
        self.base_config_path = base_config_path
        self.store_root = Path(store_root)
        self.store_root.mkdir(parents=True, exist_ok=True)
        self._base_config = self._load_base_config(base_config_path)
        self._pipelines: dict[str, Pipeline] = {}

    def _load_base_config(self, config_path: str) -> dict[str, Any]:
        with open(config_path, "r", encoding="utf-8") as handle:
            return yaml.safe_load(handle) or {}

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

    def semantic_search(self, user_id: str, query: str, top_k: int) -> list[dict[str, Any]]:
        pipe = self._pipeline_for_user(user_id)
        return pipe.search(query, top_k=top_k)

    def close(self) -> None:
        for pipeline in self._pipelines.values():
            pipeline.close()
        self._pipelines.clear()
