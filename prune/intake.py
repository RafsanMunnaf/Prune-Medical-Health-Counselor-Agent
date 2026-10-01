"""Structured constitutional intake flow (Layer 3) for Prune.

Guides the user through 12 diagnostic dimensions covering:
energy, sleep, digestion, temperature preference, thirst, emotions,
tongue appearance, menstrual health (if applicable), sweating, lower back/knees,
stress holding areas, and lifestyle habits.

The LLM summarizes the user's responses into a standardized TCM constitutional
pattern profile, which is stored in the session and used for deep context
personalization in subsequent interactions.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Callable, Optional

from openai import OpenAI

from .knowledge import intake_questions
from .session import ConstitutionalProfile, Session

_PROFILE_SYSTEM = (
    "You are a TCM intake summariser. From the user's structured intake answers, "
    "produce a SHORT constitutional profile in TCM terms (2–4 sentences). Use "
    "standard TCM patterns (e.g. Qi Deficiency, Yin Deficiency, Yang Deficiency, "
    "Damp-Phlegm, Blood Stasis, Liver Qi Stagnation). Never diagnose. Never name "
    "biomedical diseases. End with one sentence on what to be mindful of in self-care."
)


def run_intake(
    client: OpenAI,
    chat_model: str,
    session: Session,
    ask: Callable[[str], str],
    say: Callable[[str], None],
) -> ConstitutionalProfile:
    """Run the conversational intake process.

    Args:
        client: OpenAI client instance.
        chat_model: LLM model identifier.
        session: Active user session.
        ask: Callback to request single user input.
        say: Callback to output narration text.

    Returns:
        ConstitutionalProfile: The generated and saved constitutional profile.
    """
    say(
        "🌿 Let's complete your TCM constitutional intake assessment.\n"
        "I will ask 12 focused questions covering energy, sleep, digestion, "
        "temperature, thirst, emotions, and tongue signs.\n"
        "Brief answers (even 1-2 words) are completely fine."
    )

    questions = intake_questions()
    answers: dict[str, str] = {}
    for idx, q in enumerate(questions, 1):
        prompt = f"({idx}/{len(questions)}) [{q.title}] {q.text}"
        answer = ask(prompt).strip()
        answers[q.id] = answer or "(no answer)"

    say("✨ Thank you. Analyzing your responses to build your constitutional profile…")

    user_block = "\n".join(f"- {qid}: {ans}" for qid, ans in answers.items())
    resp = client.chat.completions.create(
        model=chat_model,
        temperature=0.2,
        messages=[
            {"role": "system", "content": _PROFILE_SYSTEM},
            {"role": "user", "content": f"Intake answers:\n{user_block}"},
        ],
    )
    summary: Optional[str] = (resp.choices[0].message.content or "").strip()

    profile = ConstitutionalProfile(
        completed=True,
        answers=answers,
        pattern_summary=summary,
        completed_at=datetime.now(timezone.utc).isoformat(),
    )
    session.profile = profile
    return profile
