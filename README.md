# 🌿 Prune — AI Traditional Chinese Medicine Companion & Health Intelligence Engine

[![Python](https://img.shields.io/badge/Python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-FF4B4B.svg?logo=streamlit&logoColor=white)](https://streamlit.io)
[![OpenAI](https://img.shields.io/badge/LLM-GPT--4o%20%26%20Embeddings-412991.svg?logo=openai&logoColor=white)](https://openai.com)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-100%25%20Passing-brightgreen.svg)]()

> **Prune** is an agentic, multi-layer conversational health platform built on Traditional Chinese Medicine (TCM) diagnostic theory. It blends strict clinical safety guardrails, phase-gated conversational intake state machines, vector-retrieval RAG with transparent citations, and structured constitutional pattern analysis.

---

## 📑 Table of Contents

- [Key Features](#-key-features)
- [Architecture & Multi-Layer Pipeline](#-architecture--multi-layer-pipeline)
- [Project File Structure](#-project-file-structure)
- [Quickstart & Installation](#-quickstart--installation)
- [Usage Guide](#-usage-guide)
  - [1. Streamlit Web Interface](#1-streamlit-web-interface)
  - [2. Interactive Command-Line REPL](#2-interactive-command-line-repl)
  - [3. Python Backend / REST API Integration](#3-python-backend--rest-api-integration)
- [Safety & Clinical Compliance](#-safety--clinical-compliance)
- [Curated TCM Knowledge Base](#-curated-tcm-knowledge-base)
- [Running Automated Tests](#-running-automated-tests)
- [Documentation](#-documentation)
- [Medical Disclaimer](#-medical-disclaimer)
- [License](#-license)

---

## ✨ Key Features

- 🛡️ **Layer 0 Clinical Circuit Breakers**: Hard-coded pre-LLM regex filters intercepting medical emergencies (cardiac, stroke, respiratory, crisis) and pharmaceutical dosage queries with context-aware UX recovery.
- 🔄 **Phase-Gated State Machine**: Enforces a strict two-stage intake protocol (**Triage $\to$ Synthesis**). The AI gathers focused clinical dimensions (thermal preference, digestion, energy, sleep) before running vector retrieval.
- 🔍 **In-Process RAG Vector Engine**: Normalized vector embeddings using OpenAI `text-embedding-3-small` with local SHA-256 `.npz` caching and sub-millisecond cosine similarity search.
- 🏷️ **Transparent Source Citations**: Enforces strict Content Source Boundaries with citation tags (e.g. `sp.headache.liver_yang`, `ap.GB20`, `hf.ginger`).
- 🌿 **12-Dimension Constitutional Assessment**: Guided intake questionnaire categorizing the user's primary TCM constitution with persistent session memory.
- 🎨 **Modern Streamlit Web UI**: Responsive web app with real-time state machine indicators, citation expanders, and session reset controls.
- 💻 **Interactive CLI REPL**: Full-featured terminal interface supporting slash commands (`/new`, `/history`, `/profile`, `/intake`, `/reset`).

---

## 🏛️ Architecture & Multi-Layer Pipeline

```
                               ┌────────────────────────────────┐
                               │        User User Query         │
                               └───────────────┬────────────────┘
                                               │
                                               ▼
                     ┌────────────────────────────────────────────────────┐
                     │     Layer 0: Safety & Compliance Interceptor       │
                     │  (Pre-LLM Regex Circuit Breakers & Emergency 112)  │
                     └─────────┬────────────────────────────────┬─────────┘
                               │ BLOCKED                        │ PASSED
                               ▼                                ▼
               ┌───────────────────────────────┐  ┌──────────────────────────────┐
               │ Immediate Emergency / Drug    │  │ Layer 1: Conversational      │
               │ Circuit Breaker (112/911 Alert│  │          State Machine       │
               └───────────────────────────────┘  └──────────────┬───────────────┘
                                                                 │
                                   ┌─────────────────────────────┴─────────────────────────┐
                                   │                                                       │
                          [ACUTE / CHRONIC]                                           [EDUCATION]
                                   │                                                       │
                                   ▼                                                       ▼
                     ┌───────────────────────────┐                           ┌───────────────────────────┐
                     │ Phase 1: Triage Intake    │                           │ Direct Knowledge Search   │
                     │ (Gather Context Questions;│                           │   (Theory & Organ Clock)  │
                     │      NO RAG ALLOWED)      │                           └─────────────┬─────────────┘
                     └─────────────┬─────────────┘                                         │
                                   │ [READY_FOR_RAG signal emitted]                        │
                                   ▼                                                       │
                     ┌───────────────────────────┐                                         │
                     │ Phase 2: RAG Synthesis    │◄────────────────────────────────────────┘
                     │ (Vector Retrieval & Multi-│
                     │   Pattern Differentiation)│
                     └─────────────┬─────────────┘
                                   │
                                   ▼
                     ┌───────────────────────────┐
                     │ Layer 3: Constitutional   │
                     │    Profile Memory &       │
                     │ Mandatory TCM Disclaimer  │
                     └───────────────────────────┘
```

For complete technical specifications, see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

---

## 📁 Project File Structure

```text
prune/
├── .env.example               # Configuration template (OpenAI API key & model settings)
├── .gitignore                 # Ignore rules for virtual environments, secrets, and caches
├── LICENSE                    # MIT Open Source License
├── README.md                  # Complete project documentation and quickstart
├── pyproject.toml             # Standard Python packaging configuration
├── requirements.txt           # Production dependencies
├── app.py                     # Streamlit web application entrypoint
├── main.py                    # Dual CLI launcher & backward-compatible API exporter
│
├── prune/                     # Core Modular Package
│   ├── __init__.py            # Package initialization & exports
│   ├── api.py                 # Functional API layer (JSON-ready for FastAPI / Flask)
│   ├── cli.py                 # Interactive terminal REPL with slash commands
│   ├── config.py              # Settings dataclass and environment loader
│   ├── engine.py              # Agentic RAG state machine & PruneEngine orchestrator
│   ├── intake.py              # Structured 12-question constitutional intake flow
│   ├── knowledge.py           # Curated TCM clinical knowledge base & chunk definitions
│   ├── rag.py                 # In-process semantic vector search & local caching
│   ├── safety.py              # Emergency detection & pharmaceutical refusal guardrails
│   └── session.py             # Session state machine & profile persistence
│
├── docs/                      # Technical Documentation
│   ├── ARCHITECTURE.md        # Deep dive into multi-layer system architecture
│   ├── KNOWLEDGE_BASE.md      # TCM patterns, acupoint catalog, and food energetics
│   └── SAFETY_GUIDELINES.md   # Emergency screening rules & clinical protocols
│
├── tests/                     # Automated Test Suite (pytest)
│   ├── __init__.py
│   ├── test_api.py            # API endpoint and healthcheck tests
│   ├── test_knowledge.py      # Knowledge chunk validation tests
│   ├── test_rag.py            # Vector search & cache validation tests
│   ├── test_safety.py         # Emergency & pharmaceutical refusal tests
│   └── test_session.py        # Session state machine & atomic save tests
│
└── data/                      # Local storage for session files & embedding caches
    └── .gitkeep
```

---

## 🚀 Quickstart & Installation

### 1. Prerequisites
- Python 3.9 or newer (Python 3.10+ recommended)
- An active [OpenAI API Key](https://platform.openai.com)

### 2. Clone the Repository
```bash
git clone https://github.com/RafsanMunnaf/prune.git
cd prune
```

### 3. Set Up a Virtual Environment
```bash
# On macOS / Linux:
python3 -m venv venv
source venv/bin/activate

# On Windows (PowerShell):
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables
Copy the template `.env.example` to `.env` and add your OpenAI API key:
```bash
# On Linux / macOS:
cp .env.example .env

# On Windows:
copy .env.example .env
```

Edit `.env`:
```env
OPENAI_API_KEY=sk-your-actual-openai-api-key-here
OPENAI_CHAT_MODEL=gpt-4o
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
TCM_DATA_DIR=data
```

---

## 💻 Usage Guide

### 1. Streamlit Web Interface
Launch the browser UI:
```bash
streamlit run app.py
```
- Open `http://localhost:8501` in your browser.
- Chat with Prune, observe live triage/synthesis phase badges, toggle **Premium Mode**, and explore knowledge base source citations.

---

### 2. Interactive Command-Line REPL
Run the terminal interface:
```bash
# Basic mode:
python main.py

# Premium mode (enables constitutional intake):
python main.py --premium --user my_user_name
```

#### Terminal Slash Commands:
| Command | Description |
| :--- | :--- |
| `/help` | Display the list of available commands |
| `/new` | Start a new topic (retains your constitutional profile) |
| `/intake` | Run the 12-question constitutional assessment |
| `/profile` | Display your saved TCM constitutional pattern summary |
| `/history` | View recent conversation turns |
| `/reset` | Clear all session history and reset profile |
| `/quit` | Exit the application |

---

### 3. Python Backend / REST API Integration
Prune exposes a functional API layer ready for FastAPI, Flask, or background workers:

```python
from prune import api_chat, api_get_state, api_new_topic

# Send a message and get a JSON response
response = api_chat(user_id="user_482", message="I wake up every night between 1 and 3 AM with headache.", premium=True)

print(response["reply"])
print("Active Phase:", response["state"])
print("Retrieved Sources:", response["sources"])
```

Example FastAPI endpoint:
```python
from fastapi import FastAPI
from pydantic import BaseModel
from prune import api_chat, api_get_state

app = FastAPI(title="Prune API")

class ChatRequest(BaseModel):
    user_id: str
    message: str
    premium: bool = False

@app.post("/chat")
def chat(req: ChatRequest):
    return api_chat(req.user_id, req.message, req.premium)
```

---

## 🛡️ Safety & Clinical Compliance

Prune enforces strict clinical safety protocols:
1. **Emergency Interception**: Instant redirection to emergency numbers (**112** in EU, **911** in US) upon detecting red-flag symptoms (severe chest pain, stroke signs, breathing distress, suicide/self-harm).
2. **Pharmaceutical Exclusion**: Refuses medication dosage recommendations or dangerous herb-drug interaction questions, directing users to qualified physicians/pharmacists.
3. **Mandatory Disclaimer**: Every substantive health response automatically appends an un-bypassable educational disclaimer.

See [docs/SAFETY_GUIDELINES.md](docs/SAFETY_GUIDELINES.md) for full protocol details.

---

## 📚 Curated TCM Knowledge Base

Prune is seeded with expert TCM knowledge covering:
- **Symptom $\to$ Pattern Mappings**: Liver Yang Rising, Liver Qi Stagnation, Spleen Qi Deficiency, Kidney Yang Deficiency, Blood Stagnation, Wind-Cold Invasion, Shen Disturbances.
- **Acupressure Protocols**: LI4 (*Hegu*), LV3 (*Taichong*), ST36 (*Zusanli*), SP6 (*Sanyinjiao*), PC6 (*Neiguan*), GB20 (*Fengchi*), HT7 (*Shenmen*), BL23 (*Shenshu*).
- **Dietary & Herbal Energetics**: Warming, cooling, and moistening food therapies, ginger decoctions, chrysanthemum teas, congee, and goji berries.
- **Five Element Seasonal Living**: Spring (Wood), Summer (Fire), Late Summer (Earth), Autumn (Metal), Winter (Water).

See [docs/KNOWLEDGE_BASE.md](docs/KNOWLEDGE_BASE.md) for the complete catalog.

---

## 🧪 Running Automated Tests

Run the complete test suite with `pytest`:
```bash
pytest -v
```

All unit tests cover:
- Safety emergency and pharmaceutical circuit breakers
- Multi-turn session transitions and atomic serialization
- Knowledge base integrity and ID lookup
- In-process RAG vector search, context formatting, and caching
- High-level API functions and healthcheck

---

## 📖 Documentation

- [System Architecture Specification](docs/ARCHITECTURE.md)
- [TCM Knowledge Base & Acupoint Catalog](docs/KNOWLEDGE_BASE.md)
- [Safety & Clinical Compliance Guidelines](docs/SAFETY_GUIDELINES.md)

---

## ⚠️ Medical Disclaimer

*This software is created for educational and informational purposes only based on Traditional Chinese Medicine (TCM) theory. It does not constitute medical advice, diagnosis, or treatment and should not replace consultation with a qualified physician, acupuncturist, or healthcare professional. In the event of a medical emergency, call 112, 911, or your local emergency services immediately.*

---

## 📄 License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for details.
