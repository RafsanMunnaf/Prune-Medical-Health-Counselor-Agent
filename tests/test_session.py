"""Unit tests for Prune Session and persistence."""

import os
import shutil
import tempfile
import pytest

from prune.session import (
    ConstitutionalProfile,
    Message,
    Session,
    SessionStore,
)


class TestSessionStore:
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        self.store = SessionStore(self.temp_dir)

    def teardown_method(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_new_session_defaults(self):
        session = self.store.load("user_123")
        assert session.user_id == "user_123"
        assert not session.is_premium
        assert session.conv_state == "idle"
        assert len(session.history) == 0

    def test_save_and_reload_session(self):
        session = Session(user_id="user_test", is_premium=True)
        session.conv_state = "triage"
        session.triage_turns = 2
        session.current_complaint = "Stomach bloating after eating"
        session.add(Message(role="user", content="Hello"))
        session.add(Message(role="assistant", content="Where is the pain located?", mode="triage"))
        session.profile = ConstitutionalProfile(
            completed=True,
            pattern_summary="Spleen Qi Deficiency",
        )

        self.store.save(session)

        reloaded = self.store.load("user_test")
        assert reloaded.user_id == "user_test"
        assert reloaded.is_premium
        assert reloaded.conv_state == "triage"
        assert reloaded.triage_turns == 2
        assert reloaded.current_complaint == "Stomach bloating after eating"
        assert len(reloaded.history) == 2
        assert reloaded.profile.completed
        assert reloaded.profile.pattern_summary == "Spleen Qi Deficiency"

    def test_reset_conversation(self):
        session = Session(
            user_id="user_reset",
            conv_state="synthesis",
            triage_turns=3,
            current_complaint="Insomnia",
        )
        session.reset_conversation()
        assert session.conv_state == "idle"
        assert session.triage_turns == 0
        assert session.current_complaint == ""
