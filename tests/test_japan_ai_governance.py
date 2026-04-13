"""
Tests for 34_japan_ai_governance.py — Japan AI Governance Framework
covering:
  1. JapanAPPIFilter         — APPI 2022 Arts. 15, 17, 20, 23, 28 + PPC AI Guidelines §3.2
  2. JapanFSAAIFilter        — FIEA Art. 40, FSA Customer-Oriented Conduct Principle 3,
                               Insurance Business Act Art. 113 + FSA III-2-9, FSA Stress Testing
  3. JapanAIGovernanceFilter — METI v1.1 §§4, 4.8; Japan AI Strategy 2022 §2.1;
                               METI GenAI Guidelines 2023 §3; Cabinet Office Strategy §3.3
  4. JapanCrossBorderFilter  — APPI Art. 28 + PPC; Japan AML/FSA AML; FSA Cloud; PPC US pending
  5. FilterResult.is_denied property
  6. Eight ecosystem wrappers (LangChain, CrewAI, AutoGen, SK, LlamaIndex, Haystack, DSPy, MAF)
  7. Edge cases: missing keys, empty dict, frozen dataclasses
"""

from __future__ import annotations

import importlib.util
import sys
import types

import pytest

# ---------------------------------------------------------------------------
# Module loader — use importlib per task specification
# ---------------------------------------------------------------------------

_MOD_NAME = "japan_mod"

spec = importlib.util.spec_from_file_location(
    _MOD_NAME,
    "/tmp/oss_work/regulated-ai-governance/examples/34_japan_ai_governance.py",
)
japan_mod = types.ModuleType(_MOD_NAME)
sys.modules[_MOD_NAME] = japan_mod
spec.loader.exec_module(japan_mod)


# ===========================================================================
# TestFilterResult — is_denied property
# ===========================================================================


class TestFilterResult:
    """FilterResult.is_denied must be True only for decision == 'DENIED'."""

    def test_is_denied_true_for_denied(self):
        r = japan_mod.FilterResult(filter_name="F", decision="DENIED", regulation="X", reason="Y")
        assert r.is_denied is True

    def test_is_denied_false_for_permitted(self):
        r = japan_mod.FilterResult(filter_name="F", decision="PERMITTED", regulation="X", reason="Y")
        assert r.is_denied is False

    def test_is_denied_false_for_requires_human_review(self):
        r = japan_mod.FilterResult(
            filter_name="F",
            decision="REQUIRES_HUMAN_REVIEW",
            regulation="X",
            reason="Y",
        )
        assert r.is_denied is False

    def test_is_denied_false_for_other_decision(self):
        r = japan_mod.FilterResult(filter_name="F", decision="MONITOR", regulation="X", reason="Y")
        assert r.is_denied is False

    def test_filter_result_has_required_fields(self):
        r = japan_mod.FilterResult(filter_name="F", decision="DENIED", regulation="R", reason="Reason")
        assert r.filter_name == "F"
        assert r.decision == "DENIED"
        assert r.regulation == "R"
        assert r.reason == "Reason"


# ===========================================================================
# TestJapanAPPIFilter
# ===========================================================================


