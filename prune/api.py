"""Functional API Layer for Prune.

Exposes clean, JSON-serializable functions suitable for FastAPI, Flask,
Streamlit, or background worker integrations. Reuses a singleton PruneEngine
instance across requests to preserve in-memory embeddings caches.
"""

from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict, Optional

from .engine import PruneEngine, Reply
from .session import Message, Session

_ENGINE_SINGLETON: Optional[PruneEngine] = None


def get_engine() -> PruneEngine:
    """Return the shared PruneEngine instance, initializing on first call."""
    global _ENGINE_SINGLETON
    if _ENGINE_SINGLETON is None:
        _ENGINE_SINGLETON = PruneEngine()
    return _ENGINE_SINGLETON


# Backwards compatibility alias
get_bot = get_engine


def _load_session(user_id: str, premium: bool = False) -> Session:
    """Load (or create) a session and apply the premium flag."""
    engine = get_engine()
    session = engine.sessions.load(user_id)
    if premium:
        session.is_premium = True
    return session


def _reply_to_dict(reply: Reply) -> Dict[str, Any]:
    """Convert a Reply dataclass into a JSON-serializable dict."""
    return {
        "reply": reply.text,
        "mode": reply.mode,
        "sources": reply.sources,
        "flagged": reply.flagged,
    }


def _message_to_dict(m: Message) -> Dict[str, Any]:
    """Convert a Message dataclass into a JSON-serializable dict."""
    return {
        "role": m.role,
        "content": m.content,
        "mode": m.mode,
        "sources": m.sources,
        "flagged": m.flagged,
        "timestamp": m.timestamp,
    }


def api_chat(user_id: str, message: str, premium: bool = False) -> Dict[str, Any]:
    """Send one message; receive one structured response.

    Returns:
        {
          "reply":   str,
          "mode":    "triage" | "synthesis" | "education" | "emergency" | "refused",
          "sources": list[str],
          "flagged": None | "emergency" | "drug",
          "state":   "idle" | "triage" | "synthesis" | "education",
        }
    """
    engine = get_engine()
    session = _load_session(user_id, premium)
    reply = engine.respond(session, message)
    engine.sessions.save(session)
    out = _reply_to_dict(reply)
    out["state"] = session.conv_state
    return out


def api_new_topic(user_id: str, premium: bool = False) -> Dict[str, Any]:
    """Start a fresh topic while preserving constitutional profile and history."""
    engine = get_engine()
    session = _load_session(user_id, premium)
    session.reset_conversation()
    engine.sessions.save(session)
    return {"ok": True, "state": session.conv_state}


def api_reset_session(user_id: str, premium: bool = False) -> Dict[str, Any]:
    """Reset the entire session (history + profile + state)."""
    engine = get_engine()
    session = Session(user_id=user_id, is_premium=premium)
    engine.sessions.save(session)
    return {"ok": True}


def api_get_history(user_id: str, n: int = 20) -> Dict[str, Any]:
    """Return recent conversation turns for a user."""
    engine = get_engine()
    session = engine.sessions.load(user_id)
    return {
        "user_id": user_id,
        "state": session.conv_state,
        "is_premium": session.is_premium,
        "messages": [_message_to_dict(m) for m in session.recent(n)],
    }


def api_get_state(user_id: str) -> Dict[str, Any]:
    """Return current session state metadata for UI badges."""
    engine = get_engine()
    session = engine.sessions.load(user_id)
    return {
        "user_id": user_id,
        "state": session.conv_state,
        "triage_turns": session.triage_turns,
        "current_complaint": session.current_complaint,
        "is_premium": session.is_premium,
        "profile_completed": session.profile.completed,
    }


def api_get_profile(user_id: str) -> Dict[str, Any]:
    """Return constitutional intake profile details."""
    engine = get_engine()
    session = engine.sessions.load(user_id)
    return asdict(session.profile)


def api_healthcheck() -> Dict[str, Any]:
    """Return system health check status."""
    try:
        engine = get_engine()
        return {
            "status": "healthy",
            "chat_model": engine.settings.chat_model,
            "embedding_model": engine.settings.embedding_model,
            "chunks_loaded": len(engine.retriever._chunks),
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
