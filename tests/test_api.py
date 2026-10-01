"""Unit tests for Prune functional API."""

import pytest
from unittest.mock import patch, MagicMock

from prune.api import (
    api_get_state,
    api_new_topic,
    api_reset_session,
    api_healthcheck,
)
from prune.session import Session


class TestFunctionalAPI:
    @patch("prune.api.get_engine")
    def test_api_healthcheck(self, mock_get_engine):
        mock_engine = MagicMock()
        mock_engine.settings.chat_model = "gpt-4o"
        mock_engine.settings.embedding_model = "text-embedding-3-small"
        mock_engine.retriever._chunks = ["c1", "c2"]
        mock_get_engine.return_value = mock_engine

        hc = api_healthcheck()
        assert hc["status"] == "healthy"
        assert hc["chat_model"] == "gpt-4o"
        assert hc["chunks_loaded"] == 2

    @patch("prune.api.get_engine")
    def test_api_reset_session(self, mock_get_engine):
        mock_engine = MagicMock()
        mock_get_engine.return_value = mock_engine

        res = api_reset_session("test_user", premium=True)
        assert res["ok"] is True
        mock_engine.sessions.save.assert_called_once()