class TestJapanAPPIFilter:
    """APPI 2022 Arts. 15+17, 20, 23, 28 + PPC AI Guidelines 2023 §3.2."""

    def _eval(self, **kwargs):
        return japan_mod.JapanAPPIFilter().filter(kwargs)

    # --- Art. 15 + Art. 17: DENIED ---

    def test_personal_info_no_consent_no_legitimate_purpose_denied(self):
        """Art. 15+17: personal_information_processing + no consent + no legitimate_purpose → DENIED."""
        r = self._eval(
            personal_information_processing=True,
            consent_obtained=False,
            legitimate_purpose=False,
        )
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_personal_info_denial_cites_appi_art15_art17(self):
        """Art. 15+17 denial cites APPI Art. 15 and Art. 17."""
        r = self._eval(
            personal_information_processing=True,
            consent_obtained=False,
            legitimate_purpose=False,
        )
        assert "15" in r.regulation or "APPI" in r.regulation

    def test_personal_info_with_consent_permitted(self):
        """Art. 15+17: personal_information_processing + consent_obtained=True → PERMITTED."""
        r = self._eval(personal_information_processing=True, consent_obtained=True)
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    def test_personal_info_no_consent_but_legitimate_purpose_permitted(self):
        """Art. 15+17: no consent but legitimate_purpose=True → PERMITTED."""
        r = self._eval(
            personal_information_processing=True,
            consent_obtained=False,
            legitimate_purpose=True,
        )
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    # --- Art. 20 Specially Considered PI: DENIED ---

    def test_medical_data_no_explicit_consent_denied(self):
        """Art. 20: data_type=medical + no explicit_consent_obtained → DENIED."""
        r = self._eval(data_type="medical", explicit_consent_obtained=False)
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_race_data_no_explicit_consent_denied(self):
        """Art. 20: data_type=race + no explicit_consent_obtained → DENIED."""
        r = self._eval(data_type="race", explicit_consent_obtained=False)
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_disability_data_no_explicit_consent_denied(self):
        """Art. 20: data_type=disability + no explicit_consent_obtained → DENIED."""
        r = self._eval(data_type="disability", explicit_consent_obtained=False)
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_specially_considered_pi_denial_cites_appi_art20(self):
        """Art. 20 denial cites APPI Art. 20."""
        r = self._eval(data_type="criminal", explicit_consent_obtained=False)
        assert "20" in r.regulation or "APPI" in r.regulation

    def test_medical_data_with_explicit_consent_permitted(self):
        """Art. 20: data_type=medical + explicit_consent_obtained=True → PERMITTED."""
        r = self._eval(data_type="medical", explicit_consent_obtained=True)
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    def test_non_sensitive_data_type_no_explicit_consent_permitted(self):
        """Non-sensitive data_type does not trigger Art. 20 → PERMITTED."""
        r = self._eval(data_type="name", explicit_consent_obtained=False)
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    # --- Art. 28 Cross-border Transfer: DENIED ---

    def test_cross_border_to_cn_no_consent_denied(self):
        """Art. 28: cross_border_transfer + CN + no consent → DENIED."""
        r = self._eval(
            cross_border_transfer=True,
            transfer_country="CN",
            individual_consent_for_transfer=False,
            equivalent_protection_confirmed=False,
        )
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_cross_border_to_us_no_consent_denied(self):
        """Art. 28: cross_border_transfer + US (not on PPC adequacy list) + no consent → DENIED."""
        r = self._eval(
            cross_border_transfer=True,
            transfer_country="US",
            individual_consent_for_transfer=False,
            equivalent_protection_confirmed=False,
        )
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_cross_border_to_ru_no_consent_denied(self):
        """Art. 28: cross_border_transfer + RU + no consent → DENIED."""
        r = self._eval(
            cross_border_transfer=True,
            transfer_country="RU",
            individual_consent_for_transfer=False,
            equivalent_protection_confirmed=False,
        )
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_cross_border_denial_cites_appi_art28(self):
        """Art. 28 denial cites APPI Art. 28."""
        r = self._eval(
            cross_border_transfer=True,
            transfer_country="CN",
            individual_consent_for_transfer=False,
            equivalent_protection_confirmed=False,
        )
        assert "28" in r.regulation or "APPI" in r.regulation

    def test_cross_border_to_de_eu_adequacy_permitted(self):
        """Art. 28: transfer to DE (EU adequacy) → PERMITTED."""
        r = self._eval(cross_border_transfer=True, transfer_country="DE")
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    def test_cross_border_to_uk_adequacy_permitted(self):
        """Art. 28: transfer to UK (PPC adequacy) → PERMITTED."""
        r = self._eval(cross_border_transfer=True, transfer_country="UK")
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    def test_cross_border_no_consent_but_equivalent_protection_permitted(self):
        """Art. 28: transfer with equivalent_protection_confirmed=True → PERMITTED."""
        r = self._eval(
            cross_border_transfer=True,
            transfer_country="IN",
            individual_consent_for_transfer=False,
            equivalent_protection_confirmed=True,
        )
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    # --- Art. 23 + PPC AI Guidelines §3.2: REQUIRES_HUMAN_REVIEW ---

    def test_automated_profiling_no_opt_out_requires_human_review(self):
        """Art. 23 + PPC §3.2: automated_profiling + no opt-out → REQUIRES_HUMAN_REVIEW."""
        r = self._eval(
            automated_profiling_affecting_rights=True,
            opt_out_mechanism_provided=False,
        )
        assert r.decision == "REQUIRES_HUMAN_REVIEW"
        assert not r.is_denied

    def test_automated_profiling_rhr_cites_appi_art23(self):
        """Art. 23 + PPC §3.2 REQUIRES_HUMAN_REVIEW cites APPI Art. 23."""
        r = self._eval(
            automated_profiling_affecting_rights=True,
            opt_out_mechanism_provided=False,
        )
        assert "23" in r.regulation or "PPC" in r.regulation or "APPI" in r.regulation

    def test_automated_profiling_with_opt_out_permitted(self):
        """Art. 23: automated_profiling + opt_out_mechanism_provided=True → PERMITTED."""
        r = self._eval(
            automated_profiling_affecting_rights=True,
            opt_out_mechanism_provided=True,
        )
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    # --- Edge cases ---

    def test_empty_dict_permitted(self):
        """Empty document → PERMITTED (no triggering conditions)."""
        r = japan_mod.JapanAPPIFilter().filter({})
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    def test_filter_name_set(self):
        """filter_name is set on result."""
        r = japan_mod.JapanAPPIFilter().filter({})
        assert r.filter_name


# ===========================================================================
# TestJapanFSAAIFilter
# ===========================================================================


