"""Prune — CLI Entrypoint & Backward-Compatible API Exporter.

Run interactive CLI:
    python main.py
    python main.py --premium
    python main.py --user test_user

Or run Streamlit Web UI:
    streamlit run app.py
"""

from __future__ import annotations

import sys

# Re-export key API symbols for backward compatibility
from prune import (
    PruneEngine,
    Session,
    SessionStore,
    TCMChatbot,
    api_chat,
    api_get_history,
    api_get_profile,
    api_get_state,
    api_healthcheck,
    api_new_topic,
    api_reset_session,
    get_bot,
    get_engine,
    load_settings,
    run_intake,
)
from prune.cli import main

__all__ = [
    "main",
    "api_chat",
    "api_new_topic",
    "api_reset_session",
    "api_get_history",
    "api_get_state",
    "api_get_profile",
    "api_healthcheck",
    "get_engine",
    "get_bot",
    "PruneEngine",
    "TCMChatbot",
    "Session",
    "SessionStore",
    "load_settings",
    "run_intake",
]

if __name__ == "__main__":
    raise SystemExit(main())
