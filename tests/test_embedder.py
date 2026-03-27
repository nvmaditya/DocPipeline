from __future__ import annotations

import sys
import types

import numpy as np
import pytest

from docpipe.embedder import Embedder


def test_github_embedder_requires_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)

    embedder = Embedder(model_name="openai/text-embedding-3-small", backend="github")

    with pytest.raises(RuntimeError, match="Missing GITHUB_TOKEN"):
        embedder.encode(["hello"])


def test_github_embedder_with_mock_openai(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeEmbeddings:
        def create(self, model: str, input: list[str]):
            data = [types.SimpleNamespace(embedding=[float(len(text)), 1.0, 0.5]) for text in input]
            return types.SimpleNamespace(data=data)

    class FakeOpenAI:
        def __init__(self, base_url: str, api_key: str) -> None:
            self.base_url = base_url
            self.api_key = api_key
            self.embeddings = FakeEmbeddings()

    fake_module = types.SimpleNamespace(OpenAI=FakeOpenAI)
    monkeypatch.setitem(sys.modules, "openai", fake_module)
    monkeypatch.setenv("GITHUB_TOKEN", "test-token")

    embedder = Embedder(
        model_name="openai/text-embedding-3-small",
        backend="github",
        batch_size=2,
        normalize=True,
    )

    vectors = embedder.encode(["a", "abcd"])

    assert vectors.shape == (2, 3)
    norms = np.linalg.norm(vectors, axis=1)
    assert np.allclose(norms, np.ones_like(norms))