class TestJapanFSAAIFilter:
    """FSA AI governance: FIEA Art. 40, Customer-Oriented Conduct Principle 3,
    Insurance Business Act Art. 113 + FSA III-2-9, FSA Stress Testing."""

    def _eval(self, **kwargs):
        return japan_mod.JapanFSAAIFilter().filter(kwargs)

    # --- FIEA Art. 40 Suitability Principle: DENIED ---

    def test_ai_product_recommendation_no_suitability_docs_denied(self):
        """FIEA Art. 40: ai_financial_product_recommendation + no suitability docs → DENIED."""
        r = self._eval(
            ai_financial_product_recommendation=True,
            suitability_documentation_present=False,
        )
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_fiea_art40_denial_cites_regulation(self):
        """FIEA Art. 40 denial cites FIEA Art. 40 or Suitability."""
        r = self._eval(
            ai_financial_product_recommendation=True,
            suitability_documentation_present=False,
        )
        assert "40" in r.regulation or "FIEA" in r.regulation or "Suitability" in r.regulation

    def test_ai_product_recommendation_with_suitability_docs_permitted(self):
        """FIEA Art. 40: suitability_documentation_present=True → PERMITTED."""
        r = self._eval(
            ai_financial_product_recommendation=True,
            suitability_documentation_present=True,
        )
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    # --- FSA Customer-Oriented Conduct Principle 3: DENIED ---

    def test_ai_credit_scoring_no_explainability_denied(self):
        """Principle 3: ai_credit_scoring + no explainability_to_borrower_documented → DENIED."""
        r = self._eval(ai_credit_scoring=True, explainability_to_borrower_documented=False)
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_fsa_principle3_denial_cites_regulation(self):
        """Principle 3 denial cites FSA Customer-Oriented Business Conduct."""
        r = self._eval(ai_credit_scoring=True, explainability_to_borrower_documented=False)
        assert "FSA" in r.regulation or "Principle" in r.regulation or "Customer" in r.regulation

    def test_ai_credit_scoring_with_explainability_permitted(self):
        """Principle 3: ai_credit_scoring + explainability_to_borrower_documented=True → PERMITTED."""
        r = self._eval(ai_credit_scoring=True, explainability_to_borrower_documented=True)
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    # --- Insurance Business Act Art. 113 + FSA III-2-9: DENIED ---

    def test_ai_insurance_underwriting_no_actuarial_opinion_denied(self):
        """IBA Art. 113: ai_insurance_underwriting + no actuarial_opinion → DENIED."""
        r = self._eval(
            ai_insurance_underwriting=True,
            actuarial_opinion_and_documentation_present=False,
        )
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_iba_art113_denial_cites_regulation(self):
        """IBA Art. 113 + FSA III-2-9 denial cites relevant regulation."""
        r = self._eval(
            ai_insurance_underwriting=True,
            actuarial_opinion_and_documentation_present=False,
        )
        assert "113" in r.regulation or "Insurance" in r.regulation or "FSA" in r.regulation

    def test_ai_insurance_underwriting_with_actuarial_opinion_permitted(self):
        """IBA Art. 113: actuarial_opinion present → PERMITTED."""
        r = self._eval(
            ai_insurance_underwriting=True,
            actuarial_opinion_and_documentation_present=True,
        )
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    # --- FSA Stress Testing (Financial Conglomerates): REQUIRES_HUMAN_REVIEW ---

    def test_ai_financial_model_no_stress_testing_requires_human_review(self):
        """FSA Stress Testing: ai_financial_model_in_production + no fsa_stress_testing → REQUIRES_HUMAN_REVIEW."""
        r = self._eval(ai_financial_model_in_production=True, fsa_stress_testing_completed=False)
        assert r.decision == "REQUIRES_HUMAN_REVIEW"
        assert not r.is_denied

    def test_fsa_stress_testing_rhr_cites_regulation(self):
        """FSA Stress Testing RHR cites FSA Supervisory Guidelines."""
        r = self._eval(ai_financial_model_in_production=True, fsa_stress_testing_completed=False)
        assert "FSA" in r.regulation or "Stress" in r.regulation or "Conglomerate" in r.regulation

    def test_ai_financial_model_with_stress_testing_permitted(self):
        """FSA Stress Testing: fsa_stress_testing_completed=True → PERMITTED."""
        r = self._eval(ai_financial_model_in_production=True, fsa_stress_testing_completed=True)
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    # --- Edge cases ---

    def test_empty_dict_permitted(self):
        """Empty document → PERMITTED."""
        r = japan_mod.JapanFSAAIFilter().filter({})
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    def test_filter_name_set(self):
        """filter_name is set on result."""
        r = japan_mod.JapanFSAAIFilter().filter({})
        assert r.filter_name


# ===========================================================================
# TestJapanAIGovernanceFilter
# ===========================================================================


