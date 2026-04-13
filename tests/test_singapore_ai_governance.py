"""
Tests for 33_singapore_ai_governance.py — Singapore AI Governance Framework
covering:
  1. SingaporePDPAFilter  — PDPA 2012 §§13, 15A, 26 + AI Advisory Guidelines §4.2
  2. MASFEATFilter        — MAS FEAT Principles §§2.1, 3.3, 4.1, 5.2
  3. AIVerifySingaporeFilter — AI Verify Framework §§3.1, 4.1, 4.2 + IMDA GenAI §5.1
  4. SingaporeCrossBorderFilter — MAS TRM §4.1, PDPA §26 + PDPC TIA, Cloud controls, FAA-N18
  5. FilterResult.is_denied property
  6. Eight ecosystem wrappers (LangChain, CrewAI, AutoGen, SK, LlamaIndex, Haystack, DSPy, MAF)
  7. Edge cases: missing keys, empty dict
"""

from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Module loader — use importlib per task specification
# ---------------------------------------------------------------------------

_MOD_NAME = "mod"

spec = importlib.util.spec_from_file_location(
    _MOD_NAME,
    str(Path(__file__).parent.parent / "examples" / "33_singapore_ai_governance.py"),
)
mod = types.ModuleType(_MOD_NAME)
sys.modules[_MOD_NAME] = mod
spec.loader.exec_module(mod)


# ---------------------------------------------------------------------------
# Helper: fully-compliant document (passes all four filters)
# ---------------------------------------------------------------------------


def _compliant(**overrides):
    """Return a document dict that passes all four filters."""
    defaults: dict = {}
    defaults.update(overrides)
    return defaults


# ===========================================================================
# TestFilterResult — is_denied property
# ===========================================================================


class TestFilterResult:
    """FilterResult.is_denied must be True only for decision == 'DENIED'."""

    def test_is_denied_true_for_denied(self):
        r = mod.FilterResult(filter_name="F", decision="DENIED", regulation="X", reason="Y")
        assert r.is_denied is True

    def test_is_denied_false_for_permitted(self):
        r = mod.FilterResult(filter_name="F", decision="PERMITTED", regulation="X", reason="Y")
        assert r.is_denied is False

    def test_is_denied_false_for_requires_human_review(self):
        r = mod.FilterResult(
            filter_name="F",
            decision="REQUIRES_HUMAN_REVIEW",
            regulation="X",
            reason="Y",
        )
        assert r.is_denied is False

    def test_is_denied_false_for_redacted(self):
        r = mod.FilterResult(filter_name="F", decision="REDACTED", regulation="X", reason="Y")
        assert r.is_denied is False

    def test_filter_result_has_required_fields(self):
        r = mod.FilterResult(filter_name="F", decision="DENIED", regulation="R", reason="Reason")
        assert r.filter_name == "F"
        assert r.decision == "DENIED"
        assert r.regulation == "R"
        assert r.reason == "Reason"


# ===========================================================================
# TestSingaporePDPAFilter
# ===========================================================================


