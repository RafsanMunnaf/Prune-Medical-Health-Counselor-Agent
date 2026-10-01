"""Interactive CLI REPL for Prune.

Usage:
    python -m prune.cli [--user USER_ID] [--premium] [--reset]
    python main.py [--user USER_ID] [--premium] [--reset]
"""

from __future__ import annotations

import argparse
import sys
from typing import Optional

from .config import load_settings
from .engine import PruneEngine, Reply
from .intake import run_intake
from .session import Session, SessionStore

HELP_TEXT = """\
Available Commands:
  /help       - Show this help message
  /new        - Start a new conversation topic (retains constitutional profile)
  /history    - Display the recent conversation history
  /profile    - Show your saved TCM constitutional profile
  /intake     - Run the 12-question constitutional intake assessment (requires --premium)
  /reset      - Reset and wipe all session history and profile
  /quit       - Exit the application
"""


def _print_banner(user_id: str, is_premium: bool) -> None:
    print("\n" + "═" * 68)
    print("  🌿 PRUNE — AI Traditional Chinese Medicine Companion")
    print(f"  User: {user_id} | Premium: {'Enabled' if is_premium else 'Disabled'}")
    print("  Type /help for commands, /quit to exit.")
    print("═" * 68 + "\n")


def _print_reply(reply: Reply) -> None:
    badge = {
        "triage": "🔍 TRIAGE",
        "synthesis": "🌿 SYNTHESIS",
        "education": "📚 EDUCATION",
        "emergency": "🚨 EMERGENCY",
        "refused": "🚫 REFUSED",
    }.get(reply.mode, f"💬 {reply.mode.upper()}")

    print(f"\n[{badge}]")
    if reply.sources:
        print(f"Sources: {', '.join(reply.sources)}")
    print("-" * 68)
    print(reply.text)
    print("-" * 68 + "\n")


def main(argv: Optional[list[str]] = None) -> int:
    """Run interactive terminal session."""
    parser = argparse.ArgumentParser(
        description="Prune: AI Traditional Chinese Medicine Companion"
    )
    parser.add_argument("--user", default="cli_user", help="User ID (default: cli_user)")
    parser.add_argument(
        "--premium", action="store_true", help="Enable premium features and intake"
    )
    parser.add_argument(
        "--reset", action="store_true", help="Clear session on startup"
    )
    args = parser.parse_args(argv)

    try:
        settings = load_settings()
    except RuntimeError as err:
        sys.exit(f"\n[Error] {err}\n")

    engine = PruneEngine(settings)
    store = SessionStore(settings.data_dir)

    if args.reset:
        session = Session(user_id=args.user, is_premium=args.premium)
        store.save(session)
    else:
        session = store.load(args.user)
        if args.premium:
            session.is_premium = True

    _print_banner(session.user_id, session.is_premium)

    def _ask(prompt: str) -> str:
        try:
            return input(f"\n{prompt}\n> ").strip()
        except (KeyboardInterrupt, EOFError):
            return ""

    def _say(text: str) -> None:
        print(f"\n{text}")

    while True:
        try:
            user_text = input("You > ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break

        if not user_text:
            continue

        cmd = user_text.lower()
        if cmd in ("/quit", "/exit"):
            break
        if cmd == "/help":
            print(HELP_TEXT)
            continue
        if cmd == "/new":
            session.reset_conversation()
            store.save(session)
            print("\n  🔄 New topic started. Describe your symptom or question.\n")
            continue
        if cmd == "/history":
            print("\nRecent conversation turns:")
            for m in session.recent(10):
                print(f"  [{m.role.upper()}] ({m.mode or '-'}) {m.content[:120]}…")
            print()
            continue
        if cmd == "/profile":
            if session.profile.completed:
                print(f"\nConstitutional Profile:\n{session.profile.pattern_summary}\n")
            else:
                print("\n  No profile on file yet. Run /intake to complete assessment.\n")
            continue
        if cmd == "/reset":
            session = Session(user_id=args.user, is_premium=args.premium)
            store.save(session)
            print("\n  🗑️ Session cleared.\n")
            continue
        if cmd == "/intake":
            if not session.is_premium:
                print("\n  ⚠️ Constitutional intake is a premium feature. Pass --premium to enable.\n")
                continue
            run_intake(engine.client, engine.settings.chat_model, session, _ask, _say)
            store.save(session)
            if session.profile.pattern_summary:
                _say(f"Your Saved Profile:\n{session.profile.pattern_summary}")
            continue

        reply = engine.respond(session, user_text)
        store.save(session)
        _print_reply(reply)

    store.save(session)
    print("Thank you for using Prune. Be well.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
