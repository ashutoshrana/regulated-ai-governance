"""
Tests for 31_eu_ai_act_high_risk.py — EU AI Act High-Risk Systems Governance
Framework covering Annex III high-risk AI categories, conformity assessment,
technical requirements (Arts. 9–15), transparency obligations (Arts. 13/50),
and cross-border/GPAI rules (Arts. 2/51-55).
"""

from __future__ import annotations

import importlib.util
import os
import sys
import types

import pytest

# ---------------------------------------------------------------------------
# Module loader
# ---------------------------------------------------------------------------


def _load():
    _name = "eu_ai_act_high_risk_31"
    spec = importlib.util.spec_from_file_location(
        _name,
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "examples",
            "31_eu_ai_act_high_risk.py",
        ),
    )
    mod = types.ModuleType(_name)
    sys.modules[_name] = mod
    spec.loader.exec_module(mod)
    return mod


mod = _load()


# ---------------------------------------------------------------------------
# Helper factories
# ---------------------------------------------------------------------------


def _compliant_doc(**overrides):
    """Return a fully-compliant document dict that passes all four filters."""
    defaults = dict(
        # Category / Annex III
        ai_system_category="education_vocational",
        conformity_assessment_completed=True,
        eu_database_registered=True,
        fundamental_rights_impact_assessment=True,
        prohibited_ai_practice=False,
        # Technical requirements
        high_risk_ai=True,
        risk_management_system=True,
        data_governance_documented=True,
        technical_documentation_prepared=True,
        human_oversight_measures=True,
        accuracy_robustness_tested=True,
        # Transparency
        ai_interacts_with_humans=True,
        ai_disclosure_made=True,
        synthetic_content_generated=False,
        ai_generated_labeling=True,
        emotion_recognition_system=False,
        emotion_recognition_disclosure=True,
        instructions_for_use_provided=True,
        # Cross-border / GPAI
        destination_country="Germany",
        gpai_model=False,
        gpai_technical_documentation=True,
        gpai_systemic_risk=False,
        adversarial_testing_completed=True,
        copyright_compliance_policy=True,
    )
    defaults.update(overrides)
    return defaults


# ===========================================================================
# TestEUAIActHighRiskCategoryFilter
# ===========================================================================