class TestSingaporePDPAFilter:
    """PDPA 2012 §§13, 15A, 26 + Advisory Guidelines on AI 2023 §4.2."""

    def _eval(self, **kwargs):
        return mod.SingaporePDPAFilter().filter(kwargs)

    # --- §13 Consent Obligation: DENIED ---

    def test_personal_data_no_consent_no_legitimate_purpose_denied(self):
        """§13: personal_data_processing + no consent + no legitimate_purpose → DENIED."""
        r = self._eval(personal_data_processing=True, consent_obtained=False, legitimate_purpose=False)
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_personal_data_no_consent_cites_pdpa_s13(self):
        """§13 denial cites PDPA §13."""
        r = self._eval(personal_data_processing=True, consent_obtained=False, legitimate_purpose=False)
        assert "§13" in r.regulation or "13" in r.regulation

    def test_personal_data_no_consent_has_legitimate_purpose_permitted(self):
        """§13: personal_data_processing + no consent BUT has legitimate_purpose → PERMITTED."""
        r = self._eval(personal_data_processing=True, consent_obtained=False, legitimate_purpose=True)
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    def test_personal_data_with_consent_permitted(self):
        """§13: personal_data_processing + consent → PERMITTED."""
        r = self._eval(personal_data_processing=True, consent_obtained=True)
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    # --- §15A Sensitive data: DENIED ---

    def test_health_data_no_enhanced_consent_denied(self):
        """§15A: data_type=health + no enhanced_consent_obtained → DENIED."""
        r = self._eval(data_type="health", enhanced_consent_obtained=False)
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_nric_data_no_enhanced_consent_denied(self):
        """§15A: data_type=nric + no enhanced_consent_obtained → DENIED."""
        r = self._eval(data_type="nric", enhanced_consent_obtained=False)
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_biometric_data_no_enhanced_consent_denied(self):
        """§15A: data_type=biometric + no enhanced_consent_obtained → DENIED."""
        r = self._eval(data_type="biometric", enhanced_consent_obtained=False)
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_sensitive_data_denied_cites_pdpa_s15a(self):
        """§15A denial cites PDPA §15A."""
        r = self._eval(data_type="health", enhanced_consent_obtained=False)
        assert "15A" in r.regulation or "15" in r.regulation

    def test_health_data_with_enhanced_consent_permitted(self):
        """§15A: data_type=health + enhanced_consent_obtained=True → PERMITTED."""
        r = self._eval(data_type="health", enhanced_consent_obtained=True)
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    # --- §26 Cross-border Transfer Limitation: DENIED ---

    def test_cross_border_to_cn_no_contractual_protection_denied(self):
        """§26: cross_border_transfer + CN + no contractual_protection → DENIED."""
        r = self._eval(cross_border_transfer=True, transfer_country="CN", contractual_protection=False)
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_cross_border_to_ru_no_contractual_protection_denied(self):
        """§26: cross_border_transfer + RU + no contractual_protection → DENIED."""
        r = self._eval(cross_border_transfer=True, transfer_country="RU", contractual_protection=False)
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_cross_border_denied_cites_pdpa_s26(self):
        """§26 denial cites PDPA §26."""
        r = self._eval(cross_border_transfer=True, transfer_country="CN", contractual_protection=False)
        assert "26" in r.regulation

    def test_cross_border_to_au_permitted(self):
        """§26: transfer to AU (adequate protection) → PERMITTED."""
        r = self._eval(cross_border_transfer=True, transfer_country="AU")
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    def test_cross_border_to_uk_permitted(self):
        """§26: transfer to UK (adequate protection) → PERMITTED."""
        r = self._eval(cross_border_transfer=True, transfer_country="UK")
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    def test_cross_border_with_contractual_protection_permitted(self):
        """§26: transfer to non-adequate country with contractual_protection=True → PERMITTED."""
        r = self._eval(cross_border_transfer=True, transfer_country="IN", contractual_protection=True)
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    # --- §4.2 Advisory Guidelines on AI: REQUIRES_HUMAN_REVIEW ---

    def test_automated_decision_no_human_review_requires_human_review(self):
        """§4.2: automated_decision_affecting_individual + no human_review_option → REQUIRES_HUMAN_REVIEW."""
        r = self._eval(automated_decision_affecting_individual=True, human_review_option=False)
        assert r.decision == "REQUIRES_HUMAN_REVIEW"
        assert not r.is_denied

    def test_automated_decision_rhr_cites_pdpa_ai_guidelines(self):
        """§4.2 REQUIRES_HUMAN_REVIEW cites Advisory Guidelines §4.2."""
        r = self._eval(automated_decision_affecting_individual=True, human_review_option=False)
        assert "4.2" in r.regulation or "Advisory" in r.regulation or "AI" in r.regulation

    def test_automated_decision_with_human_review_option_permitted(self):
        """§4.2: automated_decision_affecting_individual + human_review_option=True → PERMITTED."""
        r = self._eval(automated_decision_affecting_individual=True, human_review_option=True)
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    # --- Edge cases ---

    def test_empty_dict_permitted(self):
        """Empty document → PERMITTED (no triggering conditions)."""
        r = mod.SingaporePDPAFilter().filter({})
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    def test_filter_name_set(self):
        """filter_name is set on result."""
        r = mod.SingaporePDPAFilter().filter({})
        assert r.filter_name


# ===========================================================================
# TestMASFEATFilter
# ===========================================================================


