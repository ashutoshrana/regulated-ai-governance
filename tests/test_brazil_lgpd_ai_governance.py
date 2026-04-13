"""
Tests for 36_brazil_lgpd_ai_governance.py — Brazil AI Governance Framework
covering:
  1. BrazilLGPDFilter       — LGPD Arts. 7, 11, 20, 33
  2. ANPDAIFilter            — LGPD Arts. 9(V), 10 §3, 38 + ANPD Resolutions
  3. BrazilSectoralAIFilter  — CMN/BCdB, CFM, ANATEL, TSE
  4. BrazilCrossBorderFilter — LGPD Art. 33 + AML + FATF + ANPD
  5. FilterResult.is_denied property
  6. Eight ecosystem wrappers (LangChain, CrewAI, AutoGen, SK, LlamaIndex,
     Haystack, DSPy, MAF)
  7. Edge cases: missing keys, empty dict
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import types

import pytest

# ---------------------------------------------------------------------------
# Module loader — use importlib per task specification
# ---------------------------------------------------------------------------

_MOD_NAME = "mod_brazil"

spec = importlib.util.spec_from_file_location(
    _MOD_NAME,
    str(Path(__file__).parent.parent / "examples" / "36_brazil_lgpd_ai_governance.py"),
)
mod = types.ModuleType(_MOD_NAME)
sys.modules[_MOD_NAME] = mod
spec.loader.exec_module(mod)


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

    def test_default_decision_is_permitted(self):
        r = mod.FilterResult(filter_name="F")
        assert r.decision == "PERMITTED"
        assert not r.is_denied


# ===========================================================================
# TestBrazilLGPDFilter — LGPD Arts. 7, 11, 20, 33
# ===========================================================================


class TestBrazilLGPDFilter:
    """LGPD — four principal controls: Arts. 7, 11, 20, 33."""

    def _eval(self, **kwargs):
        return mod.BrazilLGPDFilter().filter(kwargs)

    # --- Art. 7 Lawfulness — DENIED ---

    def test_personal_data_no_legal_basis_denied(self):
        r = self._eval(personal_data_processing=True, legal_basis="")
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_personal_data_invalid_legal_basis_denied(self):
        r = self._eval(personal_data_processing=True, legal_basis="preference")
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_personal_data_no_basis_key_denied(self):
        r = self._eval(personal_data_processing=True)
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_personal_data_denied_cites_lgpd_art_7(self):
        r = self._eval(personal_data_processing=True, legal_basis="")
        assert "7" in r.regulation or "Lawfulness" in r.regulation

    def test_personal_data_consent_basis_permitted(self):
        r = self._eval(personal_data_processing=True, legal_basis="consent")
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    def test_personal_data_contract_performance_permitted(self):
        r = self._eval(personal_data_processing=True, legal_basis="contract_performance")
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    def test_personal_data_legal_obligation_permitted(self):
        r = self._eval(personal_data_processing=True, legal_basis="legal_obligation")
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    def test_personal_data_legitimate_interests_permitted(self):
        r = self._eval(personal_data_processing=True, legal_basis="legitimate_interests")
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    def test_personal_data_health_protection_permitted(self):
        r = self._eval(personal_data_processing=True, legal_basis="health_protection")
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    def test_personal_data_research_basis_permitted(self):
        r = self._eval(personal_data_processing=True, legal_basis="research")
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    # --- Art. 11 Sensitive Data — DENIED ---

    def test_health_data_no_explicit_consent_denied(self):
        r = self._eval(
            data_category="health",
            explicit_consent_obtained=False,
            legal_obligation_applies=False,
        )
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_biometric_data_no_explicit_consent_denied(self):
        r = self._eval(
            data_category="biometric",
            explicit_consent_obtained=False,
            legal_obligation_applies=False,
        )
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_genetic_data_no_explicit_consent_denied(self):
        r = self._eval(
            data_category="genetic",
            explicit_consent_obtained=False,
            legal_obligation_applies=False,
        )
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_racial_ethnic_origin_no_explicit_consent_denied(self):
        r = self._eval(
            data_category="racial_ethnic_origin",
            explicit_consent_obtained=False,
            legal_obligation_applies=False,
        )
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_political_opinion_no_explicit_consent_denied(self):
        r = self._eval(
            data_category="political_opinion",
            explicit_consent_obtained=False,
            legal_obligation_applies=False,
        )
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_union_membership_no_explicit_consent_denied(self):
        r = self._eval(
            data_category="union_membership",
            explicit_consent_obtained=False,
            legal_obligation_applies=False,
        )
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_religious_belief_no_explicit_consent_denied(self):
        r = self._eval(
            data_category="religious_belief",
            explicit_consent_obtained=False,
            legal_obligation_applies=False,
        )
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_sensitive_denied_cites_lgpd_art_11(self):
        r = self._eval(
            data_category="health",
            explicit_consent_obtained=False,
            legal_obligation_applies=False,
        )
        assert "11" in r.regulation or "Sensitive" in r.regulation

    def test_health_data_with_explicit_consent_permitted(self):
        r = self._eval(data_category="health", explicit_consent_obtained=True)
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    def test_health_data_with_legal_obligation_permitted(self):
        r = self._eval(
            data_category="health",
            explicit_consent_obtained=False,
            legal_obligation_applies=True,
        )
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    def test_non_sensitive_data_category_permitted(self):
        r = self._eval(data_category="name")
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    # --- Art. 33 International Transfer — DENIED ---

    def test_cross_border_to_cn_no_safeguards_denied(self):
        r = self._eval(
            cross_border_transfer=True,
            transfer_country="CN",
            standard_contractual_clauses_in_place=False,
            binding_corporate_rules_in_place=False,
            anpd_specific_authorization=False,
        )
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_cross_border_to_ru_no_safeguards_denied(self):
        r = self._eval(
            cross_border_transfer=True,
            transfer_country="RU",
            standard_contractual_clauses_in_place=False,
            binding_corporate_rules_in_place=False,
            anpd_specific_authorization=False,
        )
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_cross_border_to_us_no_safeguards_denied(self):
        r = self._eval(
            cross_border_transfer=True,
            transfer_country="US",
            standard_contractual_clauses_in_place=False,
            binding_corporate_rules_in_place=False,
            anpd_specific_authorization=False,
        )
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_cross_border_denied_cites_lgpd_art_33(self):
        r = self._eval(
            cross_border_transfer=True,
            transfer_country="CN",
            standard_contractual_clauses_in_place=False,
            binding_corporate_rules_in_place=False,
            anpd_specific_authorization=False,
        )
        assert "33" in r.regulation or "International Transfer" in r.regulation

    def test_cross_border_to_de_eu_permitted(self):
        r = self._eval(cross_border_transfer=True, transfer_country="DE")
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    def test_cross_border_to_fr_eu_permitted(self):
        r = self._eval(cross_border_transfer=True, transfer_country="FR")
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    def test_cross_border_to_uk_permitted(self):
        r = self._eval(cross_border_transfer=True, transfer_country="UK")
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    def test_cross_border_to_us_with_sccs_permitted(self):
        r = self._eval(
            cross_border_transfer=True,
            transfer_country="US",
            standard_contractual_clauses_in_place=True,
        )
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    def test_cross_border_to_cn_with_bcr_permitted(self):
        r = self._eval(
            cross_border_transfer=True,
            transfer_country="CN",
            binding_corporate_rules_in_place=True,
        )
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    def test_cross_border_with_anpd_authorization_permitted(self):
        r = self._eval(
            cross_border_transfer=True,
            transfer_country="IN",
            anpd_specific_authorization=True,
        )
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    # --- Art. 20 Automated Decisions — REQUIRES_HUMAN_REVIEW ---

    def test_automated_decision_no_human_review_rhr(self):
        r = self._eval(
            automated_decision_significant_effect=True,
            human_review_mechanism_available=False,
        )
        assert r.decision == "REQUIRES_HUMAN_REVIEW"
        assert not r.is_denied

    def test_automated_decision_rhr_cites_lgpd_art_20(self):
        r = self._eval(
            automated_decision_significant_effect=True,
            human_review_mechanism_available=False,
        )
        assert "20" in r.regulation or "Automated" in r.regulation

    def test_automated_decision_with_human_review_permitted(self):
        r = self._eval(
            automated_decision_significant_effect=True,
            human_review_mechanism_available=True,
        )
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    # --- Edge cases ---

    def test_empty_dict_permitted(self):
        r = mod.BrazilLGPDFilter().filter({})
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    def test_filter_name_set(self):
        r = mod.BrazilLGPDFilter().filter({})
        assert r.filter_name

    def test_filter_frozen_dataclass(self):
        f = mod.BrazilLGPDFilter()
        with pytest.raises((AttributeError, TypeError)):
            f.FILTER_NAME = "modified"  # type: ignore[misc]


# ===========================================================================
# TestANPDAIFilter — LGPD Arts. 9(V), 10 §3, 38 + ANPD Resolutions
# ===========================================================================


class TestANPDAIFilter:
    """ANPD AI governance — four principal controls."""

    def _eval(self, **kwargs):
        return mod.ANPDAIFilter().filter(kwargs)

    # --- LGPD Art. 38 + ANPD Resolution 02/2022 — high-risk AI without DPIA: DENIED ---

    def test_biometric_identification_no_dpia_denied(self):
        r = self._eval(processing_type="biometric_identification", dpia_completed=False)
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_large_scale_profiling_no_dpia_denied(self):
        r = self._eval(processing_type="large_scale_profiling", dpia_completed=False)
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_automated_decision_making_no_dpia_denied(self):
        r = self._eval(processing_type="automated_decision_making", dpia_completed=False)
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_sensitive_data_processing_no_dpia_denied(self):
        r = self._eval(processing_type="sensitive_data_processing", dpia_completed=False)
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_systematic_monitoring_no_dpia_denied(self):
        r = self._eval(processing_type="systematic_monitoring", dpia_completed=False)
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_high_risk_no_dpia_denied_cites_art_38(self):
        r = self._eval(processing_type="biometric_identification", dpia_completed=False)
        assert "38" in r.regulation or "DPIA" in r.regulation

    def test_high_risk_with_dpia_completed_permitted(self):
        r = self._eval(processing_type="biometric_identification", dpia_completed=True)
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    def test_low_risk_processing_no_dpia_permitted(self):
        r = self._eval(processing_type="standard_analytics", dpia_completed=False)
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    # --- LGPD Art. 9(V) + ANPD AI Guidelines 2023 §4.2 — profiling without transparency: DENIED ---

    def test_ai_profiling_no_logic_disclosure_denied(self):
        r = self._eval(
            ai_profiling_active=True,
            automated_logic_disclosed_to_data_subjects=False,
        )
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_profiling_denied_cites_lgpd_art_9(self):
        r = self._eval(
            ai_profiling_active=True,
            automated_logic_disclosed_to_data_subjects=False,
        )
        assert "9" in r.regulation or "Transparent" in r.regulation or "Profiling" in r.regulation

    def test_ai_profiling_with_logic_disclosed_permitted(self):
        r = self._eval(
            ai_profiling_active=True,
            automated_logic_disclosed_to_data_subjects=True,
        )
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    def test_no_profiling_active_permitted(self):
        r = self._eval(ai_profiling_active=False)
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    # --- LGPD Art. 10 §3 + ANPD Resolution 02/2022 §6 — legitimate interest without LIA: DENIED ---

    def test_legitimate_interest_ai_no_lia_denied(self):
        r = self._eval(
            legal_basis="legitimate_interests",
            ai_system_active=True,
            legitimate_interest_assessment_completed=False,
        )
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_legitimate_interest_no_lia_denied_cites_art_10(self):
        r = self._eval(
            legal_basis="legitimate_interests",
            ai_system_active=True,
            legitimate_interest_assessment_completed=False,
        )
        assert "10" in r.regulation or "LIA" in r.regulation

    def test_legitimate_interest_with_lia_permitted(self):
        r = self._eval(
            legal_basis="legitimate_interests",
            ai_system_active=True,
            legitimate_interest_assessment_completed=True,
        )
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    def test_consent_basis_no_lia_permitted(self):
        r = self._eval(
            legal_basis="consent",
            ai_system_active=True,
            legitimate_interest_assessment_completed=False,
        )
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    # --- Lei 12.414/2011 + ANPD credit guidance — credit scoring without SERASA/SCR: RHR ---

    def test_ai_credit_scoring_no_serasa_rhr(self):
        r = self._eval(
            ai_credit_scoring_active=True,
            serasa_scr_compliance_verified=False,
        )
        assert r.decision == "REQUIRES_HUMAN_REVIEW"
        assert not r.is_denied

    def test_credit_scoring_rhr_cites_lei_12414(self):
        r = self._eval(
            ai_credit_scoring_active=True,
            serasa_scr_compliance_verified=False,
        )
        assert "12.414" in r.regulation or "SERASA" in r.regulation or "SCR" in r.regulation

    def test_ai_credit_scoring_with_compliance_permitted(self):
        r = self._eval(
            ai_credit_scoring_active=True,
            serasa_scr_compliance_verified=True,
        )
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    # --- Edge cases ---

    def test_empty_dict_permitted(self):
        r = mod.ANPDAIFilter().filter({})
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    def test_filter_frozen_dataclass(self):
        f = mod.ANPDAIFilter()
        with pytest.raises((AttributeError, TypeError)):
            f.FILTER_NAME = "modified"  # type: ignore[misc]


# ===========================================================================
# TestBrazilSectoralAIFilter — CMN/BCdB, CFM, ANATEL, TSE
# ===========================================================================


class TestBrazilSectoralAIFilter:
    """Brazil sectoral AI governance — four principal controls."""

    def _eval(self, **kwargs):
        return mod.BrazilSectoralAIFilter().filter(kwargs)

    # --- CMN Resolution 4.993/2022 + Circular BCB 3.979 — financial AI without BCdB notification: DENIED ---

    def test_algorithmic_trading_no_bcb_notification_denied(self):
        r = self._eval(
            financial_ai_context="algorithmic_trading",
            bcb_model_notification_filed=False,
        )
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_credit_model_no_bcb_notification_denied(self):
        r = self._eval(
            financial_ai_context="credit_model",
            bcb_model_notification_filed=False,
        )
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_risk_model_no_bcb_notification_denied(self):
        r = self._eval(
            financial_ai_context="risk_model",
            bcb_model_notification_filed=False,
        )
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_underwriting_model_no_bcb_notification_denied(self):
        r = self._eval(
            financial_ai_context="underwriting_model",
            bcb_model_notification_filed=False,
        )
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_financial_denied_cites_cmn_4993(self):
        r = self._eval(
            financial_ai_context="algorithmic_trading",
            bcb_model_notification_filed=False,
        )
        assert "4.993" in r.regulation or "BCdB" in r.regulation or "BCB" in r.regulation

    def test_financial_ai_with_bcb_notification_permitted(self):
        r = self._eval(
            financial_ai_context="algorithmic_trading",
            bcb_model_notification_filed=True,
        )
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    def test_non_financial_ai_context_permitted(self):
        r = self._eval(financial_ai_context="customer_service_chatbot")
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    # --- CFM Resolution 2.314/2022 — health AI without CFM compliance: DENIED ---

    def test_health_ai_patient_data_no_cfm_compliance_denied(self):
        r = self._eval(
            health_ai_system_active=True,
            patient_data_processed=True,
            cfm_ethical_guidelines_compliant=False,
        )
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_health_ai_denied_cites_cfm_2314(self):
        r = self._eval(
            health_ai_system_active=True,
            patient_data_processed=True,
            cfm_ethical_guidelines_compliant=False,
        )
        assert "2.314" in r.regulation or "CFM" in r.regulation

    def test_health_ai_with_cfm_compliance_permitted(self):
        r = self._eval(
            health_ai_system_active=True,
            patient_data_processed=True,
            cfm_ethical_guidelines_compliant=True,
        )
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    def test_health_ai_no_patient_data_permitted(self):
        r = self._eval(
            health_ai_system_active=True,
            patient_data_processed=False,
            cfm_ethical_guidelines_compliant=False,
        )
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    # --- ANATEL Resolution 740/2020 — telecom AI without ANATEL compliance: DENIED ---

    def test_telecom_ai_no_anatel_compliance_denied(self):
        r = self._eval(
            telecom_ai_system_active=True,
            anatel_ai_ethics_framework_compliant=False,
        )
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_telecom_denied_cites_anatel_740(self):
        r = self._eval(
            telecom_ai_system_active=True,
            anatel_ai_ethics_framework_compliant=False,
        )
        assert "740" in r.regulation or "ANATEL" in r.regulation

    def test_telecom_ai_with_anatel_compliance_permitted(self):
        r = self._eval(
            telecom_ai_system_active=True,
            anatel_ai_ethics_framework_compliant=True,
        )
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    def test_no_telecom_ai_system_permitted(self):
        r = self._eval(telecom_ai_system_active=False)
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    # --- TSE Resolution 23.732/2024 — electoral AI without deepfake labeling: REQUIRES_HUMAN_REVIEW ---

    def test_electoral_ai_content_no_tse_labeling_rhr(self):
        r = self._eval(
            ai_generated_electoral_content=True,
            tse_deepfake_labeling_applied=False,
        )
        assert r.decision == "REQUIRES_HUMAN_REVIEW"
        assert not r.is_denied

    def test_electoral_rhr_cites_tse_23732(self):
        r = self._eval(
            ai_generated_electoral_content=True,
            tse_deepfake_labeling_applied=False,
        )
        assert "23.732" in r.regulation or "TSE" in r.regulation

    def test_electoral_ai_content_with_tse_labeling_permitted(self):
        r = self._eval(
            ai_generated_electoral_content=True,
            tse_deepfake_labeling_applied=True,
        )
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    def test_no_electoral_content_permitted(self):
        r = self._eval(ai_generated_electoral_content=False)
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    # --- Edge cases ---

    def test_empty_dict_permitted(self):
        r = mod.BrazilSectoralAIFilter().filter({})
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    def test_filter_frozen_dataclass(self):
        f = mod.BrazilSectoralAIFilter()
        with pytest.raises((AttributeError, TypeError)):
            f.FILTER_NAME = "modified"  # type: ignore[misc]


# ===========================================================================
# TestBrazilCrossBorderFilter — LGPD Art. 33 + AML + FATF + ANPD
# ===========================================================================


class TestBrazilCrossBorderFilter:
    """Brazil cross-border AI data flow governance — four principal controls."""

    def _eval(self, **kwargs):
        return mod.BrazilCrossBorderFilter().filter(kwargs)

    # --- LGPD Art. 33(I)/(II) — personal data to restricted countries without safeguards: DENIED ---

    def test_personal_data_to_cn_no_adequacy_denied(self):
        r = self._eval(
            personal_data_transfer_country="CN",
            anpd_adequacy_confirmed=False,
            standard_contractual_clauses_in_place=False,
        )
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_personal_data_to_ru_no_safeguards_denied(self):
        r = self._eval(
            personal_data_transfer_country="RU",
            anpd_adequacy_confirmed=False,
            standard_contractual_clauses_in_place=False,
        )
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_personal_data_to_kp_no_safeguards_denied(self):
        r = self._eval(
            personal_data_transfer_country="KP",
            anpd_adequacy_confirmed=False,
            standard_contractual_clauses_in_place=False,
        )
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_restricted_country_denied_cites_lgpd_art_33(self):
        r = self._eval(
            personal_data_transfer_country="CN",
            anpd_adequacy_confirmed=False,
            standard_contractual_clauses_in_place=False,
        )
        assert "33" in r.regulation or "adequacy" in r.regulation

    def test_personal_data_to_cn_with_sccs_permitted(self):
        r = self._eval(
            personal_data_transfer_country="CN",
            anpd_adequacy_confirmed=False,
            standard_contractual_clauses_in_place=True,
        )
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    def test_personal_data_to_cn_with_adequacy_permitted(self):
        r = self._eval(
            personal_data_transfer_country="CN",
            anpd_adequacy_confirmed=True,
        )
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    def test_personal_data_to_us_non_restricted_no_safeguards_triggers_next_check(self):
        # US is not in restricted list — only triggers if financial AI or other checks
        r = self._eval(
            personal_data_transfer_country="US",
            anpd_adequacy_confirmed=False,
            standard_contractual_clauses_in_place=False,
        )
        # Should not be DENIED for restriction — US not in restricted list
        # (may be PERMITTED or trigger another check if other keys set)
        assert r.decision != "DENIED" or "33" not in r.regulation

    # --- Lei 9.613/1998 AML + Coaf Resolution 36/2021 — financial AI to FATF non-compliant: DENIED ---

    def test_financial_ai_data_to_kp_denied(self):
        r = self._eval(
            financial_ai_data_transfer=True,
            financial_ai_data_transfer_country="KP",
        )
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_financial_ai_data_to_ir_denied(self):
        r = self._eval(
            financial_ai_data_transfer=True,
            financial_ai_data_transfer_country="IR",
        )
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_financial_ai_data_to_mm_denied(self):
        r = self._eval(
            financial_ai_data_transfer=True,
            financial_ai_data_transfer_country="MM",
        )
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_financial_ai_data_to_sy_denied(self):
        r = self._eval(
            financial_ai_data_transfer=True,
            financial_ai_data_transfer_country="SY",
        )
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_financial_ai_denied_cites_aml_law(self):
        r = self._eval(
            financial_ai_data_transfer=True,
            financial_ai_data_transfer_country="IR",
        )
        assert "9.613" in r.regulation or "AML" in r.regulation or "FATF" in r.regulation or "Coaf" in r.regulation

    def test_financial_ai_data_to_us_permitted(self):
        r = self._eval(
            financial_ai_data_transfer=True,
            financial_ai_data_transfer_country="US",
        )
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    def test_financial_ai_data_to_uk_permitted(self):
        r = self._eval(
            financial_ai_data_transfer=True,
            financial_ai_data_transfer_country="UK",
        )
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    # --- LGPD Art. 33(V) — AI processing Brazilian data offshore without ANPD authorization: DENIED ---

    def test_brazilian_data_offshore_no_anpd_auth_denied(self):
        r = self._eval(
            processes_brazilian_citizens_data=True,
            data_hosted_outside_brazil=True,
            anpd_authorization_obtained=False,
        )
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_offshore_denied_cites_lgpd_art_33_v(self):
        r = self._eval(
            processes_brazilian_citizens_data=True,
            data_hosted_outside_brazil=True,
            anpd_authorization_obtained=False,
        )
        assert "33" in r.regulation or "ANPD authorization" in r.reason

    def test_brazilian_data_offshore_with_anpd_auth_permitted(self):
        r = self._eval(
            processes_brazilian_citizens_data=True,
            data_hosted_outside_brazil=True,
            anpd_authorization_obtained=True,
        )
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    def test_brazilian_data_hosted_in_brazil_permitted(self):
        r = self._eval(
            processes_brazilian_citizens_data=True,
            data_hosted_outside_brazil=False,
        )
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    # --- LGPD Art. 11 + ANPD Resolution 02/2022 §8 — sensitive biometric cross-border without notification: RHR ---

    def test_biometric_cross_border_no_anpd_notification_rhr(self):
        r = self._eval(
            cross_border_sensitive_data_transfer=True,
            cross_border_sensitive_data_type="biometric",
            anpd_notification_provided=False,
        )
        assert r.decision == "REQUIRES_HUMAN_REVIEW"
        assert not r.is_denied

    def test_genetic_cross_border_no_anpd_notification_rhr(self):
        r = self._eval(
            cross_border_sensitive_data_transfer=True,
            cross_border_sensitive_data_type="genetic",
            anpd_notification_provided=False,
        )
        assert r.decision == "REQUIRES_HUMAN_REVIEW"
        assert not r.is_denied

    def test_health_cross_border_no_anpd_notification_rhr(self):
        r = self._eval(
            cross_border_sensitive_data_transfer=True,
            cross_border_sensitive_data_type="health",
            anpd_notification_provided=False,
        )
        assert r.decision == "REQUIRES_HUMAN_REVIEW"
        assert not r.is_denied

    def test_biometric_rhr_cites_anpd_resolution(self):
        r = self._eval(
            cross_border_sensitive_data_transfer=True,
            cross_border_sensitive_data_type="biometric",
            anpd_notification_provided=False,
        )
        assert "ANPD" in r.regulation or "11" in r.regulation

    def test_biometric_cross_border_with_anpd_notification_permitted(self):
        r = self._eval(
            cross_border_sensitive_data_transfer=True,
            cross_border_sensitive_data_type="biometric",
            anpd_notification_provided=True,
        )
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    # --- Edge cases ---

    def test_empty_dict_permitted(self):
        r = mod.BrazilCrossBorderFilter().filter({})
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    def test_filter_frozen_dataclass(self):
        f = mod.BrazilCrossBorderFilter()
        with pytest.raises((AttributeError, TypeError)):
            f.FILTER_NAME = "modified"  # type: ignore[misc]


# ===========================================================================
# Ecosystem wrappers
# ===========================================================================


class TestBrazilLangChainPolicyGuard:
    """LangChain integration — single filter and multi-filter invocation."""

    def test_invoke_single_filter_denied_raises_permission_error(self):
        guard = mod.BrazilLangChainPolicyGuard(filter_instance=mod.BrazilLGPDFilter())
        with pytest.raises(PermissionError):
            guard.invoke({"personal_data_processing": True, "legal_basis": ""})

    def test_invoke_single_filter_permitted_returns_list(self):
        guard = mod.BrazilLangChainPolicyGuard(filter_instance=mod.BrazilLGPDFilter())
        result = guard.invoke({"personal_data_processing": True, "legal_basis": "consent"})
        assert isinstance(result, list)
        assert len(result) == 1

    def test_ainvoke_delegates_to_invoke(self):
        guard = mod.BrazilLangChainPolicyGuard(filter_instance=mod.BrazilLGPDFilter())
        result = guard.ainvoke({"personal_data_processing": True, "legal_basis": "consent"})
        assert isinstance(result, list)

    def test_process_denied_raises_permission_error(self):
        guard = mod.BrazilLangChainPolicyGuard(filter_instance=mod.BrazilLGPDFilter())
        with pytest.raises(PermissionError):
            guard.process({"personal_data_processing": True, "legal_basis": ""})

    def test_process_permitted_returns_doc(self):
        guard = mod.BrazilLangChainPolicyGuard(filter_instance=mod.BrazilLGPDFilter())
        doc = {"personal_data_processing": True, "legal_basis": "consent"}
        assert guard.process(doc) is doc

    def test_multi_filter_invoke_denied_raises(self):
        guard = mod.BrazilLangChainPolicyGuard()
        with pytest.raises(PermissionError):
            guard.invoke({"personal_data_processing": True, "legal_basis": ""})

    def test_multi_filter_invoke_permitted_returns_four_results(self):
        guard = mod.BrazilLangChainPolicyGuard()
        results = guard.invoke({})
        assert len(results) == 4


class TestBrazilCrewAIGovernanceGuard:
    """CrewAI integration — _run interface."""

    def test_run_denied_raises_permission_error(self):
        guard = mod.BrazilCrewAIGovernanceGuard(mod.BrazilLGPDFilter())
        with pytest.raises(PermissionError):
            guard._run({"personal_data_processing": True, "legal_basis": ""})

    def test_run_permitted_returns_doc(self):
        guard = mod.BrazilCrewAIGovernanceGuard(mod.BrazilLGPDFilter())
        doc = {"personal_data_processing": True, "legal_basis": "consent"}
        assert guard._run(doc) is doc

    def test_has_name_and_description(self):
        guard = mod.BrazilCrewAIGovernanceGuard(mod.BrazilLGPDFilter())
        assert guard.name
        assert guard.description


class TestBrazilAutoGenGovernedAgent:
    """AutoGen integration — generate_reply interface."""

    def test_generate_reply_denied_raises_permission_error(self):
        agent = mod.BrazilAutoGenGovernedAgent(mod.BrazilLGPDFilter())
        with pytest.raises(PermissionError):
            agent.generate_reply({"personal_data_processing": True, "legal_basis": ""})

    def test_generate_reply_permitted_returns_doc(self):
        agent = mod.BrazilAutoGenGovernedAgent(mod.BrazilLGPDFilter())
        doc = {"personal_data_processing": True, "legal_basis": "consent"}
        assert agent.generate_reply(doc) is doc

    def test_generate_reply_none_messages_uses_empty_dict(self):
        agent = mod.BrazilAutoGenGovernedAgent(mod.BrazilLGPDFilter())
        result = agent.generate_reply(None)
        assert result == {}


class TestBrazilSemanticKernelPlugin:
    """Semantic Kernel integration — enforce_governance interface."""

    def test_enforce_governance_denied_raises_permission_error(self):
        plugin = mod.BrazilSemanticKernelPlugin(mod.BrazilLGPDFilter())
        with pytest.raises(PermissionError):
            plugin.enforce_governance({"personal_data_processing": True, "legal_basis": ""})

    def test_enforce_governance_permitted_returns_doc(self):
        plugin = mod.BrazilSemanticKernelPlugin(mod.BrazilLGPDFilter())
        doc = {"personal_data_processing": True, "legal_basis": "consent"}
        assert plugin.enforce_governance(doc) is doc


class TestBrazilLlamaIndexWorkflowGuard:
    """LlamaIndex integration — process_event interface."""

    def test_process_event_denied_raises_permission_error(self):
        guard = mod.BrazilLlamaIndexWorkflowGuard(mod.BrazilLGPDFilter())
        with pytest.raises(PermissionError):
            guard.process_event({"personal_data_processing": True, "legal_basis": ""})

    def test_process_event_permitted_returns_doc(self):
        guard = mod.BrazilLlamaIndexWorkflowGuard(mod.BrazilLGPDFilter())
        doc = {"personal_data_processing": True, "legal_basis": "consent"}
        assert guard.process_event(doc) is doc


class TestBrazilHaystackGovernanceComponent:
    """Haystack integration — run(documents) interface."""

    def test_run_filters_out_denied_documents(self):
        component = mod.BrazilHaystackGovernanceComponent(mod.BrazilLGPDFilter())
        docs = [
            {"personal_data_processing": True, "legal_basis": ""},  # DENIED
            {"personal_data_processing": True, "legal_basis": "consent"},  # PERMITTED
        ]
        result = component.run(docs)
        assert len(result["documents"]) == 1
        assert result["documents"][0]["legal_basis"] == "consent"

    def test_run_all_permitted_returns_all(self):
        component = mod.BrazilHaystackGovernanceComponent(mod.BrazilLGPDFilter())
        docs = [
            {"personal_data_processing": True, "legal_basis": "consent"},
            {"personal_data_processing": True, "legal_basis": "research"},
        ]
        result = component.run(docs)
        assert len(result["documents"]) == 2

    def test_run_empty_list_returns_empty(self):
        component = mod.BrazilHaystackGovernanceComponent(mod.BrazilLGPDFilter())
        result = component.run([])
        assert result["documents"] == []

    def test_run_returns_documents_key(self):
        component = mod.BrazilHaystackGovernanceComponent(mod.BrazilLGPDFilter())
        result = component.run([{}])
        assert "documents" in result


class TestBrazilDSPyGovernanceModule:
    """DSPy integration — forward(doc) interface."""

    def _make_module(self, return_val="ok"):
        """Return a callable mock module."""

        class _MockModule:
            def __call__(self, doc, **kwargs):
                return return_val

        return _MockModule()

    def test_forward_denied_raises_permission_error(self):
        dspy_mod = mod.BrazilDSPyGovernanceModule(mod.BrazilLGPDFilter(), self._make_module())
        with pytest.raises(PermissionError):
            dspy_mod.forward({"personal_data_processing": True, "legal_basis": ""})

    def test_forward_permitted_delegates_to_module(self):
        dspy_mod = mod.BrazilDSPyGovernanceModule(mod.BrazilLGPDFilter(), self._make_module("delegated"))
        assert dspy_mod.forward({"personal_data_processing": True, "legal_basis": "consent"}) == "delegated"

    def test_getattr_delegates_to_wrapped_module(self):
        inner = self._make_module()
        inner.custom_attr = "hello"  # type: ignore[attr-defined]
        dspy_mod = mod.BrazilDSPyGovernanceModule(mod.BrazilLGPDFilter(), inner)
        assert dspy_mod.custom_attr == "hello"


class TestBrazilMAFPolicyMiddleware:
    """MAF integration — process(message, next_handler) interface."""

    def test_process_denied_raises_permission_error(self):
        maf = mod.BrazilMAFPolicyMiddleware(mod.BrazilLGPDFilter())
        with pytest.raises(PermissionError):
            maf.process(
                {"personal_data_processing": True, "legal_basis": ""},
                lambda msg: msg,
            )

    def test_process_permitted_calls_next_handler(self):
        maf = mod.BrazilMAFPolicyMiddleware(mod.BrazilLGPDFilter())
        doc = {"personal_data_processing": True, "legal_basis": "consent"}
        called_with = []

        def next_handler(msg):
            called_with.append(msg)
            return msg

        result = maf.process(doc, next_handler)
        assert result is doc
        assert called_with == [doc]
