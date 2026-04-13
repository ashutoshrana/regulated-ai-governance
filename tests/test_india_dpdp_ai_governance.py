"""
Tests for 37_india_dpdp_ai_governance.py — India AI Governance Framework
covering:
  1. IndiaDPDPFilter       — DPDP Act 2023 §§5, 6, 9, 13, 16
  2. MeitYAIFilter         — MeitY AI Advisory §3.1, Draft §§4.2, 5.3,
                             MeitY Advisory March 2024 §2
  3. IndiaSectoralAIFilter — RBI RBI/2023-24/73; ICMR 2023; TRAI 2023;
                             IRDAI IRDA/SDD/GDL/MISC/115/05/2022
  4. IndiaCrossBorderFilter — DPDP §16 + MeitY empanelment + RBI/2021-22/57
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

_MOD_NAME = "mod_india"

spec = importlib.util.spec_from_file_location(
    _MOD_NAME,
    str(Path(__file__).parent.parent / "examples" / "37_india_dpdp_ai_governance.py"),
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

    def test_is_denied_false_for_other_value(self):
        r = mod.FilterResult(filter_name="F", decision="REDACTED", regulation="X", reason="Y")
        assert r.is_denied is False

    def test_filter_result_has_required_fields(self):
        r = mod.FilterResult(filter_name="F", decision="DENIED", regulation="R", reason="Reason")
        assert r.filter_name == "F"
        assert r.decision == "DENIED"
        assert r.regulation == "R"
        assert r.reason == "Reason"


# ===========================================================================
# TestIndiaDPDPFilter — DPDP Act 2023 §§5, 6, 9, 13, 16
# ===========================================================================


class TestIndiaDPDPFilter:
    """DPDP Act 2023 — four principal controls."""

    def _eval(self, **kwargs):
        return mod.IndiaDPDPFilter().filter(kwargs)

    # --- §6 Consent: DENIED ---

    def test_personal_data_no_consent_denied(self):
        r = self._eval(personal_data_processing=True, consent_obtained=False)
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_personal_data_no_consent_denied_cites_section_6(self):
        r = self._eval(personal_data_processing=True, consent_obtained=False)
        assert "§6" in r.regulation or "Consent" in r.regulation

    def test_personal_data_no_consent_no_notice_still_denied_on_consent(self):
        r = self._eval(
            personal_data_processing=True,
            consent_obtained=False,
            notice_provided=False,
        )
        assert r.decision == "DENIED"
        assert r.is_denied

    # --- §5 Notice: DENIED ---

    def test_personal_data_consent_but_no_notice_denied(self):
        r = self._eval(
            personal_data_processing=True,
            consent_obtained=True,
            notice_provided=False,
        )
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_personal_data_no_notice_denied_cites_section_5(self):
        r = self._eval(
            personal_data_processing=True,
            consent_obtained=True,
            notice_provided=False,
        )
        assert "§5" in r.regulation or "Notice" in r.regulation

    def test_personal_data_with_consent_and_notice_permitted(self):
        r = self._eval(
            personal_data_processing=True,
            consent_obtained=True,
            notice_provided=True,
        )
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    def test_no_personal_data_processing_permitted(self):
        r = self._eval(personal_data_processing=False)
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    # --- Sensitive Data (§9 + Schedule): DENIED ---

    def test_health_data_no_explicit_consent_denied(self):
        r = self._eval(data_category="health", explicit_consent_obtained=False)
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_financial_data_no_explicit_consent_denied(self):
        r = self._eval(data_category="financial", explicit_consent_obtained=False)
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_biometric_data_no_explicit_consent_denied(self):
        r = self._eval(data_category="biometric", explicit_consent_obtained=False)
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_children_data_no_explicit_consent_denied(self):
        r = self._eval(data_category="children", explicit_consent_obtained=False)
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_sensitive_denied_cites_section_9(self):
        r = self._eval(data_category="health", explicit_consent_obtained=False)
        assert "§9" in r.regulation or "Sensitive" in r.regulation

    def test_health_data_with_explicit_consent_permitted(self):
        r = self._eval(data_category="health", explicit_consent_obtained=True)
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    def test_non_sensitive_category_permitted(self):
        r = self._eval(data_category="name")
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    # --- §16 Cross-border transfer to restricted country: DENIED ---

    def test_transfer_to_cn_denied(self):
        r = self._eval(destination_country="CN")
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_transfer_to_ru_denied(self):
        r = self._eval(destination_country="RU")
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_transfer_to_kp_denied(self):
        r = self._eval(destination_country="KP")
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_transfer_to_ir_denied(self):
        r = self._eval(destination_country="IR")
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_transfer_to_sy_denied(self):
        r = self._eval(destination_country="SY")
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_transfer_to_cu_denied(self):
        r = self._eval(destination_country="CU")
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_restricted_transfer_denied_cites_section_16(self):
        r = self._eval(destination_country="CN")
        assert "§16" in r.regulation or "Transfer" in r.regulation

    def test_transfer_to_us_permitted(self):
        r = self._eval(destination_country="US")
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    def test_transfer_to_uk_permitted(self):
        r = self._eval(destination_country="UK")
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    def test_transfer_to_de_permitted(self):
        r = self._eval(destination_country="DE")
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    # --- §13 Grievance Redressal: REQUIRES_HUMAN_REVIEW ---

    def test_automated_processing_no_grievance_rhr(self):
        r = self._eval(automated_processing=True, grievance_redressal_available=False)
        assert r.decision == "REQUIRES_HUMAN_REVIEW"
        assert not r.is_denied

    def test_automated_processing_rhr_cites_section_13(self):
        r = self._eval(automated_processing=True, grievance_redressal_available=False)
        assert "§13" in r.regulation or "Grievance" in r.regulation

    def test_automated_processing_with_grievance_permitted(self):
        r = self._eval(automated_processing=True, grievance_redressal_available=True)
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    # --- Edge cases ---

    def test_empty_dict_permitted(self):
        r = mod.IndiaDPDPFilter().filter({})
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    def test_filter_name_set(self):
        r = mod.IndiaDPDPFilter().filter({})
        assert r.filter_name


# ===========================================================================
# TestMeitYAIFilter — MeitY AI Advisory + Draft AI Policy 2023
# ===========================================================================


class TestMeitYAIFilter:
    """MeitY AI governance — four principal controls."""

    def _eval(self, **kwargs):
        return mod.MeitYAIFilter().filter(kwargs)

    # --- Draft §4.2 High-Risk Impact Assessment: DENIED ---

    def test_high_risk_ai_no_impact_assessment_denied(self):
        r = self._eval(ai_risk_level="high", impact_assessment_completed=False)
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_high_risk_ai_denied_cites_section_4_2(self):
        r = self._eval(ai_risk_level="high", impact_assessment_completed=False)
        assert "4.2" in r.regulation or "impact assessment" in r.reason.lower()

    def test_high_risk_ai_with_impact_assessment_permitted(self):
        r = self._eval(ai_risk_level="high", impact_assessment_completed=True)
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    def test_low_risk_ai_no_impact_assessment_permitted(self):
        r = self._eval(ai_risk_level="low", impact_assessment_completed=False)
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    def test_medium_risk_ai_no_impact_assessment_permitted(self):
        r = self._eval(ai_risk_level="medium", impact_assessment_completed=False)
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    # --- Advisory §3.1 Explainability: DENIED ---

    def test_ai_decision_system_no_explainability_denied(self):
        r = self._eval(ai_decision_system=True, explainability_provided=False)
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_explainability_denied_cites_section_3_1(self):
        r = self._eval(ai_decision_system=True, explainability_provided=False)
        assert "3.1" in r.regulation or "Explainability" in r.regulation

    def test_ai_decision_system_with_explainability_permitted(self):
        r = self._eval(ai_decision_system=True, explainability_provided=True)
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    def test_non_decision_ai_system_no_explainability_permitted(self):
        r = self._eval(ai_decision_system=False, explainability_provided=False)
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    # --- Advisory March 2024 §2 GenAI Labeling: DENIED ---

    def test_genai_content_no_label_denied(self):
        r = self._eval(genai_content=True, genai_labeled=False)
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_genai_denied_cites_march_2024(self):
        r = self._eval(genai_content=True, genai_labeled=False)
        assert "2024" in r.regulation or "GenAI" in r.regulation or "label" in r.reason.lower()

    def test_genai_content_with_label_permitted(self):
        r = self._eval(genai_content=True, genai_labeled=True)
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    def test_non_genai_content_no_label_permitted(self):
        r = self._eval(genai_content=False, genai_labeled=False)
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    # --- Draft §5.3 Human Oversight: REQUIRES_HUMAN_REVIEW ---

    def test_affects_citizens_no_human_oversight_rhr(self):
        r = self._eval(affects_citizens=True, human_oversight=False)
        assert r.decision == "REQUIRES_HUMAN_REVIEW"
        assert not r.is_denied

    def test_citizen_oversight_rhr_cites_section_5_3(self):
        r = self._eval(affects_citizens=True, human_oversight=False)
        assert "5.3" in r.regulation or "oversight" in r.reason.lower()

    def test_affects_citizens_with_human_oversight_permitted(self):
        r = self._eval(affects_citizens=True, human_oversight=True)
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    def test_does_not_affect_citizens_no_oversight_permitted(self):
        r = self._eval(affects_citizens=False, human_oversight=False)
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    # --- Edge cases ---

    def test_empty_dict_permitted(self):
        r = mod.MeitYAIFilter().filter({})
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    def test_filter_name_set(self):
        r = mod.MeitYAIFilter().filter({})
        assert r.filter_name


# ===========================================================================
# TestIndiaSectoralAIFilter — RBI, ICMR, TRAI, IRDAI
# ===========================================================================


class TestIndiaSectoralAIFilter:
    """India sectoral AI regulations — four principal controls."""

    def _eval(self, **kwargs):
        return mod.IndiaSectoralAIFilter().filter(kwargs)

    # --- RBI Circular RBI/2023-24/73 Financial AI: DENIED ---

    def test_financial_sector_no_rbi_compliance_denied(self):
        r = self._eval(sector="financial", rbi_ai_compliant=False)
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_financial_denied_cites_rbi_circular(self):
        r = self._eval(sector="financial", rbi_ai_compliant=False)
        assert "RBI" in r.regulation or "financial" in r.reason.lower()

    def test_financial_sector_with_rbi_compliance_permitted(self):
        r = self._eval(sector="financial", rbi_ai_compliant=True)
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    # --- ICMR AI in Healthcare Guidelines 2023: DENIED ---

    def test_healthcare_sector_no_icmr_review_denied(self):
        r = self._eval(sector="healthcare", icmr_ethics_reviewed=False)
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_healthcare_denied_cites_icmr(self):
        r = self._eval(sector="healthcare", icmr_ethics_reviewed=False)
        assert "ICMR" in r.regulation or "healthcare" in r.reason.lower()

    def test_healthcare_sector_with_icmr_review_permitted(self):
        r = self._eval(sector="healthcare", icmr_ethics_reviewed=True)
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    # --- TRAI Recommendations on AI in Telecom 2023: DENIED ---

    def test_telecom_sector_no_trai_consent_denied(self):
        r = self._eval(sector="telecom", trai_ai_consent=False)
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_telecom_denied_cites_trai(self):
        r = self._eval(sector="telecom", trai_ai_consent=False)
        assert "TRAI" in r.regulation or "telecom" in r.reason.lower()

    def test_telecom_sector_with_trai_consent_permitted(self):
        r = self._eval(sector="telecom", trai_ai_consent=True)
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    # --- IRDAI Circular: REQUIRES_HUMAN_REVIEW ---

    def test_insurance_sector_no_irdai_compliance_rhr(self):
        r = self._eval(sector="insurance", irdai_compliant=False)
        assert r.decision == "REQUIRES_HUMAN_REVIEW"
        assert not r.is_denied

    def test_insurance_rhr_cites_irdai(self):
        r = self._eval(sector="insurance", irdai_compliant=False)
        assert "IRDAI" in r.regulation or "IRDA" in r.regulation

    def test_insurance_sector_with_irdai_compliance_permitted(self):
        r = self._eval(sector="insurance", irdai_compliant=True)
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    # --- Unknown sector ---

    def test_unknown_sector_permitted(self):
        r = self._eval(sector="retail", rbi_ai_compliant=False)
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    # --- Edge cases ---

    def test_empty_dict_permitted(self):
        r = mod.IndiaSectoralAIFilter().filter({})
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    def test_filter_name_set(self):
        r = mod.IndiaSectoralAIFilter().filter({})
        assert r.filter_name


# ===========================================================================
# TestIndiaCrossBorderFilter — DPDP §16 + MeitY empanelment + RBI/2021-22/57
# ===========================================================================


class TestIndiaCrossBorderFilter:
    """India cross-border data and AI controls — four principal controls."""

    def _eval(self, **kwargs):
        return mod.IndiaCrossBorderFilter().filter(kwargs)

    # --- DPDP §16 + INDIA_RESTRICTED_COUNTRIES: DENIED ---

    def test_indian_citizens_data_to_cn_denied(self):
        r = self._eval(indian_citizens_personal_data=True, destination_country="CN")
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_indian_citizens_data_to_ru_denied(self):
        r = self._eval(indian_citizens_personal_data=True, destination_country="RU")
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_indian_citizens_data_to_kp_denied(self):
        r = self._eval(indian_citizens_personal_data=True, destination_country="KP")
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_indian_citizens_data_to_ir_denied(self):
        r = self._eval(indian_citizens_personal_data=True, destination_country="IR")
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_restricted_transfer_denied_cites_dpdp_16(self):
        r = self._eval(indian_citizens_personal_data=True, destination_country="CN")
        assert "§16" in r.regulation or "DPDP" in r.regulation

    def test_indian_citizens_data_to_us_permitted(self):
        r = self._eval(indian_citizens_personal_data=True, destination_country="US")
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    def test_indian_citizens_data_to_uk_permitted(self):
        r = self._eval(indian_citizens_personal_data=True, destination_country="UK")
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    def test_no_indian_citizens_data_to_cn_permitted(self):
        r = self._eval(indian_citizens_personal_data=False, destination_country="CN")
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    # --- MeitY Cloud Empanelment: DENIED ---

    def test_critical_data_non_empanelled_cloud_denied(self):
        r = self._eval(critical_data=True, cloud_empanelled=False)
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_critical_data_non_empanelled_denied_cites_meity(self):
        r = self._eval(critical_data=True, cloud_empanelled=False)
        assert "MeitY" in r.regulation or "empanell" in r.reason.lower()

    def test_critical_data_meity_empanelled_cloud_permitted(self):
        r = self._eval(critical_data=True, cloud_empanelled=True)
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    def test_non_critical_data_non_empanelled_cloud_permitted(self):
        r = self._eval(critical_data=False, cloud_empanelled=False)
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    # --- DPDP + MeitY Clearance for sensitive training data export: DENIED ---

    def test_sensitive_training_data_no_consent_no_clearance_denied(self):
        r = self._eval(
            sensitive_training_data=True,
            dpdp_export_consent_obtained=False,
            meity_clearance_obtained=False,
        )
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_sensitive_training_data_consent_only_denied(self):
        r = self._eval(
            sensitive_training_data=True,
            dpdp_export_consent_obtained=True,
            meity_clearance_obtained=False,
        )
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_sensitive_training_data_clearance_only_denied(self):
        r = self._eval(
            sensitive_training_data=True,
            dpdp_export_consent_obtained=False,
            meity_clearance_obtained=True,
        )
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_sensitive_training_data_denied_cites_dpdp_meity(self):
        r = self._eval(
            sensitive_training_data=True,
            dpdp_export_consent_obtained=False,
            meity_clearance_obtained=False,
        )
        assert "DPDP" in r.regulation or "MeitY" in r.regulation

    def test_sensitive_training_data_both_consent_and_clearance_permitted(self):
        r = self._eval(
            sensitive_training_data=True,
            dpdp_export_consent_obtained=True,
            meity_clearance_obtained=True,
        )
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    def test_non_sensitive_training_data_no_clearance_permitted(self):
        r = self._eval(sensitive_training_data=False)
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    # --- RBI Circular RBI/2021-22/57 Payment Data: REQUIRES_HUMAN_REVIEW ---

    def test_payment_data_no_rbi_cloud_compliance_rhr(self):
        r = self._eval(payment_data=True, rbi_cloud_compliant=False)
        assert r.decision == "REQUIRES_HUMAN_REVIEW"
        assert not r.is_denied

    def test_payment_data_rhr_cites_rbi_circular(self):
        r = self._eval(payment_data=True, rbi_cloud_compliant=False)
        assert "RBI" in r.regulation or "payment" in r.reason.lower()

    def test_payment_data_rbi_cloud_compliant_permitted(self):
        r = self._eval(payment_data=True, rbi_cloud_compliant=True)
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    def test_no_payment_data_not_rbi_compliant_permitted(self):
        r = self._eval(payment_data=False, rbi_cloud_compliant=False)
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    # --- Edge cases ---

    def test_empty_dict_permitted(self):
        r = mod.IndiaCrossBorderFilter().filter({})
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    def test_filter_name_set(self):
        r = mod.IndiaCrossBorderFilter().filter({})
        assert r.filter_name


# ===========================================================================
# Constants tests
# ===========================================================================


class TestConstants:
    """Verify exported constant sets contain expected members."""

    def test_dpdp_restricted_countries_contains_cn(self):
        assert "CN" in mod.DPDP_RESTRICTED_COUNTRIES

    def test_dpdp_restricted_countries_contains_ru(self):
        assert "RU" in mod.DPDP_RESTRICTED_COUNTRIES

    def test_dpdp_restricted_countries_contains_kp(self):
        assert "KP" in mod.DPDP_RESTRICTED_COUNTRIES

    def test_india_restricted_countries_contains_ir(self):
        assert "IR" in mod.INDIA_RESTRICTED_COUNTRIES

    def test_meity_empanelled_clouds_contains_aws_mumbai(self):
        assert "aws_mumbai" in mod.MEITY_EMPANELLED_CLOUDS

    def test_meity_empanelled_clouds_contains_gcp_mumbai(self):
        assert "gcp_mumbai" in mod.MEITY_EMPANELLED_CLOUDS

    def test_meity_empanelled_clouds_contains_azure_india_central(self):
        assert "azure_india_central" in mod.MEITY_EMPANELLED_CLOUDS

    def test_meity_empanelled_clouds_contains_meity_cloud(self):
        assert "meity_cloud" in mod.MEITY_EMPANELLED_CLOUDS


# ===========================================================================
# Ecosystem wrapper tests
# ===========================================================================


class TestIndiaLangChainPolicyGuard:
    """LangChain wrapper — invoke raises PermissionError on DENIED."""

    def test_invoke_denied_raises_permission_error(self):
        guard = mod.IndiaLangChainPolicyGuard(filter_instance=mod.IndiaDPDPFilter())
        with pytest.raises(PermissionError):
            guard.invoke({"personal_data_processing": True, "consent_obtained": False})

    def test_invoke_permitted_returns_list(self):
        guard = mod.IndiaLangChainPolicyGuard(filter_instance=mod.IndiaDPDPFilter())
        r = guard.invoke({})
        assert isinstance(r, list)
        assert len(r) == 1
        assert r[0].decision == "PERMITTED"

    def test_ainvoke_permitted_returns_list(self):
        guard = mod.IndiaLangChainPolicyGuard(filter_instance=mod.IndiaDPDPFilter())
        r = guard.ainvoke({})
        assert isinstance(r, list)

    def test_process_denied_raises_permission_error(self):
        guard = mod.IndiaLangChainPolicyGuard(filter_instance=mod.IndiaDPDPFilter())
        with pytest.raises(PermissionError):
            guard.process({"personal_data_processing": True, "consent_obtained": False})

    def test_process_permitted_returns_doc(self):
        guard = mod.IndiaLangChainPolicyGuard(filter_instance=mod.IndiaDPDPFilter())
        doc = {}
        result = guard.process(doc)
        assert result is doc

    def test_multi_filter_invoke_denied_raises(self):
        guard = mod.IndiaLangChainPolicyGuard()
        with pytest.raises(PermissionError):
            guard.invoke({"personal_data_processing": True, "consent_obtained": False})

    def test_multi_filter_invoke_permitted_returns_list_of_four(self):
        guard = mod.IndiaLangChainPolicyGuard()
        r = guard.invoke({})
        assert isinstance(r, list)
        assert len(r) == 4


class TestIndiaCrewAIGovernanceGuard:
    """CrewAI wrapper — _run raises PermissionError on DENIED."""

    def test_run_denied_raises_permission_error(self):
        guard = mod.IndiaCrewAIGovernanceGuard(filter_instance=mod.IndiaDPDPFilter())
        with pytest.raises(PermissionError):
            guard._run({"personal_data_processing": True, "consent_obtained": False})

    def test_run_permitted_returns_doc(self):
        guard = mod.IndiaCrewAIGovernanceGuard(filter_instance=mod.IndiaDPDPFilter())
        doc = {}
        result = guard._run(doc)
        assert result is doc

    def test_has_name_and_description(self):
        guard = mod.IndiaCrewAIGovernanceGuard(filter_instance=mod.IndiaDPDPFilter())
        assert guard.name
        assert guard.description

    def test_run_denied_meity_filter_raises(self):
        guard = mod.IndiaCrewAIGovernanceGuard(filter_instance=mod.MeitYAIFilter())
        with pytest.raises(PermissionError):
            guard._run({"ai_risk_level": "high", "impact_assessment_completed": False})


class TestIndiaAutoGenGovernedAgent:
    """AutoGen wrapper — generate_reply raises PermissionError on DENIED."""

    def test_generate_reply_denied_raises(self):
        agent = mod.IndiaAutoGenGovernedAgent(filter_instance=mod.IndiaDPDPFilter())
        with pytest.raises(PermissionError):
            agent.generate_reply({"personal_data_processing": True, "consent_obtained": False})

    def test_generate_reply_permitted_returns_doc(self):
        agent = mod.IndiaAutoGenGovernedAgent(filter_instance=mod.IndiaDPDPFilter())
        result = agent.generate_reply({})
        assert isinstance(result, dict)

    def test_generate_reply_none_messages_permitted(self):
        agent = mod.IndiaAutoGenGovernedAgent(filter_instance=mod.IndiaDPDPFilter())
        result = agent.generate_reply(None)
        assert isinstance(result, dict)

    def test_generate_reply_sectoral_denied_raises(self):
        agent = mod.IndiaAutoGenGovernedAgent(filter_instance=mod.IndiaSectoralAIFilter())
        with pytest.raises(PermissionError):
            agent.generate_reply({"sector": "financial", "rbi_ai_compliant": False})


class TestIndiaSemanticKernelPlugin:
    """Semantic Kernel wrapper — enforce_governance raises PermissionError on DENIED."""

    def test_enforce_governance_denied_raises(self):
        plugin = mod.IndiaSemanticKernelPlugin(filter_instance=mod.IndiaDPDPFilter())
        with pytest.raises(PermissionError):
            plugin.enforce_governance({"personal_data_processing": True, "consent_obtained": False})

    def test_enforce_governance_permitted_returns_doc(self):
        plugin = mod.IndiaSemanticKernelPlugin(filter_instance=mod.IndiaDPDPFilter())
        doc = {}
        result = plugin.enforce_governance(doc)
        assert result is doc

    def test_enforce_governance_meity_denied_raises(self):
        plugin = mod.IndiaSemanticKernelPlugin(filter_instance=mod.MeitYAIFilter())
        with pytest.raises(PermissionError):
            plugin.enforce_governance({"genai_content": True, "genai_labeled": False})


class TestIndiaLlamaIndexWorkflowGuard:
    """LlamaIndex wrapper — process_event raises PermissionError on DENIED."""

    def test_process_event_denied_raises(self):
        guard = mod.IndiaLlamaIndexWorkflowGuard(filter_instance=mod.IndiaDPDPFilter())
        with pytest.raises(PermissionError):
            guard.process_event({"personal_data_processing": True, "consent_obtained": False})

    def test_process_event_permitted_returns_doc(self):
        guard = mod.IndiaLlamaIndexWorkflowGuard(filter_instance=mod.IndiaDPDPFilter())
        doc = {}
        result = guard.process_event(doc)
        assert result is doc

    def test_process_event_cross_border_denied_raises(self):
        guard = mod.IndiaLlamaIndexWorkflowGuard(filter_instance=mod.IndiaCrossBorderFilter())
        with pytest.raises(PermissionError):
            guard.process_event({"indian_citizens_personal_data": True, "destination_country": "CN"})


class TestIndiaHaystackGovernanceComponent:
    """Haystack wrapper — run filters denied documents, does not raise."""

    def test_run_filters_denied_documents(self):
        component = mod.IndiaHaystackGovernanceComponent(filter_instance=mod.IndiaDPDPFilter())
        denied_doc = {"personal_data_processing": True, "consent_obtained": False}
        permitted_doc = {}
        result = component.run([denied_doc, permitted_doc])
        assert "documents" in result
        assert len(result["documents"]) == 1
        assert result["documents"][0] is permitted_doc

    def test_run_all_permitted_returns_all(self):
        component = mod.IndiaHaystackGovernanceComponent(filter_instance=mod.IndiaDPDPFilter())
        docs = [{}, {"consent_obtained": True}]
        result = component.run(docs)
        assert len(result["documents"]) == 2

    def test_run_empty_list_returns_empty(self):
        component = mod.IndiaHaystackGovernanceComponent(filter_instance=mod.IndiaDPDPFilter())
        result = component.run([])
        assert result["documents"] == []

    def test_run_multiple_denied_docs_filtered_out(self):
        component = mod.IndiaHaystackGovernanceComponent(filter_instance=mod.MeitYAIFilter())
        denied_1 = {"ai_risk_level": "high", "impact_assessment_completed": False}
        denied_2 = {"genai_content": True, "genai_labeled": False}
        permitted = {}
        result = component.run([denied_1, denied_2, permitted])
        assert len(result["documents"]) == 1
        assert result["documents"][0] is permitted


class TestIndiaDSPyGovernanceModule:
    """DSPy wrapper — forward raises PermissionError on DENIED, delegates on PERMITTED."""

    def test_forward_denied_raises(self):
        sentinel = object()

        def dummy_module(doc, **kwargs):
            return sentinel

        module = mod.IndiaDSPyGovernanceModule(
            filter_instance=mod.IndiaDPDPFilter(),
            module=dummy_module,
        )
        with pytest.raises(PermissionError):
            module.forward({"personal_data_processing": True, "consent_obtained": False})

    def test_forward_permitted_delegates_to_module(self):
        sentinel = object()

        def dummy_module(doc, **kwargs):
            return sentinel

        module = mod.IndiaDSPyGovernanceModule(
            filter_instance=mod.IndiaDPDPFilter(),
            module=dummy_module,
        )
        result = module.forward({})
        assert result is sentinel

    def test_forward_sectoral_denied_raises(self):
        def dummy_module(doc, **kwargs):
            return doc

        module = mod.IndiaDSPyGovernanceModule(
            filter_instance=mod.IndiaSectoralAIFilter(),
            module=dummy_module,
        )
        with pytest.raises(PermissionError):
            module.forward({"sector": "healthcare", "icmr_ethics_reviewed": False})


class TestIndiaMAFPolicyMiddleware:
    """MAF middleware — process raises PermissionError on DENIED, calls next_handler on PERMITTED."""

    def test_process_denied_raises(self):
        middleware = mod.IndiaMAFPolicyMiddleware(filter_instance=mod.IndiaDPDPFilter())
        with pytest.raises(PermissionError):
            middleware.process(
                {"personal_data_processing": True, "consent_obtained": False},
                lambda msg: msg,
            )

    def test_process_permitted_calls_next_handler(self):
        sentinel = object()

        def next_handler(msg):
            return sentinel

        middleware = mod.IndiaMAFPolicyMiddleware(filter_instance=mod.IndiaDPDPFilter())
        result = middleware.process({}, next_handler)
        assert result is sentinel

    def test_process_cross_border_denied_raises(self):
        middleware = mod.IndiaMAFPolicyMiddleware(filter_instance=mod.IndiaCrossBorderFilter())
        with pytest.raises(PermissionError):
            middleware.process(
                {"indian_citizens_personal_data": True, "destination_country": "RU"},
                lambda msg: msg,
            )

    def test_process_meity_denied_raises(self):
        middleware = mod.IndiaMAFPolicyMiddleware(filter_instance=mod.MeitYAIFilter())
        with pytest.raises(PermissionError):
            middleware.process(
                {"ai_decision_system": True, "explainability_provided": False},
                lambda msg: msg,
            )
