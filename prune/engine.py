"""Core Agentic Conversational Engine for Prune.

Implements a phase-gated state machine:
  idle  ──[acute/chronic]──► triage  ──[READY_FOR_RAG signal]──► synthesis
  idle  ──[education]──────────────────────────────────────────► education
  synthesis / education ── follow-up turns stay in active state

Key Architecture Principles:
- Layer 0 (Safety Interception): Hard-coded circuit breakers for emergency and drug dosage.
- Layer 1 (Conversational State Machine): Gated multi-turn assessment without premature advice.
- Layer 2 (RAG Retrieval Engine): Context source enforcement with transparent citations.
- Layer 3 (Constitutional Personalization): Contextual awareness from intake profile.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List, Optional

from openai import OpenAI

from .config import Settings, load_settings, make_client
from .rag import RAGRetriever, serialise_hits, write_debug_log
from .safety import (
    SafetyVerdict,
    append_disclaimer,
    screen_input,
)
from .session import Message, Session, SessionStore

# ── Modes & Signals ────────────────────────────────────────────────────────
ACUTE = "acute"
CHRONIC = "chronic"
EDUCATION = "education"
_READY_SIGNAL = "[READY_FOR_RAG]"

# ── Prompts ────────────────────────────────────────────────────────────────
_ROUTER_SYSTEM = (
    "You are a classifier for Prune, a TCM wellness chatbot. "
    "Classify the user's message into exactly one of three modes.\n\n"
    "ACUTE — the user describes a personal symptom or complaint they are "
    "experiencing right now or recently. Any first-person mention of pain, "
    "discomfort, fatigue, illness, or physical/emotional problem = ACUTE. "
    "Examples: 'I have stomach pain', 'my back hurts', 'I feel tired', "
    "'I've been getting headaches', 'I can't sleep', 'feeling anxious'.\n\n"
    "CHRONIC — the user describes a long-standing personal condition "
    "(weeks, months, years) or an ongoing wellness goal. "
    "Examples: 'I've had IBS for 2 years', 'I want to improve my energy', "
    "'I have recurring migraines', 'ongoing lower back weakness'.\n\n"
    "EDUCATION — the user asks a pure theory or curiosity question with "
    "NO personal symptom. Only classify as EDUCATION when the message "
    "contains no first-person complaint. "
    "Examples: 'What is Qi?', 'How does the organ clock work?', "
    "'explain Liver Yang rising', 'what are the Five Elements?'.\n\n"
    "IMPORTANT: When in doubt between ACUTE and EDUCATION, always choose ACUTE. "
    "Any message mentioning personal pain, discomfort, or symptoms is ACUTE.\n\n"
    "Reply with exactly one word: ACUTE, CHRONIC, or EDUCATION."
)

_TRIAGE_SYSTEM = """\
You are Prune — a warm, experienced Traditional Chinese Medicine companion conducting
an initial assessment. Think like a skilled practitioner building a complete holistic picture
before drawing any conclusions.

━━━ PHASE: TRIAGE — INTAKE ONLY ━━━

Your SOLE task is to gather sufficient clinical information through focused,
one-at-a-time questions. You are strictly forbidden from providing any guidance,
pattern names, or interpretations during this phase.

ABSOLUTE RULES:
• DO NOT provide TCM pattern names, diagnoses, acupressure points, herbal
  suggestions, dietary protocols, or any form of health guidance.
• DO NOT reference or generate content from any knowledge database.
• Ask EXACTLY ONE question per response — never multiple at once.

QUESTION BANK — draw from these dimensions. Pick the most diagnostically
useful one given what the user has already told you:

  SYMPTOM CHARACTER
    • Location — where exactly? does it radiate or spread anywhere?
    • Quality  — sharp, dull, burning, aching, throbbing, heavy, distending?
    • Severity — mild/moderate/severe, on a scale of 1–10?
    • Timing   — constant or comes and goes? worse at any particular time of day?
    • Onset    — sudden or gradual? how long has it been present?

  TCM DIFFERENTIATORS (critical — ask at least 2 of these)
    • Temperature response — does warmth relieve it? does cold make it worse
      (or vice versa)? do you prefer warm or cold drinks?
    • Appetite & digestion — how is your appetite? any bloating, loose stools,
      constipation, or nausea alongside this?
    • Energy & fatigue     — how is your overall energy? do you feel more tired
      than usual?
    • Sleep                — any difficulty sleeping, waking in the night,
      or vivid dreams?
    • Emotional state      — any noticeable irritability, anxiety, low mood,
      or worry alongside this?
    • Urination/bowel      — any changes in urine colour/frequency or stool
      consistency?

  MODIFYING FACTORS
    • What makes it noticeably better?
    • What makes it noticeably worse (stress, food, weather, movement, rest)?
    • Any associated symptoms — what else is happening at the same time?

