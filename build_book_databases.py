"""
Bootstrap per-book vector databases from the Books/ folder.

Creates one isolated FAISS index + SQLite metadata store per book file
under store/community_books/<book-slug>/.  Uses the docpipe Pipeline
directly with a tuned config for book-length PDFs.

Usage:
    python build_book_databases.py                     # index all new books
    python build_book_databases.py --force             # re-index everything
    python build_book_databases.py --books History.pdf  # index specific book(s)

Requirements:
    Run from the repository root with the project venv activated.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

# Ensure project root is importable
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from docpipe.pipeline import Pipeline


# ---------------------------------------------------------------------------
# Configuration optimized for book-length PDFs
# ---------------------------------------------------------------------------

def _book_config(store_dir: Path, base_config_path: str = "config.yaml") -> dict[str, Any]:
    """Build a config dict tuned for book ingestion.

    Key decisions:
    - chunk_size 1024: books have dense paragraphs; larger chunks retain
      more surrounding context per vector, which improves RAG answer quality.
    - chunk_overlap 128: ~12% overlap prevents sentence cutting at boundaries.
    - recursive strategy: fast, deterministic, and works on any text length.
      Semantic chunking is slower and not needed for well-structured books.
    - flat FAISS index: exact inner-product search.  Per-book databases are
      small enough (<50k vectors) that brute-force is faster than HNSW and
      gives perfect recall.
    - local embedding (BAAI/bge-large-en-v1.5): state-of-the-art for retrieval,
      runs on CPU without API keys.
    """
    # Start from the project base config for extraction/embedding defaults
    with open(base_config_path, "r", encoding="utf-8") as f:
        base = yaml.safe_load(f) or {}

    return {
        "extraction": {
            "scanned_threshold": int(base.get("extraction", {}).get("scanned_threshold", 50)),
            "ocr_engine": "none",
            "ocr_language": "eng",
        },
        "chunking": {
            "strategy": "recursive",
            "chunk_size": 380,
            "chunk_overlap": 50,
        },
        "embedding": {
            "backend": str(base.get("embedding", {}).get("backend", "local")),
            "model": str(base.get("embedding", {}).get("model", "BAAI/bge-large-en-v1.5")),
            "batch_size": 64,
            "device": str(base.get("embedding", {}).get("device", "cpu")),
            "normalize": True,
            "github_endpoint": str(base.get("embedding", {}).get("github_endpoint", "https://models.github.ai/inference")),
            "github_token_env": str(base.get("embedding", {}).get("github_token_env", "GITHUB_TOKEN")),
        },
        "faiss": {
            "index_type": "flat",
        },
        "store": {
            "faiss_path": str((store_dir / "faiss.index").as_posix()),
            "sqlite_path": str((store_dir / "metadata.db").as_posix()),
        },
        "query": {
            "top_k": 5,
            "score_threshold": 0.0,
        },
    }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".pptx", ".xlsx", ".csv", ".html", ".htm", ".txt", ".md"}

def slugify(name: str) -> str:
    """Convert a filename stem to a safe directory slug."""
    slug = re.sub(r"[^a-z0-9_-]+", "-", name.strip().lower()).strip("-")
    return slug or "book"


def cleanup_stale_stores(output_dir: Path, valid_slugs: set[str]) -> list[str]:
    """Remove store directories for books that no longer exist in Books/.

    Returns list of removed directory names.
    """
    removed: list[str] = []
    if not output_dir.exists():
        return removed

    for child in output_dir.iterdir():
        if child.is_dir() and child.name not in valid_slugs:
            # Don't delete if it's not a book store (no faiss/metadata files)
            has_index = (child / "faiss.index").exists() or (child / "metadata.db").exists()
            has_config = (child / "config.book.yaml").exists() or (child / "config.community.yaml").exists()
            if has_index or has_config:
                import shutil
                shutil.rmtree(child, ignore_errors=True)
                removed.append(child.name)

    return removed


def discover_books(books_dir: Path, specific: list[str] | None = None) -> list[Path]:
    """Return sorted list of book files to process."""
    if not books_dir.exists():
        return []

    files = [
        p for p in books_dir.iterdir()
        if p.is_file() and p.suffix.lower() in ALLOWED_EXTENSIONS
    ]

    if specific:
        names_lower = {n.lower() for n in specific}
        files = [f for f in files if f.name.lower() in names_lower]

    return sorted(files, key=lambda p: p.name.lower())


def format_duration(seconds: float) -> str:
    """Human-readable duration string."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    minutes = int(seconds // 60)
    secs = seconds % 60
    return f"{minutes}m {secs:.0f}s"