class TestEUAIActHighRiskCategoryFilter:
    """Layer 1: EU AI Act 2024/1689 Annex III — High-risk AI system categories."""

    def _eval(self, **kwargs):
        return mod.EUAIActHighRiskCategoryFilter().filter(kwargs)

    # --- Art. 5 prohibited practices (checked first) ---

    def test_prohibited_ai_practice_denied(self):
        """prohibited_ai_practice=True → DENIED unconditionally."""
        result = self._eval(prohibited_ai_practice=True)
        assert result.decision == "DENIED"
        assert result.is_denied

    def test_prohibited_ai_practice_cites_art5(self):
        """DENIED for prohibited practice cites Art. 5."""
        result = self._eval(prohibited_ai_practice=True)
        combined = result.regulation_citation + " " + result.reason
        assert "5" in combined

    def test_prohibited_practice_takes_precedence_over_compliant_category(self):
        """prohibited_ai_practice=True overrides conformity_assessment_completed=True."""
        result = self._eval(
            prohibited_ai_practice=True,
            ai_system_category="education_vocational",
            conformity_assessment_completed=True,
            eu_database_registered=True,
        )
        assert result.decision == "DENIED"

    # --- Annex III §1–§4: biometric_identification, critical_infrastructure, education_vocational ---

    def test_biometric_identification_no_assessment_denied(self):
        """ai_system_category=biometric_identification + no conformity_assessment → DENIED."""
        result = self._eval(
            ai_system_category="biometric_identification",
            conformity_assessment_completed=False,
        )
        assert result.decision == "DENIED"
        assert result.is_denied

    def test_critical_infrastructure_no_assessment_denied(self):
        """ai_system_category=critical_infrastructure + no conformity_assessment → DENIED."""
        result = self._eval(
            ai_system_category="critical_infrastructure",
            conformity_assessment_completed=False,
        )
        assert result.decision == "DENIED"

    def test_education_vocational_no_assessment_denied(self):
        """ai_system_category=education_vocational + no conformity_assessment → DENIED."""
        result = self._eval(
            ai_system_category="education_vocational",
            conformity_assessment_completed=False,
        )
        assert result.decision == "DENIED"

    def test_annex_iii_1_4_denial_cites_art43(self):
        """DENIED for §1–§4 categories without assessment cites Art. 43."""
        result = self._eval(
            ai_system_category="biometric_identification",
            conformity_assessment_completed=False,
        )
        combined = result.regulation_citation + " " + result.reason
        assert "43" in combined

    # --- Annex III §5–§6: employment_workers_management, essential_services, law_enforcement ---

    def test_employment_workers_management_no_assessment_denied(self):
        """ai_system_category=employment_workers_management + no assessment → DENIED."""
        result = self._eval(
            ai_system_category="employment_workers_management",
            conformity_assessment_completed=False,
        )
        assert result.decision == "DENIED"
        assert result.is_denied

    def test_essential_services_no_assessment_denied(self):
        """ai_system_category=essential_services + no assessment → DENIED."""
        result = self._eval(
            ai_system_category="essential_services",
            conformity_assessment_completed=False,
        )
        assert result.decision == "DENIED"

    def test_law_enforcement_no_assessment_denied(self):
        """ai_system_category=law_enforcement + no assessment → DENIED."""
        result = self._eval(
            ai_system_category="law_enforcement",
            conformity_assessment_completed=False,
        )
        assert result.decision == "DENIED"

    def test_annex_iii_5_6_denial_cites_art43_1(self):
        """DENIED for §5–§6 categories without assessment cites Art. 43(1)."""
        result = self._eval(
            ai_system_category="law_enforcement",
            conformity_assessment_completed=False,
        )
        combined = result.regulation_citation + " " + result.reason
        assert "43" in combined

    # --- Annex III §7–§8: migration_asylum, administration_justice (FRIA required) ---

    def test_migration_asylum_no_fria_denied(self):
        """ai_system_category=migration_asylum + no fundamental_rights_impact_assessment → DENIED."""
        result = self._eval(
            ai_system_category="migration_asylum",
            fundamental_rights_impact_assessment=False,
        )
        assert result.decision == "DENIED"
        assert result.is_denied

    def test_administration_justice_no_fria_denied(self):
        """ai_system_category=administration_justice + no FRIA → DENIED."""
        result = self._eval(
            ai_system_category="administration_justice",
            fundamental_rights_impact_assessment=False,
        )
        assert result.decision == "DENIED"

    def test_migration_asylum_fria_denial_cites_art27(self):
        """DENIED for §7–§8 without FRIA cites Art. 27."""
        result = self._eval(
            ai_system_category="migration_asylum",
            fundamental_rights_impact_assessment=False,
        )
        combined = result.regulation_citation + " " + result.reason
        assert "27" in combined

    # --- Art. 49/71 — registered in EU database: REQUIRES_HUMAN_REVIEW ---

    def test_high_risk_with_assessment_but_no_db_registration_requires_review(self):
        """High-risk category + conformity_assessment_completed + no eu_database_registered → REQUIRES_HUMAN_REVIEW."""
        result = self._eval(
            ai_system_category="education_vocational",
            conformity_assessment_completed=True,
            eu_database_registered=False,
        )
        assert result.decision == "REQUIRES_HUMAN_REVIEW"
        assert not result.is_denied

    def test_db_registration_requires_review_cites_art49_71(self):
        """REQUIRES_HUMAN_REVIEW for missing db registration cites Art. 49/71."""
        result = self._eval(
            ai_system_category="law_enforcement",
            conformity_assessment_completed=True,
            eu_database_registered=False,
        )
        combined = result.regulation_citation + " " + result.reason
        assert "49" in combined or "71" in combined

    # --- Fully compliant / pass-through ---

    def test_high_risk_fully_compliant_approved(self):
        """Annex III category + assessment + db_registered → APPROVED."""
        result = self._eval(
            ai_system_category="biometric_identification",
            conformity_assessment_completed=True,
            eu_database_registered=True,
            fundamental_rights_impact_assessment=True,
            prohibited_ai_practice=False,
        )
        assert result.decision == "APPROVED"
        assert not result.is_denied

    def test_non_annex_iii_category_approved(self):
        """ai_system_category not in Annex III → APPROVED."""
        result = self._eval(
            ai_system_category="low_risk_chatbot",
            conformity_assessment_completed=False,
        )
        assert result.decision == "APPROVED"

    def test_missing_keys_approved(self):
        """Empty dict (all keys absent) → APPROVED."""
        result = mod.EUAIActHighRiskCategoryFilter().filter({})
        assert result.decision == "APPROVED"

    def test_compliant_not_requires_logging(self):
        """Compliant APPROVED result sets requires_logging=False."""
        result = mod.EUAIActHighRiskCategoryFilter().filter(_compliant_doc())
        assert result.requires_logging is False

    def test_denied_requires_logging(self):
        """DENIED result sets requires_logging=True."""
        result = self._eval(prohibited_ai_practice=True)
        assert result.requires_logging is True


