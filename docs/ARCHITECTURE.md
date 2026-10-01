# 🏛️ Prune — System Architecture & Design Specification

Prune is an agentic health intelligence platform designed around the principles of **Traditional Chinese Medicine (TCM)**. It incorporates strict clinical safety barriers, phase-gated conversational state machines, deterministic vector retrieval (RAG), and structured constitutional pattern analysis.

---

## 📐 Multi-Layer Pipeline Overview

```
                        ┌────────────────────────────────────────┐
                        │              User Input                │
                        └───────────────────┬────────────────────┘
                                            │
                                            ▼
                    ┌────────────────────────────────────────────────┐
                    │    Layer 0: Safety & Compliance Interceptor    │
                    │  (Pre-LLM Regex Circuit Breakers & Emergency)  │
                    └───────┬────────────────────────────────┬───────┘
                            │ BLOCKED                        │ PASSED
                            ▼                                ▼
            ┌───────────────────────────────┐   ┌──────────────────────────────┐
            │ Immediate Crisis / Drug Alert │   │ Layer 1: Conversation State  │
            │ (112/911 Referral & Recovery) │   │           Machine            │
            └───────────────────────────────┘   └──────────────┬───────────────┘
                                                               │
                                  ┌────────────────────────────┴───────────────────────────┐
                                  │                                                        │
                         [ACUTE / CHRONIC]                                            [EDUCATION]
                                  ▼                                                        ▼
                    ┌───────────────────────────┐                            ┌───────────────────────────┐
                    │   Phase 1: Triage Intake  │                            │    Direct Retrieval &     │
                    │ (LLM Gathers Context Only;│                            │     Theory Explanation    │
                    │      NO RAG ALLOWED)      │                            └─────────────┬─────────────┘
                    └─────────────┬─────────────┘                                          │
                                  │ [READY_FOR_RAG signal emitted]                         │
                                  ▼                                                        │
                    ┌───────────────────────────┐                                          │
                    │ Phase 2: RAG Synthesis    │                                          │
                    │ (Vector Search & Holistic │◄─────────────────────────────────────────┘
                    │   Pattern Differentiation)│
                    └─────────────┬─────────────┘
                                  │
                                  ▼
                    ┌───────────────────────────┐
                    │ Layer 3: Intake / Profile │
                    │ (Constitutional Memory    │
                    │     Personalization)      │
                    └─────────────┬─────────────┘
                                  │
                                  ▼
                    ┌───────────────────────────┐
                    │ Mandatory Educational     │
                    │        Disclaimer         │
                    └───────────────────────────┘
```

---

## 🛡️ Layer 0: Safety & Compliance Interceptor

### 1. Emergency Detection
- Intercepts acute life-threatening situations (cardiovascular emergencies, stroke symptoms via FAST criteria, severe respiratory distress, suicidal ideation or self-harm, anaphylaxis, severe trauma).
- Immediately halts conversation flow and surfaces local emergency numbers (**112** for EU, **911** for US).
- Never attempts TCM interpretations during an active emergency.

### 2. Pharmaceutical Guardrails
- Blocks inquiries regarding pharmaceutical dosages (e.g. mg calculations, prescription drugs) and dangerous herb-drug interactions.
- Directs users to licensed physicians or pharmacists.
- **UX Recovery Mechanism**: Softens non-emergency drug refusals with a context-aware steering note allowing the user to resume their prior TCM assessment.

---

## 🔄 Layer 1: Phase-Gated Conversational Engine

The state machine prevents the AI from jumping to premature conclusions.

### State Transitions:
1. **`idle`**: Evaluates intent using the router classifier. If purely educational, transitions to `education`. If symptom-based, transitions to `triage`.
2. **`triage`**: The LLM acts as an intake clinician.
   - **Strict Rule**: No RAG context is injected and no pattern names or advice are given.
   - Gathers symptom dimensions: location, quality, onset, severity, thermal response (warm vs. cold preference), digestive signs, energy levels, and sleep patterns.
   - When sufficient diagnostic criteria are collected (3–4 exchanges for simple complaints; 5+ dimensions for systemic complaints), the LLM emits `[READY_FOR_RAG]`.
3. **`synthesis`**: Triggered immediately upon `[READY_FOR_RAG]` detection.
   - Aggregates the entire multi-turn dialog into a unified query.
   - Retrieves top-$k$ relevant chunks from the TCM knowledge base.
   - Synthesizes theoretical pattern differentiation, self-care guidelines (acupressure, dietary energetics, lifestyle adjustments), and practitioner referral advice.
4. **`education`**: Handles theoretical, philosophical, or organ-clock inquiries without entering clinical triage.

---

## 🔍 Layer 2: RAG Vector Engine & Citation Enforcement

- **Embedding Model**: OpenAI `text-embedding-3-small` producing 1536-dimensional vectors.
- **In-Process Normalized Matrix**: Uses $L_2$-normalized numpy matrix operations for sub-millisecond cosine similarity ($S = A \cdot B^T$).
- **Deterministic Caching**: Generates a SHA-256 hash over the knowledge corpus; caches precomputed embeddings in `data/embeddings_<hash>.npz` to eliminate redundant API expenditure.
- **Content Source Boundary Enforcement**: Retrieved context is injected with explicit demarcations (`<<source id=...>>...<<end>>`). The LLM is instructed to cite source identifiers in parentheses for all factual claims.

---

## 🌿 Layer 3: Structured Constitutional Intake

- Implements a 12-question diagnostic questionnaire evaluating the 9 primary TCM constitution types (Pinghe / Balanced, Qi Deficiency, Yang Deficiency, Yin Deficiency, Phlegm-Dampness, Damp-Heat, Blood Stasis, Qi Stagnation, Special Constitution).
- Synthesizes and stores a persistent constitutional summary in the user session (`Session.profile`).
- Dynamically injects constitutional memory into subsequent symptom assessments.

---

## 💾 Session & Persistence Architecture

- **Atomic Writes**: Saves user state to temporary files before atomic file renaming (`.tmp` $\to$ `.json`) to eliminate file corruption risks.
- **Pluggable Store**: The local JSON `SessionStore` mirrors the schema required for production relational databases (PostgreSQL, Django ORM, SQLAlchemy).