class TestMASFEATFilter:
    """MAS FEAT Principles §§2.1, 3.3, 4.1, 5.2."""

    def _eval(self, **kwargs):
        return mod.MASFEATFilter().filter(kwargs)

    # --- Fairness §2.1: DENIED ---

    def test_ai_financial_decision_no_fairness_assessment_denied(self):
        """§2.1: ai_financial_decision + no fairness_assessment_documented → DENIED."""
        r = self._eval(ai_financial_decision=True, fairness_assessment_documented=False)
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_fairness_denial_cites_mas_feat_s2_1(self):
        """§2.1 denial cites MAS FEAT §2.1."""
        r = self._eval(ai_financial_decision=True, fairness_assessment_documented=False)
        assert "FEAT" in r.regulation or "2.1" in r.regulation

    def test_ai_financial_decision_with_fairness_assessment_permitted(self):
        """§2.1: ai_financial_decision + fairness_assessment_documented=True → PERMITTED."""
        r = self._eval(ai_financial_decision=True, fairness_assessment_documented=True)
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    # --- Accountability §4.1: DENIED ---

    def test_ai_system_no_human_accountability_denied(self):
        """§4.1: ai_system_deployed + no human_accountability_assigned → DENIED."""
        r = self._eval(ai_system_deployed=True, human_accountability_assigned=False, audit_trail_present=True)
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_ai_system_no_audit_trail_denied(self):
        """§4.1: ai_system_deployed + no audit_trail_present → DENIED."""
        r = self._eval(ai_system_deployed=True, human_accountability_assigned=True, audit_trail_present=False)
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_accountability_denial_cites_mas_feat_s4_1(self):
        """§4.1 denial cites MAS FEAT §4.1."""
        r = self._eval(ai_system_deployed=True, human_accountability_assigned=False, audit_trail_present=True)
        assert "4.1" in r.regulation or "FEAT" in r.regulation

    def test_ai_system_with_accountability_and_audit_permitted(self):
        """§4.1: ai_system_deployed + all controls present → PERMITTED."""
        r = self._eval(ai_system_deployed=True, human_accountability_assigned=True, audit_trail_present=True)
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    # --- Transparency §5.2: DENIED ---

    def test_customer_facing_ai_no_explainability_denied(self):
        """§5.2: customer_facing_ai + no explainability_documented → DENIED."""
        r = self._eval(customer_facing_ai=True, explainability_documented=False)
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_transparency_denial_cites_mas_feat_s5_2(self):
        """§5.2 denial cites MAS FEAT §5.2."""
        r = self._eval(customer_facing_ai=True, explainability_documented=False)
        assert "5.2" in r.regulation or "FEAT" in r.regulation

    def test_customer_facing_ai_with_explainability_permitted(self):
        """§5.2: customer_facing_ai + explainability_documented=True → PERMITTED."""
        r = self._eval(customer_facing_ai=True, explainability_documented=True)
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    # --- Ethics §3.3: REQUIRES_HUMAN_REVIEW ---

    def test_ai_model_no_robustness_testing_requires_human_review(self):
        """§3.3: ai_model_in_production + no robustness_testing_documented → REQUIRES_HUMAN_REVIEW."""
        r = self._eval(ai_model_in_production=True, robustness_testing_documented=False)
        assert r.decision == "REQUIRES_HUMAN_REVIEW"
        assert not r.is_denied

    def test_robustness_rhr_cites_mas_feat_s3_3(self):
        """§3.3 REQUIRES_HUMAN_REVIEW cites MAS FEAT §3.3."""
        r = self._eval(ai_model_in_production=True, robustness_testing_documented=False)
        assert "3.3" in r.regulation or "FEAT" in r.regulation

    def test_ai_model_with_robustness_testing_permitted(self):
        """§3.3: ai_model_in_production + robustness_testing_documented=True → PERMITTED."""
        r = self._eval(ai_model_in_production=True, robustness_testing_documented=True)
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    # --- Edge cases ---

    def test_empty_dict_permitted(self):
        """Empty document → PERMITTED."""
        r = mod.MASFEATFilter().filter({})
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    def test_filter_name_set(self):
        """filter_name is set on result."""
        r = mod.MASFEATFilter().filter({})
        assert r.filter_name


# ===========================================================================
# TestAIVerifySingaporeFilter
# ===========================================================================


