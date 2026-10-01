"""Configuration & client initialization for Prune."""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


@dataclass(frozen=True)
class Settings:
    """Application configuration and credentials."""
    api_key: str
    chat_model: str = "gpt-4o"
    embedding_model: str = "text-embedding-3-small"
    data_dir: str = "data"


def load_settings() -> Settings:
    """Load settings from environment variables with sensible defaults."""
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key or api_key.startswith("sk-your-key"):
        raise RuntimeError(
            "\n[Prune Error] OPENAI_API_KEY is not set.\n"
            "Please copy .env.example to .env and provide your OpenAI API key."
        )
    return Settings(
        api_key=api_key,
        chat_model=os.getenv("OPENAI_CHAT_MODEL", "gpt-4o"),
        embedding_model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"),
        data_dir=os.getenv("TCM_DATA_DIR", "data"),
    )


def make_client(settings: Settings) -> OpenAI:
    """Create an OpenAI client from settings."""
    return OpenAI(api_key=settings.api_key)
