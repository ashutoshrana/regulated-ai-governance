"""
Tests for 35_south_korea_ai_governance.py — South Korea AI Governance Framework
covering:
  1. KoreaPIPAFilter       — PIPA Arts. 15, 23, 28-8, 37-2 (2023 amendment)
  2. KoreaFSCAIFilter      — FSCMA Art. 7+63; CB Act Art. 26; IBA Art. 176
  3. KoreaAIBasicActFilter — AI Basic Act Arts. 35, 36, 46, 47 (enacted 2024)
  4. KoreaCrossBorderFilter — PIPA Art. 28-8 + FSC EFTA Art. 21-2 + FSC Cloud
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

_MOD_NAME = "mod_korea"

spec = importlib.util.spec_from_file_location(
    _MOD_NAME,
    str(Path(__file__).parent.parent / "examples" / "35_south_korea_ai_governance.py"),
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


# ===========================================================================
# TestKoreaPIPAFilter — PIPA Arts. 15, 23, 28-8, 37-2
# ===========================================================================


class TestKoreaPIPAFilter:
    """PIPA 2023 amendment — four principal controls."""

    def _eval(self, **kwargs):
        return mod.KoreaPIPAFilter().filter(kwargs)

    # --- Art. 15 Lawfulness of Collection: DENIED ---

    def test_personal_info_no_consent_no_purpose_denied(self):
        r = self._eval(
            personal_information_processing=True,
            consent_obtained=False,
            legitimate_purpose=False,
        )
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_personal_info_denied_cites_pipa_art_15(self):
        r = self._eval(
            personal_information_processing=True,
            consent_obtained=False,
            legitimate_purpose=False,
        )
        assert "15" in r.regulation or "Lawfulness" in r.regulation

    def test_personal_info_with_consent_permitted(self):
        r = self._eval(
            personal_information_processing=True,
            consent_obtained=True,
        )
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    def test_personal_info_no_consent_but_legitimate_purpose_permitted(self):
        r = self._eval(
            personal_information_processing=True,
            consent_obtained=False,
            legitimate_purpose=True,
        )
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    # --- Art. 23 Sensitive Information: DENIED ---

    def test_health_data_no_explicit_consent_denied(self):
        r = self._eval(data_type="health", explicit_consent_obtained=False)
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_biometric_data_no_explicit_consent_denied(self):
        r = self._eval(data_type="biometric", explicit_consent_obtained=False)
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_ideology_data_no_explicit_consent_denied(self):
        r = self._eval(data_type="ideology", explicit_consent_obtained=False)
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_criminal_data_no_explicit_consent_denied(self):
        r = self._eval(data_type="criminal", explicit_consent_obtained=False)
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_union_data_no_explicit_consent_denied(self):
        r = self._eval(data_type="union", explicit_consent_obtained=False)
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_sensitive_denied_cites_pipa_art_23(self):
        r = self._eval(data_type="health", explicit_consent_obtained=False)
        assert "23" in r.regulation or "Sensitive" in r.regulation

    def test_health_data_with_explicit_consent_permitted(self):
        r = self._eval(data_type="health", explicit_consent_obtained=True)
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    def test_non_sensitive_data_type_permitted(self):
        r = self._eval(data_type="name")
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    # --- Art. 28-8 Cross-border Transfer: DENIED ---

    def test_cross_border_to_jp_no_pipc_approval_denied(self):
        r = self._eval(
            cross_border_transfer=True,
            transfer_country="JP",
            pipc_approval_obtained=False,
            individual_consent_for_transfer=False,
        )
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_cross_border_to_us_no_pipc_approval_denied(self):
        r = self._eval(
            cross_border_transfer=True,
            transfer_country="US",
            pipc_approval_obtained=False,
            individual_consent_for_transfer=False,
        )
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_cross_border_denied_cites_pipa_art_28_8(self):
        r = self._eval(
            cross_border_transfer=True,
            transfer_country="JP",
            pipc_approval_obtained=False,
            individual_consent_for_transfer=False,
        )
        assert "28" in r.regulation or "Cross-border" in r.regulation

    def test_cross_border_to_eu_permitted(self):
        r = self._eval(cross_border_transfer=True, transfer_country="DE")
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    def test_cross_border_to_uk_permitted(self):
        r = self._eval(cross_border_transfer=True, transfer_country="UK")
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    def test_cross_border_to_ca_permitted(self):
        r = self._eval(cross_border_transfer=True, transfer_country="CA")
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    def test_cross_border_with_pipc_approval_permitted(self):
        r = self._eval(
            cross_border_transfer=True,
            transfer_country="JP",
            pipc_approval_obtained=True,
        )
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    def test_cross_border_with_individual_consent_permitted(self):
        r = self._eval(
            cross_border_transfer=True,
            transfer_country="AU",
            pipc_approval_obtained=False,
            individual_consent_for_transfer=True,
        )
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    # --- Art. 37-2 Automated Decisions: REQUIRES_HUMAN_REVIEW ---

    def test_automated_decision_no_right_to_explanation_rhr(self):
        r = self._eval(
            automated_decision_significant_legal_effect=True,
            right_to_explanation_provided=False,
        )
        assert r.decision == "REQUIRES_HUMAN_REVIEW"
        assert not r.is_denied

    def test_automated_decision_rhr_cites_pipa_art_37_2(self):
        r = self._eval(
            automated_decision_significant_legal_effect=True,
            right_to_explanation_provided=False,
        )
        assert "37" in r.regulation or "Automated" in r.regulation

    def test_automated_decision_with_explanation_permitted(self):
        r = self._eval(
            automated_decision_significant_legal_effect=True,
            right_to_explanation_provided=True,
        )
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    # --- Edge cases ---

    def test_empty_dict_permitted(self):
        r = mod.KoreaPIPAFilter().filter({})
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    def test_filter_name_set(self):
        r = mod.KoreaPIPAFilter().filter({})
        assert r.filter_name


# ===========================================================================
# TestKoreaFSCAIFilter — FSCMA Art. 7+63; CB Act Art. 26; IBA Art. 176
# ===========================================================================


class TestKoreaFSCAIFilter:
    """FSC AI financial governance — four principal controls."""

    def _eval(self, **kwargs):
        return mod.KoreaFSCAIFilter().filter(kwargs)

    # --- FSCMA Art. 7 + Robo-Advisor Guidelines: DENIED ---

    def test_ai_investment_advisory_no_registration_denied(self):
        r = self._eval(
            ai_investment_advisory=True,
            robo_advisor_registration_confirmed=False,
        )
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_robo_advisor_denied_cites_fscma_art_7(self):
        r = self._eval(
            ai_investment_advisory=True,
            robo_advisor_registration_confirmed=False,
        )
        assert "FSCMA" in r.regulation or "7" in r.regulation or "Robo" in r.regulation

    def test_ai_investment_advisory_with_registration_permitted(self):
        r = self._eval(
            ai_investment_advisory=True,
            robo_advisor_registration_confirmed=True,
        )
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    # --- CB Act Art. 26 + AI Guidelines: DENIED ---

    def test_ai_credit_scoring_no_validation_denied(self):
        r = self._eval(
            ai_credit_scoring=True,
            fsc_model_validation_completed=False,
            audit_trail_maintained=True,
        )
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_ai_credit_scoring_no_audit_trail_denied(self):
        r = self._eval(
            ai_credit_scoring=True,
            fsc_model_validation_completed=True,
            audit_trail_maintained=False,
        )
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_credit_scoring_denied_cites_cb_act_26(self):
        r = self._eval(
            ai_credit_scoring=True,
            fsc_model_validation_completed=False,
            audit_trail_maintained=True,
        )
        assert "CB Act" in r.regulation or "26" in r.regulation or "Credit" in r.regulation

    def test_ai_credit_scoring_compliant_permitted(self):
        r = self._eval(
            ai_credit_scoring=True,
            fsc_model_validation_completed=True,
            audit_trail_maintained=True,
        )
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    # --- IBA Art. 176 + FSC Supervisory Regulation: DENIED ---

    def test_insurance_ai_no_actuarial_cert_denied(self):
        r = self._eval(
            insurance_ai_underwriting=True,
            actuarial_certification_obtained=False,
        )
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_insurance_denied_cites_iba_art_176(self):
        r = self._eval(
            insurance_ai_underwriting=True,
            actuarial_certification_obtained=False,
        )
        assert "IBA" in r.regulation or "176" in r.regulation or "actuarial" in r.reason.lower()

    def test_insurance_ai_with_actuarial_cert_permitted(self):
        r = self._eval(
            insurance_ai_underwriting=True,
            actuarial_certification_obtained=True,
        )
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    # --- FSCMA Art. 63 + KSDA: REQUIRES_HUMAN_REVIEW ---

    def test_ai_trading_no_fsc_registration_rhr(self):
        r = self._eval(
            ai_trading_algorithm=True,
            fsc_algorithmic_trading_registration_confirmed=False,
        )
        assert r.decision == "REQUIRES_HUMAN_REVIEW"
        assert not r.is_denied

    def test_trading_rhr_cites_fscma_art_63(self):
        r = self._eval(
            ai_trading_algorithm=True,
            fsc_algorithmic_trading_registration_confirmed=False,
        )
        assert "63" in r.regulation or "KSDA" in r.regulation or "trading" in r.reason.lower()

    def test_ai_trading_with_registration_permitted(self):
        r = self._eval(
            ai_trading_algorithm=True,
            fsc_algorithmic_trading_registration_confirmed=True,
        )
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    # --- Edge cases ---

    def test_empty_dict_permitted(self):
        r = mod.KoreaFSCAIFilter().filter({})
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    def test_filter_name_set(self):
        r = mod.KoreaFSCAIFilter().filter({})
        assert r.filter_name


# ===========================================================================
# TestKoreaAIBasicActFilter — AI Basic Act Arts. 35, 36, 46, 47
# ===========================================================================


class TestKoreaAIBasicActFilter:
    """Korea AI Basic Act 2024 — four principal controls."""

    def _eval(self, **kwargs):
        return mod.KoreaAIBasicActFilter().filter(kwargs)

    # --- Art. 47 Impact Assessment: DENIED ---

    def test_medical_ai_no_impact_assessment_denied(self):
        r = self._eval(ai_sector="medical", impact_assessment_completed=False)
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_legal_ai_no_impact_assessment_denied(self):
        r = self._eval(ai_sector="legal", impact_assessment_completed=False)
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_education_ai_no_impact_assessment_denied(self):
        r = self._eval(ai_sector="education", impact_assessment_completed=False)
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_employment_ai_no_impact_assessment_denied(self):
        r = self._eval(ai_sector="employment", impact_assessment_completed=False)
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_impact_assessment_denied_cites_art_47(self):
        r = self._eval(ai_sector="medical", impact_assessment_completed=False)
        assert "47" in r.regulation or "Impact" in r.regulation

    def test_medical_ai_with_impact_assessment_permitted(self):
        r = self._eval(ai_sector="medical", impact_assessment_completed=True)
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    def test_non_high_impact_sector_permitted(self):
        r = self._eval(ai_sector="marketing", impact_assessment_completed=False)
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    # --- Art. 35 Transparency Obligations: DENIED ---

    def test_ai_deployed_no_transparency_denied(self):
        r = self._eval(
            ai_system_deployed_to_users=True,
            transparency_disclosure_provided=False,
        )
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_transparency_denied_cites_art_35(self):
        r = self._eval(
            ai_system_deployed_to_users=True,
            transparency_disclosure_provided=False,
        )
        assert "35" in r.regulation or "Transparency" in r.regulation

    def test_ai_deployed_with_transparency_permitted(self):
        r = self._eval(
            ai_system_deployed_to_users=True,
            transparency_disclosure_provided=True,
        )
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    # --- Art. 36 GenAI Disclosure: DENIED ---

    def test_genai_content_no_watermark_denied(self):
        r = self._eval(
            generative_ai_content=True,
            ai_generated_watermark_or_disclosure=False,
        )
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_genai_denied_cites_art_36(self):
        r = self._eval(
            generative_ai_content=True,
            ai_generated_watermark_or_disclosure=False,
        )
        assert "36" in r.regulation or "GenAI" in r.regulation

    def test_genai_content_with_watermark_permitted(self):
        r = self._eval(
            generative_ai_content=True,
            ai_generated_watermark_or_disclosure=True,
        )
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    # --- Art. 46 Human Oversight: REQUIRES_HUMAN_REVIEW ---

    def test_critical_infra_ai_no_oversight_rhr(self):
        r = self._eval(
            critical_infrastructure_ai=True,
            human_oversight_mechanism_present=False,
        )
        assert r.decision == "REQUIRES_HUMAN_REVIEW"
        assert not r.is_denied

    def test_oversight_rhr_cites_art_46(self):
        r = self._eval(
            critical_infrastructure_ai=True,
            human_oversight_mechanism_present=False,
        )
        assert "46" in r.regulation or "oversight" in r.reason.lower()

    def test_critical_infra_ai_with_oversight_permitted(self):
        r = self._eval(
            critical_infrastructure_ai=True,
            human_oversight_mechanism_present=True,
        )
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    # --- Edge cases ---

    def test_empty_dict_permitted(self):
        r = mod.KoreaAIBasicActFilter().filter({})
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    def test_filter_name_set(self):
        r = mod.KoreaAIBasicActFilter().filter({})
        assert r.filter_name


# ===========================================================================
# TestKoreaCrossBorderFilter — PIPA Art. 28-8 + FSC EFTA + FSC Cloud
# ===========================================================================


class TestKoreaCrossBorderFilter:
    """Cross-border AI data flows — four principal controls."""

    def _eval(self, **kwargs):
        return mod.KoreaCrossBorderFilter().filter(kwargs)

    # --- PIPA Art. 28-8 restricted countries: DENIED ---

    def test_personal_data_to_cn_denied(self):
        r = self._eval(
            personal_data_transfer_country="CN",
            pipc_adequacy_confirmed=False,
            explicit_individual_consent=False,
        )
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_personal_data_to_ru_denied(self):
        r = self._eval(
            personal_data_transfer_country="RU",
            pipc_adequacy_confirmed=False,
            explicit_individual_consent=False,
        )
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_personal_data_to_kp_denied(self):
        r = self._eval(
            personal_data_transfer_country="KP",
            pipc_adequacy_confirmed=False,
            explicit_individual_consent=False,
        )
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_restricted_country_denied_cites_pipa_28_8(self):
        r = self._eval(
            personal_data_transfer_country="CN",
            pipc_adequacy_confirmed=False,
            explicit_individual_consent=False,
        )
        assert "28" in r.regulation or "PIPC" in r.regulation

    def test_personal_data_to_cn_with_pipc_adequacy_permitted(self):
        r = self._eval(
            personal_data_transfer_country="CN",
            pipc_adequacy_confirmed=True,
        )
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    def test_personal_data_to_cn_with_explicit_consent_permitted(self):
        r = self._eval(
            personal_data_transfer_country="CN",
            pipc_adequacy_confirmed=False,
            explicit_individual_consent=True,
        )
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    # --- FSC EFTA Art. 21-2: DENIED ---

    def test_financial_ai_data_no_fsc_approval_no_safeguards_denied(self):
        r = self._eval(
            financial_ai_data_transfer=True,
            fsc_approved_entity=False,
            contractual_safeguards_in_place=False,
        )
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_financial_ai_denied_cites_efta_21_2(self):
        r = self._eval(
            financial_ai_data_transfer=True,
            fsc_approved_entity=False,
            contractual_safeguards_in_place=False,
        )
        assert "21" in r.regulation or "EFTA" in r.regulation or "Financial" in r.regulation

    def test_financial_ai_with_fsc_approved_entity_permitted(self):
        r = self._eval(
            financial_ai_data_transfer=True,
            fsc_approved_entity=True,
        )
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    def test_financial_ai_with_contractual_safeguards_permitted(self):
        r = self._eval(
            financial_ai_data_transfer=True,
            fsc_approved_entity=False,
            contractual_safeguards_in_place=True,
        )
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    # --- FSC Cloud Security Guidelines: DENIED ---

    def test_fsc_entity_on_aws_us_east_denied(self):
        r = self._eval(
            serves_fsc_regulated_entity=True,
            cloud_region="aws_us_east_1",
        )
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_fsc_entity_on_gcp_us_central_denied(self):
        r = self._eval(
            serves_fsc_regulated_entity=True,
            cloud_region="gcp_us_central1",
        )
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_cloud_denied_cites_fsc_cloud_guidelines(self):
        r = self._eval(
            serves_fsc_regulated_entity=True,
            cloud_region="aws_us_east_1",
        )
        assert "Cloud" in r.regulation or "FSC" in r.regulation or "Seoul" in r.regulation

    def test_fsc_entity_on_aws_seoul_permitted(self):
        r = self._eval(
            serves_fsc_regulated_entity=True,
            cloud_region="aws_ap_northeast_2",
        )
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    def test_fsc_entity_on_gcp_seoul_permitted(self):
        r = self._eval(
            serves_fsc_regulated_entity=True,
            cloud_region="gcp_asia_northeast3",
        )
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    def test_fsc_entity_on_azure_korea_central_permitted(self):
        r = self._eval(
            serves_fsc_regulated_entity=True,
            cloud_region="azure_korea_central",
        )
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    def test_non_fsc_entity_non_approved_cloud_permitted(self):
        r = self._eval(
            serves_fsc_regulated_entity=False,
            cloud_region="aws_us_east_1",
        )
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    # --- PIPA Art. 28-8 + PIPC Sensitive Data Guidelines: REQUIRES_HUMAN_REVIEW ---

    def test_cross_border_ai_training_biometric_no_pipc_notification_rhr(self):
        r = self._eval(
            cross_border_ai_training=True,
            cross_border_ai_training_data_type="biometric",
            pipc_notification_provided=False,
        )
        assert r.decision == "REQUIRES_HUMAN_REVIEW"
        assert not r.is_denied

    def test_cross_border_ai_training_health_no_pipc_notification_rhr(self):
        r = self._eval(
            cross_border_ai_training=True,
            cross_border_ai_training_data_type="health",
            pipc_notification_provided=False,
        )
        assert r.decision == "REQUIRES_HUMAN_REVIEW"
        assert not r.is_denied

    def test_sensitive_ai_training_rhr_cites_pipa_28_8(self):
        r = self._eval(
            cross_border_ai_training=True,
            cross_border_ai_training_data_type="biometric",
            pipc_notification_provided=False,
        )
        assert "28" in r.regulation or "PIPC" in r.regulation

    def test_cross_border_ai_training_biometric_with_pipc_notification_permitted(self):
        r = self._eval(
            cross_border_ai_training=True,
            cross_border_ai_training_data_type="biometric",
            pipc_notification_provided=True,
        )
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    def test_cross_border_ai_training_non_sensitive_type_permitted(self):
        r = self._eval(
            cross_border_ai_training=True,
            cross_border_ai_training_data_type="product_usage",
            pipc_notification_provided=False,
        )
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    # --- Edge cases ---

    def test_empty_dict_permitted(self):
        r = mod.KoreaCrossBorderFilter().filter({})
        assert r.decision == "PERMITTED"
        assert not r.is_denied

    def test_filter_name_set(self):
        r = mod.KoreaCrossBorderFilter().filter({})
        assert r.filter_name


# ===========================================================================
# Ecosystem wrapper tests
# ===========================================================================


class TestKoreaLangChainPolicyGuard:
    """LangChain wrapper — invoke raises PermissionError on DENIED."""

    def test_invoke_denied_raises_permission_error(self):
        guard = mod.KoreaLangChainPolicyGuard(filter_instance=mod.KoreaPIPAFilter())
        denied_doc = {
            "personal_information_processing": True,
            "consent_obtained": False,
            "legitimate_purpose": False,
        }
        with pytest.raises(PermissionError):
            guard.invoke(denied_doc)

    def test_invoke_permitted_returns_list(self):
        guard = mod.KoreaLangChainPolicyGuard(filter_instance=mod.KoreaPIPAFilter())
        r = guard.invoke({})
        assert isinstance(r, list)
        assert len(r) == 1
        assert r[0].decision == "PERMITTED"

    def test_ainvoke_permitted_returns_list(self):
        guard = mod.KoreaLangChainPolicyGuard(filter_instance=mod.KoreaPIPAFilter())
        r = guard.ainvoke({})
        assert isinstance(r, list)

    def test_process_denied_raises_permission_error(self):
        guard = mod.KoreaLangChainPolicyGuard(filter_instance=mod.KoreaPIPAFilter())
        with pytest.raises(PermissionError):
            guard.process(
                {
                    "personal_information_processing": True,
                    "consent_obtained": False,
                    "legitimate_purpose": False,
                }
            )

    def test_process_permitted_returns_doc(self):
        guard = mod.KoreaLangChainPolicyGuard(filter_instance=mod.KoreaPIPAFilter())
        doc = {}
        result = guard.process(doc)
        assert result is doc

    def test_multi_filter_invoke_denied_raises(self):
        guard = mod.KoreaLangChainPolicyGuard()
        with pytest.raises(PermissionError):
            guard.invoke(
                {
                    "personal_information_processing": True,
                    "consent_obtained": False,
                    "legitimate_purpose": False,
                }
            )

    def test_multi_filter_invoke_permitted_returns_list(self):
        guard = mod.KoreaLangChainPolicyGuard()
        r = guard.invoke({})
        assert isinstance(r, list)
        assert len(r) == 4


class TestKoreaCrewAIGovernanceGuard:
    """CrewAI wrapper — _run raises PermissionError on DENIED."""

    def test_run_denied_raises_permission_error(self):
        guard = mod.KoreaCrewAIGovernanceGuard(filter_instance=mod.KoreaPIPAFilter())
        with pytest.raises(PermissionError):
            guard._run(
                {
                    "personal_information_processing": True,
                    "consent_obtained": False,
                    "legitimate_purpose": False,
                }
            )

    def test_run_permitted_returns_doc(self):
        guard = mod.KoreaCrewAIGovernanceGuard(filter_instance=mod.KoreaPIPAFilter())
        doc = {}
        result = guard._run(doc)
        assert result is doc

    def test_has_name_and_description(self):
        guard = mod.KoreaCrewAIGovernanceGuard(filter_instance=mod.KoreaPIPAFilter())
        assert guard.name
        assert guard.description


class TestKoreaAutoGenGovernedAgent:
    """AutoGen wrapper — generate_reply raises PermissionError on DENIED."""

    def test_generate_reply_denied_raises(self):
        agent = mod.KoreaAutoGenGovernedAgent(filter_instance=mod.KoreaPIPAFilter())
        with pytest.raises(PermissionError):
            agent.generate_reply(
                {
                    "personal_information_processing": True,
                    "consent_obtained": False,
                    "legitimate_purpose": False,
                }
            )

    def test_generate_reply_permitted_returns_doc(self):
        agent = mod.KoreaAutoGenGovernedAgent(filter_instance=mod.KoreaPIPAFilter())
        result = agent.generate_reply({})
        assert isinstance(result, dict)

    def test_generate_reply_none_messages_permitted(self):
        agent = mod.KoreaAutoGenGovernedAgent(filter_instance=mod.KoreaPIPAFilter())
        result = agent.generate_reply(None)
        assert isinstance(result, dict)


class TestKoreaSemanticKernelPlugin:
    """Semantic Kernel wrapper — enforce_governance raises PermissionError on DENIED."""

    def test_enforce_governance_denied_raises(self):
        plugin = mod.KoreaSemanticKernelPlugin(filter_instance=mod.KoreaPIPAFilter())
        with pytest.raises(PermissionError):
            plugin.enforce_governance(
                {
                    "personal_information_processing": True,
                    "consent_obtained": False,
                    "legitimate_purpose": False,
                }
            )

    def test_enforce_governance_permitted_returns_doc(self):
        plugin = mod.KoreaSemanticKernelPlugin(filter_instance=mod.KoreaPIPAFilter())
        doc = {}
        result = plugin.enforce_governance(doc)
        assert result is doc


class TestKoreaLlamaIndexWorkflowGuard:
    """LlamaIndex wrapper — process_event raises PermissionError on DENIED."""

    def test_process_event_denied_raises(self):
        guard = mod.KoreaLlamaIndexWorkflowGuard(filter_instance=mod.KoreaPIPAFilter())
        with pytest.raises(PermissionError):
            guard.process_event(
                {
                    "personal_information_processing": True,
                    "consent_obtained": False,
                    "legitimate_purpose": False,
                }
            )

    def test_process_event_permitted_returns_doc(self):
        guard = mod.KoreaLlamaIndexWorkflowGuard(filter_instance=mod.KoreaPIPAFilter())
        doc = {}
        result = guard.process_event(doc)
        assert result is doc


class TestKoreaHaystackGovernanceComponent:
    """Haystack wrapper — run filters denied documents, does not raise."""

    def test_run_filters_denied_documents(self):
        component = mod.KoreaHaystackGovernanceComponent(filter_instance=mod.KoreaPIPAFilter())
        denied_doc = {
            "personal_information_processing": True,
            "consent_obtained": False,
            "legitimate_purpose": False,
        }
        permitted_doc = {}
        result = component.run([denied_doc, permitted_doc])
        assert "documents" in result
        assert len(result["documents"]) == 1
        assert result["documents"][0] is permitted_doc

    def test_run_all_permitted_returns_all(self):
        component = mod.KoreaHaystackGovernanceComponent(filter_instance=mod.KoreaPIPAFilter())
        docs = [{}, {"consent_obtained": True}]
        result = component.run(docs)
        assert len(result["documents"]) == 2

    def test_run_empty_list_returns_empty(self):
        component = mod.KoreaHaystackGovernanceComponent(filter_instance=mod.KoreaPIPAFilter())
        result = component.run([])
        assert result["documents"] == []


class TestKoreaDSPyGovernanceModule:
    """DSPy wrapper — forward raises PermissionError on DENIED, delegates on PERMITTED."""

    def test_forward_denied_raises(self):
        sentinel = object()

        def dummy_module(doc, **kwargs):
            return sentinel

        module = mod.KoreaDSPyGovernanceModule(
            filter_instance=mod.KoreaPIPAFilter(),
            module=dummy_module,
        )
        with pytest.raises(PermissionError):
            module.forward(
                {
                    "personal_information_processing": True,
                    "consent_obtained": False,
                    "legitimate_purpose": False,
                }
            )

    def test_forward_permitted_delegates_to_module(self):
        sentinel = object()

        def dummy_module(doc, **kwargs):
            return sentinel

        module = mod.KoreaDSPyGovernanceModule(
            filter_instance=mod.KoreaPIPAFilter(),
            module=dummy_module,
        )
        result = module.forward({})
        assert result is sentinel


class TestKoreaMAFPolicyMiddleware:
    """MAF middleware — process raises PermissionError on DENIED, calls next_handler on PERMITTED."""

    def test_process_denied_raises(self):
        middleware = mod.KoreaMAFPolicyMiddleware(filter_instance=mod.KoreaPIPAFilter())
        with pytest.raises(PermissionError):
            middleware.process(
                {
                    "personal_information_processing": True,
                    "consent_obtained": False,
                    "legitimate_purpose": False,
                },
                lambda msg: msg,
            )

    def test_process_permitted_calls_next_handler(self):
        sentinel = object()

        def next_handler(msg):
            return sentinel

        middleware = mod.KoreaMAFPolicyMiddleware(filter_instance=mod.KoreaPIPAFilter())
        result = middleware.process({}, next_handler)
        assert result is sentinel