class TestAIVerifySingaporeFilter:
    """AI Verify Framework §§3.1, 4.1, 4.2 + IMDA GenAI Framework 2024 §5.1."""

    def _eval(self, **kwargs):
        return mod.AIVerifySingaporeFilter().filter(kwargs)

    # --- §3.1 High-impact AI without self-assessment: DENIED ---

    def test_high_impact_ai_no_self_assessment_denied(self):
        """§3.1: high_impact_ai_system + no ai_verify_self_assessment_completed → DENIED."""
        r = self._eval(high_impact_ai_system=True, ai_verify_self_assessment_completed=False)
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_self_assessment_denial_cites_ai_verify_s3_1(self):
        """§3.1 denial cites AI Verify §3.1."""
        r = self._eval(high_impact_ai_system=True, ai_verify_self_assessment_completed=False)
        assert "3.1" in r.regulation or "AI Verify" in r.regulation

    def test_high_impact_ai_with_self_assessment_permitted(self):
        """§3.1: high_impact_ai_system + ai_verify_self_assessment_completed=True → PERMITTED."""
        r = self._eval(high_impact_ai_system=True, ai_verify_self_assessment_completed=True)
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    # --- §4.2 Explainability Testing: DENIED ---

    def test_ai_deployed_no_explainability_testing_denied(self):
        """§4.2: ai_system_deployed + no explainability_testing_completed → DENIED."""
        r = self._eval(ai_system_deployed=True, explainability_testing_completed=False)
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_explainability_denial_cites_ai_verify_s4_2(self):
        """§4.2 denial cites AI Verify §4.2."""
        r = self._eval(ai_system_deployed=True, explainability_testing_completed=False)
        assert "4.2" in r.regulation or "AI Verify" in r.regulation

    def test_ai_deployed_with_explainability_testing_permitted(self):
        """§4.2: ai_system_deployed + explainability_testing_completed=True → PERMITTED."""
        r = self._eval(ai_system_deployed=True, explainability_testing_completed=True)
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    # --- IMDA GenAI §5.1: DENIED ---

    def test_genai_no_imda_framework_compliance_denied(self):
        """IMDA GenAI §5.1: generative_ai_system + no imda_genai_framework_compliant → DENIED."""
        r = self._eval(generative_ai_system=True, imda_genai_framework_compliant=False)
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_genai_denial_cites_imda_genai_s5_1(self):
        """IMDA GenAI §5.1 denial cites IMDA GenAI Framework §5.1."""
        r = self._eval(generative_ai_system=True, imda_genai_framework_compliant=False)
        assert "5.1" in r.regulation or "IMDA" in r.regulation or "GenAI" in r.regulation

    def test_genai_with_imda_compliance_permitted(self):
        """IMDA GenAI §5.1: generative_ai_system + imda_genai_framework_compliant=True → PERMITTED."""
        r = self._eval(generative_ai_system=True, imda_genai_framework_compliant=True)
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    # --- §4.1 Fairness Testing: REQUIRES_HUMAN_REVIEW ---

    def test_bias_detected_no_mitigation_requires_human_review(self):
        """§4.1: bias_detected_in_protected_characteristics + no bias_mitigation_applied → REQUIRES_HUMAN_REVIEW."""
        r = self._eval(bias_detected_in_protected_characteristics=True, bias_mitigation_applied=False)
        assert r.decision == "REQUIRES_HUMAN_REVIEW"
        assert not r.is_denied

    def test_fairness_rhr_cites_ai_verify_s4_1(self):
        """§4.1 REQUIRES_HUMAN_REVIEW cites AI Verify §4.1."""
        r = self._eval(bias_detected_in_protected_characteristics=True, bias_mitigation_applied=False)
        assert "4.1" in r.regulation or "AI Verify" in r.regulation

    def test_bias_detected_with_mitigation_permitted(self):
        """§4.1: bias_detected + bias_mitigation_applied=True → PERMITTED."""
        r = self._eval(bias_detected_in_protected_characteristics=True, bias_mitigation_applied=True)
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    # --- Edge cases ---

    def test_empty_dict_permitted(self):
        """Empty document → PERMITTED."""
        r = mod.AIVerifySingaporeFilter().filter({})
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    def test_filter_name_set(self):
        """filter_name is set on result."""
        r = mod.AIVerifySingaporeFilter().filter({})
        assert r.filter_name


# ===========================================================================
# TestSingaporeCrossBorderFilter
# ===========================================================================


