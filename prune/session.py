"""Session & constitutional profile persistence for Prune.

Tracks multi-turn conversation state on disk as JSON.
Supports state machine tracking: idle -> triage -> synthesis / education,
and constitutional profile store.
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional


@dataclass
class Message:
    """A single turn in the conversation history."""
    role: str                       # "user" | "assistant" | "system"
    content: str
    mode: Optional[str] = None      # "triage" | "synthesis" | "education" | "emergency" | "refused" | None
    sources: List[str] = field(default_factory=list)
    flagged: Optional[str] = None   # "emergency" | "drug" | None
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


@dataclass
class ConstitutionalProfile:
    """The user's TCM constitutional pattern assessment."""
    completed: bool = False
    answers: Dict[str, str] = field(default_factory=dict)
    pattern_summary: Optional[str] = None
    completed_at: Optional[str] = None


@dataclass
class Session:
    """Full session state for a user, including conversation state machine."""
    user_id: str
    is_premium: bool = False
    profile: ConstitutionalProfile = field(default_factory=ConstitutionalProfile)
    history: List[Message] = field(default_factory=list)

    # ── State-machine tracking fields ─────────────────────────────────────
    conv_state: str = "idle"       # "idle" | "triage" | "synthesis" | "education"
    triage_turns: int = 0          # Number of Q&A exchanges in TRIAGE phase
    current_complaint: str = ""    # Original user complaint

    def add(self, msg: Message) -> None:
        """Append a message to history."""
        self.history.append(msg)

    def recent(self, n: int = 12) -> List[Message]:
        """Return the most recent n messages."""
        return self.history[-n:]

    def reset_conversation(self) -> None:
        """Start a fresh topic without wiping constitutional profile or prior history."""
        self.conv_state = "idle"
        self.triage_turns = 0
        self.current_complaint = ""


class SessionStore:
    """Local JSON-file persistence for user sessions."""

    def __init__(self, data_dir: str = "data") -> None:
        self._dir = os.path.join(data_dir, "sessions")
        os.makedirs(self._dir, exist_ok=True)

    def _path(self, user_id: str) -> str:
        safe = "".join(c for c in user_id if c.isalnum() or c in ("-", "_"))
        return os.path.join(self._dir, f"{safe or 'anon'}.json")

    def load(self, user_id: str) -> Session:
        """Load session by user_id or create a new one."""
        path = self._path(user_id)
        if not os.path.exists(path):
            return Session(user_id=user_id)
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        profile = ConstitutionalProfile(**raw.get("profile", {}))
        history = [Message(**m) for m in raw.get("history", [])]
        return Session(
            user_id=raw.get("user_id", user_id),
            is_premium=raw.get("is_premium", False),
            profile=profile,
            history=history,
            conv_state=raw.get("conv_state", "idle"),
            triage_turns=raw.get("triage_turns", 0),
            current_complaint=raw.get("current_complaint", ""),
        )

    def save(self, session: Session) -> None:
        """Persist session atomically to disk."""
        path = self._path(session.user_id)
        payload = {
            "user_id": session.user_id,
            "is_premium": session.is_premium,
            "profile": asdict(session.profile),
            "history": [asdict(m) for m in session.history],
            "conv_state": session.conv_state,
            "triage_turns": session.triage_turns,
            "current_complaint": session.current_complaint,
        }
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        os.replace(tmp, path)
