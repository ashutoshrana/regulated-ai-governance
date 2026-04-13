"""Tests for NIST AI Risk Management Framework 1.0 + AI 600-1 GenAI Profile module."""

from __future__ import annotations

import json

from regulated_ai_governance.regulations.nist_ai_rmf import (
    NIST_GENAI_HIGH_RISK_ACTIONS,
    NISTAIRMFFunction,
    NISTAIRMFRiskAssessment,
    NISTAIRMFRiskCategory,
    make_nist_ai_rmf_policy,
)

# ---------------------------------------------------------------------------
# NISTAIRMFFunction
# ---------------------------------------------------------------------------


class TestNISTAIRMFFunction:
    def test_govern_value(self) -> None:
        assert NISTAIRMFFunction.GOVERN == "GOVERN"

    def test_map_value(self) -> None:
        assert NISTAIRMFFunction.MAP == "MAP"

    def test_measure_value(self) -> None:
        assert NISTAIRMFFunction.MEASURE == "MEASURE"

    def test_manage_value(self) -> None:
        assert NISTAIRMFFunction.MANAGE == "MANAGE"

    def test_four_functions_defined(self) -> None:
        values = {f.value for f in NISTAIRMFFunction}
        assert values == {"GOVERN", "MAP", "MEASURE", "MANAGE"}

    def test_is_string_enum(self) -> None:
        assert isinstance(NISTAIRMFFunction.GOVERN, str)


# ---------------------------------------------------------------------------
# NISTAIRMFRiskCategory
# ---------------------------------------------------------------------------


class TestNISTAIRMFRiskCategory:
    def test_confabulation_value(self) -> None:
        assert NISTAIRMFRiskCategory.CONFABULATION == "confabulation"

    def test_data_bias_value(self) -> None:
        assert NISTAIRMFRiskCategory.DATA_BIAS == "data_bias"

    def test_human_ai_configuration_value(self) -> None:
        assert NISTAIRMFRiskCategory.HUMAN_AI_CONFIGURATION == "human_ai_configuration"

    def test_information_integrity_value(self) -> None:
        assert NISTAIRMFRiskCategory.INFORMATION_INTEGRITY == "information_integrity"

    def test_data_privacy_value(self) -> None:
        assert NISTAIRMFRiskCategory.DATA_PRIVACY == "data_privacy"

    def test_explainability_value(self) -> None:
        assert NISTAIRMFRiskCategory.EXPLAINABILITY == "explainability"

    def test_harmful_bias_value(self) -> None:
        assert NISTAIRMFRiskCategory.HARMFUL_BIAS == "harmful_bias"

    def test_security_value(self) -> None:
        assert NISTAIRMFRiskCategory.SECURITY == "security"

    def test_eight_categories_defined(self) -> None:
        assert len(NISTAIRMFRiskCategory) == 8

    def test_is_string_enum(self) -> None:
        assert isinstance(NISTAIRMFRiskCategory.CONFABULATION, str)


# ---------------------------------------------------------------------------
# NISTAIRMFRiskAssessment
# ---------------------------------------------------------------------------