class TestSingaporeCrossBorderFilter:
    """Cross-border AI data flows under Singapore frameworks."""

    def _eval(self, **kwargs):
        return mod.SingaporeCrossBorderFilter().filter(kwargs)

    # --- MAS TRM §4.1: DENIED ---

    def test_financial_ai_data_non_mas_entity_no_safeguards_denied(self):
        """MAS TRM §4.1: financial AI data + non-MAS entity + no safeguards → DENIED."""
        r = self._eval(
            financial_ai_data_transfer=True,
            recipient_mas_supervised=False,
            contractual_safeguards_documented=False,
        )
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_mas_trm_denial_cites_s4_1(self):
        """MAS TRM §4.1 denial cites MAS TRM §4.1."""
        r = self._eval(
            financial_ai_data_transfer=True,
            recipient_mas_supervised=False,
            contractual_safeguards_documented=False,
        )
        assert "4.1" in r.regulation or "MAS" in r.regulation

    def test_financial_ai_data_mas_supervised_permitted(self):
        """MAS TRM §4.1: financial AI data + recipient_mas_supervised=True → PERMITTED."""
        r = self._eval(
            financial_ai_data_transfer=True,
            recipient_mas_supervised=True,
        )
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    # --- PDPA §26 + PDPC TIA: DENIED ---

    def test_personal_data_to_cn_no_pdpc_approval_denied(self):
        """PDPA §26: personal data to CN + no pdpc_adequacy_approval → DENIED."""
        r = self._eval(personal_data_transfer_country="CN", pdpc_adequacy_approval=False)
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_personal_data_to_ru_no_pdpc_approval_denied(self):
        """PDPA §26: personal data to RU + no pdpc_adequacy_approval → DENIED."""
        r = self._eval(personal_data_transfer_country="RU", pdpc_adequacy_approval=False)
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_pdpc_tia_denial_cites_pdpa_s26(self):
        """PDPA §26 denial cites PDPA §26."""
        r = self._eval(personal_data_transfer_country="CN", pdpc_adequacy_approval=False)
        assert "26" in r.regulation or "PDPA" in r.regulation

    def test_personal_data_to_cn_with_pdpc_approval_permitted(self):
        """PDPA §26: personal data to CN + pdpc_adequacy_approval=True → PERMITTED."""
        r = self._eval(personal_data_transfer_country="CN", pdpc_adequacy_approval=True)
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    # --- MAS Cloud Provider controls: DENIED ---

    def test_mas_regulated_entity_non_whitelisted_cloud_denied(self):
        """MAS Cloud: serves_mas_regulated_entity + non-whitelisted region → DENIED."""
        r = self._eval(serves_mas_regulated_entity=True, cloud_region="aws_us_east_1")
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_mas_cloud_denial_cites_mas_cloud_controls(self):
        """MAS Cloud denial cites MAS Cloud Provider controls."""
        r = self._eval(serves_mas_regulated_entity=True, cloud_region="gcp_us_central1")
        assert "MAS" in r.regulation or "Cloud" in r.regulation

    def test_mas_regulated_entity_aws_singapore_permitted(self):
        """MAS Cloud: serves_mas_regulated_entity + aws_singapore → PERMITTED."""
        r = self._eval(serves_mas_regulated_entity=True, cloud_region="aws_singapore")
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    def test_mas_regulated_entity_gcp_singapore_permitted(self):
        """MAS Cloud: serves_mas_regulated_entity + gcp_singapore → PERMITTED."""
        r = self._eval(serves_mas_regulated_entity=True, cloud_region="gcp_singapore")
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    # --- MAS AML/CFT FAA-N18: REQUIRES_HUMAN_REVIEW ---

    def test_training_data_to_kp_requires_human_review(self):
        """FAA-N18: training_data_export_jurisdiction=KP (FATF non-compliant) → REQUIRES_HUMAN_REVIEW."""
        r = self._eval(training_data_export_jurisdiction="KP")
        assert r.decision == "REQUIRES_HUMAN_REVIEW"
        assert not r.is_denied

    def test_training_data_to_ir_requires_human_review(self):
        """FAA-N18: training_data_export_jurisdiction=IR → REQUIRES_HUMAN_REVIEW."""
        r = self._eval(training_data_export_jurisdiction="IR")
        assert r.decision == "REQUIRES_HUMAN_REVIEW"
        assert not r.is_denied

    def test_fatf_rhr_cites_faa_n18(self):
        """FAA-N18 REQUIRES_HUMAN_REVIEW cites MAS AML/CFT Notice FAA-N18."""
        r = self._eval(training_data_export_jurisdiction="KP")
        assert "FAA-N18" in r.regulation or "AML" in r.regulation or "MAS" in r.regulation

    def test_training_data_to_sg_permitted(self):
        """No FATF concern for Singapore-domestic training data → PERMITTED."""
        r = self._eval(training_data_export_jurisdiction="SG")
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    # --- Edge cases ---

    def test_empty_dict_permitted(self):
        """Empty document → PERMITTED."""
        r = mod.SingaporeCrossBorderFilter().filter({})
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    def test_filter_name_set(self):
        """filter_name is set on result."""
        r = mod.SingaporeCrossBorderFilter().filter({})
        assert r.filter_name


# ===========================================================================
# TestIntegrationWrappers — all 8 ecosystem wrappers
# ===========================================================================