class TestJapanAIGovernanceFilter:
    """METI AI Governance Guidelines v1.1 §§4, 4.8; Japan AI Strategy 2022 §2.1;
    METI GenAI Guidelines 2023 §3; Cabinet Office AI Strategy §3.3."""

    def _eval(self, **kwargs):
        return japan_mod.JapanAIGovernanceFilter().filter(kwargs)

    # --- METI v1.1 §4 — DENIED ---

    def test_high_impact_ai_no_meti_self_assessment_denied(self):
        """METI v1.1 §4: high_impact_ai_system + no meti_ai_governance_self_assessment → DENIED."""
        r = self._eval(
            high_impact_ai_system=True,
            meti_ai_governance_self_assessment_completed=False,
        )
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_meti_self_assessment_denial_cites_regulation(self):
        """METI v1.1 §4 denial cites METI AI Governance Guideline."""
        r = self._eval(
            high_impact_ai_system=True,
            meti_ai_governance_self_assessment_completed=False,
        )
        assert "METI" in r.regulation or "v1.1" in r.regulation or "§4" in r.regulation

    def test_high_impact_ai_with_meti_self_assessment_permitted(self):
        """METI v1.1 §4: self-assessment completed → PERMITTED."""
        r = self._eval(
            high_impact_ai_system=True,
            meti_ai_governance_self_assessment_completed=True,
        )
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    # --- Japan AI Strategy 2022 §2.1 + METI v1.1 §4.8 — DENIED ---

    def test_ai_system_no_human_oversight_denied(self):
        """AI Strategy §2.1 + METI §4.8: ai_system_deployed + no human_oversight → DENIED."""
        r = self._eval(ai_system_deployed=True, human_oversight_mechanism_present=False)
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_human_oversight_denial_cites_regulation(self):
        """AI Strategy §2.1 + METI §4.8 denial cites Japan AI Strategy 2022 or METI."""
        r = self._eval(ai_system_deployed=True, human_oversight_mechanism_present=False)
        regulation = r.regulation.lower()
        assert "ai strategy" in regulation or "meti" in regulation or "oversight" in regulation

    def test_ai_system_with_human_oversight_permitted(self):
        """AI Strategy §2.1: ai_system_deployed + human_oversight_mechanism_present=True → PERMITTED."""
        r = self._eval(ai_system_deployed=True, human_oversight_mechanism_present=True)
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    # --- METI GenAI Guidelines 2023 §3 — DENIED ---

    def test_generative_ai_no_meti_genai_compliance_denied(self):
        """METI GenAI §3: generative_ai_system + no meti_genai_compliance → DENIED."""
        r = self._eval(
            generative_ai_system=True,
            meti_genai_guidelines_compliance_documented=False,
        )
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_genai_denial_cites_meti_genai_guidelines(self):
        """METI GenAI §3 denial cites METI Generative AI Guidelines 2023."""
        r = self._eval(
            generative_ai_system=True,
            meti_genai_guidelines_compliance_documented=False,
        )
        assert "METI" in r.regulation or "GenAI" in r.regulation or "Generative" in r.regulation

    def test_generative_ai_with_meti_genai_compliance_permitted(self):
        """METI GenAI §3: compliance documented → PERMITTED."""
        r = self._eval(
            generative_ai_system=True,
            meti_genai_guidelines_compliance_documented=True,
        )
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    # --- Cabinet Office AI Strategy §3.3 — REQUIRES_HUMAN_REVIEW ---

    def test_public_services_ai_no_cabinet_risk_assessment_requires_human_review(self):
        """Cabinet Office §3.3: ai_for_public_services + no risk assessment → REQUIRES_HUMAN_REVIEW."""
        r = self._eval(
            ai_for_public_services=True,
            cabinet_office_risk_assessment_completed=False,
        )
        assert r.decision == "REQUIRES_HUMAN_REVIEW"
        assert not r.is_denied

    def test_public_services_rhr_cites_cabinet_office(self):
        """Cabinet Office §3.3 REQUIRES_HUMAN_REVIEW cites Cabinet Office strategy."""
        r = self._eval(
            ai_for_public_services=True,
            cabinet_office_risk_assessment_completed=False,
        )
        assert "Cabinet" in r.regulation or "§3.3" in r.regulation or "AI Strategy" in r.regulation

    def test_public_services_ai_with_cabinet_risk_assessment_permitted(self):
        """Cabinet Office §3.3: risk assessment completed → PERMITTED."""
        r = self._eval(
            ai_for_public_services=True,
            cabinet_office_risk_assessment_completed=True,
        )
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    # --- Edge cases ---

    def test_empty_dict_permitted(self):
        """Empty document → PERMITTED."""
        r = japan_mod.JapanAIGovernanceFilter().filter({})
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    def test_filter_name_set(self):
        """filter_name is set on result."""
        r = japan_mod.JapanAIGovernanceFilter().filter({})
        assert r.filter_name


# ===========================================================================
# TestJapanCrossBorderFilter
# ===========================================================================