class TestNISTAIRMFRiskAssessment:
    def _make_assessment(self) -> NISTAIRMFRiskAssessment:
        return NISTAIRMFRiskAssessment(
            system_id="rag_tutoring_v2",
            risk_categories=[
                NISTAIRMFRiskCategory.CONFABULATION,
                NISTAIRMFRiskCategory.DATA_PRIVACY,
            ],
            risk_level="high",
            gov_measures=["ai_policy_documented", "accountability_assigned"],
            map_measures=["use_case_catalogued", "stakeholders_identified"],
            measure_measures=["hallucination_rate_measured", "bias_evaluation_run"],
            manage_measures=["human_review_gate_added", "output_filter_deployed"],
            timestamp_utc="2025-09-01T08:00:00Z",
            assessor_id="compliance-agent-001",
        )

    def test_to_log_entry_is_json(self) -> None:
        assessment = self._make_assessment()
        entry = assessment.to_log_entry()
        parsed = json.loads(entry)
        assert isinstance(parsed, dict)

    def test_framework_field(self) -> None:
        assessment = self._make_assessment()
        parsed = json.loads(assessment.to_log_entry())
        assert parsed["framework"] == "NIST_AI_RMF_1_0"

    def test_record_type_field(self) -> None:
        assessment = self._make_assessment()
        parsed = json.loads(assessment.to_log_entry())
        assert parsed["record_type"] == "risk_assessment"

    def test_system_id_in_log(self) -> None:
        assessment = self._make_assessment()
        parsed = json.loads(assessment.to_log_entry())
        assert parsed["system_id"] == "rag_tutoring_v2"

    def test_risk_categories_sorted_in_log(self) -> None:
        assessment = self._make_assessment()
        parsed = json.loads(assessment.to_log_entry())
        cats = parsed["risk_categories"]
        assert cats == sorted(cats)

    def test_risk_level_in_log(self) -> None:
        assessment = self._make_assessment()
        parsed = json.loads(assessment.to_log_entry())
        assert parsed["risk_level"] == "high"

    def test_gov_measures_sorted_in_log(self) -> None:
        assessment = self._make_assessment()
        parsed = json.loads(assessment.to_log_entry())
        m = parsed["gov_measures"]
        assert m == sorted(m)

    def test_assessor_id_in_log(self) -> None:
        assessment = self._make_assessment()
        parsed = json.loads(assessment.to_log_entry())
        assert parsed["assessor_id"] == "compliance-agent-001"

    def test_default_assessor_id_empty(self) -> None:
        assessment = NISTAIRMFRiskAssessment(
            system_id="sys",
            risk_categories=[NISTAIRMFRiskCategory.SECURITY],
            risk_level="low",
            gov_measures=[],
            map_measures=[],
            measure_measures=[],
            manage_measures=[],
            timestamp_utc="2025-01-01T00:00:00Z",
        )
        assert assessment.assessor_id == ""

    def test_content_hash_is_hex_string(self) -> None:
        assessment = self._make_assessment()
        h = assessment.content_hash()
        assert len(h) == 64
        int(h, 16)  # valid hex

    def test_content_hash_stability(self) -> None:
        assessment = self._make_assessment()
        assert assessment.content_hash() == assessment.content_hash()

    def test_content_hash_differs_for_different_data(self) -> None:
        a1 = self._make_assessment()
        a2 = NISTAIRMFRiskAssessment(
            system_id="other_system",
            risk_categories=[NISTAIRMFRiskCategory.HARMFUL_BIAS],
            risk_level="medium",
            gov_measures=["policy_approved"],
            map_measures=["risk_identified"],
            measure_measures=["bias_measured"],
            manage_measures=["bias_mitigated"],
            timestamp_utc="2025-10-01T12:00:00Z",
        )
        assert a1.content_hash() != a2.content_hash()

    def test_to_log_entry_json_serialisable(self) -> None:
        assessment = self._make_assessment()
        json.dumps(json.loads(assessment.to_log_entry()))  # round-trip should not raise


# ---------------------------------------------------------------------------
# NIST_GENAI_HIGH_RISK_ACTIONS
# ---------------------------------------------------------------------------


class TestNISTGenAIHighRiskActions:
    def test_is_frozenset(self) -> None:
        assert isinstance(NIST_GENAI_HIGH_RISK_ACTIONS, frozenset)

    def test_unverified_generation_present(self) -> None:
        assert "unverified_generation" in NIST_GENAI_HIGH_RISK_ACTIONS

    def test_autonomous_decision_present(self) -> None:
        assert "autonomous_decision_without_oversight" in NIST_GENAI_HIGH_RISK_ACTIONS

    def test_share_pii_present(self) -> None:
        assert "share_pii_without_consent" in NIST_GENAI_HIGH_RISK_ACTIONS

    def test_at_least_ten_actions(self) -> None:
        assert len(NIST_GENAI_HIGH_RISK_ACTIONS) >= 10


