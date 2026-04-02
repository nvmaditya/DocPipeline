"""Community database bootstrap and listing service."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
from typing import Any

from ..adapters.pipeline_adapter import PipelineAdapter


@dataclass
class CommunityDatabaseRecord:
    database_id: str
    title: str
    source_file: str
    documents: int
    chunks: int
    faiss_path: str
    sqlite_path: str


class CommunityService:
    def __init__(
        self,
        pipeline_adapter: PipelineAdapter,
        books_root: str = "Books",
        manifest_name: str = "manifest.json",
    ) -> None:
        self._pipeline_adapter = pipeline_adapter
        self._books_root = Path(books_root)
        self._manifest_path = self._pipeline_adapter.community_store_root / manifest_name

    def _book_files(self) -> list[Path]:
        if not self._books_root.exists():
            return []

        allowed = {".pdf", ".docx", ".pptx", ".xlsx", ".csv", ".html", ".htm", ".txt", ".md"}
        files = [
            p
            for p in self._books_root.iterdir()
            if p.is_file() and p.suffix.lower() in allowed
        ]
        return sorted(files, key=lambda p: p.name.lower())

    def _database_id(self, file_path: Path) -> str:
        stem = re.sub(r"[^a-z0-9_-]+", "-", file_path.stem.strip().lower())
        stem = stem.strip("-")
        return stem or "book"

    def bootstrap_indexes(self) -> list[CommunityDatabaseRecord]:
        records: list[CommunityDatabaseRecord] = []
        for source_file in self._book_files():
            db_id = self._database_id(source_file)
            stats = self._pipeline_adapter.bootstrap_community_database(
                database_id=db_id,
                source_file=str(source_file),
            )
            records.append(
                CommunityDatabaseRecord(
                    database_id=db_id,
                    title=source_file.stem,
                    source_file=str(source_file.resolve()),
                    documents=int(stats["documents"]),
                    chunks=int(stats["chunks"]),
                    faiss_path=str(stats["faiss_path"]),
                    sqlite_path=str(stats["sqlite_path"]),
                )
            )

        self._write_manifest(records)
        return records

    def list_databases(self) -> list[CommunityDatabaseRecord]:
        if self._manifest_path.exists():
            return self._read_manifest()
        return self.bootstrap_indexes()

    def _read_manifest(self) -> list[CommunityDatabaseRecord]:
        try:
            data: dict[str, Any] = json.loads(
                self._manifest_path.read_text(encoding="utf-8")
            )
        except (json.JSONDecodeError, OSError):
            return self.bootstrap_indexes()

        records: list[CommunityDatabaseRecord] = []
        for entry in data.get("databases", []):
            # Skip entries whose FAISS index no longer exists (book was removed)
            faiss_path = str(entry.get("faiss_path", ""))
            if faiss_path and not Path(faiss_path).exists():
                continue
            records.append(
                CommunityDatabaseRecord(
                    database_id=str(entry["database_id"]),
                    title=str(entry["title"]),
                    source_file=str(entry["source_file"]),
                    documents=int(entry["documents"]),
                    chunks=int(entry["chunks"]),
                    faiss_path=faiss_path,
                    sqlite_path=str(entry["sqlite_path"]),
                )
            )
        return records

    def _build_fallback_module_content(self, topic: str, extractor_failure: str | None) -> str:
        """Return deterministic local content when the web extractor cannot provide output."""
        lines = [
            f"Topic: {topic}",
            "",
            "This module was created with local fallback content because external enrichment",
            "did not complete successfully in time.",
            "",
            "Suggested learning outline:",
            "1. Define the topic and key terms.",
            "2. Identify core concepts and their relationships.",
            "3. Collect examples, applications, and common misconceptions.",
            "4. Summarize practical takeaways and next study steps.",
        ]
        if extractor_failure:
            lines.extend(["", "Extractor diagnostics:", extractor_failure[:2000]])
        return "\n".join(lines).strip() + "\n"


    def create_module(self, topic: str) -> CommunityDatabaseRecord:
        import subprocess
        import sys

        web_extractor_dir = Path("web_extractor").resolve()
        safe_topic = "".join(c for c in topic if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_topic = safe_topic.replace(' ', '_')[:50]
        timeout_seconds = int(os.getenv("BACKEND_WEB_EXTRACTOR_TIMEOUT_SECONDS", "35"))
        extractor_failure: str | None = None

        try:
            subprocess.run(
                [sys.executable, "main.py", topic],
                cwd=str(web_extractor_dir),
                check=True,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
            )
        except subprocess.TimeoutExpired as e:
            extractor_failure = (
                f"web_extractor timed out after {timeout_seconds}s for topic '{topic}'."
            )
        except subprocess.CalledProcessError as e:
            extractor_failure = (
                "web_extractor subprocess failed. "
                f"stderr/stdout: {(e.stderr or e.stdout or '').strip()}"
            )
        except OSError as e:
            extractor_failure = f"web_extractor process could not be started: {e}"

        output_dir = web_extractor_dir / "outputs" / safe_topic
        ai_content_path = output_dir / "ai_generated_content.txt"
        summary_path = output_dir / "summary.txt"

        target_content_path = ai_content_path if ai_content_path.exists() else summary_path
        if target_content_path.exists():
            content = target_content_path.read_text(encoding="utf-8")
            if not content.strip():
                content = self._build_fallback_module_content(topic, extractor_failure)
        else:
            content = self._build_fallback_module_content(topic, extractor_failure)

        book_path = self._books_root / f"{safe_topic}.txt"
        self._books_root.mkdir(parents=True, exist_ok=True)
        book_path.write_text(content, encoding="utf-8")

        db_id = self._database_id(book_path)
        stats = self._pipeline_adapter.bootstrap_community_database(
            database_id=db_id,
            source_file=str(book_path.resolve()),
        )

        record = CommunityDatabaseRecord(
            database_id=db_id,
            title=book_path.stem,
            source_file=str(book_path.resolve()),
            documents=int(stats["documents"]),
            chunks=int(stats["chunks"]),
            faiss_path=str(stats["faiss_path"]),
            sqlite_path=str(stats["sqlite_path"]),
        )

        records = self.list_databases()
        updated = []
        found = False
        for r in records:
            if r.database_id == record.database_id:
                updated.append(record)
                found = True
            else:
                updated.append(r)
        if not found:
            updated.append(record)

        self._write_manifest(updated)
        return record

    def _write_manifest(self, records: list[CommunityDatabaseRecord]) -> None:
        payload: dict[str, Any] = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "databases": [
                {
                    "database_id": record.database_id,
                    "title": record.title,
                    "source_file": record.source_file,
                    "documents": record.documents,
                    "chunks": record.chunks,
                    "faiss_path": record.faiss_path,
                    "sqlite_path": record.sqlite_path,
                }
                for record in records
            ],
        }

        self._manifest_path.parent.mkdir(parents=True, exist_ok=True)
        self._manifest_path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=True),
            encoding="utf-8",
        )
