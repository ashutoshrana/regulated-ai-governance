"""
Tests for 38_uae_saudi_ai_governance.py — UAE & Saudi Arabia AI Governance

Covers:
  1. UAEPDPLFilter       — UAE PDPL Arts. 6, 9, 13, 22
  2. UAEAIRegFilter      — UAE AI Strategy 2031 §4; DIFC DFSA RPP Module;
                           ADGM FSRA AI Risk Management; UAE AI Ethics Principles
  3. SaudiNDMOFilter     — Saudi PDPL Arts. 5, 23, 29; NDMO DGF v2.0
  4. GCCCrossBorderFilter — GCC adequacy; FATF high-risk; SDAIA export;
                            GCC national cloud sovereignty
  5. FilterResult.is_denied property
  6. Eight ecosystem wrappers (LangChain, CrewAI, AutoGen, SK, LlamaIndex,
     Haystack, DSPy, MAF)
  7. Edge cases: missing keys, empty dict, None values
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

_MOD_NAME = "mod_uae_saudi"

spec = importlib.util.spec_from_file_location(
    _MOD_NAME,
    str(Path(__file__).parent.parent / "examples" / "38_uae_saudi_ai_governance.py"),
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
        r = mod.FilterResult(filter_name="F", decision="PENDING", regulation="X", reason="Y")
        assert r.is_denied is False

    def test_filter_result_has_required_fields(self):
        r = mod.FilterResult(filter_name="F", decision="DENIED", regulation="R", reason="Reason")
        assert r.filter_name == "F"
        assert r.decision == "DENIED"
        assert r.regulation == "R"
        assert r.reason == "Reason"

    def test_filter_result_default_decision_permitted(self):
        r = mod.FilterResult(filter_name="F", regulation="R", reason="ok")
        assert r.decision == "PERMITTED"
        assert r.is_denied is False


# ===========================================================================
# TestUAEPDPLFilter — UAE PDPL Arts. 6, 9, 13, 22
# ===========================================================================


class TestUAEPDPLFilter:
    """UAE Personal Data Protection Law (Federal Decree-Law No. 45/2021)."""

    def _eval(self, **kwargs):
        return mod.UAEPDPLFilter().filter(kwargs)

    # --- Art. 6 Lawful Basis: DENIED ---

    def test_personal_data_no_legal_basis_denied(self):
        r = self._eval(personal_data_processing=True, uae_legal_basis=None)
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_personal_data_no_legal_basis_cites_art6(self):
        r = self._eval(personal_data_processing=True, uae_legal_basis=None)
        assert "Art. 6" in r.regulation or "legal_basis" in r.regulation.lower() or "6" in r.regulation

    def test_personal_data_no_legal_basis_filter_name(self):
        r = self._eval(personal_data_processing=True, uae_legal_basis=None)
        assert r.filter_name == "UAE_PDPL_FILTER"

    def test_personal_data_false_no_trigger(self):
        # personal_data_processing=False should not trigger Art. 6
        r = self._eval(personal_data_processing=False, uae_legal_basis=None)
        assert (
            r.decision != "DENIED"
            or "Art. 9" in r.regulation
            or "Art. 22" in r.regulation
            or r.decision in {"PERMITTED", "REQUIRES_HUMAN_REVIEW"}
        )

    def test_personal_data_with_legal_basis_permitted(self):
        r = self._eval(personal_data_processing=True, uae_legal_basis="consent")
        assert r.decision == "PERMITTED"

    def test_personal_data_legal_basis_true_permitted(self):
        r = self._eval(personal_data_processing=True, uae_legal_basis=True)
        assert r.decision == "PERMITTED"

    # --- Art. 9 Sensitive Data: DENIED ---

    def test_health_data_no_explicit_consent_denied(self):
        r = self._eval(data_category="health", explicit_consent_obtained=False)
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_health_data_cites_art9(self):
        r = self._eval(data_category="health", explicit_consent_obtained=False)
        assert "Art. 9" in r.regulation or "9" in r.regulation

    def test_financial_data_no_explicit_consent_denied(self):
        r = self._eval(data_category="financial", explicit_consent_obtained=False)
        assert r.decision == "DENIED"

    def test_biometric_data_no_explicit_consent_denied(self):
        r = self._eval(data_category="biometric", explicit_consent_obtained=False)
        assert r.decision == "DENIED"

    def test_religious_data_no_explicit_consent_denied(self):
        r = self._eval(data_category="religious", explicit_consent_obtained=False)
        assert r.decision == "DENIED"

    def test_sensitive_data_with_explicit_consent_permitted(self):
        r = self._eval(data_category="health", explicit_consent_obtained=True)
        assert r.decision == "PERMITTED"

    def test_non_sensitive_data_no_explicit_consent_permitted(self):
        r = self._eval(data_category="name", explicit_consent_obtained=False)
        assert r.decision == "PERMITTED"

    # --- Art. 22 Cross-Border: DENIED ---

    def test_transfer_to_cn_without_dta_denied(self):
        r = self._eval(destination_country="CN", data_transfer_agreement=False)
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_transfer_to_cn_cites_art22(self):
        r = self._eval(destination_country="CN", data_transfer_agreement=False)
        assert "Art. 22" in r.regulation or "22" in r.regulation

    def test_transfer_to_ru_without_dta_denied(self):
        r = self._eval(destination_country="RU", data_transfer_agreement=False)
        assert r.decision == "DENIED"

    def test_transfer_to_kp_without_dta_denied(self):
        r = self._eval(destination_country="KP", data_transfer_agreement=False)
        assert r.decision == "DENIED"

    def test_transfer_to_ir_without_dta_denied(self):
        r = self._eval(destination_country="IR", data_transfer_agreement=False)
        assert r.decision == "DENIED"

    def test_transfer_to_by_without_dta_denied(self):
        r = self._eval(destination_country="BY", data_transfer_agreement=False)
        assert r.decision == "DENIED"

    def test_transfer_to_sy_without_dta_denied(self):
        r = self._eval(destination_country="SY", data_transfer_agreement=False)
        assert r.decision == "DENIED"

    def test_transfer_to_non_adequate_with_dta_permitted(self):
        r = self._eval(destination_country="CN", data_transfer_agreement=True)
        assert r.decision == "PERMITTED"

    def test_transfer_to_us_permitted(self):
        # US is not in UAE_NON_ADEQUATE_COUNTRIES
        r = self._eval(destination_country="US")
        assert r.decision == "PERMITTED"

    def test_transfer_no_destination_permitted(self):
        r = self._eval()
        assert r.decision == "PERMITTED"

    # --- Art. 13 Automated Decision-Making: REQUIRES_HUMAN_REVIEW ---

    def test_automated_decision_no_human_review_rhr(self):
        r = self._eval(automated_decision=True, human_review=False)
        assert r.decision == "REQUIRES_HUMAN_REVIEW"
        assert not r.is_denied

    def test_automated_decision_rhr_cites_art13(self):
        r = self._eval(automated_decision=True, human_review=False)
        assert "Art. 13" in r.regulation or "13" in r.regulation

    def test_automated_decision_with_human_review_permitted(self):
        r = self._eval(automated_decision=True, human_review=True)
        assert r.decision == "PERMITTED"

    def test_no_automated_decision_permitted(self):
        r = self._eval(automated_decision=False)
        assert r.decision == "PERMITTED"

    # --- Edge cases ---

    def test_empty_dict_permitted(self):
        r = mod.UAEPDPLFilter().filter({})
        assert r.decision == "PERMITTED"

    def test_filter_name_constant(self):
        assert mod.UAEPDPLFilter().FILTER_NAME == "UAE_PDPL_FILTER"


# ===========================================================================
# TestUAEAIRegFilter — UAE AI Strategy 2031 + ADGM + DIFC
# ===========================================================================


class TestUAEAIRegFilter:
    """UAE AI Strategy 2031 §4, DIFC DFSA RPP Module, ADGM FSRA AI RMF,
    UAE AI Ethics Principles."""

    def _eval(self, **kwargs):
        return mod.UAEAIRegFilter().filter(kwargs)

    # --- UAE AI Strategy §4 High-Risk: DENIED ---

    def test_high_risk_ai_no_impact_assessment_denied(self):
        r = self._eval(ai_risk_level="high", uae_ai_impact_assessed=False)
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_high_risk_cites_uae_ai_strategy(self):
        r = self._eval(ai_risk_level="high", uae_ai_impact_assessed=False)
        assert "UAE AI Strategy" in r.regulation or "AI Strategy" in r.regulation or "§4" in r.regulation

    def test_high_risk_ai_filter_name(self):
        r = self._eval(ai_risk_level="high", uae_ai_impact_assessed=False)
        assert r.filter_name == "UAE_AI_REG_FILTER"

    def test_high_risk_ai_with_impact_assessment_permitted(self):
        r = self._eval(ai_risk_level="high", uae_ai_impact_assessed=True)
        assert r.decision == "PERMITTED"

    def test_low_risk_ai_no_impact_assessment_permitted(self):
        r = self._eval(ai_risk_level="low", uae_ai_impact_assessed=False)
        assert r.decision == "PERMITTED"

    def test_medium_risk_no_impact_assessment_permitted(self):
        r = self._eval(ai_risk_level="medium", uae_ai_impact_assessed=False)
        assert r.decision == "PERMITTED"

    # --- DIFC DFSA: DENIED ---

    def test_difc_no_dfsa_compliant_denied(self):
        r = self._eval(jurisdiction="DIFC", dfsa_ai_compliant=False)
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_difc_denied_cites_dfsa(self):
        r = self._eval(jurisdiction="DIFC", dfsa_ai_compliant=False)
        assert "DFSA" in r.regulation or "DIFC" in r.regulation

    def test_difc_with_dfsa_compliant_permitted(self):
        r = self._eval(jurisdiction="DIFC", dfsa_ai_compliant=True)
        assert r.decision == "PERMITTED"

    def test_non_difc_no_dfsa_permitted(self):
        r = self._eval(jurisdiction="mainland", dfsa_ai_compliant=False)
        assert r.decision == "PERMITTED"

    # --- ADGM FSRA: DENIED ---

    def test_adgm_no_fsra_compliant_denied(self):
        r = self._eval(jurisdiction="ADGM", fsra_ai_compliant=False)
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_adgm_denied_cites_fsra(self):
        r = self._eval(jurisdiction="ADGM", fsra_ai_compliant=False)
        assert "FSRA" in r.regulation or "ADGM" in r.regulation

    def test_adgm_with_fsra_compliant_permitted(self):
        r = self._eval(jurisdiction="ADGM", fsra_ai_compliant=True)
        assert r.decision == "PERMITTED"

    def test_non_adgm_no_fsra_permitted(self):
        r = self._eval(jurisdiction="mainland", fsra_ai_compliant=False)
        assert r.decision == "PERMITTED"

    # --- UAE AI Ethics Principles — GenAI Transparency: REQUIRES_HUMAN_REVIEW ---

    def test_genai_no_transparency_rhr(self):
        r = self._eval(genai_application=True, uae_transparency_requirement=False)
        assert r.decision == "REQUIRES_HUMAN_REVIEW"
        assert not r.is_denied

    def test_genai_rhr_cites_uae_ai_ethics(self):
        r = self._eval(genai_application=True, uae_transparency_requirement=False)
        assert "UAE AI Ethics" in r.regulation or "Transparency" in r.regulation or "Ethics" in r.regulation

    def test_genai_with_transparency_permitted(self):
        r = self._eval(genai_application=True, uae_transparency_requirement=True)
        assert r.decision == "PERMITTED"

    def test_no_genai_application_permitted(self):
        r = self._eval(genai_application=False)
        assert r.decision == "PERMITTED"

    # --- Edge cases ---

    def test_empty_dict_permitted(self):
        r = mod.UAEAIRegFilter().filter({})
        assert r.decision == "PERMITTED"

    def test_filter_name_constant(self):
        assert mod.UAEAIRegFilter().FILTER_NAME == "UAE_AI_REG_FILTER"


# ===========================================================================
# TestSaudiNDMOFilter — Saudi PDPL Arts. 5, 23, 29 + NDMO DGF
# ===========================================================================


class TestSaudiNDMOFilter:
    """Saudi Arabia PDPL (Royal Decree M/19) + NDMO Data Governance Framework."""

    def _eval(self, **kwargs):
        return mod.SaudiNDMOFilter().filter(kwargs)

    # --- PDPL Art. 5 Lawful Basis: DENIED ---

    def test_personal_data_no_saudi_consent_denied(self):
        r = self._eval(personal_data_processing=True, saudi_consent_obtained=False)
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_personal_data_denied_cites_art5(self):
        r = self._eval(personal_data_processing=True, saudi_consent_obtained=False)
        assert "Art. 5" in r.regulation or "5" in r.regulation

    def test_personal_data_denied_filter_name(self):
        r = self._eval(personal_data_processing=True, saudi_consent_obtained=False)
        assert r.filter_name == "SAUDI_NDMO_FILTER"

    def test_personal_data_with_consent_permitted(self):
        r = self._eval(personal_data_processing=True, saudi_consent_obtained=True, ndmo_compliant=True)
        assert r.decision == "PERMITTED"

    def test_no_personal_data_processing_no_art5_trigger(self):
        r = self._eval(personal_data_processing=False, saudi_consent_obtained=False, ndmo_compliant=True)
        assert r.decision == "PERMITTED"

    # --- PDPL Art. 23 Sensitive Data: DENIED ---

    def test_health_data_no_explicit_consent_denied(self):
        r = self._eval(data_category="health", explicit_consent_obtained=False)
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_health_data_denied_cites_art23(self):
        r = self._eval(data_category="health", explicit_consent_obtained=False)
        assert "Art. 23" in r.regulation or "23" in r.regulation

    def test_genetic_data_no_consent_denied(self):
        r = self._eval(data_category="genetic", explicit_consent_obtained=False)
        assert r.decision == "DENIED"

    def test_biometric_data_no_consent_denied(self):
        r = self._eval(data_category="biometric", explicit_consent_obtained=False)
        assert r.decision == "DENIED"

    def test_financial_data_no_consent_denied(self):
        r = self._eval(data_category="financial", explicit_consent_obtained=False)
        assert r.decision == "DENIED"

    def test_criminal_data_no_consent_denied(self):
        r = self._eval(data_category="criminal", explicit_consent_obtained=False)
        assert r.decision == "DENIED"

    def test_sensitive_with_explicit_consent_permitted(self):
        r = self._eval(data_category="health", explicit_consent_obtained=True, ndmo_compliant=True)
        assert r.decision == "PERMITTED"

    def test_non_sensitive_category_permitted(self):
        r = self._eval(data_category="name", explicit_consent_obtained=False, ndmo_compliant=True)
        assert r.decision == "PERMITTED"

    # --- PDPL Art. 29 Cross-Border: DENIED ---

    def test_transfer_to_non_adequate_without_sdaia_denied(self):
        r = self._eval(destination_country="CN", sdaia_authorization=False)
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_transfer_denied_cites_art29(self):
        r = self._eval(destination_country="CN", sdaia_authorization=False)
        assert "Art. 29" in r.regulation or "29" in r.regulation or "SDAIA" in r.regulation

    def test_transfer_to_non_adequate_with_sdaia_auth_permitted(self):
        r = self._eval(destination_country="CN", sdaia_authorization=True, ndmo_compliant=True)
        assert r.decision == "PERMITTED"

    def test_transfer_to_adequate_country_no_sdaia_permitted(self):
        # AE is in SAUDI_ADEQUATE_COUNTRIES
        r = self._eval(destination_country="AE", sdaia_authorization=False, ndmo_compliant=True)
        assert r.decision == "PERMITTED"

    def test_transfer_to_us_permitted(self):
        r = self._eval(destination_country="US", sdaia_authorization=False, ndmo_compliant=True)
        assert r.decision == "PERMITTED"

    def test_transfer_to_uk_permitted(self):
        r = self._eval(destination_country="UK", sdaia_authorization=False, ndmo_compliant=True)
        assert r.decision == "PERMITTED"

    def test_no_destination_country_permitted(self):
        r = self._eval(ndmo_compliant=True)
        assert r.decision == "PERMITTED"

    # --- NDMO DGF: REQUIRES_HUMAN_REVIEW ---

    def test_ndmo_not_compliant_rhr(self):
        r = self._eval(ndmo_compliant=False)
        assert r.decision == "REQUIRES_HUMAN_REVIEW"
        assert not r.is_denied

    def test_ndmo_rhr_cites_ndmo(self):
        r = self._eval(ndmo_compliant=False)
        assert "NDMO" in r.regulation

    def test_ndmo_compliant_permitted(self):
        r = self._eval(ndmo_compliant=True)
        assert r.decision == "PERMITTED"

    # --- Edge cases ---

    def test_empty_dict_rhr_due_to_ndmo(self):
        # empty dict → ndmo_compliant is falsy → REQUIRES_HUMAN_REVIEW
        r = mod.SaudiNDMOFilter().filter({})
        assert r.decision == "REQUIRES_HUMAN_REVIEW"

    def test_filter_name_constant(self):
        assert mod.SaudiNDMOFilter().FILTER_NAME == "SAUDI_NDMO_FILTER"


# ===========================================================================
# TestGCCCrossBorderFilter — GCC adequacy, FATF, SDAIA export, national cloud
# ===========================================================================


class TestGCCCrossBorderFilter:
    """GCC cross-border data and AI controls."""

    def _eval(self, **kwargs):
        return mod.GCCCrossBorderFilter().filter(kwargs)

    # --- GCC Adequacy: DENIED ---

    def test_personal_data_to_non_adequate_country_denied(self):
        r = self._eval(personal_data=True, destination_country="VN")
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_personal_data_denied_cites_gcc_framework(self):
        r = self._eval(personal_data=True, destination_country="VN")
        assert "UAE PDPL" in r.regulation or "Saudi PDPL" in r.regulation or "GCC" in r.regulation

    def test_personal_data_denied_filter_name(self):
        r = self._eval(personal_data=True, destination_country="VN")
        assert r.filter_name == "GCC_CROSS_BORDER_FILTER"

    def test_personal_data_to_us_permitted(self):
        r = self._eval(personal_data=True, destination_country="US")
        assert r.decision == "PERMITTED"

    def test_personal_data_to_uk_permitted(self):
        r = self._eval(personal_data=True, destination_country="UK")
        assert r.decision == "PERMITTED"

    def test_personal_data_to_de_permitted(self):
        r = self._eval(personal_data=True, destination_country="DE")
        assert r.decision == "PERMITTED"

    def test_personal_data_to_ae_permitted(self):
        r = self._eval(personal_data=True, destination_country="AE")
        assert r.decision == "PERMITTED"

    def test_personal_data_to_sa_permitted(self):
        r = self._eval(personal_data=True, destination_country="SA")
        assert r.decision == "PERMITTED"

    def test_personal_data_to_ca_permitted(self):
        r = self._eval(personal_data=True, destination_country="CA")
        assert r.decision == "PERMITTED"

    def test_personal_data_to_jp_permitted(self):
        r = self._eval(personal_data=True, destination_country="JP")
        assert r.decision == "PERMITTED"

    def test_no_personal_data_non_adequate_permitted(self):
        r = self._eval(personal_data=False, destination_country="VN")
        assert r.decision == "PERMITTED"

    # --- FATF High-Risk: DENIED ---

    def test_financial_data_to_kp_denied(self):
        r = self._eval(financial_data=True, destination_country="KP")
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_financial_data_to_kp_cites_fatf(self):
        r = self._eval(financial_data=True, destination_country="KP")
        assert "FATF" in r.regulation

    def test_financial_data_to_ir_denied(self):
        r = self._eval(financial_data=True, destination_country="IR")
        assert r.decision == "DENIED"

    def test_financial_data_to_mm_denied(self):
        r = self._eval(financial_data=True, destination_country="MM")
        assert r.decision == "DENIED"

    def test_financial_data_to_us_permitted(self):
        r = self._eval(financial_data=True, destination_country="US")
        assert r.decision == "PERMITTED"

    def test_no_financial_data_to_kp_permitted(self):
        # financial_data=False + KP: KP is also non-adequate
        # personal_data not set → first check passes
        # financial_data False → second check passes
        # no saudi_citizen_training_data → third passes
        # no critical_data → fourth passes
        r = self._eval(financial_data=False, destination_country="KP")
        assert r.decision == "PERMITTED"

    # --- SDAIA Export Approval: DENIED ---

    def test_saudi_citizen_training_data_no_sdaia_approval_denied(self):
        r = self._eval(saudi_citizen_training_data=True, sdaia_export_approval=False)
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_saudi_citizen_training_denied_cites_sdaia(self):
        r = self._eval(saudi_citizen_training_data=True, sdaia_export_approval=False)
        assert "SDAIA" in r.regulation

    def test_saudi_citizen_training_with_sdaia_approval_permitted(self):
        r = self._eval(saudi_citizen_training_data=True, sdaia_export_approval=True)
        assert r.decision == "PERMITTED"

    def test_no_saudi_citizen_training_permitted(self):
        r = self._eval(saudi_citizen_training_data=False, sdaia_export_approval=False)
        assert r.decision == "PERMITTED"

    # --- GCC National Cloud Sovereignty: REQUIRES_HUMAN_REVIEW ---

    def test_critical_data_non_gcc_cloud_rhr(self):
        r = self._eval(critical_data=True, cloud_region="aws_eu_west")
        assert r.decision == "REQUIRES_HUMAN_REVIEW"
        assert not r.is_denied

    def test_critical_data_rhr_cites_national_cloud_policy(self):
        r = self._eval(critical_data=True, cloud_region="aws_eu_west")
        assert "TRA" in r.regulation or "NDMO" in r.regulation or "Cloud" in r.regulation

    def test_critical_data_on_uae_gov_cloud_permitted(self):
        r = self._eval(critical_data=True, cloud_region="uae_gov_cloud")
        assert r.decision == "PERMITTED"

    def test_critical_data_on_ksa_gov_cloud_permitted(self):
        r = self._eval(critical_data=True, cloud_region="ksa_gov_cloud")
        assert r.decision == "PERMITTED"

    def test_critical_data_on_aws_uae_permitted(self):
        r = self._eval(critical_data=True, cloud_region="aws_uae")
        assert r.decision == "PERMITTED"

    def test_critical_data_on_gcp_doha_permitted(self):
        r = self._eval(critical_data=True, cloud_region="gcp_doha")
        assert r.decision == "PERMITTED"

    def test_critical_data_on_azure_uae_north_permitted(self):
        r = self._eval(critical_data=True, cloud_region="azure_uae_north")
        assert r.decision == "PERMITTED"

    def test_critical_data_on_azure_ksa_permitted(self):
        r = self._eval(critical_data=True, cloud_region="azure_ksa")
        assert r.decision == "PERMITTED"

    def test_no_critical_data_non_gcc_cloud_permitted(self):
        r = self._eval(critical_data=False, cloud_region="aws_eu_west")
        assert r.decision == "PERMITTED"

    def test_critical_data_no_cloud_region_rhr(self):
        r = self._eval(critical_data=True)
        assert r.decision == "REQUIRES_HUMAN_REVIEW"

    # --- Edge cases ---

    def test_empty_dict_permitted(self):
        r = mod.GCCCrossBorderFilter().filter({})
        assert r.decision == "PERMITTED"

    def test_filter_name_constant(self):
        assert mod.GCCCrossBorderFilter().FILTER_NAME == "GCC_CROSS_BORDER_FILTER"


# ===========================================================================
# TestConstants — module-level constants
# ===========================================================================


class TestConstants:
    """Verify constant sets contain expected values."""

    def test_uae_non_adequate_contains_cn(self):
        assert "CN" in mod.UAE_NON_ADEQUATE_COUNTRIES

    def test_uae_non_adequate_contains_ru(self):
        assert "RU" in mod.UAE_NON_ADEQUATE_COUNTRIES

    def test_uae_non_adequate_contains_kp(self):
        assert "KP" in mod.UAE_NON_ADEQUATE_COUNTRIES

    def test_uae_non_adequate_contains_ir(self):
        assert "IR" in mod.UAE_NON_ADEQUATE_COUNTRIES

    def test_saudi_adequate_contains_ae(self):
        assert "AE" in mod.SAUDI_ADEQUATE_COUNTRIES

    def test_saudi_adequate_contains_us(self):
        assert "US" in mod.SAUDI_ADEQUATE_COUNTRIES

    def test_gcc_adequate_contains_ae(self):
        assert "AE" in mod.GCC_ADEQUATE_COUNTRIES

    def test_gcc_adequate_contains_sa(self):
        assert "SA" in mod.GCC_ADEQUATE_COUNTRIES

    def test_gcc_adequate_contains_de(self):
        assert "DE" in mod.GCC_ADEQUATE_COUNTRIES

    def test_fatf_high_risk_contains_kp(self):
        assert "KP" in mod.FATF_HIGH_RISK

    def test_fatf_high_risk_contains_ir(self):
        assert "IR" in mod.FATF_HIGH_RISK

    def test_fatf_high_risk_contains_mm(self):
        assert "MM" in mod.FATF_HIGH_RISK

    def test_gcc_national_clouds_contains_uae_gov_cloud(self):
        assert "uae_gov_cloud" in mod.GCC_NATIONAL_CLOUDS

    def test_gcc_national_clouds_contains_ksa_gov_cloud(self):
        assert "ksa_gov_cloud" in mod.GCC_NATIONAL_CLOUDS

    def test_gcc_national_clouds_contains_azure_uae_north(self):
        assert "azure_uae_north" in mod.GCC_NATIONAL_CLOUDS


# ===========================================================================
# Ecosystem Wrapper Tests
# ===========================================================================


class TestUAELangChainPolicyGuard:
    """LangChain wrapper — process() and invoke() behaviour."""

    def test_process_denied_raises_permission_error(self):
        guard = mod.UAELangChainPolicyGuard(mod.UAEPDPLFilter())
        with pytest.raises(PermissionError):
            guard.process({"personal_data_processing": True, "uae_legal_basis": None})

    def test_process_permitted_returns_doc(self):
        guard = mod.UAELangChainPolicyGuard(mod.UAEPDPLFilter())
        doc = {"personal_data_processing": True, "uae_legal_basis": "consent"}
        result = guard.process(doc)
        assert result is doc

    def test_invoke_single_filter_denied_raises(self):
        guard = mod.UAELangChainPolicyGuard(mod.UAEAIRegFilter())
        with pytest.raises(PermissionError):
            guard.invoke({"ai_risk_level": "high", "uae_ai_impact_assessed": False})

    def test_invoke_single_filter_permitted_returns_list(self):
        guard = mod.UAELangChainPolicyGuard(mod.UAEAIRegFilter())
        results = guard.invoke({"ai_risk_level": "low"})
        assert isinstance(results, list)
        assert len(results) == 1

    def test_invoke_multi_filter_permitted(self):
        guard = mod.UAELangChainPolicyGuard()
        results = guard.invoke(
            {
                "personal_data_processing": True,
                "uae_legal_basis": "consent",
                "saudi_consent_obtained": True,
                "ndmo_compliant": True,
            }
        )
        assert all(not r.is_denied for r in results)

    def test_ainvoke_delegates_to_invoke(self):
        guard = mod.UAELangChainPolicyGuard(mod.UAEPDPLFilter())
        doc = {"personal_data_processing": True, "uae_legal_basis": "consent"}
        assert guard.ainvoke(doc) == guard.invoke(doc)


class TestUAECrewAIGovernanceGuard:
    """CrewAI wrapper — _run() behaviour."""

    def test_run_denied_raises_permission_error(self):
        guard = mod.UAECrewAIGovernanceGuard(mod.UAEPDPLFilter())
        with pytest.raises(PermissionError):
            guard._run({"data_category": "biometric", "explicit_consent_obtained": False})

    def test_run_permitted_returns_doc(self):
        guard = mod.UAECrewAIGovernanceGuard(mod.UAEPDPLFilter())
        doc = {"data_category": "biometric", "explicit_consent_obtained": True}
        assert guard._run(doc) is doc

    def test_run_rhr_not_raised(self):
        guard = mod.UAECrewAIGovernanceGuard(mod.UAEPDPLFilter())
        result = guard._run({"automated_decision": True, "human_review": False})
        # RHR is not DENIED so no exception
        assert result is not None

    def test_name_attribute_set(self):
        guard = mod.UAECrewAIGovernanceGuard(mod.UAEPDPLFilter())
        assert guard.name == "UAEGovernanceGuard"

    def test_description_attribute_set(self):
        guard = mod.UAECrewAIGovernanceGuard(mod.UAEPDPLFilter())
        assert "UAE" in guard.description or "governance" in guard.description.lower()


class TestUAEAutoGenGovernedAgent:
    """AutoGen wrapper — generate_reply() behaviour."""

    def test_generate_reply_denied_raises(self):
        agent = mod.UAEAutoGenGovernedAgent(mod.UAEAIRegFilter())
        with pytest.raises(PermissionError):
            agent.generate_reply({"jurisdiction": "DIFC", "dfsa_ai_compliant": False})

    def test_generate_reply_permitted_returns_doc(self):
        agent = mod.UAEAutoGenGovernedAgent(mod.UAEAIRegFilter())
        doc = {"jurisdiction": "DIFC", "dfsa_ai_compliant": True}
        assert agent.generate_reply(doc) is doc

    def test_generate_reply_none_messages_returns_empty(self):
        agent = mod.UAEAutoGenGovernedAgent(mod.UAEAIRegFilter())
        result = agent.generate_reply(None)
        assert result == {}

    def test_generate_reply_empty_dict_permitted(self):
        agent = mod.UAEAutoGenGovernedAgent(mod.UAEAIRegFilter())
        result = agent.generate_reply({})
        assert result == {}


class TestUAESemanticKernelPlugin:
    """Semantic Kernel wrapper — enforce_governance() behaviour."""

    def test_enforce_governance_denied_raises(self):
        plugin = mod.UAESemanticKernelPlugin(mod.SaudiNDMOFilter())
        with pytest.raises(PermissionError):
            plugin.enforce_governance({"personal_data_processing": True, "saudi_consent_obtained": False})

    def test_enforce_governance_permitted_returns_doc(self):
        plugin = mod.UAESemanticKernelPlugin(mod.SaudiNDMOFilter())
        doc = {"ndmo_compliant": True}
        assert plugin.enforce_governance(doc) is doc

    def test_enforce_governance_rhr_not_raised(self):
        plugin = mod.UAESemanticKernelPlugin(mod.SaudiNDMOFilter())
        doc = {"ndmo_compliant": False}
        result = plugin.enforce_governance(doc)
        assert result is doc


class TestUAELlamaIndexWorkflowGuard:
    """LlamaIndex wrapper — process_event() behaviour."""

    def test_process_event_denied_raises(self):
        guard = mod.UAELlamaIndexWorkflowGuard(mod.GCCCrossBorderFilter())
        with pytest.raises(PermissionError):
            guard.process_event({"personal_data": True, "destination_country": "VN"})

    def test_process_event_permitted_returns_doc(self):
        guard = mod.UAELlamaIndexWorkflowGuard(mod.GCCCrossBorderFilter())
        doc = {"personal_data": True, "destination_country": "US"}
        assert guard.process_event(doc) is doc

    def test_process_event_empty_permitted(self):
        guard = mod.UAELlamaIndexWorkflowGuard(mod.GCCCrossBorderFilter())
        result = guard.process_event({})
        assert result == {}


class TestUAEHaystackGovernanceComponent:
    """Haystack wrapper — run() behaviour."""

    def test_run_filters_out_denied_documents(self):
        comp = mod.UAEHaystackGovernanceComponent(mod.UAEPDPLFilter())
        docs = [
            {"personal_data_processing": True, "uae_legal_basis": None},  # DENIED
            {"personal_data_processing": True, "uae_legal_basis": "consent"},  # PERMITTED
        ]
        result = comp.run(docs)
        assert len(result["documents"]) == 1

    def test_run_empty_list_returns_empty(self):
        comp = mod.UAEHaystackGovernanceComponent(mod.UAEPDPLFilter())
        result = comp.run([])
        assert result == {"documents": []}

    def test_run_all_permitted_returns_all(self):
        comp = mod.UAEHaystackGovernanceComponent(mod.UAEPDPLFilter())
        docs = [{"data_category": "name"}]
        result = comp.run(docs)
        assert len(result["documents"]) == 1

    def test_run_rhr_documents_pass_through(self):
        comp = mod.UAEHaystackGovernanceComponent(mod.UAEPDPLFilter())
        docs = [{"automated_decision": True, "human_review": False}]  # RHR not DENIED
        result = comp.run(docs)
        assert len(result["documents"]) == 1


class TestUAEDSPyGovernanceModule:
    """DSPy wrapper — forward() behaviour."""

    def test_forward_denied_raises_permission_error(self):
        def mock_module(d, **kw):
            return d

        dspy_mod = mod.UAEDSPyGovernanceModule(mod.UAEAIRegFilter(), mock_module)
        with pytest.raises(PermissionError):
            dspy_mod.forward({"jurisdiction": "ADGM", "fsra_ai_compliant": False})

    def test_forward_permitted_delegates_to_module(self):
        sentinel = object()

        def mock_module(d, **kw):
            return sentinel

        dspy_mod = mod.UAEDSPyGovernanceModule(mod.UAEAIRegFilter(), mock_module)
        result = dspy_mod.forward({"jurisdiction": "ADGM", "fsra_ai_compliant": True})
        assert result is sentinel

    def test_forward_empty_doc_permitted(self):
        def mock_module(d, **kw):
            return "ok"

        dspy_mod = mod.UAEDSPyGovernanceModule(mod.UAEAIRegFilter(), mock_module)
        assert dspy_mod.forward({}) == "ok"


class TestUAEMAFPolicyMiddleware:
    """MAF middleware — process() behaviour."""

    def test_process_denied_raises_permission_error(self):
        middleware = mod.UAEMAFPolicyMiddleware(mod.GCCCrossBorderFilter())
        with pytest.raises(PermissionError):
            middleware.process(
                {"financial_data": True, "destination_country": "KP"},
                lambda m: m,
            )

    def test_process_permitted_calls_next_handler(self):
        middleware = mod.UAEMAFPolicyMiddleware(mod.GCCCrossBorderFilter())
        sentinel = object()
        result = middleware.process(
            {"financial_data": True, "destination_country": "US"},
            lambda m: sentinel,
        )
        assert result is sentinel

    def test_process_empty_message_permitted(self):
        middleware = mod.UAEMAFPolicyMiddleware(mod.GCCCrossBorderFilter())
        result = middleware.process({}, lambda m: "passed")
        assert result == "passed"

    def test_process_rhr_calls_next_handler(self):
        middleware = mod.UAEMAFPolicyMiddleware(mod.GCCCrossBorderFilter())
        called = []
        middleware.process(
            {"critical_data": True, "cloud_region": "aws_eu_west"},
            lambda m: called.append(True),
        )
        assert called  # next_handler was called because RHR is not DENIED