# ---------------------------------------------------------------------------
# make_nist_ai_rmf_policy
# ---------------------------------------------------------------------------


class TestNISTAIRMFPolicy:
    def test_confabulation_risk_denies_unverified_generation(self) -> None:
        policy = make_nist_ai_rmf_policy(risk_categories=[NISTAIRMFRiskCategory.CONFABULATION])
        permitted, reason = policy.permits("unverified_generation")
        assert not permitted
        assert "unverified_generation" in reason

    def test_confabulation_risk_denies_autonomous_decision(self) -> None:
        policy = make_nist_ai_rmf_policy(risk_categories=[NISTAIRMFRiskCategory.CONFABULATION])
        permitted, _ = policy.permits("autonomous_decision_without_oversight")
        assert not permitted

    def test_data_privacy_risk_denies_pii_sharing(self) -> None:
        policy = make_nist_ai_rmf_policy(risk_categories=[NISTAIRMFRiskCategory.DATA_PRIVACY])
        permitted, reason = policy.permits("share_pii_without_consent")
        assert not permitted
        assert "share_pii_without_consent" in reason

    def test_data_privacy_risk_denies_cross_purpose_use(self) -> None:
        policy = make_nist_ai_rmf_policy(risk_categories=[NISTAIRMFRiskCategory.DATA_PRIVACY])
        permitted, _ = policy.permits("cross_purpose_data_use")
        assert not permitted

    def test_human_ai_configuration_adds_escalation(self) -> None:
        policy = make_nist_ai_rmf_policy(risk_categories=[NISTAIRMFRiskCategory.HUMAN_AI_CONFIGURATION])
        rule = policy.escalation_for("automated_decision")
        assert rule is not None

    def test_escalation_target_default(self) -> None:
        policy = make_nist_ai_rmf_policy(risk_categories=[NISTAIRMFRiskCategory.CONFABULATION])
        rule = policy.escalation_for("unverified_generation")
        assert rule is not None
        assert "officer" in rule.escalate_to or "risk" in rule.escalate_to

    def test_custom_escalation_target(self) -> None:
        policy = make_nist_ai_rmf_policy(
            risk_categories=[NISTAIRMFRiskCategory.CONFABULATION],
            escalate_high_risk_to="ai_governance_board",
        )
        rule = policy.escalation_for("unverified_generation")
        assert rule is not None
        assert rule.escalate_to == "ai_governance_board"

    def test_harmful_bias_risk_denies_unbiased_generation(self) -> None:
        policy = make_nist_ai_rmf_policy(risk_categories=[NISTAIRMFRiskCategory.HARMFUL_BIAS])
        permitted, _ = policy.permits("generate_without_bias_check")
        assert not permitted

    def test_security_risk_denies_content_filter_bypass(self) -> None:
        policy = make_nist_ai_rmf_policy(risk_categories=[NISTAIRMFRiskCategory.SECURITY])
        permitted, _ = policy.permits("bypass_content_filter")
        assert not permitted

    def test_default_all_risks_applied(self) -> None:
        policy = make_nist_ai_rmf_policy()
        # Should deny actions from multiple categories
        perm_unverified, _ = policy.permits("unverified_generation")
        perm_pii, _ = policy.permits("share_pii_without_consent")
        assert not perm_unverified
        assert not perm_pii

    def test_permitted_action_allowed(self) -> None:
        policy = make_nist_ai_rmf_policy(risk_categories=[NISTAIRMFRiskCategory.CONFABULATION])
        permitted, _ = policy.permits("log_risk_assessment")
        assert permitted

    def test_unknown_action_denied(self) -> None:
        policy = make_nist_ai_rmf_policy(risk_categories=[NISTAIRMFRiskCategory.CONFABULATION])
        permitted, _ = policy.permits("completely_unknown_action")
        assert not permitted
