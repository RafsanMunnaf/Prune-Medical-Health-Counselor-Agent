"""Hard-coded safety & clinical compliance layer for Prune.

Per system specifications, this layer is non-negotiable and cannot be bypassed
by user input or prompt engineering. It runs BEFORE the LLM sees a message,
and automatically enforces disclaimers on health outputs.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

# ---------------------------------------------------------------------------
# Mandatory disclaimer appended to every substantive health output.
# ---------------------------------------------------------------------------
DISCLAIMER = (
    "\n\n---\n"
    "*Disclaimer: This information is educational and based on Traditional "
    "Chinese Medicine (TCM) theory. It does not constitute medical advice, "
    "diagnosis, or treatment, and does not replace consultation with a "
    "qualified healthcare professional.*"
)

# ---------------------------------------------------------------------------
# Emergency interception. Any of these patterns immediately routes the user
# to emergency services (112 in EU / 911 / 999).
# ---------------------------------------------------------------------------
_EMERGENCY_RE = re.compile(
    # ── Cardiovascular / chest ───────────────────────────────────────────────
    r"\bchest pain\b"
    r"|\bcrushing (?:chest )?pressure\b"
    r"|\bheart attack\b"
    r"|\bpain radiating to (?:the )?(?:left )?arm\b"
    r"|\bpain in (?:my )?chest\b"
    r"|\bchest tightness\b.{0,30}\b(?:sweat|sweating|dizzy|nausea)\b"
    # ── Neurological / stroke (FAST criteria) ────────────────────────────────
    r"|\bstroke\b"
    r"|\bface (?:droop|drooping|numb)\b"
    r"|\bfacial drooping\b"
    r"|\bslurred speech\b"
    r"|\bsudden (?:numbness|weakness|confusion|vision loss|severe headache)\b"
    r"|\bworst headache of my life\b"
    r"|\bthunderclap headache\b"
    r"|\barm (?:suddenly )?(?:numb|weak)(?:ness)?\b"
    # ── Respiratory ─────────────────────────────────────────────────────────
    r"|\bcan(?:'t| not|not) breathe\b"
    r"|\bcannot breathe\b"
    r"|\bnot breathing\b"
    r"|\btrouble breathing\b"
    r"|\bdifficulty breathing\b"
    r"|\bshortness of breath\b"
    r"|\bchoking\b"
    r"|\bstop(?:ped)? breathing\b"
    # ── Consciousness / trauma ──────────────────────────────────────────────
    r"|\bunconscious\b"
    r"|\bunresponsive\b"
    r"|\bcollapses?\b"
    r"|\bpassed? out\b"
    r"|\bsevere bleeding\b"
    r"|\bbleeding\b.{0,30}\bstop\b"
    r"|\bcoughing up blood\b"
    r"|\bvomiting blood\b"
    r"|\bseizure\b"
    r"|\boverdose\b"
    r"|\banaphylaxis\b"
    r"|\bsevere allergic reaction\b"
    # ── Mental health crisis ────────────────────────────────────────────────
    r"|\bsuicid"
    r"|\bkill myself\b"
    r"|\bend my life\b"
    r"|\bself[- ]harm\b"
    r"|\bwant to die\b"
    r"|\btake my own life\b",
    re.IGNORECASE,
)

EMERGENCY_RESPONSE = (
    "🚨 **MEDICAL EMERGENCY DETECTED.**\n\n"
    "Please stop interacting with this application and contact emergency "
    "services immediately (**Dial 112** in the EU, **911** in the US, or your local emergency number).\n\n"
    "Prune is an educational TCM companion and cannot provide assistance for severe or acute medical emergencies."
)

# ---------------------------------------------------------------------------
# Pharmaceutical & drug interaction refusal.
# ---------------------------------------------------------------------------
_DRUG_RE = re.compile(
    # ── Named antibiotics ────────────────────────────────────────────────────
    r"\b(?:amoxicillin|amoxicilline|ampicillin|penicillin|ciprofloxacin|"
    r"doxycycline|azithromycin|metronidazole|tetracycline|cephalexin|"
    r"clarithromycin|levofloxacin|moxifloxacin|trimethoprim|sulfamethoxazole|"
    r"erythromycin|clindamycin|nitrofurantoin|vancomycin|linezolid)\b"
    # ── Anticoagulants / cardiovascular ─────────────────────────────────────
    r"|\b(?:warfarin|heparin|rivaroxaban|apixaban|dabigatran|edoxaban|"
    r"clopidogrel|ticagrelor|digoxin|amlodipine|lisinopril|ramipril|"
    r"losartan|valsartan|candesartan|atenolol|bisoprolol|metoprolol|"
    r"hydrochlorothiazide|furosemide|spironolactone)\b"
    # ── Statins ──────────────────────────────────────────────────────────────
    r"|\b(?:atorvastatin|simvastatin|rosuvastatin|pravastatin|fluvastatin)\b"
    # ── NSAIDs / analgesics / opioids ────────────────────────────────────────
    r"|\b(?:ibuprofen|naproxen|diclofenac|celecoxib|paracetamol|acetaminophen|"
    r"tramadol|codeine|morphine|oxycodone|fentanyl|aspirin)\b"
    # ── Psychiatric / neurological ───────────────────────────────────────────
    r"|\b(?:fluoxetine|sertraline|paroxetine|escitalopram|citalopram|"
    r"venlafaxine|duloxetine|mirtazapine|bupropion|quetiapine|olanzapine|"
    r"risperidone|aripiprazole|haloperidol|valproate|lamotrigine|"
    r"phenytoin|carbamazepine|levetiracetam|gabapentin|pregabalin)\b"
    # ── Diabetes / endocrine ─────────────────────────────────────────────────
    r"|\b(?:metformin|insulin|glibenclamide|gliclazide|sitagliptin|"
    r"empagliflozin|dapagliflozin|levothyroxine|thyroxine)\b"
    # ── Steroids / immunosuppressants ────────────────────────────────────────
    r"|\b(?:prednisolone|prednisone|dexamethasone|hydrocortisone|"
    r"methylprednisolone|cyclosporine|tacrolimus|azathioprine|methotrexate)\b"
    # ── Other common pharmaceuticals ─────────────────────────────────────────
    r"|\b(?:omeprazole|lansoprazole|pantoprazole|tamoxifen|"
    r"acyclovir|valacyclovir|oseltamivir|theophylline)\b"
    # ── Category and query patterns ──────────────────────────────────────────
    r"|\bantibiotic[s]?\b"
    r"|\b(?:drug|medication) interaction\b"
    r"|\bhow many mg\b"
    r"|\b\d+\s*mg\b"
    r"|\bblood thinner[s]?\b"
    r"|\b(?:dose|dosage|how much .* (?:take|mg))\b"
    r"|\b(?:interact(?:s|ing|ion)?|mix|combine)\b.{0,50}\b(?:herb[s]?|herbal|supplement[s]?|tcm)\b"
    r"|\b(?:herb[s]?|herbal|supplement[s]?|tcm)\b.{0,50}\b(?:interact(?:s|ing|ion)?|safe to take)\b",
    re.IGNORECASE,
)

DRUG_REFUSAL_RESPONSE = (
    "I cannot provide guidance on pharmaceutical drugs, dosages, or their "
    "interactions with TCM therapies. Please consult your prescribing "
    "physician or a qualified pharmacist regarding your medication.\n\n"
    "If you'd like, I can discuss the **TCM perspective** on the "
    "underlying pattern or symptom without discussing prescription drugs."
)


@dataclass
class SafetyVerdict:
    """Result of running an input through the safety layer."""
    blocked: bool
    response: Optional[str] = None
    reason: Optional[str] = None  # "emergency" | "drug" | None


def screen_input(user_text: str) -> SafetyVerdict:
    """Run the pre-LLM safety screen on a user message."""
    if not user_text or not user_text.strip():
        return SafetyVerdict(blocked=False)

    if _EMERGENCY_RE.search(user_text):
        return SafetyVerdict(
            blocked=True, response=EMERGENCY_RESPONSE, reason="emergency"
        )
    if _DRUG_RE.search(user_text):
        return SafetyVerdict(
            blocked=True, response=DRUG_REFUSAL_RESPONSE, reason="drug"
        )
    return SafetyVerdict(blocked=False)


def append_disclaimer(text: str) -> str:
    """Append mandatory educational disclaimer on health outputs."""
    if not text:
        return text
    if "Disclaimer:" in text:
        return text
    return text.rstrip() + DISCLAIMER
