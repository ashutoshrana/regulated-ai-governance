"""
Tests for 21_japan_ai_governance.py — Four-layer Japan AI governance framework
covering APPI Data Protection, METI AI Principles, MHLW Medical AI, and
Cabinet Office AI Strategy.
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
    spec = importlib.util.spec_from_file_location(
        "japan_ai_governance_21",
        os.path.join(os.path.dirname(__file__), "..", "examples", "21_japan_ai_governance.py"),
    )
    mod = types.ModuleType("japan_ai_governance_21")
    sys.modules["japan_ai_governance_21"] = mod
    spec.loader.exec_module(mod)
    return mod


mod = _load()


# ---------------------------------------------------------------------------
# Helper factories
# ---------------------------------------------------------------------------


def _ctx(**overrides):
    """Return a fully-compliant LOW-risk GENERAL-sector context."""
    defaults = dict(
        user_id="u1",
        sector=mod.JapanSector.GENERAL,
        ai_risk_level=mod.JapanAIRiskLevel.LOW,
        is_automated_decision=False,
        involves_personal_information=False,
        involves_sensitive_personal_info=False,
        has_appi_consent=True,
        has_third_party_provision_basis=True,
        is_cross_border_transfer=False,
        transfer_to_adequate_country=False,
        is_medical_ai=False,
        has_physician_oversight=False,
        is_public_sector_ai=False,
        human_oversight_available=True,
        explainability_available=True,
        fairness_testing_done=True,
        accountability_chain_defined=True,
        has_ai_safety_assessment=True,
        audit_trail_enabled=True,
        data_minimization_applied=True,
    )
    defaults.update(overrides)
    return mod.JapanAIContext(**defaults)


def _doc(**overrides):
    """Return a minimal, non-sensitive document."""
    defaults = dict(
        document_id="d1",
        contains_personal_information=False,
        contains_sensitive_personal_info=False,
        data_classification="INTERNAL",
        is_medical_data=False,
        is_government_data=False,
        requires_human_decision=False,
    )
    defaults.update(overrides)
    return mod.JapanAIDocument(**defaults)


# ===========================================================================
# TestAPPIDataProtectionFilter
# ===========================================================================


class TestAPPIDataProtectionFilter:
    """Layer 1: APPI (Act on the Protection of Personal Information, 2022 amendments)."""

    def _eval(self, ctx, doc=None):
        if doc is None:
            doc = _doc()
        return mod.APPIDataProtectionFilter().evaluate(ctx, doc)

    def test_sensitive_pi_without_consent_denied(self):
        """Sensitive PI + no APPI consent → DENIED (APPI Art. 20-2)."""
        ctx = _ctx(involves_sensitive_personal_info=True, has_appi_consent=False)
        result = self._eval(ctx)
        assert result.decision == mod.JapanAIDecision.DENIED
        assert result.is_denied

    def test_sensitive_pi_without_consent_cites_article_20_2(self):
        """Sensitive PI denial cites Article 20-2."""
        ctx = _ctx(involves_sensitive_personal_info=True, has_appi_consent=False)
        result = self._eval(ctx)
        assert "20-2" in result.regulation_citation or "20" in result.regulation_citation

    def test_personal_info_without_third_party_basis_denied(self):
        """Personal info + no third-party provision basis + no consent → DENIED (Art. 27)."""
        ctx = _ctx(
            involves_personal_information=True,
            has_third_party_provision_basis=False,
            has_appi_consent=False,
        )
        result = self._eval(ctx)
        assert result.decision == mod.JapanAIDecision.DENIED
        assert result.is_denied

    def test_personal_info_without_third_party_basis_cites_article_27(self):
        """Third-party provision denial cites Article 27."""
        ctx = _ctx(
            involves_personal_information=True,
            has_third_party_provision_basis=False,
            has_appi_consent=False,
        )
        result = self._eval(ctx)
        assert "27" in result.regulation_citation

    def test_cross_border_to_non_adequate_country_denied(self):
        """Cross-border transfer + not adequate country → DENIED (Art. 28)."""
        ctx = _ctx(is_cross_border_transfer=True, transfer_to_adequate_country=False)
        result = self._eval(ctx)
        assert result.decision == mod.JapanAIDecision.DENIED
        assert result.is_denied

    def test_document_has_sensitive_pi_context_does_not_redacted(self):
        """Document has sensitive PI but context does not declare it → REDACTED."""
        ctx = _ctx(involves_sensitive_personal_info=False)
        doc = _doc(contains_sensitive_personal_info=True)
        result = self._eval(ctx, doc)
        assert result.decision == mod.JapanAIDecision.REDACTED
        assert not result.is_denied

    def test_no_data_minimization_high_risk_requires_human_review(self):
        """No data minimization + HIGH risk → REQUIRES_HUMAN_REVIEW."""
        ctx = _ctx(
            data_minimization_applied=False,
            ai_risk_level=mod.JapanAIRiskLevel.HIGH,
        )
        result = self._eval(ctx)
        assert result.decision == mod.JapanAIDecision.REQUIRES_HUMAN_REVIEW
        assert not result.is_denied

    def test_all_compliant_low_risk_approved(self):
        """All compliant, LOW risk → APPROVED."""
        ctx = _ctx()
        result = self._eval(ctx)
        assert result.decision == mod.JapanAIDecision.APPROVED
        assert not result.is_denied

    def test_cross_border_to_adequate_country_approved(self):
        """Cross-border transfer to adequate country → APPROVED."""
        ctx = _ctx(is_cross_border_transfer=True, transfer_to_adequate_country=True)
        result = self._eval(ctx)
        assert result.decision == mod.JapanAIDecision.APPROVED
        assert not result.is_denied

    def test_is_denied_false_for_redacted(self):
        """is_denied is False for REDACTED (not DENIED)."""
        ctx = _ctx(involves_sensitive_personal_info=False)
        doc = _doc(contains_sensitive_personal_info=True)
        result = self._eval(ctx, doc)
        assert result.decision == mod.JapanAIDecision.REDACTED
        assert not result.is_denied


# ===========================================================================
# TestMETIAIPrinciplesFilter
# ===========================================================================


class TestMETIAIPrinciplesFilter:
    """Layer 2: METI AI Governance Guidelines v1.1 (July 2022)."""

    def _eval(self, ctx, doc=None):
        if doc is None:
            doc = _doc()
        return mod.METIAIPrinciplesFilter().evaluate(ctx, doc)

    def test_high_risk_automated_no_human_oversight_denied(self):
        """HIGH risk + automated decision + no human oversight → DENIED."""
        ctx = _ctx(
            ai_risk_level=mod.JapanAIRiskLevel.HIGH,
            is_automated_decision=True,
            human_oversight_available=False,
        )
        result = self._eval(ctx)
        assert result.decision == mod.JapanAIDecision.DENIED
        assert result.is_denied

    def test_automated_no_explainability_requires_human_review(self):
        """Automated decision + no explainability → REQUIRES_HUMAN_REVIEW."""
        ctx = _ctx(
            is_automated_decision=True,
            explainability_available=False,
            human_oversight_available=True,
        )
        result = self._eval(ctx)
        assert result.decision == mod.JapanAIDecision.REQUIRES_HUMAN_REVIEW
        assert not result.is_denied

    def test_high_risk_no_fairness_testing_requires_human_review(self):
        """HIGH risk + no fairness testing → REQUIRES_HUMAN_REVIEW."""
        ctx = _ctx(
            ai_risk_level=mod.JapanAIRiskLevel.HIGH,
            fairness_testing_done=False,
        )
        result = self._eval(ctx)
        assert result.decision == mod.JapanAIDecision.REQUIRES_HUMAN_REVIEW
        assert not result.is_denied

    def test_high_risk_no_accountability_chain_requires_human_review(self):
        """HIGH risk + no accountability chain → REQUIRES_HUMAN_REVIEW."""
        ctx = _ctx(
            ai_risk_level=mod.JapanAIRiskLevel.HIGH,
            accountability_chain_defined=False,
        )
        result = self._eval(ctx)
        assert result.decision == mod.JapanAIDecision.REQUIRES_HUMAN_REVIEW
        assert not result.is_denied

    def test_high_risk_no_safety_assessment_requires_human_review(self):
        """HIGH risk + no safety assessment → REQUIRES_HUMAN_REVIEW."""
        ctx = _ctx(
            ai_risk_level=mod.JapanAIRiskLevel.HIGH,
            has_ai_safety_assessment=False,
        )
        result = self._eval(ctx)
        assert result.decision == mod.JapanAIDecision.REQUIRES_HUMAN_REVIEW
        assert not result.is_denied

    def test_all_compliant_low_risk_approved(self):
        """All compliant, LOW risk → APPROVED."""
        ctx = _ctx()
        result = self._eval(ctx)
        assert result.decision == mod.JapanAIDecision.APPROVED
        assert not result.is_denied

    def test_medium_risk_no_fairness_testing_requires_human_review(self):
        """MEDIUM risk + no fairness testing → REQUIRES_HUMAN_REVIEW."""
        ctx = _ctx(
            ai_risk_level=mod.JapanAIRiskLevel.MEDIUM,
            fairness_testing_done=False,
        )
        result = self._eval(ctx)
        assert result.decision == mod.JapanAIDecision.REQUIRES_HUMAN_REVIEW
        assert not result.is_denied

    def test_regulation_citation_mentions_meti(self):
        """Denial regulation_citation mentions METI."""
        ctx = _ctx(
            ai_risk_level=mod.JapanAIRiskLevel.HIGH,
            is_automated_decision=True,
            human_oversight_available=False,
        )
        result = self._eval(ctx)
        assert "METI" in result.regulation_citation


# ===========================================================================
# TestMHLWMedicalAIFilter
# ===========================================================================


class TestMHLWMedicalAIFilter:
    """Layer 3: MHLW AI Guidelines for Medical Institutions."""

    def _eval(self, ctx, doc=None):
        if doc is None:
            doc = _doc()
        return mod.MHLWMedicalAIFilter().evaluate(ctx, doc)

    def test_not_medical_ai_approved(self):
        """Non-medical AI → APPROVED (MHLW not applicable)."""
        ctx = _ctx(is_medical_ai=False)
        result = self._eval(ctx)
        assert result.decision == mod.JapanAIDecision.APPROVED
        assert not result.is_denied

    def test_medical_ai_no_physician_oversight_denied(self):
        """Medical AI + no physician oversight → DENIED."""
        ctx = _ctx(is_medical_ai=True, has_physician_oversight=False)
        result = self._eval(ctx)
        assert result.decision == mod.JapanAIDecision.DENIED
        assert result.is_denied

    def test_medical_ai_medical_data_no_audit_trail_requires_human_review(self):
        """Medical AI + medical data + no audit trail → REQUIRES_HUMAN_REVIEW."""
        ctx = _ctx(
            is_medical_ai=True,
            has_physician_oversight=True,
            audit_trail_enabled=False,
        )
        doc = _doc(is_medical_data=True)
        result = self._eval(ctx, doc)
        assert result.decision == mod.JapanAIDecision.REQUIRES_HUMAN_REVIEW
        assert not result.is_denied

    def test_medical_ai_no_explainability_requires_human_review(self):
        """Medical AI + no explainability → REQUIRES_HUMAN_REVIEW."""
        ctx = _ctx(
            is_medical_ai=True,
            has_physician_oversight=True,
            explainability_available=False,
        )
        result = self._eval(ctx)
        assert result.decision == mod.JapanAIDecision.REQUIRES_HUMAN_REVIEW
        assert not result.is_denied

    def test_medical_ai_all_compliant_approved(self):
        """Medical AI + all controls satisfied → APPROVED."""
        ctx = _ctx(
            is_medical_ai=True,
            has_physician_oversight=True,
            audit_trail_enabled=True,
            explainability_available=True,
        )
        result = self._eval(ctx)
        assert result.decision == mod.JapanAIDecision.APPROVED
        assert not result.is_denied

    def test_is_denied_false_for_requires_human_review(self):
        """is_denied is False for REQUIRES_HUMAN_REVIEW."""
        ctx = _ctx(
            is_medical_ai=True,
            has_physician_oversight=True,
            explainability_available=False,
        )
        result = self._eval(ctx)
        assert result.decision == mod.JapanAIDecision.REQUIRES_HUMAN_REVIEW
        assert not result.is_denied


# ===========================================================================
# TestCabinetOfficeAIStrategyFilter
# ===========================================================================


class TestCabinetOfficeAIStrategyFilter:
    """Layer 4: Cabinet Office Social Principles of Human-Centric AI (2019)."""

    def _eval(self, ctx, doc=None):
        if doc is None:
            doc = _doc()
        return mod.CabinetOfficeAIStrategyFilter().evaluate(ctx, doc)

    def test_non_public_sector_low_risk_approved(self):
        """Non-public-sector + LOW risk → APPROVED."""
        ctx = _ctx(is_public_sector_ai=False, ai_risk_level=mod.JapanAIRiskLevel.LOW)
        result = self._eval(ctx)
        assert result.decision == mod.JapanAIDecision.APPROVED
        assert not result.is_denied

    def test_public_sector_no_human_oversight_denied(self):
        """Public sector + no human oversight → DENIED."""
        ctx = _ctx(is_public_sector_ai=True, human_oversight_available=False)
        result = self._eval(ctx)
        assert result.decision == mod.JapanAIDecision.DENIED
        assert result.is_denied

    def test_public_sector_no_audit_trail_requires_human_review(self):
        """Public sector + no audit trail → REQUIRES_HUMAN_REVIEW."""
        ctx = _ctx(
            is_public_sector_ai=True,
            human_oversight_available=True,
            audit_trail_enabled=False,
        )
        result = self._eval(ctx)
        assert result.decision == mod.JapanAIDecision.REQUIRES_HUMAN_REVIEW
        assert not result.is_denied

    def test_public_sector_no_fairness_testing_requires_human_review(self):
        """Public sector + no fairness testing → REQUIRES_HUMAN_REVIEW."""
        ctx = _ctx(
            is_public_sector_ai=True,
            human_oversight_available=True,
            audit_trail_enabled=True,
            fairness_testing_done=False,
        )
        result = self._eval(ctx)
        assert result.decision == mod.JapanAIDecision.REQUIRES_HUMAN_REVIEW
        assert not result.is_denied

    def test_public_sector_all_compliant_approved(self):
        """Public sector + all controls satisfied → APPROVED."""
        ctx = _ctx(
            is_public_sector_ai=True,
            human_oversight_available=True,
            audit_trail_enabled=True,
            fairness_testing_done=True,
        )
        result = self._eval(ctx)
        assert result.decision == mod.JapanAIDecision.APPROVED
        assert not result.is_denied

    def test_regulation_citation_mentions_cabinet_office(self):
        """Denial regulation_citation mentions Cabinet Office."""
        ctx = _ctx(is_public_sector_ai=True, human_oversight_available=False)
        result = self._eval(ctx)
        assert "Cabinet Office" in result.regulation_citation


# ===========================================================================
# TestJapanAIGovernanceReport
# ===========================================================================


class TestJapanAIGovernanceReport:
    """Aggregated JapanAIGovernanceReport via the orchestrator."""

    def _evaluate(self, ctx, doc=None):
        if doc is None:
            doc = _doc()
        orchestrator = mod.JapanAIGovernanceOrchestrator()
        results = orchestrator.evaluate(ctx, doc)
        return mod.JapanAIGovernanceReport(
            context=ctx, document=doc, filter_results=results
        )

    def test_any_filter_denied_overall_denied(self):
        """If any filter returns DENIED, overall_decision is DENIED."""
        # Sensitive PI without consent triggers APPI DENIED
        ctx = _ctx(involves_sensitive_personal_info=True, has_appi_consent=False)
        report = self._evaluate(ctx)
        assert report.overall_decision == mod.JapanAIDecision.DENIED

    def test_no_denied_but_review_overall_requires_human_review(self):
        """No DENIED but at least one REQUIRES_HUMAN_REVIEW → REQUIRES_HUMAN_REVIEW."""
        # No data minimization on MEDIUM risk triggers REQUIRES_HUMAN_REVIEW in APPI
        ctx = _ctx(
            data_minimization_applied=False,
            ai_risk_level=mod.JapanAIRiskLevel.MEDIUM,
        )
        report = self._evaluate(ctx)
        assert report.overall_decision == mod.JapanAIDecision.REQUIRES_HUMAN_REVIEW

    def test_all_approved_overall_approved(self):
        """All filters APPROVED → overall_decision is APPROVED."""
        ctx = _ctx()
        report = self._evaluate(ctx)
        assert report.overall_decision == mod.JapanAIDecision.APPROVED

    def test_is_compliant_false_when_denied(self):
        """is_compliant is False when any filter is DENIED."""
        ctx = _ctx(involves_sensitive_personal_info=True, has_appi_consent=False)
        report = self._evaluate(ctx)
        assert not report.is_compliant
