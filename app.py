"""Prune — Streamlit Web Interface.

Run:
    streamlit run app.py
"""

from __future__ import annotations

import uuid
import streamlit as st

from prune import (
    api_chat,
    api_get_profile,
    api_get_state,
    api_healthcheck,
    api_new_topic,
    api_reset_session,
)

# ── Page config ───────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Prune — AI TCM Health Companion",
    page_icon="🌿",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ── Custom CSS for visual polish ───────────────────────────────────────────
st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1b4332;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        color: #52796f;
        font-size: 1.05rem;
        margin-bottom: 1.5rem;
    }
    .badge-pill {
        display: inline-block;
        padding: 0.25rem 0.6rem;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    .stChatMessage {
        border-radius: 10px;
        padding: 0.5rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Session defaults ──────────────────────────────────────────────────────
if "user_id" not in st.session_state:
    st.session_state.user_id = f"prune_user_{uuid.uuid4().hex[:10]}"
if "messages" not in st.session_state:
    st.session_state.messages = []
if "premium" not in st.session_state:
    st.session_state.premium = False

USER_ID = st.session_state.user_id

# ── Mode badge helper ─────────────────────────────────────────────────────
MODE_BADGE = {
    "triage": ("🔍", "Triage — Gathering Clinical Details"),
    "synthesis": ("🌿", "Synthesis — Educational TCM Assessment"),
    "education": ("📚", "Education — Theory & Philosophy"),
    "emergency": ("🚨", "Emergency Alert"),
    "refused": ("🚫", "Out of Scope / Circuit Breaker"),
}


def mode_label(mode: str, sources: list) -> str:
    icon, label = MODE_BADGE.get(mode, ("💬", mode.title() if mode else "General"))
    if mode in ("synthesis", "education") and sources:
        label += f" • {len(sources)} source{'s' if len(sources) > 1 else ''}"
    return f"{icon} **{label}**"


# ── Sidebar ───────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🌿 **Prune**")
    st.caption("AI Traditional Chinese Medicine Companion")
    st.divider()

    st.session_state.premium = st.toggle(
        "✨ Premium Mode", value=st.session_state.premium
    )

    st.subheader("Session Controls")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 New Topic", use_container_width=True):
            api_new_topic(USER_ID, st.session_state.premium)
            st.session_state.messages.append({
                "role": "system",
                "content": "*(New topic started — describe your symptom or question.)*",
                "mode": None,
                "sources": [],
            })
            st.rerun()

    with col2:
        if st.button("🗑️ Reset", use_container_width=True):
            api_reset_session(USER_ID, st.session_state.premium)
            st.session_state.messages = []
            st.rerun()

    st.divider()

    # Live state badge
    state_info = api_get_state(USER_ID)
    phase = state_info.get("state", "idle")
    phase_colors = {
        "idle": "🟡 Idle",
        "triage": "🔵 Triage",
        "synthesis": "🟢 Synthesis",
        "education": "🟣 Education",
    }
    st.markdown(f"**State:** `{phase_colors.get(phase, phase)}`")
    if state_info.get("triage_turns"):
        st.caption(f"Triage Exchanges: {state_info['triage_turns']}")

    if state_info.get("profile_completed"):
        st.success("✅ Constitutional Profile Active")
        profile = api_get_profile(USER_ID)
        with st.expander("View Saved Profile"):
            st.markdown(profile.get("pattern_summary", "No summary available"))

    st.divider()
    st.caption("🚨 For severe symptoms or medical emergencies, please call **112 / 911**.")

# ── Main header ───────────────────────────────────────────────────────────
st.markdown('<div class="main-header">🌿 Prune</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">'
    "Holistic symptom assessment & constitutional pattern insights powered by Traditional Chinese Medicine theory."
    "</div>",
    unsafe_allow_html=True,
)

# ── Render chat history ───────────────────────────────────────────────────
for msg in st.session_state.messages:
    if msg["role"] == "system":
        st.info(msg["content"])
        continue

    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant" and msg.get("mode"):
            st.caption(mode_label(msg["mode"], msg.get("sources", [])))
        st.markdown(msg["content"])
        if msg.get("sources"):
            with st.expander("🔍 View Knowledge Base Citations", expanded=False):
                for src in msg["sources"]:
                    st.code(src, language="text")

# ── Chat input ────────────────────────────────────────────────────────────
user_input = st.chat_input("Describe your symptom or ask a TCM theory question…")

if user_input:
    # Add user message
    st.session_state.messages.append({
        "role": "user",
        "content": user_input,
        "mode": None,
        "sources": [],
    })
    with st.chat_message("user"):
        st.markdown(user_input)

    # Call Prune API
    with st.chat_message("assistant"):
        with st.spinner("Analyzing TCM patterns…"):
            result = api_chat(USER_ID, user_input, st.session_state.premium)

        mode = result.get("mode", "")
        reply = result.get("reply", "")
        sources = result.get("sources", [])

        if mode:
            st.caption(mode_label(mode, sources))
        st.markdown(reply)
        if sources:
            with st.expander("🔍 View Knowledge Base Citations", expanded=False):
                for src in sources:
                    st.code(src, language="text")

    st.session_state.messages.append({
        "role": "assistant",
        "content": reply,
        "mode": mode,
        "sources": sources,
    })

    st.rerun()
