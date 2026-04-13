"""
Tests for 30_us_state_ai_laws.py — US State AI Laws Governance Framework
covering Colorado SB 205/AI Act 2024, Illinois BIPA + AI Video Interview Act,
Virginia VCDPA AI provisions, and a multi-state cross-border applicability filter.
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
    _name = "us_state_ai_laws_30"
    spec = importlib.util.spec_from_file_location(
        _name,
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "examples",
            "30_us_state_ai_laws.py",
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
        high_risk_ai=True,
        impact_assessment_completed=True,
        bias_testing_completed=True,
        automated_employment_decision=False,
        human_oversight=True,
        biometric_identifier=False,
        written_consent=True,
        biometric_data_type=None,
        biipa_written_consent=True,
        biipa_retention_policy=True,
        video_interview_ai=False,
        ai_video_disclosure=True,
        third_party_sharing=False,
        automated_profiling=False,
        consequential_decision=False,
        human_review_available=True,
        sensitive_data_ai_processing=False,
        consent_obtained=True,
        ai_system_type="low_risk",
        data_protection_assessment=True,
        child_data_ai=False,
        consumer_state="New York",
        ai_decision_making=False,
        ccpa_ai_disclosure=True,
        automated_decision=False,
        opt_out_offered=True,
    )
    defaults.update(overrides)
    return defaults


# ===========================================================================
# TestColoradoSB205Filter
# ===========================================================================


class TestColoradoSB205Filter:
    """Layer 1: Colorado AI Act 2024 (SB 24-205) + Colorado Privacy Act CRS §6-1-1306."""

    def _eval(self, **kwargs):
        return mod.ColoradoSB205Filter().filter(kwargs)

    # --- CRS §6-1-1702 — high-risk AI without impact assessment ---

    def test_high_risk_no_impact_assessment_denied(self):
        """high_risk_ai=True + no impact_assessment_completed → DENIED."""
        result = self._eval(high_risk_ai=True, impact_assessment_completed=False)
        assert result.decision == "DENIED"
        assert result.is_denied

    def test_high_risk_no_impact_assessment_cites_6_1_1702(self):
        """DENIED for high-risk without impact assessment cites §6-1-1702."""
        result = self._eval(high_risk_ai=True, impact_assessment_completed=False)
        combined = result.regulation_citation + " " + result.reason
        assert "1702" in combined

    def test_high_risk_with_impact_assessment_no_denied_for_1702(self):
        """high_risk_ai=True WITH impact_assessment_completed → not denied for §6-1-1702."""
        result = self._eval(
            high_risk_ai=True,
            impact_assessment_completed=True,
            bias_testing_completed=True,
        )
        assert result.decision == "APPROVED"

    def test_non_high_risk_no_impact_assessment_approved(self):
        """high_risk_ai=False + no impact_assessment_completed → APPROVED (§6-1-1702 not triggered)."""
        result = self._eval(high_risk_ai=False, impact_assessment_completed=False)
        assert result.decision == "APPROVED"

    # --- CRS §6-1-1306(1)(a)(IV) — automated employment decision without human review ---

    def test_automated_employment_no_human_oversight_denied(self):
        """automated_employment_decision=True + human_oversight=False → DENIED."""
        result = self._eval(
            high_risk_ai=False,
            automated_employment_decision=True,
            human_oversight=False,
        )
        assert result.decision == "DENIED"
        assert result.is_denied

    def test_automated_employment_no_human_oversight_cites_6_1_1306(self):
        """DENIED for automated employment without oversight cites §6-1-1306."""
        result = self._eval(
            high_risk_ai=False,
            automated_employment_decision=True,
            human_oversight=False,
        )
        combined = result.regulation_citation + " " + result.reason
        assert "1306" in combined

    def test_automated_employment_with_human_oversight_approved(self):
        """automated_employment_decision=True WITH human_oversight → APPROVED."""
        result = self._eval(
            high_risk_ai=False,
            automated_employment_decision=True,
            human_oversight=True,
        )
        assert result.decision == "APPROVED"

    def test_non_automated_employment_no_oversight_approved(self):
        """automated_employment_decision=False → APPROVED (§6-1-1306 not triggered)."""
        result = self._eval(automated_employment_decision=False, human_oversight=False)
        assert result.decision == "APPROVED"

    # --- Colorado AI Act §6-1-1704 — biometric identifier without written consent ---

    def test_biometric_no_written_consent_denied(self):
        """biometric_identifier=True + written_consent=False → DENIED."""
        result = self._eval(
            high_risk_ai=False,
            biometric_identifier=True,
            written_consent=False,
        )
        assert result.decision == "DENIED"
        assert result.is_denied

    def test_biometric_no_written_consent_cites_6_1_1704(self):
        """DENIED for biometric without consent cites §6-1-1704."""
        result = self._eval(
            high_risk_ai=False,
            biometric_identifier=True,
            written_consent=False,
        )
        combined = result.regulation_citation + " " + result.reason
        assert "1704" in combined

    def test_biometric_with_written_consent_approved(self):
        """biometric_identifier=True WITH written_consent → APPROVED."""
        result = self._eval(biometric_identifier=True, written_consent=True)
        assert result.decision == "APPROVED"

    def test_no_biometric_no_consent_approved(self):
        """biometric_identifier=False + no written_consent → APPROVED (§6-1-1704 not triggered)."""
        result = self._eval(biometric_identifier=False, written_consent=False)
        assert result.decision == "APPROVED"

    # --- Colorado AI Act §6-1-1703 — high-risk AI without bias testing ---

    def test_high_risk_no_bias_testing_requires_review(self):
        """high_risk_ai=True + bias_testing_completed=False (with impact_assessment) → REQUIRES_HUMAN_REVIEW."""
        result = self._eval(
            high_risk_ai=True,
            impact_assessment_completed=True,
            bias_testing_completed=False,
        )
        assert result.decision == "REQUIRES_HUMAN_REVIEW"
        assert not result.is_denied

    def test_high_risk_no_bias_testing_cites_6_1_1703(self):
        """REQUIRES_HUMAN_REVIEW for no bias testing cites §6-1-1703."""
        result = self._eval(
            high_risk_ai=True,
            impact_assessment_completed=True,
            bias_testing_completed=False,
        )
        combined = result.regulation_citation + " " + result.reason
        assert "1703" in combined

    def test_high_risk_with_bias_testing_approved(self):
        """high_risk_ai=True WITH bias_testing_completed → APPROVED."""
        result = self._eval(
            high_risk_ai=True,
            impact_assessment_completed=True,
            bias_testing_completed=True,
        )
        assert result.decision == "APPROVED"

    # --- Compliant baseline ---

    def test_compliant_baseline_approved(self):
        """Fully compliant doc → APPROVED."""
        result = mod.ColoradoSB205Filter().filter(_compliant_doc())
        assert result.decision == "APPROVED"
        assert not result.is_denied

    def test_compliant_not_requires_logging(self):
        """Compliant approval sets requires_logging=False."""
        result = mod.ColoradoSB205Filter().filter(_compliant_doc())
        assert result.requires_logging is False

    def test_denied_requires_logging(self):
        """DENIED result sets requires_logging=True."""
        result = self._eval(high_risk_ai=True, impact_assessment_completed=False)
        assert result.requires_logging is True

    def test_missing_keys_approved(self):
        """Empty dict (all keys absent) → APPROVED (no conditions triggered)."""
        result = mod.ColoradoSB205Filter().filter({})
        assert result.decision == "APPROVED"


# ===========================================================================
# TestIllinoisBIPAAIFilter
# ===========================================================================


class TestIllinoisBIPAAIFilter:
    """Layer 2: Illinois BIPA (740 ILCS 14) + AI Video Interview Act (820 ILCS 42)."""

    def _eval(self, **kwargs):
        return mod.IllinoisBIPAAIFilter().filter(kwargs)

    # --- 740 ILCS 14/15(b) — biometric identifier without written release ---

    def test_fingerprint_no_consent_denied(self):
        """biometric_data_type=fingerprint + no biipa_written_consent → DENIED."""
        result = self._eval(
            biometric_data_type="fingerprint",
            biipa_written_consent=False,
            biipa_retention_policy=True,
        )
        assert result.decision == "DENIED"
        assert result.is_denied

    def test_face_geometry_no_consent_denied(self):
        """biometric_data_type=face_geometry + no biipa_written_consent → DENIED."""
        result = self._eval(
            biometric_data_type="face_geometry",
            biipa_written_consent=False,
            biipa_retention_policy=True,
        )
        assert result.decision == "DENIED"

    def test_voiceprint_no_consent_denied(self):
        """biometric_data_type=voiceprint + no biipa_written_consent → DENIED."""
        result = self._eval(
            biometric_data_type="voiceprint",
            biipa_written_consent=False,
            biipa_retention_policy=True,
        )
        assert result.decision == "DENIED"

    def test_biometric_no_consent_cites_740_ilcs_14_15b(self):
        """DENIED for biometric without consent cites 740 ILCS 14/15(b)."""
        result = self._eval(
            biometric_data_type="iris",
            biipa_written_consent=False,
            biipa_retention_policy=True,
        )
        combined = result.regulation_citation + " " + result.reason
        assert "14/15(b)" in combined or ("14" in combined and "15" in combined)

    def test_biometric_with_consent_approved(self):
        """biometric_data_type=fingerprint WITH biipa_written_consent + retention_policy → APPROVED."""
        result = self._eval(
            biometric_data_type="fingerprint",
            biipa_written_consent=True,
            biipa_retention_policy=True,
        )
        assert result.decision == "APPROVED"

    # --- 740 ILCS 14/15(a) — biometric identifier without retention policy ---

    def test_biometric_no_retention_policy_denied(self):
        """biometric_data_type + consent present + no retention_policy → DENIED (§15(a))."""
        result = self._eval(
            biometric_data_type="retina",
            biipa_written_consent=True,
            biipa_retention_policy=False,
        )
        assert result.decision == "DENIED"
        assert result.is_denied

    def test_biometric_no_retention_policy_cites_740_ilcs_14_15a(self):
        """DENIED for no retention policy cites 740 ILCS 14/15(a)."""
        result = self._eval(
            biometric_data_type="retina",
            biipa_written_consent=True,
            biipa_retention_policy=False,
        )
        combined = result.regulation_citation + " " + result.reason
        assert "15(a)" in combined or ("14" in combined and "15" in combined and "retention" in result.reason.lower())

    # --- 820 ILCS 42/10 — AI video interview without disclosure ---

    def test_video_interview_ai_no_disclosure_denied(self):
        """video_interview_ai=True + ai_video_disclosure=False → DENIED."""
        result = self._eval(
            video_interview_ai=True,
            ai_video_disclosure=False,
        )
        assert result.decision == "DENIED"
        assert result.is_denied

    def test_video_interview_ai_no_disclosure_cites_820_ilcs_42(self):
        """DENIED for video AI without disclosure cites 820 ILCS 42/10."""
        result = self._eval(
            video_interview_ai=True,
            ai_video_disclosure=False,
        )
        combined = result.regulation_citation + " " + result.reason
        assert "820" in combined or "42" in combined

    def test_video_interview_ai_with_disclosure_approved(self):
        """video_interview_ai=True WITH ai_video_disclosure → APPROVED."""
        result = self._eval(
            video_interview_ai=True,
            ai_video_disclosure=True,
        )
        assert result.decision == "APPROVED"

    # --- 740 ILCS 14/15(d) — biometric third-party sharing without consent ---

    def test_biometric_third_party_no_consent_denied(self):
        """biometric_data_type + third_party_sharing=True + no biipa_written_consent → DENIED (§15(d))."""
        result = self._eval(
            biometric_data_type="hand_geometry",
            biipa_written_consent=False,
            biipa_retention_policy=True,
            third_party_sharing=True,
        )
        # §15(b) fires before §15(d) — either is DENIED
        assert result.decision == "DENIED"

    def test_third_party_sharing_without_biometric_approved(self):
        """third_party_sharing=True but no biometric_data_type → APPROVED."""
        result = self._eval(third_party_sharing=True, biipa_written_consent=False)
        assert result.decision == "APPROVED"

    # --- Compliant baseline ---

    def test_compliant_baseline_approved(self):
        """Fully compliant doc → APPROVED."""
        result = mod.IllinoisBIPAAIFilter().filter(_compliant_doc())
        assert result.decision == "APPROVED"
        assert not result.is_denied

    def test_compliant_not_requires_logging(self):
        """Compliant approval sets requires_logging=False."""
        result = mod.IllinoisBIPAAIFilter().filter(_compliant_doc())
        assert result.requires_logging is False

    def test_missing_keys_approved(self):
        """Empty dict → APPROVED."""
        result = mod.IllinoisBIPAAIFilter().filter({})
        assert result.decision == "APPROVED"

    def test_non_bipa_biometric_type_approved(self):
        """biometric_data_type=dna (not in BIPA) → APPROVED."""
        result = self._eval(
            biometric_data_type="dna",
            biipa_written_consent=False,
            biipa_retention_policy=False,
        )
        assert result.decision == "APPROVED"


# ===========================================================================
# TestVirginiaAIProvisionsFilter
# ===========================================================================


class TestVirginiaAIProvisionsFilter:
    """Layer 3: Virginia VCDPA AI provisions (Va. Code §59.1-577 et seq.)."""

    def _eval(self, **kwargs):
        return mod.VirginiaAIProvisionsFilter().filter(kwargs)

    # --- Va. Code §59.1-579 — automated profiling without human review ---

    def test_automated_profiling_consequential_no_review_requires_human_review(self):
        """automated_profiling + consequential_decision + no human_review → REQUIRES_HUMAN_REVIEW."""
        result = self._eval(
            automated_profiling=True,
            consequential_decision=True,
            human_review_available=False,
        )
        assert result.decision == "REQUIRES_HUMAN_REVIEW"
        assert not result.is_denied

    def test_automated_profiling_no_review_cites_59_1_579(self):
        """REQUIRES_HUMAN_REVIEW for profiling without review cites Va. Code §59.1-579."""
        result = self._eval(
            automated_profiling=True,
            consequential_decision=True,
            human_review_available=False,
        )
        combined = result.regulation_citation + " " + result.reason
        assert "579" in combined

    def test_automated_profiling_with_review_approved(self):
        """automated_profiling + consequential_decision WITH human_review → APPROVED."""
        result = self._eval(
            automated_profiling=True,
            consequential_decision=True,
            human_review_available=True,
        )
        assert result.decision == "APPROVED"

    def test_non_consequential_profiling_no_review_approved(self):
        """automated_profiling + NOT consequential_decision → APPROVED (§59.1-579 not triggered)."""
        result = self._eval(
            automated_profiling=True,
            consequential_decision=False,
            human_review_available=False,
        )
        assert result.decision == "APPROVED"

    # --- Va. Code §59.1-578(A) — sensitive data in AI without consent ---

    def test_sensitive_data_no_consent_denied(self):
        """sensitive_data_ai_processing=True + consent_obtained=False → DENIED."""
        result = self._eval(
            sensitive_data_ai_processing=True,
            consent_obtained=False,
        )
        assert result.decision == "DENIED"
        assert result.is_denied

    def test_sensitive_data_no_consent_cites_59_1_578a(self):
        """DENIED for sensitive data without consent cites Va. Code §59.1-578(A)."""
        result = self._eval(
            sensitive_data_ai_processing=True,
            consent_obtained=False,
        )
        combined = result.regulation_citation + " " + result.reason
        assert "578" in combined

    def test_sensitive_data_with_consent_approved(self):
        """sensitive_data_ai_processing=True WITH consent_obtained → APPROVED."""
        result = self._eval(
            sensitive_data_ai_processing=True,
            consent_obtained=True,
        )
        assert result.decision == "APPROVED"

    # --- Va. Code §59.1-581 — high-risk AI without data protection assessment ---

    def test_high_risk_no_assessment_denied(self):
        """ai_system_type=high_risk + no data_protection_assessment → DENIED."""
        result = self._eval(
            ai_system_type="high_risk",
            data_protection_assessment=False,
        )
        assert result.decision == "DENIED"
        assert result.is_denied

    def test_high_risk_no_assessment_cites_59_1_581(self):
        """DENIED for high-risk without assessment cites Va. Code §59.1-581."""
        result = self._eval(
            ai_system_type="high_risk",
            data_protection_assessment=False,
        )
        combined = result.regulation_citation + " " + result.reason
        assert "581" in combined

    def test_high_risk_with_assessment_approved(self):
        """ai_system_type=high_risk WITH data_protection_assessment → APPROVED."""
        result = self._eval(
            ai_system_type="high_risk",
            data_protection_assessment=True,
        )
        assert result.decision == "APPROVED"

    def test_low_risk_no_assessment_approved(self):
        """ai_system_type=low_risk + no assessment → APPROVED (§59.1-581 not triggered)."""
        result = self._eval(ai_system_type="low_risk", data_protection_assessment=False)
        assert result.decision == "APPROVED"

    # --- Va. Code §59.1-578(B) — child data in AI ---

    def test_child_data_ai_denied(self):
        """child_data_ai=True → DENIED (unconditional)."""
        result = self._eval(child_data_ai=True)
        assert result.decision == "DENIED"
        assert result.is_denied

    def test_child_data_ai_cites_59_1_578b(self):
        """DENIED for child data AI cites Va. Code §59.1-578(B)."""
        result = self._eval(child_data_ai=True)
        combined = result.regulation_citation + " " + result.reason
        assert "578" in combined

    def test_no_child_data_approved(self):
        """child_data_ai=False → APPROVED (§59.1-578(B) not triggered)."""
        result = self._eval(child_data_ai=False)
        assert result.decision == "APPROVED"

    # --- Compliant baseline ---

    def test_compliant_baseline_approved(self):
        """Fully compliant doc → APPROVED."""
        result = mod.VirginiaAIProvisionsFilter().filter(_compliant_doc())
        assert result.decision == "APPROVED"
        assert not result.is_denied

    def test_compliant_not_requires_logging(self):
        """Compliant approval sets requires_logging=False."""
        result = mod.VirginiaAIProvisionsFilter().filter(_compliant_doc())
        assert result.requires_logging is False

    def test_missing_keys_approved(self):
        """Empty dict → APPROVED."""
        result = mod.VirginiaAIProvisionsFilter().filter({})
        assert result.decision == "APPROVED"


# ===========================================================================
# TestUSStateAICrossBorderFilter
# ===========================================================================


class TestUSStateAICrossBorderFilter:
    """Layer 4: US multi-state AI law applicability framework."""

    def _eval(self, **kwargs):
        return mod.USStateAICrossBorderFilter().filter(kwargs)

    # --- Illinois BIPA extraterritorial ---

    def test_illinois_biometric_no_consent_denied(self):
        """consumer_state=Illinois + biometric_data_type + no biipa_written_consent → DENIED."""
        result = self._eval(
            consumer_state="Illinois",
            biometric_data_type="fingerprint",
            biipa_written_consent=False,
        )
        assert result.decision == "DENIED"
        assert result.is_denied

    def test_illinois_biometric_no_consent_cites_bipa(self):
        """DENIED for IL biometric cites 740 ILCS 14 BIPA."""
        result = self._eval(
            consumer_state="Illinois",
            biometric_data_type="voiceprint",
            biipa_written_consent=False,
        )
        combined = result.regulation_citation + " " + result.reason
        assert "BIPA" in combined or "740" in combined or "Illinois" in combined

    def test_illinois_biometric_with_consent_approved(self):
        """consumer_state=Illinois + biometric + biipa_written_consent=True → APPROVED."""
        result = self._eval(
            consumer_state="Illinois",
            biometric_data_type="fingerprint",
            biipa_written_consent=True,
        )
        assert result.decision == "APPROVED"

    def test_illinois_no_biometric_type_approved(self):
        """consumer_state=Illinois + no biometric_data_type → APPROVED (BIPA not triggered)."""
        result = self._eval(
            consumer_state="Illinois",
            biometric_data_type=None,
            biipa_written_consent=False,
        )
        assert result.decision == "APPROVED"

    # --- Colorado AI Act extraterritorial ---

    def test_colorado_high_risk_no_assessment_denied(self):
        """consumer_state=Colorado + high_risk_ai + no impact_assessment → DENIED."""
        result = self._eval(
            consumer_state="Colorado",
            high_risk_ai=True,
            impact_assessment_completed=False,
        )
        assert result.decision == "DENIED"
        assert result.is_denied

    def test_colorado_high_risk_no_assessment_cites_colorado_ai_act(self):
        """DENIED for CO high-risk without assessment cites Colorado AI Act §6-1-1702."""
        result = self._eval(
            consumer_state="Colorado",
            high_risk_ai=True,
            impact_assessment_completed=False,
        )
        combined = result.regulation_citation + " " + result.reason
        assert "Colorado" in combined or "1702" in combined

    def test_colorado_high_risk_with_assessment_approved(self):
        """consumer_state=Colorado + high_risk_ai WITH impact_assessment → APPROVED."""
        result = self._eval(
            consumer_state="Colorado",
            high_risk_ai=True,
            impact_assessment_completed=True,
        )
        assert result.decision == "APPROVED"

    # --- VA/TX/CT opt-out required ---

    def test_virginia_automated_consequential_no_opt_out_requires_review(self):
        """consumer_state=Virginia + automated + consequential + no opt_out → REQUIRES_HUMAN_REVIEW."""
        result = self._eval(
            consumer_state="Virginia",
            automated_decision=True,
            consequential_decision=True,
            opt_out_offered=False,
        )
        assert result.decision == "REQUIRES_HUMAN_REVIEW"
        assert not result.is_denied

    def test_texas_automated_consequential_no_opt_out_requires_review(self):
        """consumer_state=Texas + automated + consequential + no opt_out → REQUIRES_HUMAN_REVIEW."""
        result = self._eval(
            consumer_state="Texas",
            automated_decision=True,
            consequential_decision=True,
            opt_out_offered=False,
        )
        assert result.decision == "REQUIRES_HUMAN_REVIEW"

    def test_connecticut_automated_consequential_no_opt_out_requires_review(self):
        """consumer_state=Connecticut + automated + consequential + no opt_out → REQUIRES_HUMAN_REVIEW."""
        result = self._eval(
            consumer_state="Connecticut",
            automated_decision=True,
            consequential_decision=True,
            opt_out_offered=False,
        )
        assert result.decision == "REQUIRES_HUMAN_REVIEW"

    def test_va_tx_ct_with_opt_out_approved(self):
        """consumer_state=Virginia + automated + consequential WITH opt_out → APPROVED."""
        result = self._eval(
            consumer_state="Virginia",
            automated_decision=True,
            consequential_decision=True,
            opt_out_offered=True,
        )
        assert result.decision == "APPROVED"

    def test_va_tx_ct_requires_review_cites_multistate(self):
        """REQUIRES_HUMAN_REVIEW for VA/TX/CT cites multi-state consumer AI rights."""
        result = self._eval(
            consumer_state="Texas",
            automated_decision=True,
            consequential_decision=True,
            opt_out_offered=False,
        )
        combined = result.regulation_citation + " " + result.reason
        assert any(s in combined for s in ["Virginia", "Texas", "Connecticut", "VCDPA", "TDPSA", "CTDPA"])

    # --- California CPRA ---

    def test_california_ai_decision_no_disclosure_denied(self):
        """consumer_state=California + ai_decision_making + no ccpa_ai_disclosure → DENIED."""
        result = self._eval(
            consumer_state="California",
            ai_decision_making=True,
            ccpa_ai_disclosure=False,
        )
        assert result.decision == "DENIED"
        assert result.is_denied

    def test_california_ai_decision_no_disclosure_cites_cpra(self):
        """DENIED for CA without disclosure cites Cal. Civ. Code §1798.185(a)(16)."""
        result = self._eval(
            consumer_state="California",
            ai_decision_making=True,
            ccpa_ai_disclosure=False,
        )
        combined = result.regulation_citation + " " + result.reason
        assert "California" in combined or "CPRA" in combined or "1798" in combined

    def test_california_with_disclosure_approved(self):
        """consumer_state=California + ai_decision_making WITH ccpa_ai_disclosure → APPROVED."""
        result = self._eval(
            consumer_state="California",
            ai_decision_making=True,
            ccpa_ai_disclosure=True,
        )
        assert result.decision == "APPROVED"

    def test_california_no_ai_decision_making_approved(self):
        """consumer_state=California + ai_decision_making=False → APPROVED (CPRA not triggered)."""
        result = self._eval(
            consumer_state="California",
            ai_decision_making=False,
            ccpa_ai_disclosure=False,
        )
        assert result.decision == "APPROVED"

    # --- Compliant baseline + edge cases ---

    def test_compliant_baseline_approved(self):
        """Fully compliant doc → APPROVED."""
        result = mod.USStateAICrossBorderFilter().filter(_compliant_doc())
        assert result.decision == "APPROVED"
        assert not result.is_denied

    def test_compliant_not_requires_logging(self):
        """Compliant approval sets requires_logging=False."""
        result = mod.USStateAICrossBorderFilter().filter(_compliant_doc())
        assert result.requires_logging is False

    def test_unknown_state_approved(self):
        """consumer_state=Oregon (no specific rule) → APPROVED."""
        result = self._eval(
            consumer_state="Oregon",
            high_risk_ai=True,
            impact_assessment_completed=False,
            ai_decision_making=True,
            ccpa_ai_disclosure=False,
        )
        assert result.decision == "APPROVED"

    def test_missing_keys_approved(self):
        """Empty dict → APPROVED."""
        result = mod.USStateAICrossBorderFilter().filter({})
        assert result.decision == "APPROVED"


# ===========================================================================
# TestFilterResult
# ===========================================================================


class TestFilterResult:
    """FilterResult dataclass property tests."""

    def test_is_denied_true_only_for_denied(self):
        """is_denied is True only when decision is 'DENIED'."""
        result_denied = mod.FilterResult(filter_name="test", decision="DENIED")
        result_review = mod.FilterResult(filter_name="test", decision="REQUIRES_HUMAN_REVIEW")
        result_approved = mod.FilterResult(filter_name="test", decision="APPROVED")
        assert result_denied.is_denied is True
        assert result_review.is_denied is False
        assert result_approved.is_denied is False

    def test_default_decision_approved(self):
        """Default decision is APPROVED."""
        result = mod.FilterResult(filter_name="test")
        assert result.decision == "APPROVED"
        assert not result.is_denied

    def test_default_requires_logging_true(self):
        """Default requires_logging is True."""
        result = mod.FilterResult(filter_name="test")
        assert result.requires_logging is True


# ===========================================================================
# TestIntegrationWrappers — all 8 wrappers instantiate without error
# ===========================================================================


class TestIntegrationWrappers:
    """Integration wrappers instantiate and handle clean docs without error."""

    def test_langchain_policy_guard_instantiates(self):
        """USStateAILangChainPolicyGuard instantiates without error."""
        guard = mod.USStateAILangChainPolicyGuard()
        assert guard is not None

    def test_langchain_policy_guard_invoke_clean(self):
        """USStateAILangChainPolicyGuard.invoke returns 4 results for clean doc."""
        guard = mod.USStateAILangChainPolicyGuard()
        results = guard.invoke(_compliant_doc())
        assert len(results) == 4

    def test_langchain_policy_guard_ainvoke_clean(self):
        """USStateAILangChainPolicyGuard.ainvoke returns 4 results for clean doc."""
        guard = mod.USStateAILangChainPolicyGuard()
        results = guard.ainvoke(_compliant_doc())
        assert len(results) == 4

    def test_langchain_policy_guard_raises_on_denied(self):
        """USStateAILangChainPolicyGuard.invoke raises PermissionError on DENIED."""
        guard = mod.USStateAILangChainPolicyGuard()
        with pytest.raises(PermissionError):
            guard.invoke({"high_risk_ai": True, "impact_assessment_completed": False})

    def test_crewai_governance_guard_instantiates(self):
        """USStateAICrewAIGovernanceGuard instantiates without error."""
        guard = mod.USStateAICrewAIGovernanceGuard()
        assert guard is not None

    def test_crewai_governance_guard_run_clean(self):
        """USStateAICrewAIGovernanceGuard._run returns 4 results for clean doc."""
        guard = mod.USStateAICrewAIGovernanceGuard()
        results = guard._run(_compliant_doc())
        assert len(results) == 4

    def test_crewai_governance_guard_raises_on_denied(self):
        """USStateAICrewAIGovernanceGuard._run raises PermissionError on DENIED."""
        guard = mod.USStateAICrewAIGovernanceGuard()
        with pytest.raises(PermissionError):
            guard._run({"biometric_identifier": True, "written_consent": False})

    def test_autogen_governed_agent_instantiates(self):
        """USStateAIAutoGenGovernedAgent instantiates without error."""
        agent = mod.USStateAIAutoGenGovernedAgent()
        assert agent is not None

    def test_autogen_governed_agent_generate_reply_clean(self):
        """USStateAIAutoGenGovernedAgent.generate_reply returns 4 results for clean doc."""
        agent = mod.USStateAIAutoGenGovernedAgent()
        results = agent.generate_reply(_compliant_doc())
        assert len(results) == 4

    def test_semantic_kernel_plugin_instantiates(self):
        """USStateAISemanticKernelPlugin instantiates without error."""
        plugin = mod.USStateAISemanticKernelPlugin()
        assert plugin is not None

    def test_semantic_kernel_plugin_enforce_clean(self):
        """USStateAISemanticKernelPlugin.enforce_governance returns 4 results for clean doc."""
        plugin = mod.USStateAISemanticKernelPlugin()
        results = plugin.enforce_governance(_compliant_doc())
        assert len(results) == 4

    def test_llama_index_workflow_guard_instantiates(self):
        """USStateAILlamaIndexWorkflowGuard instantiates without error."""
        guard = mod.USStateAILlamaIndexWorkflowGuard()
        assert guard is not None

    def test_llama_index_workflow_guard_process_event_clean(self):
        """USStateAILlamaIndexWorkflowGuard.process_event returns 4 results for clean doc."""
        guard = mod.USStateAILlamaIndexWorkflowGuard()
        results = guard.process_event(_compliant_doc())
        assert len(results) == 4

    def test_haystack_governance_component_instantiates(self):
        """USStateAIHaystackGovernanceComponent instantiates without error."""
        comp = mod.USStateAIHaystackGovernanceComponent()
        assert comp is not None

    def test_haystack_governance_component_run_clean(self):
        """USStateAIHaystackGovernanceComponent.run returns all clean docs."""
        comp = mod.USStateAIHaystackGovernanceComponent()
        result = comp.run([_compliant_doc(), _compliant_doc()])
        assert len(result["documents"]) == 2

    def test_haystack_governance_component_filters_denied(self):
        """USStateAIHaystackGovernanceComponent.run excludes DENIED documents."""
        comp = mod.USStateAIHaystackGovernanceComponent()
        denied_doc = {"high_risk_ai": True, "impact_assessment_completed": False}
        result = comp.run([_compliant_doc(), denied_doc])
        assert len(result["documents"]) == 1

    def test_dspy_governance_module_instantiates(self):
        """USStateAIDSPyGovernanceModule instantiates without error."""
        dummy_module = lambda doc, **kw: doc  # noqa: E731
        module = mod.USStateAIDSPyGovernanceModule(dummy_module)
        assert module is not None

    def test_dspy_governance_module_forward_clean(self):
        """USStateAIDSPyGovernanceModule.forward passes clean doc to wrapped module."""
        sentinel = object()
        dummy_module = lambda doc, **kw: sentinel  # noqa: E731
        module = mod.USStateAIDSPyGovernanceModule(dummy_module)
        result = module.forward(_compliant_doc())
        assert result is sentinel

    def test_dspy_governance_module_forward_raises_on_denied(self):
        """USStateAIDSPyGovernanceModule.forward raises PermissionError on DENIED."""
        dummy_module = lambda doc, **kw: doc  # noqa: E731
        module = mod.USStateAIDSPyGovernanceModule(dummy_module)
        with pytest.raises(PermissionError):
            module.forward({"child_data_ai": True})

    def test_maf_policy_middleware_instantiates(self):
        """USStateAIMAFPolicyMiddleware instantiates without error."""
        middleware = mod.USStateAIMAFPolicyMiddleware()
        assert middleware is not None

    def test_maf_policy_middleware_process_clean(self):
        """USStateAIMAFPolicyMiddleware.process calls next_handler for clean doc."""
        middleware = mod.USStateAIMAFPolicyMiddleware()
        called = []
        middleware.process(_compliant_doc(), lambda msg: called.append(msg))
        assert len(called) == 1

    def test_maf_policy_middleware_process_raises_on_denied(self):
        """USStateAIMAFPolicyMiddleware.process raises PermissionError on DENIED."""
        middleware = mod.USStateAIMAFPolicyMiddleware()
        with pytest.raises(PermissionError):
            middleware.process(
                {"automated_employment_decision": True, "human_oversight": False},
                lambda msg: None,
            )
