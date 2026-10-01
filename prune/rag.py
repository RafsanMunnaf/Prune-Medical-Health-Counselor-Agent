"""RAG retrieval engine for Prune.

Implements semantic vector search over the seeded TCM knowledge base.
Uses OpenAI text-embedding-3-small and an in-process normalized numpy matrix
for ultra-fast cosine similarity lookups. Embeddings are cached on disk to
prevent unnecessary API calls across application restarts.
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from typing import List, Tuple

import numpy as np
from openai import OpenAI

from .knowledge import KnowledgeChunk, all_chunks


@dataclass
class RetrievedChunk:
    """A retrieved knowledge chunk accompanied by its similarity score."""
    chunk: KnowledgeChunk
    score: float


class RAGRetriever:
    """In-process semantic retrieval engine over the TCM knowledge base."""

    def __init__(
        self,
        client: OpenAI,
        embedding_model: str = "text-embedding-3-small",
        cache_dir: str = "data",
    ) -> None:
        self._client = client
        self._embedding_model = embedding_model
        self._cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)

        self._chunks: List[KnowledgeChunk] = all_chunks()
        self._matrix: np.ndarray = self._load_or_build_index()

    def _index_signature(self) -> str:
        """Compute a deterministic hash representing the current knowledge base."""
        h = hashlib.sha256()
        h.update(self._embedding_model.encode("utf-8"))
        for c in self._chunks:
            h.update(c.id.encode("utf-8"))
            h.update(c.embedding_text().encode("utf-8"))
        return h.hexdigest()[:16]

    def _cache_path(self) -> str:
        return os.path.join(
            self._cache_dir, f"embeddings_{self._index_signature()}.npz"
        )

    def _load_or_build_index(self) -> np.ndarray:
        """Load precomputed embeddings from cache or compute them in batch."""
        path = self._cache_path()
        if os.path.exists(path):
            with np.load(path) as data:
                return data["matrix"]

        texts = [c.embedding_text() for c in self._chunks]
        resp = self._client.embeddings.create(
            model=self._embedding_model, input=texts
        )
        vectors = np.array([d.embedding for d in resp.data], dtype=np.float32)

        # L2 normalize vectors so dot-product equals cosine similarity
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        vectors = vectors / norms
        np.savez_compressed(path, matrix=vectors)
        return vectors

    def _embed_query(self, query: str) -> np.ndarray:
        """Embed and normalize a single search query."""
        resp = self._client.embeddings.create(
            model=self._embedding_model, input=[query]
        )
        v = np.array(resp.data[0].embedding, dtype=np.float32)
        n = np.linalg.norm(v)
        return v / n if n else v

    def retrieve(self, query: str, k: int = 6) -> List[RetrievedChunk]:
        """Retrieve the top-k most relevant knowledge chunks for a query."""
        if not query or not query.strip():
            return []
        qv = self._embed_query(query)
        scores = self._matrix @ qv
        top_idx = np.argsort(-scores)[:k]
        return [
            RetrievedChunk(chunk=self._chunks[i], score=float(scores[i]))
            for i in top_idx
        ]

    def format_context(self, hits: List[RetrievedChunk]) -> str:
        """Format retrieved chunks for injection into the LLM prompt.

        Enforces Content Source Boundaries with source IDs for citations.
        """
        if not hits:
            return "[NO_RAG_HITS]"
        blocks = []
        for h in hits:
            blocks.append(
                f"<<source id={h.chunk.id} collection={h.chunk.collection} score={h.score:.3f}>>\n"
                f"{h.chunk.title}\n{h.chunk.text}\n<<end>>"
            )
        return "\n\n".join(blocks)


def serialise_hits(hits: List[RetrievedChunk]) -> List[Tuple[str, float]]:
    """Convert hit objects into a lightweight (id, score) list."""
    return [(h.chunk.id, h.score) for h in hits]


def write_debug_log(path: str, payload: dict) -> None:
    """Append JSON record to debug log."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")
