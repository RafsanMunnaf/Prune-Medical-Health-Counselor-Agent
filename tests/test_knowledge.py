"""Unit tests for Prune TCM Knowledge Base."""

import pytest
from prune.knowledge import (
    all_chunks,
    get_chunk_by_id,
    intake_questions,
)


class TestKnowledgeBase:
    def test_chunks_loaded(self):
        chunks = all_chunks()
        assert len(chunks) > 20
        for c in chunks:
            assert c.id
            assert c.collection
            assert c.title
            assert c.text
            assert c.embedding_text()

    def test_get_chunk_by_id(self):
        chunk = get_chunk_by_id("sp.headache.liver_yang")
        assert chunk is not None
        assert "Liver Yang" in chunk.title

        non_existent = get_chunk_by_id("non.existent.id")
        assert non_existent is None

    def test_intake_questions(self):
        questions = intake_questions()
        assert len(questions) == 12
        assert any(q.id == "iq.energy" for q in questions)
        assert any(q.id == "iq.tongue" for q in questions)