READINESS RULES:
• For a SIMPLE, well-localised complaint (e.g. headache with clear character):
  collect location, quality, onset, 1 TCM differentiator → emit [READY_FOR_RAG]
  after 3–4 exchanges.
• For a VAGUE or systemic complaint (e.g. fatigue, anxiety, general unwellness):
  you MUST collect at least 5 dimensions including 2 TCM differentiators before
  emitting [READY_FOR_RAG]. Vague complaints need more context.
• When you have enough: write a warm transition sentence on the line before the
  signal. Example: "Thank you — I have a much clearer picture now."
  Then on the next line output exactly:
      [READY_FOR_RAG]

Tone: warm, unhurried, empathetic. One focused question at a time.
"""

_SYNTHESIS_SYSTEM = """\
You are Prune — a warm, educational TCM companion (NOT a clinician).

━━━ PHASE: SYNTHESIS — PURE TCM EDUCATION ━━━

Based on the user's intake information and retrieved TCM knowledge, provide
EDUCATIONAL context about TCM concepts and theory. You are explaining how
TCM theory GENERALLY relates symptoms to energetic patterns.

CRITICAL DISTINCTION:
❌ NEVER say: "Your symptoms relate to Spleen Qi deficiency..."
❌ NEVER say: "Based on what you've told me, you have..."
❌ NEVER assume facts not stated (e.g., menstruation, age, gender)
✅ DO say: "In TCM theory, sharp abdominal pain is often associated with patterns
   like Qi or Blood Stagnation. Here's what TCM theory says about these..."
✅ DO say: "In TCM theory, loose stools combined with bloating can relate to
   Spleen Qi deficiency. This pattern in TCM is characterized by..."

ABSOLUTE RULES:
• Use ONLY content inside <RAG_CONTEXT> for all TCM claims.
• Cite source ids in parentheses for every claim, e.g. (sp.blood_stagnation, ap.GB20).
• Frame EVERYTHING as TCM theory, not the user's personal medical condition.
• Do NOT diagnose. Do NOT prescribe.

STRUCTURE — use these exact sections:

  1. RELEVANT TCM CONCEPTS
     Explain which TCM patterns theory associates with the described symptoms.

  2. HOW PRACTITIONERS DIFFERENTIATE
     Explain what a TCM practitioner looks for (tongue, pulse, thermal signs)
     to distinguish between related patterns.

  3. TCM THEORY ON LIFESTYLE & WELLNESS
     From the retrieved context, explain general dietary, acupressure, or
     lifestyle approaches discussed in TCM theory for these patterns.

  4. NEXT STEPS
     Encourage seeking consultation with a qualified TCM practitioner or healthcare provider.

• Do NOT add a disclaimer — the system appends it automatically.
• Tone: warm, curious, educational, grounded.
"""

_EDUCATION_SYSTEM = """\
You are Prune — a warm, educational Traditional Chinese Medicine companion.

━━━ MODE: EDUCATION ━━━

The user has a curiosity or theory question — no active personal symptom.

RULES:
• Use ONLY content inside <RAG_CONTEXT> for substantive claims. If the answer
  is not in the context, say so and offer to cover a related topic that is.
• Give a clear, accessible, plain-language explanation.
• Distinguish TCM-theory concepts from biomedical ones where relevant.
• Cite source ids in parentheses where appropriate, e.g. (ot.liver).
• Keep the response focused. End with one optional follow-up direction.
• Do NOT add a disclaimer — the system appends it automatically.
• Tone: warm, curious, educational.
"""

_FOLLOWUP_SYSTEM = """\
You are Prune — a warm, professional TCM educational companion.

━━━ MODE: FOLLOW-UP (post-synthesis) ━━━

The user is continuing a conversation about an already-assessed symptom picture.
The <RAG_CONTEXT> contains freshly retrieved knowledge relevant to their question.

