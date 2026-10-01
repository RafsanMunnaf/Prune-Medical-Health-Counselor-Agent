# 🛡️ Prune — Safety, Clinical Compliance & Triage Protocols

Safety and clinical compliance are built into the bedrock of Prune. This document details the guardrails, emergency triggers, pharmaceutical boundaries, and ethical guidelines governing all interactions.

---

## 🚨 Emergency Protocols

### Red-Flag Detection Triggers
Prune continuously monitors incoming text for symptoms that require immediate acute biomedical intervention:

1. **Cardiovascular**: Severe or crushing chest pain, radiating left arm/jaw pain, acute chest tightness with diaphoresis (sweating).
2. **Neurological (FAST Criteria)**: Facial drooping, unilateral arm/leg weakness, slurred speech, sudden loss of vision, sudden confusion, thunderclap headache ("worst headache of life").
3. **Respiratory**: Acute shortness of breath, inability to breathe, choking, stridor.
4. **Consciousness / Trauma**: Loss of consciousness, unresponsiveness, severe hemorrhaging / uncontrolled bleeding, coughing/vomiting blood, seizures, acute poisoning/overdose.
5. **Mental Health Crisis**: Suicidal ideation, intent to harm oneself, acute distress.

### Emergency Response Behavior
- Pre-LLM interception triggers before any generative model is invoked.
- Outputs standardized emergency guidance directing the user to dial **112** (European Union) or **911** (United States).
- Immediately logs the flagged event with anonymized metadata to `data/flagged_conversations.jsonl`.
- **Absolute Rule**: Prune will NEVER provide TCM analysis, acupressure, or dietary guidance during an active emergency event.

---

## 💊 Pharmaceutical & Drug Interaction Guardrails

1. **No Drug Dosages**: Inquiries regarding dosage calculations (e.g. mg amounts, pill frequencies) for pharmaceuticals are refused unconditionally.
2. **No Drug Interactions**: Herb-drug interaction inquiries (e.g., combining Blood-moving herbs like *Dan Shen* or *Hong Hua* with anticoagulants like *Warfarin*) are referred to a prescribing clinician or pharmacist.
3. **UX Recovery Flow**: For drug refusals, Prune provides a gentle redirection back to the safe, non-pharmaceutical TCM energetic discussion if an active assessment was ongoing.

---

## 📜 Educational Framing & Disclaimers

- **Non-Diagnostic**: Prune does not issue medical diagnoses. All symptom evaluations are framed theoretically: *"In Traditional Chinese Medicine theory, this combination of symptoms is often discussed in relation to..."*
- **Mandatory Disclaimer**: An un-bypassable educational disclaimer is programmatically enforced on every substantive health response.