# ===========================================================================
# TestEUAIActTechnicalRequirementsFilter
# ===========================================================================


class TestEUAIActTechnicalRequirementsFilter:
    """Layer 2: EU AI Act Arts. 9–15 — Technical requirements for high-risk AI."""

    def _eval(self, **kwargs):
        return mod.EUAIActTechnicalRequirementsFilter().filter(kwargs)

    # --- Art. 9 — risk management system ---

    def test_high_risk_no_risk_management_denied(self):
        """high_risk_ai=True + no risk_management_system → DENIED."""
        result = self._eval(
            high_risk_ai=True,
            risk_management_system=False,
            data_governance_documented=True,
            technical_documentation_prepared=True,
            human_oversight_measures=True,
            accuracy_robustness_tested=True,
        )
        assert result.decision == "DENIED"
        assert result.is_denied

    def test_risk_management_denial_cites_art9(self):
        """DENIED for missing risk management cites Art. 9."""
        result = self._eval(high_risk_ai=True, risk_management_system=False)
        combined = result.regulation_citation + " " + result.reason
        assert "9" in combined

    # --- Art. 10 — data governance ---

    def test_high_risk_no_data_governance_denied(self):
        """high_risk_ai=True + no data_governance_documented → DENIED."""
        result = self._eval(
            high_risk_ai=True,
            risk_management_system=True,
            data_governance_documented=False,
            technical_documentation_prepared=True,
            human_oversight_measures=True,
            accuracy_robustness_tested=True,
        )
        assert result.decision == "DENIED"
        assert result.is_denied

    def test_data_governance_denial_cites_art10(self):
        """DENIED for missing data governance cites Art. 10."""
        result = self._eval(
            high_risk_ai=True,
            risk_management_system=True,
            data_governance_documented=False,
        )
        combined = result.regulation_citation + " " + result.reason
        assert "10" in combined

    # --- Art. 11 + Annex IV — technical documentation ---

    def test_high_risk_no_technical_docs_denied(self):
        """high_risk_ai=True + no technical_documentation_prepared → DENIED."""
        result = self._eval(
            high_risk_ai=True,
            risk_management_system=True,
            data_governance_documented=True,
            technical_documentation_prepared=False,
            human_oversight_measures=True,
            accuracy_robustness_tested=True,
        )
        assert result.decision == "DENIED"
        assert result.is_denied

    def test_technical_docs_denial_cites_art11(self):
        """DENIED for missing technical documentation cites Art. 11."""
        result = self._eval(
            high_risk_ai=True,
            risk_management_system=True,
            data_governance_documented=True,
            technical_documentation_prepared=False,
        )
        combined = result.regulation_citation + " " + result.reason
        assert "11" in combined

    # --- Art. 14 — human oversight ---

    def test_high_risk_no_human_oversight_denied(self):
        """high_risk_ai=True + no human_oversight_measures → DENIED."""
        result = self._eval(
            high_risk_ai=True,
            risk_management_system=True,
            data_governance_documented=True,
            technical_documentation_prepared=True,
            human_oversight_measures=False,
            accuracy_robustness_tested=True,
        )
        assert result.decision == "DENIED"
        assert result.is_denied

    def test_human_oversight_denial_cites_art14(self):
        """DENIED for missing human oversight cites Art. 14."""
        result = self._eval(
            high_risk_ai=True,
            risk_management_system=True,
            data_governance_documented=True,
            technical_documentation_prepared=True,
            human_oversight_measures=False,
        )
        combined = result.regulation_citation + " " + result.reason
        assert "14" in combined

    # --- Art. 15 — accuracy/robustness testing (REQUIRES_HUMAN_REVIEW) ---

    def test_high_risk_no_accuracy_testing_requires_review(self):
        """high_risk_ai=True + all other fields OK + no accuracy_robustness_tested → REQUIRES_HUMAN_REVIEW."""
        result = self._eval(
            high_risk_ai=True,
            risk_management_system=True,
            data_governance_documented=True,
            technical_documentation_prepared=True,
            human_oversight_measures=True,
            accuracy_robustness_tested=False,
        )
        assert result.decision == "REQUIRES_HUMAN_REVIEW"
        assert not result.is_denied

    def test_accuracy_testing_review_cites_art15(self):
        """REQUIRES_HUMAN_REVIEW for missing accuracy testing cites Art. 15."""
        result = self._eval(
            high_risk_ai=True,
            risk_management_system=True,
            data_governance_documented=True,
            technical_documentation_prepared=True,
            human_oversight_measures=True,
            accuracy_robustness_tested=False,
        )
        combined = result.regulation_citation + " " + result.reason
        assert "15" in combined

    # --- Non-high-risk pass-through ---

    def test_non_high_risk_no_requirements_approved(self):
        """high_risk_ai=False + no other fields → APPROVED."""
        result = self._eval(high_risk_ai=False)
        assert result.decision == "APPROVED"

    def test_non_high_risk_ignores_missing_docs(self):
        """high_risk_ai=False + all docs absent → APPROVED (Arts. 9-15 not triggered)."""
        result = self._eval(
            high_risk_ai=False,
            risk_management_system=False,
            data_governance_documented=False,
            technical_documentation_prepared=False,
            human_oversight_measures=False,
            accuracy_robustness_tested=False,
        )
        assert result.decision == "APPROVED"

    def test_compliant_high_risk_approved(self):
        """high_risk_ai=True + all requirements met → APPROVED."""
        result = mod.EUAIActTechnicalRequirementsFilter().filter(_compliant_doc())
        assert result.decision == "APPROVED"
        assert not result.is_denied

    def test_compliant_not_requires_logging(self):
        """Compliant APPROVED result sets requires_logging=False."""
        result = mod.EUAIActTechnicalRequirementsFilter().filter(_compliant_doc())
        assert result.requires_logging is False

    def test_missing_keys_non_high_risk_approved(self):
        """Empty dict → APPROVED (high_risk_ai absent = falsy)."""
        result = mod.EUAIActTechnicalRequirementsFilter().filter({})
        assert result.decision == "APPROVED"