class TestJapanCrossBorderFilter:
    """Cross-border AI data flows: APPI Art. 28 + PPC; Japan AML/FSA AML;
    FSA Cloud Governance; PPC US adequacy pending."""

    def _eval(self, **kwargs):
        return japan_mod.JapanCrossBorderFilter().filter(kwargs)

    # --- APPI Art. 28 + PPC — personal data to CN/RU/KP: DENIED ---

    def test_personal_data_to_cn_no_ppc_adequacy_denied(self):
        """APPI Art. 28: personal_data_transfer_country=CN + no ppc_adequacy → DENIED."""
        r = self._eval(
            personal_data_transfer_country="CN",
            ppc_adequacy_or_equivalent_confirmed=False,
        )
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_personal_data_to_ru_no_ppc_adequacy_denied(self):
        """APPI Art. 28: personal_data_transfer_country=RU + no ppc_adequacy → DENIED."""
        r = self._eval(
            personal_data_transfer_country="RU",
            ppc_adequacy_or_equivalent_confirmed=False,
        )
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_personal_data_to_kp_no_ppc_adequacy_denied(self):
        """APPI Art. 28: personal_data_transfer_country=KP + no ppc_adequacy → DENIED."""
        r = self._eval(
            personal_data_transfer_country="KP",
            ppc_adequacy_or_equivalent_confirmed=False,
        )
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_ppc_restricted_denial_cites_appi_art28(self):
        """APPI Art. 28 denial cites APPI Art. 28 + PPC."""
        r = self._eval(
            personal_data_transfer_country="CN",
            ppc_adequacy_or_equivalent_confirmed=False,
        )
        assert "28" in r.regulation or "APPI" in r.regulation or "PPC" in r.regulation

    def test_personal_data_to_cn_with_ppc_adequacy_permitted(self):
        """APPI Art. 28: CN + ppc_adequacy_or_equivalent_confirmed=True → PERMITTED."""
        r = self._eval(
            personal_data_transfer_country="CN",
            ppc_adequacy_or_equivalent_confirmed=True,
        )
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    # --- Japan AML + FSA AML/CFT: DENIED ---

    def test_financial_ai_data_to_kp_fatf_denied(self):
        """AML: financial_ai_data_transfer_jurisdiction=KP (FATF blacklist) → DENIED."""
        r = self._eval(financial_ai_data_transfer_jurisdiction="KP")
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_financial_ai_data_to_ir_fatf_denied(self):
        """AML: financial_ai_data_transfer_jurisdiction=IR (FATF blacklist) → DENIED."""
        r = self._eval(financial_ai_data_transfer_jurisdiction="IR")
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_financial_ai_data_to_mm_fatf_denied(self):
        """AML: financial_ai_data_transfer_jurisdiction=MM (FATF grey list) → DENIED."""
        r = self._eval(financial_ai_data_transfer_jurisdiction="MM")
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_aml_denial_cites_japan_aml_fsa(self):
        """AML denial cites Japan AML Act or FSA AML/CFT Guidelines."""
        r = self._eval(financial_ai_data_transfer_jurisdiction="KP")
        assert "AML" in r.regulation or "FIEA" in r.regulation or "FSA" in r.regulation

    def test_financial_ai_data_to_us_fatf_compliant_permitted(self):
        """AML: financial_ai_data_transfer_jurisdiction=US (FATF compliant) → PERMITTED."""
        r = self._eval(financial_ai_data_transfer_jurisdiction="US")
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    # --- FSA Cloud Governance Framework: DENIED ---

    def test_fsa_regulated_entity_non_approved_cloud_denied(self):
        """FSA Cloud: serves_fsa_regulated_entity + aws_us_east_1 (non-approved) → DENIED."""
        r = self._eval(serves_fsa_regulated_entity=True, cloud_region="aws_us_east_1")
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_fsa_cloud_denial_cites_regulation(self):
        """FSA Cloud denial cites FSA Cloud Governance Framework."""
        r = self._eval(serves_fsa_regulated_entity=True, cloud_region="gcp_us_central1")
        assert "FSA" in r.regulation or "Cloud" in r.regulation or "Tokyo" in r.regulation

    def test_fsa_regulated_entity_aws_tokyo_permitted(self):
        """FSA Cloud: serves_fsa_regulated_entity + aws_tokyo → PERMITTED."""
        r = self._eval(serves_fsa_regulated_entity=True, cloud_region="aws_tokyo")
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    def test_fsa_regulated_entity_gcp_tokyo_permitted(self):
        """FSA Cloud: serves_fsa_regulated_entity + gcp_tokyo → PERMITTED."""
        r = self._eval(serves_fsa_regulated_entity=True, cloud_region="gcp_tokyo")
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    def test_fsa_regulated_entity_azure_japan_east_permitted(self):
        """FSA Cloud: serves_fsa_regulated_entity + azure_japan_east → PERMITTED."""
        r = self._eval(serves_fsa_regulated_entity=True, cloud_region="azure_japan_east")
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    # --- APPI Art. 28 + PPC US adequacy pending: REQUIRES_HUMAN_REVIEW ---

    def test_japanese_nationals_data_to_us_no_consent_no_sccs_requires_human_review(self):
        """APPI Art. 28 + PPC US: japanese nationals + US + no consent + no SCCs → REQUIRES_HUMAN_REVIEW."""
        r = self._eval(
            japanese_nationals_personal_data=True,
            transfer_destination="US",
            individual_consent_for_us_transfer=False,
            sccs_equivalent_safeguards=False,
        )
        assert r.decision == "REQUIRES_HUMAN_REVIEW"
        assert not r.is_denied

    def test_us_transfer_rhr_cites_appi_art28_ppc(self):
        """APPI Art. 28 + PPC US RHR cites relevant regulation."""
        r = self._eval(
            japanese_nationals_personal_data=True,
            transfer_destination="US",
            individual_consent_for_us_transfer=False,
            sccs_equivalent_safeguards=False,
        )
        assert "28" in r.regulation or "PPC" in r.regulation or "APPI" in r.regulation

    def test_japanese_nationals_to_us_with_individual_consent_permitted(self):
        """APPI Art. 28: japanese nationals + US + individual_consent_for_us_transfer=True → PERMITTED."""
        r = self._eval(
            japanese_nationals_personal_data=True,
            transfer_destination="US",
            individual_consent_for_us_transfer=True,
            sccs_equivalent_safeguards=False,
        )
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    def test_japanese_nationals_to_us_with_sccs_equivalent_permitted(self):
        """APPI Art. 28: japanese nationals + US + sccs_equivalent_safeguards=True → PERMITTED."""
        r = self._eval(
            japanese_nationals_personal_data=True,
            transfer_destination="US",
            individual_consent_for_us_transfer=False,
            sccs_equivalent_safeguards=True,
        )
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    # --- Edge cases ---

    def test_empty_dict_permitted(self):
        """Empty document → PERMITTED."""
        r = japan_mod.JapanCrossBorderFilter().filter({})
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    def test_filter_name_set(self):
        """filter_name is set on result."""
        r = japan_mod.JapanCrossBorderFilter().filter({})
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
        """JapanLangChainPolicyGuard instantiates with a filter."""
        g = japan_mod.JapanLangChainPolicyGuard(japan_mod.JapanAPPIFilter())
        assert g is not None

    def test_langchain_permitted_returns_doc(self):
        """LangChain: PERMITTED doc is returned unchanged."""
        g = japan_mod.JapanLangChainPolicyGuard(japan_mod.JapanAPPIFilter())
        doc = {"note": "clean"}
        result = g.process(doc)
        assert result is doc

    def test_langchain_denied_raises_permission_error(self):
        """LangChain: DENIED raises PermissionError."""
        g = japan_mod.JapanLangChainPolicyGuard(japan_mod.JapanAPPIFilter())
        with pytest.raises(PermissionError) as exc_info:
            g.process(
                {
                    "personal_information_processing": True,
                    "consent_obtained": False,
                    "legitimate_purpose": False,
                }
            )
        assert exc_info.value.args[0]

    def test_langchain_permission_error_contains_regulation(self):
        """LangChain PermissionError message contains regulation string."""
        g = japan_mod.JapanLangChainPolicyGuard(japan_mod.JapanAPPIFilter())
        with pytest.raises(PermissionError) as exc_info:
            g.process(
                {
                    "personal_information_processing": True,
                    "consent_obtained": False,
                    "legitimate_purpose": False,
                }
            )
        assert "APPI" in str(exc_info.value) or "15" in str(exc_info.value)

    # -----------------------------------------------------------------------
    # CrewAI
    # -----------------------------------------------------------------------

    def test_crewai_instantiates(self):
        """JapanCrewAIGovernanceGuard instantiates with a filter."""
        g = japan_mod.JapanCrewAIGovernanceGuard(japan_mod.JapanFSAAIFilter())
        assert g is not None

    def test_crewai_permitted_returns_doc(self):
        """CrewAI: PERMITTED doc is returned unchanged."""
        g = japan_mod.JapanCrewAIGovernanceGuard(japan_mod.JapanFSAAIFilter())
        doc = {"ok": True}
        result = g._run(doc)
        assert result is doc

    def test_crewai_denied_raises_permission_error(self):
        """CrewAI: DENIED raises PermissionError."""
        g = japan_mod.JapanCrewAIGovernanceGuard(japan_mod.JapanFSAAIFilter())
        with pytest.raises(PermissionError):
            g._run(
                {
                    "ai_financial_product_recommendation": True,
                    "suitability_documentation_present": False,
                }
            )

    def test_crewai_requires_human_review_returns_doc(self):
        """CrewAI: REQUIRES_HUMAN_REVIEW does NOT raise — returns doc."""
        g = japan_mod.JapanCrewAIGovernanceGuard(japan_mod.JapanFSAAIFilter())
        doc = {"ai_financial_model_in_production": True, "fsa_stress_testing_completed": False}
        result = g._run(doc)
        assert result is doc

    # -----------------------------------------------------------------------
    # AutoGen
    # -----------------------------------------------------------------------

    def test_autogen_instantiates(self):
        """JapanAutoGenGovernedAgent instantiates with a filter."""
        a = japan_mod.JapanAutoGenGovernedAgent(japan_mod.JapanAIGovernanceFilter())
        assert a is not None

    def test_autogen_permitted_returns_doc(self):
        """AutoGen: PERMITTED doc is returned unchanged."""
        a = japan_mod.JapanAutoGenGovernedAgent(japan_mod.JapanAIGovernanceFilter())
        doc = {"safe": True}
        result = a.generate_reply(doc)
        assert result is doc

    def test_autogen_denied_raises_permission_error(self):
        """AutoGen: DENIED raises PermissionError."""
        a = japan_mod.JapanAutoGenGovernedAgent(japan_mod.JapanAIGovernanceFilter())
        with pytest.raises(PermissionError):
            a.generate_reply(
                {
                    "high_impact_ai_system": True,
                    "meti_ai_governance_self_assessment_completed": False,
                }
            )

    def test_autogen_requires_human_review_returns_doc(self):
        """AutoGen: REQUIRES_HUMAN_REVIEW does NOT raise — returns doc."""
        a = japan_mod.JapanAutoGenGovernedAgent(japan_mod.JapanAIGovernanceFilter())
        doc = {"ai_for_public_services": True, "cabinet_office_risk_assessment_completed": False}
        result = a.generate_reply(doc)
        assert result is doc

    # -----------------------------------------------------------------------
    # Semantic Kernel
    # -----------------------------------------------------------------------

    def test_semantic_kernel_instantiates(self):
        """JapanSemanticKernelPlugin instantiates with a filter."""
        p = japan_mod.JapanSemanticKernelPlugin(japan_mod.JapanCrossBorderFilter())
        assert p is not None

    def test_semantic_kernel_permitted_returns_doc(self):
        """Semantic Kernel: PERMITTED doc is returned unchanged."""
        p = japan_mod.JapanSemanticKernelPlugin(japan_mod.JapanCrossBorderFilter())
        doc = {"nothing": "sensitive"}
        result = p.enforce_governance(doc)
        assert result is doc

    def test_semantic_kernel_denied_raises_permission_error(self):
        """Semantic Kernel: DENIED raises PermissionError."""
        p = japan_mod.JapanSemanticKernelPlugin(japan_mod.JapanCrossBorderFilter())
        with pytest.raises(PermissionError):
            p.enforce_governance(
                {
                    "personal_data_transfer_country": "CN",
                    "ppc_adequacy_or_equivalent_confirmed": False,
                }
            )

    def test_semantic_kernel_requires_human_review_returns_doc(self):
        """Semantic Kernel: REQUIRES_HUMAN_REVIEW does NOT raise — returns doc."""
        p = japan_mod.JapanSemanticKernelPlugin(japan_mod.JapanCrossBorderFilter())
        doc = {
            "japanese_nationals_personal_data": True,
            "transfer_destination": "US",
            "individual_consent_for_us_transfer": False,
            "sccs_equivalent_safeguards": False,
        }
        result = p.enforce_governance(doc)
        assert result is doc

    # -----------------------------------------------------------------------
    # LlamaIndex
    # -----------------------------------------------------------------------

    def test_llama_index_instantiates(self):
        """JapanLlamaIndexWorkflowGuard instantiates with a filter."""
        g = japan_mod.JapanLlamaIndexWorkflowGuard(japan_mod.JapanAPPIFilter())
        assert g is not None

    def test_llama_index_permitted_returns_doc(self):
        """LlamaIndex: PERMITTED doc is returned unchanged."""
        g = japan_mod.JapanLlamaIndexWorkflowGuard(japan_mod.JapanAPPIFilter())
        doc = {"payload": "clean"}
        result = g.process_event(doc)
        assert result is doc

    def test_llama_index_denied_raises_permission_error(self):
        """LlamaIndex: DENIED raises PermissionError."""
        g = japan_mod.JapanLlamaIndexWorkflowGuard(japan_mod.JapanAPPIFilter())
        with pytest.raises(PermissionError):
            g.process_event({"data_type": "medical", "explicit_consent_obtained": False})

    def test_llama_index_requires_human_review_returns_doc(self):
        """LlamaIndex: REQUIRES_HUMAN_REVIEW does NOT raise — returns doc."""
        g = japan_mod.JapanLlamaIndexWorkflowGuard(japan_mod.JapanAPPIFilter())
        doc = {"automated_profiling_affecting_rights": True, "opt_out_mechanism_provided": False}
        result = g.process_event(doc)
        assert result is doc

    # -----------------------------------------------------------------------
    # Haystack
    # -----------------------------------------------------------------------

    def test_haystack_instantiates(self):
        """JapanHaystackGovernanceComponent instantiates with a filter."""
        c = japan_mod.JapanHaystackGovernanceComponent(japan_mod.JapanFSAAIFilter())
        assert c is not None

    def test_haystack_returns_all_clean_docs(self):
        """Haystack: all clean docs returned unchanged."""
        c = japan_mod.JapanHaystackGovernanceComponent(japan_mod.JapanFSAAIFilter())
        docs = [{"id": 1}, {"id": 2}]
        result = c.run(docs)
        assert len(result["documents"]) == 2

    def test_haystack_excludes_denied_docs(self):
        """Haystack: DENIED document is excluded from output."""
        c = japan_mod.JapanHaystackGovernanceComponent(japan_mod.JapanFSAAIFilter())
        clean = {"id": "ok"}
        denied = {"ai_credit_scoring": True, "explainability_to_borrower_documented": False}
        result = c.run([clean, denied])
        assert len(result["documents"]) == 1
        assert result["documents"][0] is clean

    def test_haystack_requires_human_review_passes_through(self):
        """Haystack: REQUIRES_HUMAN_REVIEW doc is NOT excluded."""
        c = japan_mod.JapanHaystackGovernanceComponent(japan_mod.JapanFSAAIFilter())
        rhr_doc = {"ai_financial_model_in_production": True, "fsa_stress_testing_completed": False}
        result = c.run([rhr_doc])
        assert len(result["documents"]) == 1

    # -----------------------------------------------------------------------
    # DSPy
    # -----------------------------------------------------------------------

    def test_dspy_instantiates(self):
        """JapanDSPyGovernanceModule instantiates with a filter and module."""
        dummy = lambda doc, **kw: doc  # noqa: E731
        m = japan_mod.JapanDSPyGovernanceModule(japan_mod.JapanAIGovernanceFilter(), dummy)
        assert m is not None

    def test_dspy_permitted_calls_wrapped_module(self):
        """DSPy: PERMITTED doc is forwarded to the wrapped module."""
        sentinel = object()
        dummy = lambda doc, **kw: sentinel  # noqa: E731
        m = japan_mod.JapanDSPyGovernanceModule(japan_mod.JapanAIGovernanceFilter(), dummy)
        result = m.forward({"id": "clean"})
        assert result is sentinel

    def test_dspy_denied_raises_permission_error(self):
        """DSPy: DENIED raises PermissionError."""
        dummy = lambda doc, **kw: doc  # noqa: E731
        m = japan_mod.JapanDSPyGovernanceModule(japan_mod.JapanAIGovernanceFilter(), dummy)
        with pytest.raises(PermissionError):
            m.forward(
                {
                    "generative_ai_system": True,
                    "meti_genai_guidelines_compliance_documented": False,
                }
            )

    def test_dspy_requires_human_review_calls_wrapped_module(self):
        """DSPy: REQUIRES_HUMAN_REVIEW is forwarded to wrapped module (no raise)."""
        sentinel = object()
        dummy = lambda doc, **kw: sentinel  # noqa: E731
        m = japan_mod.JapanDSPyGovernanceModule(japan_mod.JapanAIGovernanceFilter(), dummy)
        doc = {"ai_for_public_services": True, "cabinet_office_risk_assessment_completed": False}
        result = m.forward(doc)
        assert result is sentinel

    # -----------------------------------------------------------------------
    # MAF (Microsoft Agent Framework)
    # -----------------------------------------------------------------------

    def test_maf_instantiates(self):
        """JapanMAFPolicyMiddleware instantiates with a filter."""
        mw = japan_mod.JapanMAFPolicyMiddleware(japan_mod.JapanCrossBorderFilter())
        assert mw is not None

    def test_maf_permitted_calls_next_handler(self):
        """MAF: PERMITTED message is forwarded to next_handler."""
        mw = japan_mod.JapanMAFPolicyMiddleware(japan_mod.JapanCrossBorderFilter())
        called = []
        mw.process({"id": "clean"}, lambda msg: called.append(msg))
        assert len(called) == 1

    def test_maf_denied_raises_permission_error(self):
        """MAF: DENIED raises PermissionError before next_handler is called."""
        mw = japan_mod.JapanMAFPolicyMiddleware(japan_mod.JapanCrossBorderFilter())
        called = []
        with pytest.raises(PermissionError):
            mw.process(
                {
                    "personal_data_transfer_country": "RU",
                    "ppc_adequacy_or_equivalent_confirmed": False,
                },
                lambda msg: called.append(msg),
            )
        assert len(called) == 0

    def test_maf_requires_human_review_calls_next_handler(self):
        """MAF: REQUIRES_HUMAN_REVIEW is forwarded to next_handler (no raise)."""
        mw = japan_mod.JapanMAFPolicyMiddleware(japan_mod.JapanCrossBorderFilter())
        called = []
        mw.process(
            {
                "japanese_nationals_personal_data": True,
                "transfer_destination": "US",
                "individual_consent_for_us_transfer": False,
                "sccs_equivalent_safeguards": False,
            },
            lambda msg: called.append(msg),
        )
        assert len(called) == 1


