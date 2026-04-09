from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from .chunkers import RecursiveChunker, SemanticChunker
from .cleaner import clean_text
from .embedder import Embedder
from .extractors import ExtractorRouter
from .query import build_rag_prompt, collect_sources, join_ranked_results
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
            backend=str(embedding_cfg.get("backend", "local")),
            github_endpoint=str(embedding_cfg.get("github_endpoint", "https://models.github.ai/inference")),
            github_token_env=str(embedding_cfg.get("github_token_env", "GITHUB_TOKEN")),
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

    def ask(
        self,
        question: str,
        top_k: Optional[int] = None,
        llm_backend: Optional[str] = None,
        llm_model: Optional[str] = None,
        llm_client: Any = None,
    ) -> Dict[str, Any]:
        query_cfg = self.config.get("query", {})
        backend = str(llm_backend or query_cfg.get("llm_backend", "github")).lower()
        model = str(llm_model or query_cfg.get("llm_model", "openai/gpt-5"))
        github_endpoint = str(query_cfg.get("github_endpoint", "https://models.github.ai/inference"))
        github_token_env = str(query_cfg.get("github_token_env", "GITHUB_TOKEN"))

        ranked = self.search(question, top_k=top_k)
        if not ranked:
            return {"response": "I do not have enough information in the indexed documents.", "sources": []}

        prompt = build_rag_prompt(question, ranked)
        sources = collect_sources(ranked)

        if str(query_cfg.get("use_llm", "true")).lower() == "false":
            return {
                "response": "I found relevant documents but LLM processing is disabled locally. Please review the sources below.",
                "sources": sources,
            }

        if llm_client is not None:
            response = llm_client(prompt, model)
            return {"response": response, "sources": sources}

        if backend == "groq":
            groq_api_key = str(query_cfg.get("groq_api_key", ""))
            response = self._ask_with_groq(prompt=prompt, model=model, api_key=groq_api_key)
            return {"response": response, "sources": sources}

        if backend == "gemini":
            gemini_api_key = str(query_cfg.get("gemini_api_key", ""))
            response = self._ask_with_gemini(prompt=prompt, model=model, api_key=gemini_api_key)
            return {"response": response, "sources": sources}

        if backend == "github":
            response = self._ask_with_github_models(prompt=prompt, model=model, endpoint=github_endpoint, token_env=github_token_env)
            return {"response": response, "sources": sources}

        if backend == "ollama":
            try:
                import ollama
            except Exception as exc:
                raise RuntimeError("Ollama client not installed. Install `ollama` package to use --rag.") from exc

            result = ollama.chat(
                model=model,
                messages=[
                    {"role": "system", "content": "Answer with citations and stay grounded in provided context."},
                    {"role": "user", "content": prompt},
                ],
            )
            response = result.get("message", {}).get("content", "")

        return {"response": response, "sources": sources}

    def _ask_with_groq(self, prompt: str, model: str, api_key: str) -> str:
        if not api_key or api_key == "PASTE_YOUR_GROQ_API_KEY_HERE":
            raise RuntimeError("Groq API key not configured. Set groq_api_key in config.yaml.")

        from openai import OpenAI

        client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=api_key)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a retrieval assistant. Stay grounded in provided context and cite sources."},
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message.content or ""

    def _ask_with_gemini(self, prompt: str, model: str, api_key: str) -> str:
        if not api_key or api_key == "PASTE_YOUR_GEMINI_API_KEY_HERE":
            raise RuntimeError("Gemini API key not configured. Set gemini_api_key in config.yaml.")

        try:
            from google import genai
        except Exception as exc:
            raise RuntimeError("google-genai package is required. Run: pip install google-genai") from exc

        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config={
                "system_instruction": "You are a retrieval assistant. Stay grounded in provided context and cite sources.",
            },
        )
        return response.text or ""

    def _ask_with_github_models(self, prompt: str, model: str, endpoint: str, token_env: str) -> str:
        token = os.getenv(token_env)
        if not token:
            if "localhost" in endpoint or "127.0.0.1" in endpoint:
                token = "ollama"
            else:
                raise RuntimeError(f"Missing {token_env}. Set this environment variable to use the chat API.")

        try:
            from openai import OpenAI
        except Exception as exc:
            raise RuntimeError("OpenAI SDK is required for GitHub chat API. Install `openai`.") from exc

        client = OpenAI(base_url=endpoint, api_key=token)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a retrieval assistant. Stay grounded in provided context and cite sources."},
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message.content or ""

    def stats(self) -> Dict[str, int]:
        return self.sqlite.stats()

    def close(self) -> None:
        self.sqlite.close()
