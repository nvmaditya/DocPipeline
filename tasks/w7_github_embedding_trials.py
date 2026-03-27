from __future__ import annotations

import json
from pathlib import Path

from docpipe.cleaner import clean_text
from docpipe.embedder import Embedder
from docpipe.extractors import ExtractorRouter

PDF_PATH = Path(
    r"C:\Code\MinorProject\document-pipeline\store\backend_users\1d45383d-798c-4f9c-876d-a10960c1d152\uploads\2f9dfd65-c2d7-4e6f-9786-bf717c60598e_sepmunit3.pdf"
)
MODELS = [
    "openai/text-embedding-3-small",
    "openai/text-embedding-3-large",
    "openai/text-embedding-ada-002",
]


def load_sample_text(path: Path, max_chars: int = 2000) -> str:
    router = ExtractorRouter(scanned_threshold=50, ocr_engine="none", ocr_language="eng")
    extractor = router.route(str(path))
    records = extractor.extract(str(path))
    cleaned = [clean_text(row.get("text", "")) for row in records]
    text = "\n".join(chunk for chunk in cleaned if chunk).strip()
    return text[:max_chars] if len(text) > max_chars else text


def main() -> None:
    sample = load_sample_text(PDF_PATH)
    results: list[dict[str, object]] = []

    for model in MODELS:
        row: dict[str, object] = {"model": model}
        try:
            embedder = Embedder(model_name=model, backend="github", batch_size=8, normalize=True)
            vectors = embedder.encode([sample])
            row["status"] = "ok"
            row["shape"] = list(vectors.shape)
        except Exception as exc:  # noqa: BLE001
            row["status"] = "error"
            row["error"] = str(exc)
        results.append(row)

    report = {
        "pdf_path": str(PDF_PATH),
        "sample_chars": len(sample),
        "models": results,
    }
    out_path = Path("tasks/w7-github-embedding-model-trial.json")
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