# ===========================================================================
# TestEUAIActTransparencyFilter
# ===========================================================================


class TestEUAIActTransparencyFilter:
    """Layer 3: EU AI Act Arts. 13/50/52 — Transparency and information obligations."""

    def _eval(self, **kwargs):
        return mod.EUAIActTransparencyFilter().filter(kwargs)

    # --- Art. 50(1) — AI interaction disclosure ---

    def test_ai_interacts_humans_no_disclosure_denied(self):
        """ai_interacts_with_humans=True + no ai_disclosure_made → DENIED."""
        result = self._eval(
            ai_interacts_with_humans=True,
            ai_disclosure_made=False,
        )
        assert result.decision == "DENIED"
        assert result.is_denied

    def test_ai_interaction_denial_cites_art50_1(self):
        """DENIED for missing AI disclosure cites Art. 50(1)."""
        result = self._eval(
            ai_interacts_with_humans=True,
            ai_disclosure_made=False,
        )
        combined = result.regulation_citation + " " + result.reason
        assert "50" in combined

    def test_ai_interacts_humans_with_disclosure_approved(self):
        """ai_interacts_with_humans=True WITH ai_disclosure_made → APPROVED."""
        result = self._eval(
            ai_interacts_with_humans=True,
            ai_disclosure_made=True,
        )
        assert result.decision == "APPROVED"

    # --- Art. 50(4) — AI-generated content labeling (deepfakes) ---

    def test_synthetic_content_no_labeling_denied(self):
        """synthetic_content_generated=True + no ai_generated_labeling → DENIED."""
        result = self._eval(
            synthetic_content_generated=True,
            ai_generated_labeling=False,
        )
        assert result.decision == "DENIED"
        assert result.is_denied

    def test_synthetic_content_denial_cites_art50_4(self):
        """DENIED for unlabeled synthetic content cites Art. 50(4)."""
        result = self._eval(
            synthetic_content_generated=True,
            ai_generated_labeling=False,
        )
        combined = result.regulation_citation + " " + result.reason
        assert "50" in combined

    def test_synthetic_content_with_labeling_approved(self):
        """synthetic_content_generated=True WITH ai_generated_labeling → APPROVED."""
        result = self._eval(
            synthetic_content_generated=True,
            ai_generated_labeling=True,
        )
        assert result.decision == "APPROVED"

    # --- Art. 50(3) — emotion recognition disclosure ---

    def test_emotion_recognition_no_disclosure_denied(self):
        """emotion_recognition_system=True + no emotion_recognition_disclosure → DENIED."""
        result = self._eval(
            emotion_recognition_system=True,
            emotion_recognition_disclosure=False,
        )
        assert result.decision == "DENIED"
        assert result.is_denied

    def test_emotion_recognition_denial_cites_art50_3(self):
        """DENIED for missing emotion recognition disclosure cites Art. 50(3)."""
        result = self._eval(
            emotion_recognition_system=True,
            emotion_recognition_disclosure=False,
        )
        combined = result.regulation_citation + " " + result.reason
        assert "50" in combined

    def test_emotion_recognition_with_disclosure_approved(self):
        """emotion_recognition_system=True WITH disclosure → APPROVED."""
        result = self._eval(
            emotion_recognition_system=True,
            emotion_recognition_disclosure=True,
        )
        assert result.decision == "APPROVED"

    # --- Art. 13 — instructions for use (REQUIRES_HUMAN_REVIEW) ---

    def test_high_risk_no_instructions_requires_review(self):
        """high_risk_ai=True + no instructions_for_use_provided → REQUIRES_HUMAN_REVIEW."""
        result = self._eval(
            high_risk_ai=True,
            instructions_for_use_provided=False,
        )
        assert result.decision == "REQUIRES_HUMAN_REVIEW"
        assert not result.is_denied

    def test_instructions_review_cites_art13(self):
        """REQUIRES_HUMAN_REVIEW for missing instructions cites Art. 13."""
        result = self._eval(
            high_risk_ai=True,
            instructions_for_use_provided=False,
        )
        combined = result.regulation_citation + " " + result.reason
        assert "13" in combined

    def test_high_risk_with_instructions_approved(self):
        """high_risk_ai=True WITH instructions_for_use_provided → APPROVED."""
        result = self._eval(
            high_risk_ai=True,
            instructions_for_use_provided=True,
        )
        assert result.decision == "APPROVED"

    # --- Compliant pass-through ---

    def test_compliant_baseline_approved(self):
        """Fully compliant doc → APPROVED."""
        result = mod.EUAIActTransparencyFilter().filter(_compliant_doc())
        assert result.decision == "APPROVED"
        assert not result.is_denied

    def test_compliant_not_requires_logging(self):
        """Compliant APPROVED result sets requires_logging=False."""
        result = mod.EUAIActTransparencyFilter().filter(_compliant_doc())
        assert result.requires_logging is False

    def test_missing_keys_approved(self):
        """Empty dict → APPROVED."""
        result = mod.EUAIActTransparencyFilter().filter({})
        assert result.decision == "APPROVED"


