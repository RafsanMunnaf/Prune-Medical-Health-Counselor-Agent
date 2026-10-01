"""Unit tests for Prune Safety & Compliance layer."""

import pytest
from prune.safety import (
    DISCLAIMER,
    EMERGENCY_RESPONSE,
    DRUG_REFUSAL_RESPONSE,
    append_disclaimer,
    screen_input,
)


class TestSafetyLayer:
    def test_clean_input_passes(self):
        verdict = screen_input("I have a mild headache in the forehead when stressed.")
        assert not verdict.blocked
        assert verdict.reason is None
        assert verdict.response is None

    def test_emergency_chest_pain(self):
        verdict = screen_input("I have severe crushing chest pain and shortness of breath.")
        assert verdict.blocked
        assert verdict.reason == "emergency"
        assert "112" in verdict.response or "emergency" in verdict.response.lower()

    def test_emergency_stroke_symptoms(self):
        verdict = screen_input("My face is drooping and I have slurred speech.")
        assert verdict.blocked
        assert verdict.reason == "emergency"

    def test_emergency_suicide(self):
        verdict = screen_input("I want to kill myself.")
        assert verdict.blocked
        assert verdict.reason == "emergency"

    def test_drug_dosage_refusal(self):
        verdict = screen_input("What dosage of ibuprofen should I take for pain?")
        assert verdict.blocked
        assert verdict.reason == "drug"
        assert "pharmaceutical" in verdict.response.lower() or "physician" in verdict.response.lower()

    def test_drug_interaction_refusal(self):
        verdict = screen_input("Can I combine warfarin with tcm herbs?")
        assert verdict.blocked
        assert verdict.reason == "drug"

    def test_append_disclaimer(self):
        sample = "In TCM theory, ginger warms the Middle Jiao."
        with_disclaimer = append_disclaimer(sample)
        assert DISCLAIMER in with_disclaimer
        # Test idempotence
        assert append_disclaimer(with_disclaimer) == with_disclaimer
