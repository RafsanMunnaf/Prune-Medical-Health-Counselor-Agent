"""Prune: AI Traditional Chinese Medicine Companion & Health Intelligence Engine.

A multi-layered agentic conversational AI system for Traditional Chinese Medicine (TCM)
wellness, constitutional diagnosis, and symptom pattern differentiation.
"""

from .api import (
    api_chat,
    api_get_history,
    api_get_profile,
    api_get_state,
    api_healthcheck,
    api_new_topic,
    api_reset_session,
    get_bot,
    get_engine,
)
from .config import Settings, load_settings, make_client
from .engine import PruneEngine, Reply, TCMChatbot
from .intake import run_intake
from .knowledge import KnowledgeChunk, all_chunks, get_chunk_by_id, intake_questions
from .rag import RAGRetriever, RetrievedChunk
from .safety import DISCLAIMER, SafetyVerdict, append_disclaimer, screen_input
from .session import ConstitutionalProfile, Message, Session, SessionStore

__version__ = "1.0.0"

__all__ = [
    "PruneEngine",
    "TCMChatbot",
    "Reply",
    "Session",
    "SessionStore",
    "Message",
    "ConstitutionalProfile",
    "Settings",
    "load_settings",
    "make_client",
    "RAGRetriever",
    "RetrievedChunk",
    "KnowledgeChunk",
    "all_chunks",
    "get_chunk_by_id",
    "intake_questions",
    "screen_input",
    "append_disclaimer",
    "DISCLAIMER",
    "SafetyVerdict",
    "run_intake",
    "api_chat",
    "api_new_topic",
    "api_reset_session",
    "api_get_history",
    "api_get_state",
    "api_get_profile",
    "api_healthcheck",
    "get_engine",
    "get_bot",
    "__version__",
]