# ===========================================================================
# Additional edge-case tests
# ===========================================================================


class TestEdgeCases:
    """Additional edge cases covering boundary conditions across filters."""

    def test_appi_case_insensitive_data_type_medical_upper(self):
        """APPI Art. 20: data_type='MEDICAL' (uppercase) triggers denial."""
        r = japan_mod.JapanAPPIFilter().filter({"data_type": "MEDICAL", "explicit_consent_obtained": False})
        assert r.decision == "DENIED"

    def test_appi_creed_data_denied(self):
        """APPI Art. 20: data_type=creed triggers denial without explicit consent."""
        r = japan_mod.JapanAPPIFilter().filter({"data_type": "creed", "explicit_consent_obtained": False})
        assert r.decision == "DENIED"

    def test_appi_cross_border_fr_eu_member_state_permitted(self):
        """APPI Art. 28: transfer to FR (EU member state, adequacy) → PERMITTED."""
        r = japan_mod.JapanAPPIFilter().filter({"cross_border_transfer": True, "transfer_country": "FR"})
        assert r.decision == "PERMITTED"

    def test_fsa_no_flags_empty_dict_permitted(self):
        """FSA filter: empty dict → PERMITTED."""
        r = japan_mod.JapanFSAAIFilter().filter({})
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    def test_governance_filter_ai_system_not_deployed_no_oversight_trigger(self):
        """METI: ai_system_deployed=False → human oversight check not triggered → PERMITTED."""
        r = japan_mod.JapanAIGovernanceFilter().filter(
            {"ai_system_deployed": False, "human_oversight_mechanism_present": False}
        )
        assert r.decision == "PERMITTED"

    def test_cross_border_fsa_no_cloud_region_no_trigger(self):
        """FSA Cloud: serves_fsa_regulated_entity=True but cloud_region='' → no check → PERMITTED."""
        r = japan_mod.JapanCrossBorderFilter().filter({"serves_fsa_regulated_entity": True, "cloud_region": ""})
        assert r.decision == "PERMITTED"

    def test_cross_border_fatf_ly_denied(self):
        """AML: financial_ai_data_transfer_jurisdiction=LY (FATF grey list) → DENIED."""
        r = japan_mod.JapanCrossBorderFilter().filter({"financial_ai_data_transfer_jurisdiction": "LY"})
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_cross_border_fatf_sy_denied(self):
        """AML: financial_ai_data_transfer_jurisdiction=SY (FATF grey list) → DENIED."""
        r = japan_mod.JapanCrossBorderFilter().filter({"financial_ai_data_transfer_jurisdiction": "SY"})
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_filter_result_default_decision_is_permitted(self):
        """FilterResult default decision is PERMITTED."""
        r = japan_mod.FilterResult(filter_name="X")
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    def test_appi_filter_is_frozen_dataclass(self):
        """JapanAPPIFilter is a frozen dataclass (immutable)."""
        f = japan_mod.JapanAPPIFilter()
        with pytest.raises((AttributeError, TypeError)):
            f.FILTER_NAME = "CHANGED"  # type: ignore[misc]

    def test_fsa_filter_is_frozen_dataclass(self):
        """JapanFSAAIFilter is a frozen dataclass (immutable)."""
        f = japan_mod.JapanFSAAIFilter()
        with pytest.raises((AttributeError, TypeError)):
            f.FILTER_NAME = "CHANGED"  # type: ignore[misc]

    def test_governance_filter_is_frozen_dataclass(self):
        """JapanAIGovernanceFilter is a frozen dataclass (immutable)."""
        f = japan_mod.JapanAIGovernanceFilter()
        with pytest.raises((AttributeError, TypeError)):
            f.FILTER_NAME = "CHANGED"  # type: ignore[misc]

    def test_cross_border_filter_is_frozen_dataclass(self):
        """JapanCrossBorderFilter is a frozen dataclass (immutable)."""
        f = japan_mod.JapanCrossBorderFilter()
        with pytest.raises((AttributeError, TypeError)):
            f.FILTER_NAME = "CHANGED"  # type: ignore[misc]

    def test_langchain_multi_filter_all_clean_returns_results(self):
        """LangChain multi-filter mode: clean doc returns list of 4 FilterResults."""
        g = japan_mod.JapanLangChainPolicyGuard()
        results = g.invoke({"id": "clean"})
        assert isinstance(results, list)
        assert len(results) == 4

    def test_langchain_ainvoke_same_as_invoke(self):
        """LangChain ainvoke delegates to invoke (synchronous)."""
        g = japan_mod.JapanLangChainPolicyGuard(japan_mod.JapanAPPIFilter())
        doc = {"note": "clean"}
        assert g.ainvoke(doc) == g.invoke(doc)