class TestIntegrationWrappers:
    """All 8 ecosystem wrappers: DENIED raises PermissionError; PERMITTED passes through."""

    # -----------------------------------------------------------------------
    # LangChain
    # -----------------------------------------------------------------------

    def test_langchain_instantiates(self):
        """SingaporeLangChainPolicyGuard instantiates with a filter."""
        g = mod.SingaporeLangChainPolicyGuard(mod.SingaporePDPAFilter())
        assert g is not None

    def test_langchain_permitted_returns_doc(self):
        """LangChain: PERMITTED doc is returned unchanged."""
        g = mod.SingaporeLangChainPolicyGuard(mod.SingaporePDPAFilter())
        doc = {"note": "clean"}
        result = g.process(doc)
        assert result is doc

    def test_langchain_denied_raises_permission_error(self):
        """LangChain: DENIED raises PermissionError with regulation."""
        g = mod.SingaporeLangChainPolicyGuard(mod.SingaporePDPAFilter())
        with pytest.raises(PermissionError) as exc_info:
            g.process({"personal_data_processing": True, "consent_obtained": False, "legitimate_purpose": False})
        assert exc_info.value.args[0]  # message is non-empty (regulation citation)

    def test_langchain_permission_error_contains_regulation(self):
        """PermissionError message contains PDPA regulation string."""
        g = mod.SingaporeLangChainPolicyGuard(mod.SingaporePDPAFilter())
        with pytest.raises(PermissionError) as exc_info:
            g.process({"personal_data_processing": True, "consent_obtained": False, "legitimate_purpose": False})
        assert "PDPA" in str(exc_info.value) or "13" in str(exc_info.value)

    # -----------------------------------------------------------------------
    # CrewAI
    # -----------------------------------------------------------------------

    def test_crewai_instantiates(self):
        """SingaporeCrewAIGovernanceGuard instantiates with a filter."""
        g = mod.SingaporeCrewAIGovernanceGuard(mod.MASFEATFilter())
        assert g is not None

    def test_crewai_permitted_returns_doc(self):
        """CrewAI: PERMITTED doc is returned unchanged."""
        g = mod.SingaporeCrewAIGovernanceGuard(mod.MASFEATFilter())
        doc = {"ok": True}
        result = g._run(doc)
        assert result is doc

    def test_crewai_denied_raises_permission_error(self):
        """CrewAI: DENIED raises PermissionError."""
        g = mod.SingaporeCrewAIGovernanceGuard(mod.MASFEATFilter())
        with pytest.raises(PermissionError):
            g._run({"ai_financial_decision": True, "fairness_assessment_documented": False})

    def test_crewai_requires_human_review_returns_doc(self):
        """CrewAI: REQUIRES_HUMAN_REVIEW does NOT raise — returns doc."""
        g = mod.SingaporeCrewAIGovernanceGuard(mod.MASFEATFilter())
        doc = {"ai_model_in_production": True, "robustness_testing_documented": False}
        result = g._run(doc)
        assert result is doc

    # -----------------------------------------------------------------------
    # AutoGen
    # -----------------------------------------------------------------------

    def test_autogen_instantiates(self):
        """SingaporeAutoGenGovernedAgent instantiates with a filter."""
        a = mod.SingaporeAutoGenGovernedAgent(mod.AIVerifySingaporeFilter())
        assert a is not None

    def test_autogen_permitted_returns_doc(self):
        """AutoGen: PERMITTED doc is returned unchanged."""
        a = mod.SingaporeAutoGenGovernedAgent(mod.AIVerifySingaporeFilter())
        doc = {"safe": True}
        result = a.generate_reply(doc)
        assert result is doc

    def test_autogen_denied_raises_permission_error(self):
        """AutoGen: DENIED raises PermissionError."""
        a = mod.SingaporeAutoGenGovernedAgent(mod.AIVerifySingaporeFilter())
        with pytest.raises(PermissionError):
            a.generate_reply({"high_impact_ai_system": True, "ai_verify_self_assessment_completed": False})

    def test_autogen_requires_human_review_returns_doc(self):
        """AutoGen: REQUIRES_HUMAN_REVIEW does NOT raise — returns doc."""
        a = mod.SingaporeAutoGenGovernedAgent(mod.AIVerifySingaporeFilter())
        doc = {"bias_detected_in_protected_characteristics": True, "bias_mitigation_applied": False}
        result = a.generate_reply(doc)
        assert result is doc

    # -----------------------------------------------------------------------
    # Semantic Kernel
    # -----------------------------------------------------------------------

    def test_semantic_kernel_instantiates(self):
        """SingaporeSemanticKernelPlugin instantiates with a filter."""
        p = mod.SingaporeSemanticKernelPlugin(mod.SingaporeCrossBorderFilter())
        assert p is not None

    def test_semantic_kernel_permitted_returns_doc(self):
        """Semantic Kernel: PERMITTED doc is returned unchanged."""
        p = mod.SingaporeSemanticKernelPlugin(mod.SingaporeCrossBorderFilter())
        doc = {"nothing": "sensitive"}
        result = p.enforce_governance(doc)
        assert result is doc

    def test_semantic_kernel_denied_raises_permission_error(self):
        """Semantic Kernel: DENIED raises PermissionError."""
        p = mod.SingaporeSemanticKernelPlugin(mod.SingaporeCrossBorderFilter())
        with pytest.raises(PermissionError):
            p.enforce_governance(
                {
                    "financial_ai_data_transfer": True,
                    "recipient_mas_supervised": False,
                    "contractual_safeguards_documented": False,
                }
            )

    def test_semantic_kernel_requires_human_review_returns_doc(self):
        """Semantic Kernel: REQUIRES_HUMAN_REVIEW does NOT raise — returns doc."""
        p = mod.SingaporeSemanticKernelPlugin(mod.SingaporeCrossBorderFilter())
        doc = {"training_data_export_jurisdiction": "KP"}
        result = p.enforce_governance(doc)
        assert result is doc

    # -----------------------------------------------------------------------
    # LlamaIndex
    # -----------------------------------------------------------------------

    def test_llama_index_instantiates(self):
        """SingaporeLlamaIndexWorkflowGuard instantiates with a filter."""
        g = mod.SingaporeLlamaIndexWorkflowGuard(mod.SingaporePDPAFilter())
        assert g is not None

    def test_llama_index_permitted_returns_doc(self):
        """LlamaIndex: PERMITTED doc is returned unchanged."""
        g = mod.SingaporeLlamaIndexWorkflowGuard(mod.SingaporePDPAFilter())
        doc = {"payload": "clean"}
        result = g.process_event(doc)
        assert result is doc

    def test_llama_index_denied_raises_permission_error(self):
        """LlamaIndex: DENIED raises PermissionError."""
        g = mod.SingaporeLlamaIndexWorkflowGuard(mod.SingaporePDPAFilter())
        with pytest.raises(PermissionError):
            g.process_event({"data_type": "nric", "enhanced_consent_obtained": False})

    def test_llama_index_requires_human_review_returns_doc(self):
        """LlamaIndex: REQUIRES_HUMAN_REVIEW does NOT raise — returns doc."""
        g = mod.SingaporeLlamaIndexWorkflowGuard(mod.SingaporePDPAFilter())
        doc = {"automated_decision_affecting_individual": True, "human_review_option": False}
        result = g.process_event(doc)
        assert result is doc

    # -----------------------------------------------------------------------
    # Haystack
    # -----------------------------------------------------------------------

    def test_haystack_instantiates(self):
        """SingaporeHaystackGovernanceComponent instantiates with a filter."""
        c = mod.SingaporeHaystackGovernanceComponent(mod.MASFEATFilter())
        assert c is not None

    def test_haystack_returns_all_clean_docs(self):
        """Haystack: all clean docs returned unchanged."""
        c = mod.SingaporeHaystackGovernanceComponent(mod.MASFEATFilter())
        docs = [{"id": 1}, {"id": 2}]
        result = c.run(docs)
        assert len(result["documents"]) == 2

    def test_haystack_excludes_denied_docs(self):
        """Haystack: DENIED document is excluded from output."""
        c = mod.SingaporeHaystackGovernanceComponent(mod.MASFEATFilter())
        clean = {"id": "ok"}
        denied = {"ai_financial_decision": True, "fairness_assessment_documented": False}
        result = c.run([clean, denied])
        assert len(result["documents"]) == 1
        assert result["documents"][0] is clean

    def test_haystack_requires_human_review_passes_through(self):
        """Haystack: REQUIRES_HUMAN_REVIEW doc is NOT excluded."""
        c = mod.SingaporeHaystackGovernanceComponent(mod.MASFEATFilter())
        rhr_doc = {"ai_model_in_production": True, "robustness_testing_documented": False}
        result = c.run([rhr_doc])
        assert len(result["documents"]) == 1

    # -----------------------------------------------------------------------
    # DSPy
    # -----------------------------------------------------------------------

    def test_dspy_instantiates(self):
        """SingaporeDSPyGovernanceModule instantiates with a filter and module."""
        dummy = lambda doc, **kw: doc  # noqa: E731
        m = mod.SingaporeDSPyGovernanceModule(mod.AIVerifySingaporeFilter(), dummy)
        assert m is not None

    def test_dspy_permitted_calls_wrapped_module(self):
        """DSPy: PERMITTED doc is forwarded to the wrapped module."""
        sentinel = object()
        dummy = lambda doc, **kw: sentinel  # noqa: E731
        m = mod.SingaporeDSPyGovernanceModule(mod.AIVerifySingaporeFilter(), dummy)
        result = m.forward({"id": "clean"})
        assert result is sentinel

    def test_dspy_denied_raises_permission_error(self):
        """DSPy: DENIED raises PermissionError."""
        dummy = lambda doc, **kw: doc  # noqa: E731
        m = mod.SingaporeDSPyGovernanceModule(mod.AIVerifySingaporeFilter(), dummy)
        with pytest.raises(PermissionError):
            m.forward({"high_impact_ai_system": True, "ai_verify_self_assessment_completed": False})

    def test_dspy_requires_human_review_calls_wrapped_module(self):
        """DSPy: REQUIRES_HUMAN_REVIEW doc is forwarded to the wrapped module (no raise)."""
        sentinel = object()
        dummy = lambda doc, **kw: sentinel  # noqa: E731
        m = mod.SingaporeDSPyGovernanceModule(mod.AIVerifySingaporeFilter(), dummy)
        doc = {"bias_detected_in_protected_characteristics": True, "bias_mitigation_applied": False}
        result = m.forward(doc)
        assert result is sentinel

    # -----------------------------------------------------------------------
    # MAF (Microsoft Agent Framework)
    # -----------------------------------------------------------------------

    def test_maf_instantiates(self):
        """SingaporeMAFPolicyMiddleware instantiates with a filter."""
        mw = mod.SingaporeMAFPolicyMiddleware(mod.SingaporeCrossBorderFilter())
        assert mw is not None

    def test_maf_permitted_calls_next_handler(self):
        """MAF: PERMITTED message is forwarded to next_handler."""
        mw = mod.SingaporeMAFPolicyMiddleware(mod.SingaporeCrossBorderFilter())
        called = []
        mw.process({"id": "clean"}, lambda msg: called.append(msg))
        assert len(called) == 1

    def test_maf_denied_raises_permission_error(self):
        """MAF: DENIED raises PermissionError."""
        mw = mod.SingaporeMAFPolicyMiddleware(mod.SingaporeCrossBorderFilter())
        with pytest.raises(PermissionError):
            mw.process(
                {
                    "financial_ai_data_transfer": True,
                    "recipient_mas_supervised": False,
                    "contractual_safeguards_documented": False,
                },
                lambda msg: None,
            )

    def test_maf_requires_human_review_calls_next_handler(self):
        """MAF: REQUIRES_HUMAN_REVIEW message is forwarded to next_handler (no raise)."""
        mw = mod.SingaporeMAFPolicyMiddleware(mod.SingaporeCrossBorderFilter())
        called = []
        mw.process({"training_data_export_jurisdiction": "KP"}, lambda msg: called.append(msg))
        assert len(called) == 1

    def test_maf_permission_error_contains_regulation(self):
        """MAF: PermissionError message contains MAS regulation string."""
        mw = mod.SingaporeMAFPolicyMiddleware(mod.SingaporeCrossBorderFilter())
        with pytest.raises(PermissionError) as exc_info:
            mw.process(
                {
                    "financial_ai_data_transfer": True,
                    "recipient_mas_supervised": False,
                    "contractual_safeguards_documented": False,
                },
                lambda msg: None,
            )
        assert "MAS" in str(exc_info.value) or "4.1" in str(exc_info.value)