RULES:
• Use ONLY content inside <RAG_CONTEXT> for any new health claims.
• Reference the conversation history where relevant for continuity.
• Cite source ids in parentheses.
• NEVER diagnose biomedical disease. NEVER recommend pharmaceutical treatments.
• Do NOT add a disclaimer — the system appends it automatically.
• Tone: warm, conversational, concise.
"""


@dataclass
class Reply:
    """Structure of an engine response."""
    text: str
    mode: str
    sources: List[str]
    flagged: Optional[str] = None


class PruneEngine:
    """Agentic RAG orchestrator with phase-gated state machine."""

    def __init__(self, settings: Optional[Settings] = None) -> None:
        self.settings: Settings = settings or load_settings()
        self.client: OpenAI = make_client(self.settings)
        self.retriever = RAGRetriever(
            client=self.client,
            embedding_model=self.settings.embedding_model,
            cache_dir=self.settings.data_dir,
        )
        self.sessions = SessionStore(self.settings.data_dir)
        self._flag_log = os.path.join(
            self.settings.data_dir, "flagged_conversations.jsonl"
        )

    def respond(self, session: Session, user_text: str) -> Reply:
        """Process a user message through the complete multi-layer pipeline."""
        # ── LAYER 0: Safety interception (Pre-LLM circuit breaker) ────────
        verdict = screen_input(user_text)
        if verdict.blocked:
            self._log_flagged(session, user_text, verdict.reason or "blocked")
            blk_mode = "emergency" if verdict.reason == "emergency" else "refused"
            response_text = verdict.response or ""

            # UX recovery: steer back to active assessment on drug refusals
            if verdict.reason == "drug":
                if session.conv_state == "triage" and session.current_complaint:
                    preview = session.current_complaint[:80] + ("…" if len(session.current_complaint) > 80 else "")
                    response_text += (
                        "\n\n---\n"
                        f"*We were previously discussing your concern: "
                        f"“{preview}”. Whenever you're ready, feel free to continue.*"
                    )
                elif session.conv_state in ("synthesis", "education") and session.current_complaint:
                    response_text += (
                        "\n\n---\n"
                        "*If you have further questions about your symptoms from "
                        "a TCM perspective, feel free to continue.*"
                    )

            session.add(Message(role="user", content=user_text))
            session.add(
                Message(
                    role="assistant",
                    content=response_text,
                    mode=blk_mode,
                    flagged=verdict.reason,
                )
            )
            return Reply(
                text=response_text,
                mode=blk_mode,
                sources=[],
                flagged=verdict.reason,
            )

        # ── LAYER 1: State-machine routing ────────────────────────────────
        if session.conv_state == "idle":
            initial_mode = self._classify(user_text)
            if initial_mode == EDUCATION:
                session.conv_state = "education"
            else:
                session.conv_state = "triage"
                session.current_complaint = user_text
                session.triage_turns = 0
        elif session.conv_state == "education":
            # Switch to triage if user begins describing personal symptoms
            if self._classify(user_text) != EDUCATION:
                session.conv_state = "triage"
                session.current_complaint = user_text
                session.triage_turns = 0

        # ── LAYER 2: Dispatch by state ────────────────────────────────────
        if session.conv_state == "triage":
            return self._handle_triage(session, user_text)

        if session.conv_state == "synthesis":
            return self._handle_synthesis(session, user_text)

        if session.conv_state == "education":
            return self._handle_education(session, user_text)

        return self._handle_synthesis(session, user_text)

    # ── Phase Handlers ────────────────────────────────────────────────────
    def _handle_triage(self, session: Session, user_text: str) -> Reply:
        """TRIAGE: Gather clinical details. No RAG retrieval allowed."""
        session.add(Message(role="user", content=user_text))

        msgs: list[dict] = [{"role": "system", "content": self._triage_system(session)}]
        for m in session.recent(10):
            if m.role in ("user", "assistant"):
                msgs.append({"role": m.role, "content": m.content})

        completion = self.client.chat.completions.create(
            model=self.settings.chat_model,
            temperature=0.4,
            messages=msgs,
        )
        raw = (completion.choices[0].message.content or "").strip()

        if _READY_SIGNAL in raw:
            # Transition to synthesis
            before_signal = raw.split(_READY_SIGNAL)[0].strip()
            session.conv_state = "synthesis"
            session.triage_turns += 1

            rag_query = self._build_rag_query(session)
            hits = self.retriever.retrieve(rag_query, k=7)
            rag_block = self.retriever.format_context(hits)
            sources = [h.chunk.id for h in hits]

            synth_raw = self._call_synthesis_llm(session, rag_block)
            synth_final = append_disclaimer(synth_raw)

            full_response = (
                f"{before_signal}\n\n{synth_final}" if before_signal else synth_final
            )

            session.add(
                Message(
                    role="assistant",
                    content=full_response,
                    mode="synthesis",
                    sources=sources,
                )
            )
            return Reply(text=full_response, mode="synthesis", sources=sources)
        else:
            session.triage_turns += 1
            session.add(Message(role="assistant", content=raw, mode="triage"))
            return Reply(text=raw, mode="triage", sources=[])

    def _handle_synthesis(self, session: Session, user_text: str) -> Reply:
        """SYNTHESIS: Retrieve RAG and provide educational synthesis."""
        session.add(Message(role="user", content=user_text))

        rag_query = self._build_rag_query(session)
        hits = self.retriever.retrieve(rag_query, k=7)
        rag_block = self.retriever.format_context(hits)
        sources = [h.chunk.id for h in hits]

        synth_raw = self._call_synthesis_llm(session, rag_block, followup=True)
        final = append_disclaimer(synth_raw)

        session.add(
            Message(role="assistant", content=final, mode="synthesis", sources=sources)
        )
        return Reply(text=final, mode="synthesis", sources=sources)

    def _handle_education(self, session: Session, user_text: str) -> Reply:
        """EDUCATION: Immediate RAG retrieval for theory questions."""
        session.add(Message(role="user", content=user_text))

        hits = self.retriever.retrieve(user_text, k=6)
        rag_block = self.retriever.format_context(hits)
        sources = [h.chunk.id for h in hits]

        sys_parts = [_EDUCATION_SYSTEM]
        if session.profile.completed and session.profile.pattern_summary:
            sys_parts.append("USER PROFILE:\n" + session.profile.pattern_summary)

        msgs: list[dict] = [{"role": "system", "content": "\n\n".join(sys_parts)}]
        for m in session.recent(6):
            if m.role in ("user", "assistant"):
                msgs.append({"role": m.role, "content": m.content})
        msgs.append({
            "role": "user",
            "content": f"<RAG_CONTEXT>\n{rag_block}\n</RAG_CONTEXT>\n\nQuestion:\n{user_text}",
        })

        completion = self.client.chat.completions.create(
            model=self.settings.chat_model,
            temperature=0.3,
            messages=msgs,
        )
        raw = (completion.choices[0].message.content or "").strip()
        final = append_disclaimer(raw)

        session.add(
            Message(role="assistant", content=final, mode="education", sources=sources)
        )
        return Reply(text=final, mode="education", sources=sources)

    # ── Helpers ───────────────────────────────────────────────────────────
    def _classify(self, text: str) -> str:
        try:
            r = self.client.chat.completions.create(
                model=self.settings.chat_model,
                temperature=0,
                max_tokens=4,
                messages=[
                    {"role": "system", "content": _ROUTER_SYSTEM},
                    {"role": "user", "content": text},
                ],
            )
            tok = (r.choices[0].message.content or "").strip().upper()
            if "EDUCATION" in tok:
                return EDUCATION
            if "CHRONIC" in tok:
                return CHRONIC
        except Exception:
            pass
        return ACUTE

    def _triage_system(self, session: Session) -> str:
        parts = [_TRIAGE_SYSTEM]
        if session.profile.completed and session.profile.pattern_summary:
            parts.append(
                "NOTE — USER CONSTITUTIONAL PROFILE (for context only, "
                "do NOT reveal it during triage):\n"
                + session.profile.pattern_summary
            )
        parts.append(
            f"NOTE — Current triage turn: {session.triage_turns + 1}. "
            f"Original complaint: \"{session.current_complaint}\""
        )
        return "\n\n".join(parts)

    def _build_rag_query(self, session: Session) -> str:
        parts = [session.current_complaint] if session.current_complaint else []
        for m in session.history:
            if m.role == "user" and m.content not in parts:
                parts.append(m.content)
        return " | ".join(parts) if parts else session.current_complaint

    def _call_synthesis_llm(
        self, session: Session, rag_block: str, followup: bool = False
    ) -> str:
        sys_prompt = _FOLLOWUP_SYSTEM if followup else _SYNTHESIS_SYSTEM
        parts = [sys_prompt]
        if session.profile.completed and session.profile.pattern_summary:
            parts.append(
                "USER CONSTITUTIONAL PROFILE (for context):\n"
                + session.profile.pattern_summary
            )

        msgs: list[dict] = [{"role": "system", "content": "\n\n".join(parts)}]
        for m in session.recent(10):
            if m.role in ("user", "assistant"):
                msgs.append({"role": m.role, "content": m.content})
        msgs.append({
            "role": "user",
            "content": (
                f"<RAG_CONTEXT>\n{rag_block}\n</RAG_CONTEXT>\n\n"
                "Synthesize an educational TCM assessment based on the above information."
            ),
        })

        completion = self.client.chat.completions.create(
            model=self.settings.chat_model,
            temperature=0.3,
            messages=msgs,
        )
        return (completion.choices[0].message.content or "").strip()

    def _log_flagged(self, session: Session, text: str, reason: str) -> None:
        os.makedirs(os.path.dirname(self._flag_log), exist_ok=True)
        with open(self._flag_log, "a", encoding="utf-8") as f:
            f.write(
                json.dumps(
                    {
                        "ts": datetime.now(timezone.utc).isoformat(),
                        "user_id": session.user_id,
                        "reason": reason,
                        "text": text,
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )


# Backwards compatibility alias
TCMChatbot = PruneEngine
