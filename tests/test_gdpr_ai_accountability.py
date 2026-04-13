"""
Tests for 32_gdpr_ai_accountability.py — GDPR AI Accountability Governance
Framework covering automated individual decision-making (Art. 22),
transparency and information obligations (Arts. 12–14), Data Protection
Impact Assessment (Art. 35), data minimisation and privacy by design
(Arts. 5/25).
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
    _name = "gdpr_ai_accountability_32"
    spec = importlib.util.spec_from_file_location(
        _name,
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "examples",
            "32_gdpr_ai_accountability.py",
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
        # Automated decisions
        automated_decision=True,
        legal_or_significant_effect=True,
        legal_basis_art22="explicit_consent",
        right_to_explanation_provided=True,
        special_category_data=False,
        explicit_consent_special_category=True,
        automated_profiling=False,
        opt_out_mechanism=True,
        # Transparency
        personal_data_collection=True,
        privacy_notice_provided=True,
        ai_system=True,
        personal_data_processing=True,
        ai_logic_disclosed=True,
        cross_border_transfer=False,
        transfer_safeguards_disclosed=True,
        data_retention_period_missing=False,
        # DPIA
        high_risk_processing=True,
        dpia_completed=True,
        residual_risks_acceptable=True,
        systematic_monitoring_public=False,
        large_scale_special_category=False,
        # Data minimisation
        excessive_data_collection=False,
        ai_training_data=True,
        purpose_limitation_documented=True,
        retention_period_exceeded=False,
        privacy_by_design_required=True,
        privacy_by_design_implemented=True,
    )
    defaults.update(overrides)
    return defaults


# ===========================================================================
# TestGDPRAutomatedDecisionFilter
# ===========================================================================


class TestGDPRAutomatedDecisionFilter:
    """Layer 1: GDPR Art. 22 — Automated individual decision-making."""

    def _eval(self, **kwargs):
        return mod.GDPRAutomatedDecisionFilter().filter(kwargs)

    # --- Art. 22(1) — no valid legal basis ---

    def test_automated_decision_no_legal_basis_denied(self):
        """automated_decision + legal_or_significant_effect + invalid legal_basis → DENIED."""
        result = self._eval(
            automated_decision=True,
            legal_or_significant_effect=True,
            legal_basis_art22="legitimate_interest",
        )
        assert result.decision == "DENIED"
        assert result.is_denied

    def test_automated_decision_missing_legal_basis_key_denied(self):
        """automated_decision + legal_or_significant_effect + legal_basis_art22 absent → DENIED."""
        result = self._eval(
            automated_decision=True,
            legal_or_significant_effect=True,
        )
        assert result.decision == "DENIED"
        assert result.is_denied

    def test_legal_basis_explicit_consent_passes_art22_1(self):
        """legal_basis_art22='explicit_consent' satisfies Art. 22(1)."""
        result = self._eval(
            automated_decision=True,
            legal_or_significant_effect=True,
            legal_basis_art22="explicit_consent",
            right_to_explanation_provided=True,
        )
        assert result.decision == "APPROVED"

    def test_legal_basis_contract_necessity_passes_art22_1(self):
        """legal_basis_art22='contract_necessity' satisfies Art. 22(1)."""
        result = self._eval(
            automated_decision=True,
            legal_or_significant_effect=True,
            legal_basis_art22="contract_necessity",
            right_to_explanation_provided=True,
        )
        assert result.decision == "APPROVED"

    def test_legal_basis_eu_member_state_law_passes_art22_1(self):
        """legal_basis_art22='eu_member_state_law' satisfies Art. 22(1)."""
        result = self._eval(
            automated_decision=True,
            legal_or_significant_effect=True,
            legal_basis_art22="eu_member_state_law",
            right_to_explanation_provided=True,
        )
        assert result.decision == "APPROVED"

    def test_art22_1_denial_cites_art22(self):
        """DENIED for missing legal basis cites Art. 22."""
        result = self._eval(
            automated_decision=True,
            legal_or_significant_effect=True,
            legal_basis_art22="invalid_basis",
        )
        combined = result.regulation_citation + " " + result.reason
        assert "22" in combined

    # --- Art. 22(3) + Recital 71 — right to explanation ---

    def test_automated_decision_no_explanation_denied(self):
        """automated_decision + legal_or_significant_effect + valid basis + no right_to_explanation → DENIED."""
        result = self._eval(
            automated_decision=True,
            legal_or_significant_effect=True,
            legal_basis_art22="explicit_consent",
            right_to_explanation_provided=False,
        )
        assert result.decision == "DENIED"
        assert result.is_denied

    def test_art22_3_denial_cites_recital71(self):
        """DENIED for missing explanation cites Art. 22(3) or Recital 71."""
        result = self._eval(
            automated_decision=True,
            legal_or_significant_effect=True,
            legal_basis_art22="explicit_consent",
            right_to_explanation_provided=False,
        )
        combined = result.regulation_citation + " " + result.reason
        assert "22" in combined or "71" in combined

    # --- Art. 22(4) + Art. 9 — special category data ---

    def test_automated_decision_special_category_no_consent_denied(self):
        """automated_decision + special_category_data + no explicit_consent_special_category → DENIED."""
        result = self._eval(
            automated_decision=True,
            special_category_data=True,
            explicit_consent_special_category=False,
        )
        assert result.decision == "DENIED"
        assert result.is_denied

    def test_art22_4_denial_cites_art9(self):
        """DENIED for special category without consent cites Art. 22(4) or Art. 9."""
        result = self._eval(
            automated_decision=True,
            special_category_data=True,
            explicit_consent_special_category=False,
        )
        combined = result.regulation_citation + " " + result.reason
        assert "9" in combined or "22" in combined

    def test_automated_decision_special_category_with_consent_approved(self):
        """automated_decision + special_category_data + explicit_consent_special_category → not DENIED."""
        result = self._eval(
            automated_decision=True,
            legal_or_significant_effect=False,
            special_category_data=True,
            explicit_consent_special_category=True,
        )
        assert not result.is_denied

    # --- Art. 21(2) — opt-out for profiling (REQUIRES_HUMAN_REVIEW) ---

    def test_automated_profiling_no_opt_out_requires_review(self):
        """automated_profiling=True + no opt_out_mechanism → REQUIRES_HUMAN_REVIEW."""
        result = self._eval(
            automated_profiling=True,
            opt_out_mechanism=False,
        )
        assert result.decision == "REQUIRES_HUMAN_REVIEW"
        assert not result.is_denied

    def test_profiling_review_cites_art21(self):
        """REQUIRES_HUMAN_REVIEW for missing opt-out cites Art. 21(2)."""
        result = self._eval(
            automated_profiling=True,
            opt_out_mechanism=False,
        )
        combined = result.regulation_citation + " " + result.reason
        assert "21" in combined

    def test_automated_profiling_with_opt_out_approved(self):
        """automated_profiling=True WITH opt_out_mechanism → APPROVED."""
        result = self._eval(
            automated_profiling=True,
            opt_out_mechanism=True,
        )
        assert result.decision == "APPROVED"

    # --- Compliant pass-through ---

    def test_compliant_baseline_approved(self):
        """Fully compliant doc → APPROVED."""
        result = mod.GDPRAutomatedDecisionFilter().filter(_compliant_doc())
        assert result.decision == "APPROVED"
        assert not result.is_denied

    def test_compliant_not_requires_logging(self):
        """Compliant APPROVED result sets requires_logging=False."""
        result = mod.GDPRAutomatedDecisionFilter().filter(_compliant_doc())
        assert result.requires_logging is False

    def test_missing_keys_approved(self):
        """Empty dict (all keys absent) → APPROVED."""
        result = mod.GDPRAutomatedDecisionFilter().filter({})
        assert result.decision == "APPROVED"


# ===========================================================================
# TestGDPRTransparencyFilter
# ===========================================================================


class TestGDPRTransparencyFilter:
    """Layer 2: GDPR Arts. 12–14 — Transparency and information obligations."""

    def _eval(self, **kwargs):
        return mod.GDPRTransparencyFilter().filter(kwargs)

    # --- Art. 13(1) — privacy notice at collection ---

    def test_personal_data_collection_no_privacy_notice_denied(self):
        """personal_data_collection=True + no privacy_notice_provided → DENIED."""
        result = self._eval(
            personal_data_collection=True,
            privacy_notice_provided=False,
        )
        assert result.decision == "DENIED"
        assert result.is_denied

    def test_privacy_notice_denial_cites_art13(self):
        """DENIED for missing privacy notice cites Art. 13."""
        result = self._eval(
            personal_data_collection=True,
            privacy_notice_provided=False,
        )
        combined = result.regulation_citation + " " + result.reason
        assert "13" in combined

    def test_personal_data_collection_with_notice_approved(self):
        """personal_data_collection=True WITH privacy_notice_provided → APPROVED."""
        result = self._eval(
            personal_data_collection=True,
            privacy_notice_provided=True,
        )
        assert result.decision == "APPROVED"

    # --- Art. 13(2)(f) + Recital 60 — AI logic disclosure ---

    def test_ai_system_personal_data_no_logic_disclosure_denied(self):
        """ai_system=True + personal_data_processing=True + no ai_logic_disclosed → DENIED."""
        result = self._eval(
            ai_system=True,
            personal_data_processing=True,
            ai_logic_disclosed=False,
        )
        assert result.decision == "DENIED"
        assert result.is_denied

    def test_ai_logic_denial_cites_art13_2f(self):
        """DENIED for missing AI logic disclosure cites Art. 13(2)(f) or Recital 60."""
        result = self._eval(
            ai_system=True,
            personal_data_processing=True,
            ai_logic_disclosed=False,
        )
        combined = result.regulation_citation + " " + result.reason
        assert "13" in combined or "60" in combined

    def test_ai_system_with_logic_disclosed_approved(self):
        """ai_system=True + personal_data_processing + ai_logic_disclosed → APPROVED."""
        result = self._eval(
            ai_system=True,
            personal_data_processing=True,
            ai_logic_disclosed=True,
        )
        assert result.decision == "APPROVED"

    # --- Art. 13(1)(f) — cross-border transfer safeguards ---

    def test_cross_border_transfer_no_safeguards_denied(self):
        """cross_border_transfer=True + no transfer_safeguards_disclosed → DENIED."""
        result = self._eval(
            cross_border_transfer=True,
            transfer_safeguards_disclosed=False,
        )
        assert result.decision == "DENIED"
        assert result.is_denied

    def test_cross_border_denial_cites_art13_1f(self):
        """DENIED for undisclosed cross-border transfer cites Art. 13(1)(f)."""
        result = self._eval(
            cross_border_transfer=True,
            transfer_safeguards_disclosed=False,
        )
        combined = result.regulation_citation + " " + result.reason
        assert "13" in combined

    def test_cross_border_with_safeguards_approved(self):
        """cross_border_transfer=True WITH transfer_safeguards_disclosed → APPROVED."""
        result = self._eval(
            cross_border_transfer=True,
            transfer_safeguards_disclosed=True,
        )
        assert result.decision == "APPROVED"

    # --- Art. 13(2)(a) — retention period missing (REQUIRES_HUMAN_REVIEW) ---

    def test_retention_period_missing_requires_review(self):
        """data_retention_period_missing=True → REQUIRES_HUMAN_REVIEW."""
        result = self._eval(data_retention_period_missing=True)
        assert result.decision == "REQUIRES_HUMAN_REVIEW"
        assert not result.is_denied

    def test_retention_period_review_cites_art13_2a(self):
        """REQUIRES_HUMAN_REVIEW for missing retention period cites Art. 13(2)(a)."""
        result = self._eval(data_retention_period_missing=True)
        combined = result.regulation_citation + " " + result.reason
        assert "13" in combined

    # --- Compliant pass-through ---

    def test_compliant_baseline_approved(self):
        """Fully compliant doc → APPROVED."""
        result = mod.GDPRTransparencyFilter().filter(_compliant_doc())
        assert result.decision == "APPROVED"
        assert not result.is_denied

    def test_compliant_not_requires_logging(self):
        """Compliant APPROVED result sets requires_logging=False."""
        result = mod.GDPRTransparencyFilter().filter(_compliant_doc())
        assert result.requires_logging is False

    def test_missing_keys_approved(self):
        """Empty dict → APPROVED."""
        result = mod.GDPRTransparencyFilter().filter({})
        assert result.decision == "APPROVED"


# ===========================================================================
# TestGDPRDPIAFilter
# ===========================================================================


class TestGDPRDPIAFilter:
    """Layer 3: GDPR Art. 35 — Data Protection Impact Assessment."""

    def _eval(self, **kwargs):
        return mod.GDPRDPIAFilter().filter(kwargs)

    # --- Art. 35(1) — high-risk processing without DPIA ---

    def test_high_risk_no_dpia_denied(self):
        """high_risk_processing=True + no dpia_completed → DENIED."""
        result = self._eval(
            high_risk_processing=True,
            dpia_completed=False,
        )
        assert result.decision == "DENIED"
        assert result.is_denied

    def test_high_risk_no_dpia_cites_art35_1(self):
        """DENIED for high-risk processing without DPIA cites Art. 35(1)."""
        result = self._eval(
            high_risk_processing=True,
            dpia_completed=False,
        )
        combined = result.regulation_citation + " " + result.reason
        assert "35" in combined

    def test_high_risk_with_dpia_residual_acceptable_approved(self):
        """high_risk_processing + dpia_completed + residual_risks_acceptable → APPROVED."""
        result = self._eval(
            high_risk_processing=True,
            dpia_completed=True,
            residual_risks_acceptable=True,
        )
        assert result.decision == "APPROVED"

    # --- Art. 35(3)(c) — systematic public monitoring ---

    def test_systematic_monitoring_no_dpia_denied(self):
        """systematic_monitoring_public=True + no dpia_completed → DENIED."""
        result = self._eval(
            systematic_monitoring_public=True,
            dpia_completed=False,
        )
        assert result.decision == "DENIED"
        assert result.is_denied

    def test_systematic_monitoring_denial_cites_art35_3c(self):
        """DENIED for systematic monitoring without DPIA cites Art. 35(3)(c)."""
        result = self._eval(
            systematic_monitoring_public=True,
            dpia_completed=False,
        )
        combined = result.regulation_citation + " " + result.reason
        assert "35" in combined

    def test_systematic_monitoring_with_dpia_approved(self):
        """systematic_monitoring_public=True WITH dpia_completed → not DENIED."""
        result = self._eval(
            systematic_monitoring_public=True,
            dpia_completed=True,
        )
        assert not result.is_denied

    # --- Art. 35(3)(b) — large-scale special category data ---

    def test_large_scale_special_category_no_dpia_denied(self):
        """large_scale_special_category=True + no dpia_completed → DENIED."""
        result = self._eval(
            large_scale_special_category=True,
            dpia_completed=False,
        )
        assert result.decision == "DENIED"
        assert result.is_denied

    def test_large_scale_denial_cites_art35_3b(self):
        """DENIED for large-scale special category without DPIA cites Art. 35(3)(b)."""
        result = self._eval(
            large_scale_special_category=True,
            dpia_completed=False,
        )
        combined = result.regulation_citation + " " + result.reason
        assert "35" in combined

    def test_large_scale_with_dpia_approved(self):
        """large_scale_special_category=True WITH dpia_completed → not DENIED."""
        result = self._eval(
            large_scale_special_category=True,
            dpia_completed=True,
        )
        assert not result.is_denied

    # --- Art. 36(1) — unacceptable residual risks (REQUIRES_HUMAN_REVIEW) ---

    def test_dpia_completed_residual_risks_unacceptable_requires_review(self):
        """high_risk_processing + dpia_completed + residual_risks_acceptable=False → REQUIRES_HUMAN_REVIEW."""
        result = self._eval(
            high_risk_processing=True,
            dpia_completed=True,
            residual_risks_acceptable=False,
        )
        assert result.decision == "REQUIRES_HUMAN_REVIEW"
        assert not result.is_denied

    def test_residual_risks_review_cites_art36(self):
        """REQUIRES_HUMAN_REVIEW for residual risks cites Art. 36."""
        result = self._eval(
            high_risk_processing=True,
            dpia_completed=True,
            residual_risks_acceptable=False,
        )
        combined = result.regulation_citation + " " + result.reason
        assert "36" in combined

    # --- Compliant pass-through ---

    def test_compliant_baseline_approved(self):
        """Fully compliant doc → APPROVED."""
        result = mod.GDPRDPIAFilter().filter(_compliant_doc())
        assert result.decision == "APPROVED"
        assert not result.is_denied

    def test_compliant_not_requires_logging(self):
        """Compliant APPROVED result sets requires_logging=False."""
        result = mod.GDPRDPIAFilter().filter(_compliant_doc())
        assert result.requires_logging is False

    def test_missing_keys_approved(self):
        """Empty dict → APPROVED."""
        result = mod.GDPRDPIAFilter().filter({})
        assert result.decision == "APPROVED"


# ===========================================================================
# TestGDPRDataMinimisationFilter
# ===========================================================================


class TestGDPRDataMinimisationFilter:
    """Layer 4: GDPR Arts. 5/25 — Data minimisation and privacy by design."""

    def _eval(self, **kwargs):
        return mod.GDPRDataMinimisationFilter().filter(kwargs)

    # --- Art. 5(1)(c) — excessive data collection ---

    def test_excessive_data_collection_denied(self):
        """excessive_data_collection=True → DENIED."""
        result = self._eval(excessive_data_collection=True)
        assert result.decision == "DENIED"
        assert result.is_denied

    def test_excessive_data_denial_cites_art5_1c(self):
        """DENIED for excessive data collection cites Art. 5(1)(c)."""
        result = self._eval(excessive_data_collection=True)
        combined = result.regulation_citation + " " + result.reason
        assert "5" in combined

    def test_no_excessive_data_collection_approved(self):
        """excessive_data_collection=False → not DENIED from this rule."""
        result = self._eval(excessive_data_collection=False)
        assert not result.is_denied

    # --- Art. 5(1)(b) + Art. 89 — AI training without purpose limitation ---

    def test_ai_training_no_purpose_limitation_denied(self):
        """ai_training_data=True + no purpose_limitation_documented → DENIED."""
        result = self._eval(
            ai_training_data=True,
            purpose_limitation_documented=False,
        )
        assert result.decision == "DENIED"
        assert result.is_denied

    def test_ai_training_denial_cites_art5_1b_art89(self):
        """DENIED for AI training without purpose limitation cites Art. 5(1)(b) or Art. 89."""
        result = self._eval(
            ai_training_data=True,
            purpose_limitation_documented=False,
        )
        combined = result.regulation_citation + " " + result.reason
        assert "5" in combined or "89" in combined

    def test_ai_training_with_purpose_limitation_approved(self):
        """ai_training_data=True WITH purpose_limitation_documented → not DENIED from this rule."""
        result = self._eval(
            ai_training_data=True,
            purpose_limitation_documented=True,
        )
        assert not result.is_denied

    # --- Art. 5(1)(e) — retention period exceeded ---

    def test_retention_period_exceeded_denied(self):
        """retention_period_exceeded=True → DENIED."""
        result = self._eval(retention_period_exceeded=True)
        assert result.decision == "DENIED"
        assert result.is_denied

    def test_retention_exceeded_denial_cites_art5_1e(self):
        """DENIED for exceeded retention period cites Art. 5(1)(e)."""
        result = self._eval(retention_period_exceeded=True)
        combined = result.regulation_citation + " " + result.reason
        assert "5" in combined

    def test_retention_within_period_approved(self):
        """retention_period_exceeded=False → not DENIED from this rule."""
        result = self._eval(retention_period_exceeded=False)
        assert not result.is_denied

    # --- Art. 25 — privacy by design required but not implemented (REQUIRES_HUMAN_REVIEW) ---

    def test_privacy_by_design_required_not_implemented_requires_review(self):
        """privacy_by_design_required=True + no privacy_by_design_implemented → REQUIRES_HUMAN_REVIEW."""
        result = self._eval(
            privacy_by_design_required=True,
            privacy_by_design_implemented=False,
        )
        assert result.decision == "REQUIRES_HUMAN_REVIEW"
        assert not result.is_denied

    def test_privacy_by_design_review_cites_art25(self):
        """REQUIRES_HUMAN_REVIEW for missing privacy by design cites Art. 25."""
        result = self._eval(
            privacy_by_design_required=True,
            privacy_by_design_implemented=False,
        )
        combined = result.regulation_citation + " " + result.reason
        assert "25" in combined

    def test_privacy_by_design_implemented_approved(self):
        """privacy_by_design_required=True WITH privacy_by_design_implemented → APPROVED."""
        result = self._eval(
            privacy_by_design_required=True,
            privacy_by_design_implemented=True,
        )
        assert result.decision == "APPROVED"

    # --- Compliant pass-through ---

    def test_compliant_baseline_approved(self):
        """Fully compliant doc → APPROVED."""
        result = mod.GDPRDataMinimisationFilter().filter(_compliant_doc())
        assert result.decision == "APPROVED"
        assert not result.is_denied

    def test_compliant_not_requires_logging(self):
        """Compliant APPROVED result sets requires_logging=False."""
        result = mod.GDPRDataMinimisationFilter().filter(_compliant_doc())
        assert result.requires_logging is False

    def test_missing_keys_approved(self):
        """Empty dict → APPROVED."""
        result = mod.GDPRDataMinimisationFilter().filter({})
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

    def test_automated_decision_filter_is_frozen(self):
        """GDPRAutomatedDecisionFilter is a frozen dataclass (immutable)."""
        f = mod.GDPRAutomatedDecisionFilter()
        with pytest.raises((AttributeError, TypeError)):
            f.FILTER_NAME = "MODIFIED"  # type: ignore[misc]

    def test_transparency_filter_is_frozen(self):
        """GDPRTransparencyFilter is a frozen dataclass."""
        f = mod.GDPRTransparencyFilter()
        with pytest.raises((AttributeError, TypeError)):
            f.FILTER_NAME = "MODIFIED"  # type: ignore[misc]

    def test_dpia_filter_is_frozen(self):
        """GDPRDPIAFilter is a frozen dataclass."""
        f = mod.GDPRDPIAFilter()
        with pytest.raises((AttributeError, TypeError)):
            f.FILTER_NAME = "MODIFIED"  # type: ignore[misc]

    def test_data_minimisation_filter_is_frozen(self):
        """GDPRDataMinimisationFilter is a frozen dataclass."""
        f = mod.GDPRDataMinimisationFilter()
        with pytest.raises((AttributeError, TypeError)):
            f.FILTER_NAME = "MODIFIED"  # type: ignore[misc]

    def test_requires_human_review_is_not_denied(self):
        """REQUIRES_HUMAN_REVIEW decision sets is_denied=False."""
        result = mod.FilterResult(filter_name="test", decision="REQUIRES_HUMAN_REVIEW")
        assert result.is_denied is False

    def test_missing_keys_default_to_approved_automated_decision(self):
        """Empty dict → APPROVED for GDPRAutomatedDecisionFilter (all keys absent)."""
        result = mod.GDPRAutomatedDecisionFilter().filter({})
        assert result.decision == "APPROVED"

    def test_no_legal_or_significant_effect_skips_art22_1(self):
        """automated_decision=True but legal_or_significant_effect absent → not denied by Art. 22(1)."""
        result = mod.GDPRAutomatedDecisionFilter().filter(
            {"automated_decision": True, "legal_or_significant_effect": False}
        )
        # No legal/significant effect means Art. 22(1) check is not triggered
        assert not result.is_denied

    def test_profiling_with_opt_out_not_denied(self):
        """automated_profiling=True WITH opt_out_mechanism=True → APPROVED."""
        result = mod.GDPRAutomatedDecisionFilter().filter({"automated_profiling": True, "opt_out_mechanism": True})
        assert result.decision == "APPROVED"
        assert not result.is_denied


# ===========================================================================
# TestIntegrationWrappers — all 8 wrappers
# ===========================================================================


class TestIntegrationWrappers:
    """Integration wrappers instantiate and enforce GDPR governance correctly."""

    # --- GDPRLangChainPolicyGuard ---

    def test_langchain_guard_raises_on_denied(self):
        """GDPRLangChainPolicyGuard.invoke raises PermissionError on DENIED."""
        guard = mod.GDPRLangChainPolicyGuard()
        with pytest.raises(PermissionError):
            guard.invoke({"excessive_data_collection": True})

    def test_langchain_guard_ainvoke_passes_compliant(self):
        """GDPRLangChainPolicyGuard.ainvoke returns 4 results for clean doc."""
        guard = mod.GDPRLangChainPolicyGuard()
        results = guard.ainvoke(_compliant_doc())
        assert len(results) == 4

    # --- GDPRCrewAIGovernanceGuard ---

    def test_crewai_guard_raises_on_denied(self):
        """GDPRCrewAIGovernanceGuard._run raises PermissionError on DENIED."""
        guard = mod.GDPRCrewAIGovernanceGuard()
        with pytest.raises(PermissionError):
            guard._run(
                {
                    "personal_data_collection": True,
                    "privacy_notice_provided": False,
                }
            )

    def test_crewai_guard_passes_compliant(self):
        """GDPRCrewAIGovernanceGuard._run returns 4 results for clean doc."""
        guard = mod.GDPRCrewAIGovernanceGuard()
        results = guard._run(_compliant_doc())
        assert len(results) == 4

    # --- GDPRAutoGenGovernedAgent ---

    def test_autogen_agent_raises_on_denied(self):
        """GDPRAutoGenGovernedAgent.generate_reply raises PermissionError on DENIED."""
        agent = mod.GDPRAutoGenGovernedAgent()
        with pytest.raises(PermissionError):
            agent.generate_reply(
                {
                    "high_risk_processing": True,
                    "dpia_completed": False,
                }
            )

    def test_autogen_agent_passes_compliant(self):
        """GDPRAutoGenGovernedAgent.generate_reply returns 4 results for clean doc."""
        agent = mod.GDPRAutoGenGovernedAgent()
        results = agent.generate_reply(_compliant_doc())
        assert len(results) == 4

    # --- GDPRSemanticKernelPlugin ---

    def test_semantic_kernel_raises_on_denied(self):
        """GDPRSemanticKernelPlugin.enforce_governance raises PermissionError on DENIED."""
        plugin = mod.GDPRSemanticKernelPlugin()
        with pytest.raises(PermissionError):
            plugin.enforce_governance(
                {
                    "automated_decision": True,
                    "legal_or_significant_effect": True,
                    "legal_basis_art22": "not_valid",
                }
            )

    def test_semantic_kernel_passes_compliant(self):
        """GDPRSemanticKernelPlugin.enforce_governance returns 4 results for clean doc."""
        plugin = mod.GDPRSemanticKernelPlugin()
        results = plugin.enforce_governance(_compliant_doc())
        assert len(results) == 4

    # --- GDPRLlamaIndexWorkflowGuard ---

    def test_llama_index_raises_on_denied(self):
        """GDPRLlamaIndexWorkflowGuard.process_event raises PermissionError on DENIED."""
        guard = mod.GDPRLlamaIndexWorkflowGuard()
        with pytest.raises(PermissionError):
            guard.process_event(
                {
                    "retention_period_exceeded": True,
                }
            )

    def test_llama_index_passes_compliant(self):
        """GDPRLlamaIndexWorkflowGuard.process_event returns 4 results for clean doc."""
        guard = mod.GDPRLlamaIndexWorkflowGuard()
        results = guard.process_event(_compliant_doc())
        assert len(results) == 4

    # --- GDPRHaystackGovernanceComponent ---

    def test_haystack_component_excludes_denied_documents(self):
        """GDPRHaystackGovernanceComponent.run excludes DENIED documents."""
        comp = mod.GDPRHaystackGovernanceComponent()
        denied_doc = {"excessive_data_collection": True}
        result = comp.run([_compliant_doc(), denied_doc])
        assert len(result["documents"]) == 1

    def test_haystack_component_passes_compliant(self):
        """GDPRHaystackGovernanceComponent.run passes all clean docs."""
        comp = mod.GDPRHaystackGovernanceComponent()
        result = comp.run([_compliant_doc(), _compliant_doc()])
        assert len(result["documents"]) == 2

    # --- GDPRDSPyGovernanceModule ---

    def test_dspy_module_raises_on_denied(self):
        """GDPRDSPyGovernanceModule.forward raises PermissionError on DENIED."""
        dummy_module = lambda doc, **kw: doc  # noqa: E731
        module = mod.GDPRDSPyGovernanceModule(dummy_module)
        with pytest.raises(PermissionError):
            module.forward(
                {
                    "ai_training_data": True,
                    "purpose_limitation_documented": False,
                }
            )

    def test_dspy_module_passes_compliant(self):
        """GDPRDSPyGovernanceModule.forward passes clean doc to wrapped module."""
        sentinel = object()
        dummy_module = lambda doc, **kw: sentinel  # noqa: E731
        module = mod.GDPRDSPyGovernanceModule(dummy_module)
        result = module.forward(_compliant_doc())
        assert result is sentinel

    # --- GDPRMAFPolicyMiddleware ---

    def test_maf_middleware_raises_on_denied(self):
        """GDPRMAFPolicyMiddleware.process raises PermissionError on DENIED."""
        middleware = mod.GDPRMAFPolicyMiddleware()
        with pytest.raises(PermissionError):
            middleware.process(
                {
                    "cross_border_transfer": True,
                    "transfer_safeguards_disclosed": False,
                },
                lambda msg: None,
            )

    def test_maf_middleware_passes_compliant(self):
        """GDPRMAFPolicyMiddleware.process calls next_handler for clean doc."""
        middleware = mod.GDPRMAFPolicyMiddleware()
        called = []
        middleware.process(_compliant_doc(), lambda msg: called.append(msg))
        assert len(called) == 1