# ---------------------------------------------------------------------------
# Core indexing logic
# ---------------------------------------------------------------------------

def index_book(
    source_file: Path,
    community_store_root: Path,
    base_config_path: str,
    force: bool = False,
) -> dict[str, Any]:
    """Index a single book file into its own vector database.

    Returns a summary dict with stats.
    """
    db_id = slugify(source_file.stem)
    store_dir = community_store_root / db_id
    store_dir.mkdir(parents=True, exist_ok=True)

    faiss_path = store_dir / "faiss.index"
    sqlite_path = store_dir / "metadata.db"

    # Skip if already indexed (unless --force)
    if not force and faiss_path.exists() and sqlite_path.exists():
        print(f"  ⏭  Already indexed — skipping (use --force to rebuild)")
        # Read existing stats
        cfg = _book_config(store_dir, base_config_path)
        cfg_path = store_dir / "config.book.yaml"
        cfg_path.write_text(yaml.safe_dump(cfg, sort_keys=False), encoding="utf-8")
        pipe = Pipeline(config=str(cfg_path))
        try:
            stats = pipe.stats()
            return {
                "database_id": db_id,
                "title": source_file.stem,
                "source_file": str(source_file.resolve()),
                "documents": stats["documents"],
                "chunks": stats["chunks"],
                "faiss_path": str(faiss_path),
                "sqlite_path": str(sqlite_path),
                "status": "skipped",
            }
        finally:
            pipe.close()

    # Wipe existing store for clean rebuild
    if force:
        for f in [faiss_path, sqlite_path]:
            if f.exists():
                f.unlink()

    # Generate config and write to store dir
    cfg = _book_config(store_dir, base_config_path)
    cfg_path = store_dir / "config.book.yaml"
    cfg_path.write_text(yaml.safe_dump(cfg, sort_keys=False), encoding="utf-8")

    # Run the pipeline
    pipe = Pipeline(config=str(cfg_path))
    try:
        t0 = time.perf_counter()
        ingested = pipe.ingest(str(source_file))
        elapsed = time.perf_counter() - t0

        if ingested < 1:
            raise RuntimeError(f"Ingestion produced 0 documents for {source_file.name}")

        stats = pipe.stats()
        print(f"  ✅ {stats['chunks']} chunks, {stats['documents']} doc(s) — {format_duration(elapsed)}")

        return {
            "database_id": db_id,
            "title": source_file.stem,
            "source_file": str(source_file.resolve()),
            "documents": stats["documents"],
            "chunks": stats["chunks"],
            "faiss_path": str(faiss_path),
            "sqlite_path": str(sqlite_path),
            "status": "indexed",
            "elapsed_seconds": round(elapsed, 2),
        }
    finally:
        pipe.close()


# ---------------------------------------------------------------------------
# Manifest
# ---------------------------------------------------------------------------