# ===========================================================================
# TestEdgeCases — missing keys and empty dict across all filters
# ===========================================================================


class TestEdgeCases:
    """Missing keys and empty dict edge cases."""

    def test_pdpa_missing_all_keys_permitted(self):
        """PDPA: dict with unrelated keys → PERMITTED."""
        r = mod.SingaporePDPAFilter().filter({"foo": "bar"})
        assert r.decision == "PERMITTED"

    def test_mas_feat_missing_all_keys_permitted(self):
        """MAS FEAT: dict with unrelated keys → PERMITTED."""
        r = mod.MASFEATFilter().filter({"foo": "bar"})
        assert r.decision == "PERMITTED"

    def test_ai_verify_missing_all_keys_permitted(self):
        """AI Verify: dict with unrelated keys → PERMITTED."""
        r = mod.AIVerifySingaporeFilter().filter({"foo": "bar"})
        assert r.decision == "PERMITTED"

    def test_cross_border_missing_all_keys_permitted(self):
        """Cross-border: dict with unrelated keys → PERMITTED."""
        r = mod.SingaporeCrossBorderFilter().filter({"foo": "bar"})
        assert r.decision == "PERMITTED"

    def test_all_filters_empty_dict_permitted(self):
        """All four filters return PERMITTED for empty dict."""
        for cls in (
            mod.SingaporePDPAFilter,
            mod.MASFEATFilter,
            mod.AIVerifySingaporeFilter,
            mod.SingaporeCrossBorderFilter,
        ):
            r = cls().filter({})
            assert r.decision == "PERMITTED", f"{cls.__name__} failed on empty dict"

    def test_pdpa_personal_data_processing_true_consent_false_no_legitimate_purpose_key(self):
        """PDPA §13: explicit False consent + no legitimate_purpose key → DENIED."""
        r = mod.SingaporePDPAFilter().filter({"personal_data_processing": True, "consent_obtained": False})
        assert r.decision == "DENIED"

    def test_cross_border_kp_restricted(self):
        """Cross-border: PDPA §26 blocks transfer to KP (also FATF blacklisted)."""
        r = mod.SingaporeCrossBorderFilter().filter(
            {"personal_data_transfer_country": "KP", "pdpc_adequacy_approval": False}
        )
        assert r.decision == "DENIED"

    def test_filter_result_decision_defaults_to_permitted(self):
        """FilterResult default decision is PERMITTED."""
        r = mod.FilterResult(filter_name="F")
        assert r.decision == "PERMITTED"
        assert not r.is_denied