# ===========================================================================
# TestEUAIActCrossBorderFilter
# ===========================================================================


class TestEUAIActCrossBorderFilter:
    """Layer 4: EU AI Act Art. 2 — Territorial scope + GPAI model rules Arts. 51–55."""

    def _eval(self, **kwargs):
        return mod.EUAIActCrossBorderFilter().filter(kwargs)

    # --- Art. 2(1)(c) + export control: China and Russia ---

    def test_china_high_risk_denied(self):
        """destination_country=China + high_risk_ai=True → DENIED."""
        result = self._eval(destination_country="China", high_risk_ai=True)
        assert result.decision == "DENIED"
        assert result.is_denied

    def test_russia_high_risk_denied(self):
        """destination_country=Russia + high_risk_ai=True → DENIED."""
        result = self._eval(destination_country="Russia", high_risk_ai=True)
        assert result.decision == "DENIED"
        assert result.is_denied

    def test_export_denial_cites_art2(self):
        """DENIED for prohibited export cites Art. 2(1)(c)."""
        result = self._eval(destination_country="China", high_risk_ai=True)
        combined = result.regulation_citation + " " + result.reason
        assert "2" in combined

    def test_china_non_high_risk_approved(self):
        """destination_country=China + high_risk_ai=False → APPROVED (export rule not triggered)."""
        result = self._eval(destination_country="China", high_risk_ai=False)
        assert result.decision == "APPROVED"

    def test_permitted_country_high_risk_approved(self):
        """destination_country=Germany + high_risk_ai=True → APPROVED."""
        result = self._eval(destination_country="Germany", high_risk_ai=True)
        assert result.decision == "APPROVED"

    # --- Art. 53 — GPAI technical documentation ---

    def test_gpai_no_technical_docs_denied(self):
        """gpai_model=True + no gpai_technical_documentation → DENIED."""
        result = self._eval(
            gpai_model=True,
            gpai_technical_documentation=False,
            copyright_compliance_policy=True,
        )
        assert result.decision == "DENIED"
        assert result.is_denied

    def test_gpai_docs_denial_cites_art53(self):
        """DENIED for GPAI without technical documentation cites Art. 53."""
        result = self._eval(
            gpai_model=True,
            gpai_technical_documentation=False,
        )
        combined = result.regulation_citation + " " + result.reason
        assert "53" in combined

    def test_gpai_with_technical_docs_and_copyright_approved(self):
        """gpai_model=True + gpai_technical_documentation + copyright_compliance_policy → APPROVED."""
        result = self._eval(
            gpai_model=True,
            gpai_technical_documentation=True,
            copyright_compliance_policy=True,
        )
        assert result.decision == "APPROVED"

    # --- Art. 55 — GPAI systemic risk adversarial testing ---

    def test_gpai_systemic_risk_no_adversarial_testing_denied(self):
        """gpai_systemic_risk=True + no adversarial_testing_completed → DENIED."""
        result = self._eval(
            gpai_model=True,
            gpai_technical_documentation=True,
            gpai_systemic_risk=True,
            adversarial_testing_completed=False,
            copyright_compliance_policy=True,
        )
        assert result.decision == "DENIED"
        assert result.is_denied

    def test_systemic_risk_denial_cites_art55(self):
        """DENIED for systemic risk without adversarial testing cites Art. 55."""
        result = self._eval(
            gpai_model=True,
            gpai_technical_documentation=True,
            gpai_systemic_risk=True,
            adversarial_testing_completed=False,
        )
        combined = result.regulation_citation + " " + result.reason
        assert "55" in combined

    # --- Art. 53(1)(c) — GPAI copyright compliance policy (REQUIRES_HUMAN_REVIEW) ---

    def test_gpai_no_copyright_policy_requires_review(self):
        """gpai_model=True + gpai_technical_documentation + no copyright_compliance_policy → REQUIRES_HUMAN_REVIEW."""
        result = self._eval(
            gpai_model=True,
            gpai_technical_documentation=True,
            gpai_systemic_risk=False,
            copyright_compliance_policy=False,
        )
        assert result.decision == "REQUIRES_HUMAN_REVIEW"
        assert not result.is_denied

    def test_copyright_review_cites_art53_1c(self):
        """REQUIRES_HUMAN_REVIEW for missing copyright policy cites Art. 53(1)(c)."""
        result = self._eval(
            gpai_model=True,
            gpai_technical_documentation=True,
            copyright_compliance_policy=False,
        )
        combined = result.regulation_citation + " " + result.reason
        assert "53" in combined

    # --- Compliant pass-through ---

    def test_compliant_baseline_approved(self):
        """Fully compliant doc → APPROVED."""
        result = mod.EUAIActCrossBorderFilter().filter(_compliant_doc())
        assert result.decision == "APPROVED"
        assert not result.is_denied

    def test_compliant_not_requires_logging(self):
        """Compliant APPROVED result sets requires_logging=False."""
        result = mod.EUAIActCrossBorderFilter().filter(_compliant_doc())
        assert result.requires_logging is False

    def test_missing_keys_approved(self):
        """Empty dict → APPROVED."""
        result = mod.EUAIActCrossBorderFilter().filter({})
        assert result.decision == "APPROVED"


