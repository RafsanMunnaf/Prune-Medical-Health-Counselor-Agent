"""Unit tests for Prune RAG retrieval engine."""

import os
import shutil
import tempfile
import numpy as np
import pytest
from unittest.mock import MagicMock

from prune.rag import RAGRetriever, RetrievedChunk, serialise_hits
from prune.knowledge import KnowledgeChunk


class TestRAGRetriever:
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        self.mock_client = MagicMock()

        # Mock embeddings response for seed knowledge initialization
        fake_vector = [0.1] * 1536
        mock_embedding_data = [MagicMock(embedding=fake_vector) for _ in range(50)]
        self.mock_client.embeddings.create.return_value = MagicMock(data=mock_embedding_data)

    def teardown_method(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_retriever_initialization_and_cache(self):
        retriever = RAGRetriever(
            client=self.mock_client,
            embedding_model="text-embedding-3-small",
            cache_dir=self.temp_dir,
        )
        assert len(retriever._chunks) > 0
        assert isinstance(retriever._matrix, np.ndarray)

        # Verify cache file exists
        cache_files = [f for f in os.listdir(self.temp_dir) if f.endswith(".npz")]
        assert len(cache_files) == 1

    def test_format_context(self):
        retriever = RAGRetriever(
            client=self.mock_client,
            embedding_model="text-embedding-3-small",
            cache_dir=self.temp_dir,
        )
        chunk = KnowledgeChunk(
            id="test.chunk",
            collection="treatment",
            title="Test Title",
            text="Test Text Content",
        )
        hits = [RetrievedChunk(chunk=chunk, score=0.89)]
        context = retriever.format_context(hits)

        assert "<<source id=test.chunk collection=treatment score=0.890>>" in context
        assert "Test Title" in context
        assert "Test Text Content" in context
        assert "<<end>>" in context

    def test_format_context_empty(self):
        retriever = RAGRetriever(
            client=self.mock_client,
            embedding_model="text-embedding-3-small",
            cache_dir=self.temp_dir,
        )
        assert retriever.format_context([]) == "[NO_RAG_HITS]"

    def test_serialise_hits(self):
        chunk = KnowledgeChunk(
            id="test.id", collection="acupressure", title="A", text="B"
        )
        hits = [RetrievedChunk(chunk=chunk, score=0.95)]
        serialized = serialise_hits(hits)
        assert serialized == [("test.id", 0.95)]