def write_manifest(records: list[dict[str, Any]], manifest_path: Path) -> None:
    """Write the community manifest.json for the backend list_databases() cache."""
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "databases": [
            {
                "database_id": r["database_id"],
                "title": r["title"],
                "source_file": r["source_file"],
                "documents": r["documents"],
                "chunks": r["chunks"],
                "faiss_path": r["faiss_path"],
                "sqlite_path": r["sqlite_path"],
            }
            for r in records
        ],
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(payload, indent=2, ensure_ascii=True), encoding="utf-8")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build per-book vector databases from the Books/ folder.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python build_book_databases.py                       # index all new books
  python build_book_databases.py --force               # rebuild all
  python build_book_databases.py --books Physics.pdf   # index one specific book
  python build_book_databases.py --books Physics.pdf History.pdf  # multiple
        """,
    )
    parser.add_argument(
        "--books-dir", default="Books",
        help="Path to the folder containing book files (default: Books)",
    )
    parser.add_argument(
        "--output-dir", default="store/community_books",
        help="Output root for per-book FAISS/SQLite stores (default: store/community_books)",
    )
    parser.add_argument(
        "--config", default="config.yaml",
        help="Path to base docpipe config for embedding defaults (default: config.yaml)",
    )
    parser.add_argument(
        "--force", action="store_true",
        help="Re-index all books even if indexes already exist",
    )
    parser.add_argument(
        "--books", nargs="+", default=None,
        help="Specific book filename(s) to index (e.g. Physics.pdf)",
    )
    return parser.parse_args(argv)


def _preflight_check(cfg: dict[str, Any]) -> None:
    """Verify embedding backend is reachable before starting a long indexing job."""
    emb = cfg.get("embedding", {})
    backend = str(emb.get("backend", "local"))
    token_env = str(emb.get("github_token_env", "OLLAMA_API_KEY"))
    endpoint = str(emb.get("github_endpoint", "http://localhost:11434/v1"))

    if backend == "github":
        # Auto-set dummy token for Ollama if not already set
        if not os.environ.get(token_env):
            os.environ[token_env] = "ollama"
            print(f"  ℹ  {token_env} not set — defaulting to 'ollama' (ok for local Ollama)")

        # Check Ollama is reachable
        import urllib.request, urllib.error
        health_url = endpoint.rstrip("/").replace("/v1", "") + "/api/tags"
        try:
            urllib.request.urlopen(health_url, timeout=3)
            print(f"  ✅ Ollama reachable at {endpoint}")
        except Exception as exc:
            raise RuntimeError(
                f"Cannot reach Ollama at {endpoint}.\n"
                f"  Start Ollama with: ollama serve\n"
                f"  Then re-run this script.\n  Detail: {exc}"
            )


def main() -> int:
    args = parse_args()
    books_dir = Path(args.books_dir)
    output_dir = Path(args.output_dir)

    print("=" * 60)
    print("  Book → Vector Database Builder")
    print("=" * 60)
    print(f"  Books dir   : {books_dir.resolve()}")
    print(f"  Output dir  : {output_dir.resolve()}")
    print(f"  Base config : {args.config}")
    print(f"  Force       : {args.force}")
    print()

    # Load base config and run preflight checks
    with open(args.config, "r", encoding="utf-8") as f:
        base_cfg = yaml.safe_load(f) or {}
    try:
        _preflight_check(base_cfg)
    except RuntimeError as exc:
        print(f"\n❌ Preflight failed: {exc}")
        return 1
    print()

    book_files = discover_books(books_dir, args.books)

    if not book_files:
        print("⚠  No book files found.")
        return 1

    print(f"Found {len(book_files)} book(s) to process:\n")
    for bf in book_files:
        print(f"  • {bf.name}  ({bf.stat().st_size / 1024 / 1024:.1f} MB)")
    print()

    total_t0 = time.perf_counter()
    records: list[dict[str, Any]] = []
    errors: list[str] = []

    for i, book_file in enumerate(book_files, 1):
        print(f"[{i}/{len(book_files)}] {book_file.name}")
        try:
            record = index_book(
                source_file=book_file,
                community_store_root=output_dir,
                base_config_path=args.config,
                force=args.force,
            )
            records.append(record)
        except Exception as exc:
            msg = f"  ❌ FAILED: {exc}"
            print(msg)
            errors.append(f"{book_file.name}: {exc}")

    total_elapsed = time.perf_counter() - total_t0

    # Cleanup stale stores for books that were removed from Books/
    valid_slugs = {slugify(bf.stem) for bf in book_files}
    removed = cleanup_stale_stores(output_dir, valid_slugs)
    if removed:
        print(f"\n🧹 Cleaned up {len(removed)} stale store(s): {', '.join(removed)}")

    # Write manifest for the backend API cache
    if records:
        manifest_path = output_dir / "manifest.json"
        write_manifest(records, manifest_path)
        print(f"\n📄 Manifest written: {manifest_path}")

    # Summary
    print("\n" + "=" * 60)
    print("  Summary")
    print("=" * 60)
    indexed = [r for r in records if r.get("status") == "indexed"]
    skipped = [r for r in records if r.get("status") == "skipped"]
    total_chunks = sum(r["chunks"] for r in records)

    print(f"  Indexed : {len(indexed)}")
    print(f"  Skipped : {len(skipped)}")
    print(f"  Errors  : {len(errors)}")
    print(f"  Total   : {len(records)} database(s), {total_chunks} chunks")
    print(f"  Time    : {format_duration(total_elapsed)}")

    if errors:
        print(f"\n⚠  Errors:")
        for e in errors:
            print(f"    • {e}")

    print()
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