# ===========================================================================
# TestFilterResult — edge cases
# ===========================================================================


class TestFilterResult:
    """FilterResult dataclass property and edge-case tests."""

    def test_is_denied_true_only_for_denied(self):
        """is_denied is True only when decision == 'DENIED'."""
        result_denied = mod.FilterResult(filter_name="test", decision="DENIED")
        result_review = mod.FilterResult(filter_name="test", decision="REQUIRES_HUMAN_REVIEW")
        result_approved = mod.FilterResult(filter_name="test", decision="APPROVED")
        assert result_denied.is_denied is True
        assert result_review.is_denied is False
        assert result_approved.is_denied is False

    def test_default_decision_approved(self):
        """Default decision is 'APPROVED'."""
        result = mod.FilterResult(filter_name="test")
        assert result.decision == "APPROVED"
        assert not result.is_denied

    def test_default_requires_logging_true(self):
        """Default requires_logging is True."""
        result = mod.FilterResult(filter_name="test")
        assert result.requires_logging is True

    def test_filter_result_is_not_frozen(self):
        """FilterResult (non-frozen) can be mutated after creation."""
        result = mod.FilterResult(filter_name="test", decision="APPROVED")
        result.decision = "DENIED"
        assert result.is_denied is True

    def test_high_risk_category_filter_is_frozen(self):
        """EUAIActHighRiskCategoryFilter is a frozen dataclass (immutable)."""
        f = mod.EUAIActHighRiskCategoryFilter()
        with pytest.raises((AttributeError, TypeError)):
            f.FILTER_NAME = "MODIFIED"  # type: ignore[misc]

    def test_technical_requirements_filter_is_frozen(self):
        """EUAIActTechnicalRequirementsFilter is a frozen dataclass."""
        f = mod.EUAIActTechnicalRequirementsFilter()
        with pytest.raises((AttributeError, TypeError)):
            f.FILTER_NAME = "MODIFIED"  # type: ignore[misc]

    def test_transparency_filter_is_frozen(self):
        """EUAIActTransparencyFilter is a frozen dataclass."""
        f = mod.EUAIActTransparencyFilter()
        with pytest.raises((AttributeError, TypeError)):
            f.FILTER_NAME = "MODIFIED"  # type: ignore[misc]

    def test_cross_border_filter_is_frozen(self):
        """EUAIActCrossBorderFilter is a frozen dataclass."""
        f = mod.EUAIActCrossBorderFilter()
        with pytest.raises((AttributeError, TypeError)):
            f.FILTER_NAME = "MODIFIED"  # type: ignore[misc]

    def test_requires_human_review_is_not_denied(self):
        """REQUIRES_HUMAN_REVIEW decision sets is_denied=False."""
        result = mod.FilterResult(filter_name="test", decision="REQUIRES_HUMAN_REVIEW")
        assert result.is_denied is False

    def test_empty_category_not_in_annex_iii(self):
        """ai_system_category=None → APPROVED (not in Annex III categories)."""
        result = mod.EUAIActHighRiskCategoryFilter().filter(
            {"ai_system_category": None, "conformity_assessment_completed": False}
        )
        assert result.decision == "APPROVED"


# ===========================================================================
# TestIntegrationWrappers — all 8 wrappers
# ===========================================================================


class TestIntegrationWrappers:
    """Integration wrappers instantiate and enforce governance correctly."""

    # --- EUAIActLangChainPolicyGuard ---

    def test_langchain_guard_raises_on_denied(self):
        """EUAIActLangChainPolicyGuard.invoke raises PermissionError on DENIED."""
        guard = mod.EUAIActLangChainPolicyGuard()
        with pytest.raises(PermissionError):
            guard.invoke({"prohibited_ai_practice": True})

    def test_langchain_guard_ainvoke_passes_compliant(self):
        """EUAIActLangChainPolicyGuard.ainvoke returns 4 results for clean doc."""
        guard = mod.EUAIActLangChainPolicyGuard()
        results = guard.ainvoke(_compliant_doc())
        assert len(results) == 4

    # --- EUAIActCrewAIGovernanceGuard ---

    def test_crewai_guard_raises_on_denied(self):
        """EUAIActCrewAIGovernanceGuard._run raises PermissionError on DENIED."""
        guard = mod.EUAIActCrewAIGovernanceGuard()
        with pytest.raises(PermissionError):
            guard._run(
                {
                    "ai_system_category": "biometric_identification",
                    "conformity_assessment_completed": False,
                }
            )

    def test_crewai_guard_passes_compliant(self):
        """EUAIActCrewAIGovernanceGuard._run returns 4 results for clean doc."""
        guard = mod.EUAIActCrewAIGovernanceGuard()
        results = guard._run(_compliant_doc())
        assert len(results) == 4

    # --- EUAIActAutoGenGovernedAgent ---

    def test_autogen_agent_raises_on_denied(self):
        """EUAIActAutoGenGovernedAgent.generate_reply raises PermissionError on DENIED."""
        agent = mod.EUAIActAutoGenGovernedAgent()
        with pytest.raises(PermissionError):
            agent.generate_reply(
                {
                    "high_risk_ai": True,
                    "risk_management_system": False,
                }
            )

    def test_autogen_agent_passes_compliant(self):
        """EUAIActAutoGenGovernedAgent.generate_reply returns 4 results for clean doc."""
        agent = mod.EUAIActAutoGenGovernedAgent()
        results = agent.generate_reply(_compliant_doc())
        assert len(results) == 4

    # --- EUAIActSemanticKernelPlugin ---

    def test_semantic_kernel_raises_on_denied(self):
        """EUAIActSemanticKernelPlugin.enforce_governance raises PermissionError on DENIED."""
        plugin = mod.EUAIActSemanticKernelPlugin()
        with pytest.raises(PermissionError):
            plugin.enforce_governance(
                {
                    "ai_interacts_with_humans": True,
                    "ai_disclosure_made": False,
                }
            )

    def test_semantic_kernel_passes_compliant(self):
        """EUAIActSemanticKernelPlugin.enforce_governance returns 4 results for clean doc."""
        plugin = mod.EUAIActSemanticKernelPlugin()
        results = plugin.enforce_governance(_compliant_doc())
        assert len(results) == 4

    # --- EUAIActLlamaIndexWorkflowGuard ---

    def test_llama_index_raises_on_denied(self):
        """EUAIActLlamaIndexWorkflowGuard.process_event raises PermissionError on DENIED."""
        guard = mod.EUAIActLlamaIndexWorkflowGuard()
        with pytest.raises(PermissionError):
            guard.process_event(
                {
                    "destination_country": "Russia",
                    "high_risk_ai": True,
                }
            )

    def test_llama_index_passes_compliant(self):
        """EUAIActLlamaIndexWorkflowGuard.process_event returns 4 results for clean doc."""
        guard = mod.EUAIActLlamaIndexWorkflowGuard()
        results = guard.process_event(_compliant_doc())
        assert len(results) == 4

    # --- EUAIActHaystackGovernanceComponent ---

    def test_haystack_component_raises_on_denied(self):
        """EUAIActHaystackGovernanceComponent.run excludes DENIED documents."""
        comp = mod.EUAIActHaystackGovernanceComponent()
        denied_doc = {"prohibited_ai_practice": True}
        result = comp.run([_compliant_doc(), denied_doc])
        assert len(result["documents"]) == 1

    def test_haystack_component_passes_compliant(self):
        """EUAIActHaystackGovernanceComponent.run passes all clean docs."""
        comp = mod.EUAIActHaystackGovernanceComponent()
        result = comp.run([_compliant_doc(), _compliant_doc()])
        assert len(result["documents"]) == 2

    # --- EUAIActDSPyGovernanceModule ---

    def test_dspy_module_raises_on_denied(self):
        """EUAIActDSPyGovernanceModule.forward raises PermissionError on DENIED."""
        dummy_module = lambda doc, **kw: doc  # noqa: E731
        module = mod.EUAIActDSPyGovernanceModule(dummy_module)
        with pytest.raises(PermissionError):
            module.forward(
                {
                    "synthetic_content_generated": True,
                    "ai_generated_labeling": False,
                }
            )

    def test_dspy_module_passes_compliant(self):
        """EUAIActDSPyGovernanceModule.forward passes clean doc to wrapped module."""
        sentinel = object()
        dummy_module = lambda doc, **kw: sentinel  # noqa: E731
        module = mod.EUAIActDSPyGovernanceModule(dummy_module)
        result = module.forward(_compliant_doc())
        assert result is sentinel

    # --- EUAIActMAFPolicyMiddleware ---

    def test_maf_middleware_raises_on_denied(self):
        """EUAIActMAFPolicyMiddleware.process raises PermissionError on DENIED."""
        middleware = mod.EUAIActMAFPolicyMiddleware()
        with pytest.raises(PermissionError):
            middleware.process(
                {
                    "gpai_model": True,
                    "gpai_technical_documentation": False,
                },
                lambda msg: None,
            )

    def test_maf_middleware_passes_compliant(self):
        """EUAIActMAFPolicyMiddleware.process calls next_handler for clean doc."""
        middleware = mod.EUAIActMAFPolicyMiddleware()
        called = []
        middleware.process(_compliant_doc(), lambda msg: called.append(msg))
        assert len(called) == 1
