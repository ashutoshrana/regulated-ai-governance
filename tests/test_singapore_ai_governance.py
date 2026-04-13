"""
Tests for 20_singapore_ai_governance.py — Four-layer Singapore AI governance
framework covering PDPC Model AI Governance, PDPA, MAS FEAT, and IMDA Testing.
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
        "singapore_ai_governance_20",
        os.path.join(os.path.dirname(__file__), "..", "examples", "20_singapore_ai_governance.py"),
    )
    mod = types.ModuleType("singapore_ai_governance_20")
    sys.modules["singapore_ai_governance_20"] = mod
    spec.loader.exec_module(mod)
    return mod


mod = _load()


# ---------------------------------------------------------------------------
# Helper factories
# ---------------------------------------------------------------------------


def _base_ctx(**overrides):
    """Return a fully-compliant LOW-risk GENERAL-sector context."""
    defaults = dict(
        user_id="u1",
        sector=mod.SingaporeSector.GENERAL,
        ai_risk_level=mod.SingaporeAIRiskLevel.LOW,
        is_automated_decision=False,
        involves_personal_data=False,
        has_pdpa_consent=True,
        has_data_protection_officer=True,
        is_financial_institution=False,
        has_mas_approval=False,
        is_government_system=False,
        has_ai_impact_assessment=True,
        explainability_available=True,
        audit_trail_enabled=True,
        bias_testing_done=True,
        human_review_available=True,
        is_cross_border_transfer=False,
        transfer_adequate_protection=False,
        model_registered=True,
    )
    defaults.update(overrides)
    return mod.SingaporeAIContext(**defaults)


def _base_doc(**overrides):
    """Return a minimal, non-sensitive document."""
    defaults = dict(
        document_id="d1",
        contains_personal_data=False,
        data_classification="INTERNAL",
        is_financial_data=False,
        is_health_data=False,
        is_government_data=False,
        requires_human_decision=False,
    )
    defaults.update(overrides)
    return mod.SingaporeAIDocument(**defaults)


# Convenience shorthands for HIGH-risk compliant contexts
def _high_ctx(**overrides):
    """HIGH-risk, fully compliant context."""
    base = dict(
        ai_risk_level=mod.SingaporeAIRiskLevel.HIGH,
        is_automated_decision=True,
        has_ai_impact_assessment=True,
        explainability_available=True,
        audit_trail_enabled=True,
        human_review_available=True,
        bias_testing_done=True,
        model_registered=True,
    )
    base.update(overrides)
    return _base_ctx(**base)


def _financial_ctx(**overrides):
    """HIGH-risk, FINANCIAL_SERVICES sector, fully compliant."""
    base = dict(
        sector=mod.SingaporeSector.FINANCIAL_SERVICES,
        ai_risk_level=mod.SingaporeAIRiskLevel.HIGH,
        is_automated_decision=True,
        is_financial_institution=True,
        has_mas_approval=True,
        explainability_available=True,
        audit_trail_enabled=True,
        has_ai_impact_assessment=True,
        human_review_available=True,
        bias_testing_done=True,
        model_registered=True,
    )
    base.update(overrides)
    return _base_ctx(**base)


# ===========================================================================
# TestPDPCModelAIGovernanceFilter
# ===========================================================================


class TestPDPCModelAIGovernanceFilter:
    """Layer 1: PDPC Model AI Governance Framework v2 (2020)."""

    def _eval(self, ctx, doc=None):
        if doc is None:
            doc = _base_doc()
        return mod.PDPCModelAIGovernanceFilter().evaluate(ctx, doc)

    def test_high_risk_automated_no_human_review_denied(self):
        """HIGH risk + automated decision + no human review → DENIED."""
        ctx = _high_ctx(human_review_available=False)
        result = self._eval(ctx)
        assert result.is_denied
        assert result.decision == mod.SingaporeAIDecision.DENIED

    def test_high_risk_automated_no_human_review_cites_pdpc(self):
        """Denial for missing human review cites PDPC in regulation_citation."""
        ctx = _high_ctx(human_review_available=False)
        result = self._eval(ctx)
        assert "PDPC" in result.regulation_citation

    def test_automated_no_explainability_requires_human_review(self):
        """Automated decision + no explainability → REQUIRES_HUMAN_REVIEW."""
        ctx = _base_ctx(
            ai_risk_level=mod.SingaporeAIRiskLevel.MEDIUM,
            is_automated_decision=True,
            explainability_available=False,
            audit_trail_enabled=True,
            human_review_available=True,
        )
        result = self._eval(ctx)
        assert result.decision == mod.SingaporeAIDecision.REQUIRES_HUMAN_REVIEW
        assert not result.is_denied

    def test_automated_no_explainability_cites_pdpc(self):
        """REQUIRES_HUMAN_REVIEW for explainability gap cites PDPC."""
        ctx = _base_ctx(
            ai_risk_level=mod.SingaporeAIRiskLevel.MEDIUM,
            is_automated_decision=True,
            explainability_available=False,
            audit_trail_enabled=True,
            human_review_available=True,
        )
        result = self._eval(ctx)
        assert "PDPC" in result.regulation_citation

    def test_medium_risk_no_audit_trail_requires_human_review(self):
        """MEDIUM risk + no audit trail → REQUIRES_HUMAN_REVIEW."""
        ctx = _base_ctx(
            ai_risk_level=mod.SingaporeAIRiskLevel.MEDIUM,
            audit_trail_enabled=False,
        )
        result = self._eval(ctx)
        assert result.decision == mod.SingaporeAIDecision.REQUIRES_HUMAN_REVIEW

    def test_high_risk_no_ai_impact_assessment_requires_human_review(self):
        """HIGH risk + no AI impact assessment → REQUIRES_HUMAN_REVIEW."""
        ctx = _high_ctx(has_ai_impact_assessment=False)
        result = self._eval(ctx)
        assert result.decision == mod.SingaporeAIDecision.REQUIRES_HUMAN_REVIEW

    def test_low_risk_all_compliant_approved(self):
        """LOW risk, all controls satisfied → APPROVED."""
        ctx = _base_ctx()
        result = self._eval(ctx)
        assert result.decision == mod.SingaporeAIDecision.APPROVED
        assert not result.is_denied

    def test_high_risk_automated_all_compliant_approved(self):
        """HIGH risk + automated + all controls satisfied → APPROVED."""
        ctx = _high_ctx()
        result = self._eval(ctx)
        assert result.decision == mod.SingaporeAIDecision.APPROVED
        assert not result.is_denied


# ===========================================================================
# TestPDPADataProtectionFilter
# ===========================================================================


class TestPDPADataProtectionFilter:
    """Layer 2: Personal Data Protection Act 2012 (PDPA)."""

    def _eval(self, ctx, doc=None):
        if doc is None:
            doc = _base_doc()
        return mod.PDPADataProtectionFilter().evaluate(ctx, doc)

    def test_personal_data_without_consent_denied(self):
        """Personal data involved + no consent → DENIED."""
        ctx = _base_ctx(involves_personal_data=True, has_pdpa_consent=False)
        result = self._eval(ctx)
        assert result.is_denied
        assert result.decision == mod.SingaporeAIDecision.DENIED

    def test_personal_data_without_consent_cites_pdpa(self):
        """Denial for missing consent references PDPA or Personal Data Protection Act."""
        ctx = _base_ctx(involves_personal_data=True, has_pdpa_consent=False)
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "PDPA" in combined or "Personal Data Protection Act" in combined

    def test_cross_border_without_adequate_protection_denied(self):
        """Cross-border transfer + no adequate protection → DENIED."""
        ctx = _base_ctx(
            is_cross_border_transfer=True,
            transfer_adequate_protection=False,
        )
        result = self._eval(ctx)
        assert result.is_denied
        assert result.decision == mod.SingaporeAIDecision.DENIED

    def test_cross_border_denial_cites_pdpa(self):
        """Denial for cross-border transfer references PDPA or Personal Data Protection Act."""
        ctx = _base_ctx(
            is_cross_border_transfer=True,
            transfer_adequate_protection=False,
        )
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "PDPA" in combined or "Personal Data Protection Act" in combined

    def test_document_has_personal_data_context_does_not_redacted(self):
        """Document has personal data but context does not declare it → REDACTED."""
        ctx = _base_ctx(involves_personal_data=False)
        doc = _base_doc(contains_personal_data=True)
        result = self._eval(ctx, doc)
        assert result.decision == mod.SingaporeAIDecision.REDACTED
        # REDACTED is not DENIED
        assert not result.is_denied

    def test_low_risk_no_personal_data_approved(self):
        """No personal data, no cross-border → APPROVED."""
        ctx = _base_ctx(involves_personal_data=False)
        result = self._eval(ctx)
        assert result.decision == mod.SingaporeAIDecision.APPROVED
        assert not result.is_denied

    def test_personal_data_with_consent_no_cross_border_approved(self):
        """Personal data + consent + no cross-border → APPROVED."""
        ctx = _base_ctx(
            involves_personal_data=True,
            has_pdpa_consent=True,
            sector=mod.SingaporeSector.GENERAL,
            has_data_protection_officer=True,
            is_cross_border_transfer=False,
        )
        result = self._eval(ctx)
        assert result.decision == mod.SingaporeAIDecision.APPROVED

    def test_non_general_sector_personal_data_no_dpo_requires_review(self):
        """Non-GENERAL sector + personal data + no DPO → REQUIRES_HUMAN_REVIEW."""
        ctx = _base_ctx(
            sector=mod.SingaporeSector.HEALTHCARE,
            involves_personal_data=True,
            has_pdpa_consent=True,
            has_data_protection_officer=False,
        )
        result = self._eval(ctx)
        assert result.decision == mod.SingaporeAIDecision.REQUIRES_HUMAN_REVIEW
        assert not result.is_denied


# ===========================================================================
# TestMASFEATFilter
# ===========================================================================


class TestMASFEATFilter:
    """Layer 3: MAS FEAT Principles — financial institutions only."""

    def _eval(self, ctx, doc=None):
        if doc is None:
            doc = _base_doc()
        return mod.MASFEATFilter().evaluate(ctx, doc)

    def test_non_financial_institution_approved(self):
        """Non-financial institution → APPROVED (FEAT not applicable)."""
        ctx = _base_ctx(is_financial_institution=False)
        result = self._eval(ctx)
        assert result.decision == mod.SingaporeAIDecision.APPROVED
        assert not result.is_denied

    def test_financial_no_bias_testing_denied(self):
        """Financial institution + no bias testing → DENIED (F.1)."""
        ctx = _financial_ctx(bias_testing_done=False)
        result = self._eval(ctx)
        assert result.is_denied
        assert result.decision == mod.SingaporeAIDecision.DENIED

    def test_financial_no_bias_testing_cites_mas_feat(self):
        """Denial for missing bias testing cites MAS FEAT."""
        ctx = _financial_ctx(bias_testing_done=False)
        result = self._eval(ctx)
        assert "MAS FEAT" in result.regulation_citation or "FEAT" in result.regulation_citation

    def test_financial_high_risk_no_explainability_denied(self):
        """Financial institution + HIGH risk + no explainability → DENIED (T.1)."""
        ctx = _financial_ctx(
            ai_risk_level=mod.SingaporeAIRiskLevel.HIGH,
            explainability_available=False,
        )
        result = self._eval(ctx)
        assert result.is_denied
        assert result.decision == mod.SingaporeAIDecision.DENIED

    def test_financial_high_risk_no_mas_approval_requires_review(self):
        """Financial institution + HIGH risk + no MAS approval → REQUIRES_HUMAN_REVIEW (A.2)."""
        ctx = _financial_ctx(
            ai_risk_level=mod.SingaporeAIRiskLevel.HIGH,
            has_mas_approval=False,
        )
        result = self._eval(ctx)
        assert result.decision == mod.SingaporeAIDecision.REQUIRES_HUMAN_REVIEW
        assert not result.is_denied

    def test_financial_medium_risk_no_explainability_denied(self):
        """Financial institution + MEDIUM risk + no explainability → DENIED (T.1)."""
        ctx = _financial_ctx(
            ai_risk_level=mod.SingaporeAIRiskLevel.MEDIUM,
            explainability_available=False,
        )
        result = self._eval(ctx)
        assert result.is_denied

    def test_financial_all_compliant_approved(self):
        """Financial institution + all FEAT requirements satisfied → APPROVED."""
        ctx = _financial_ctx()
        result = self._eval(ctx)
        assert result.decision == mod.SingaporeAIDecision.APPROVED
        assert not result.is_denied


# ===========================================================================
# TestIMDATestingFilter
# ===========================================================================


class TestIMDATestingFilter:
    """Layer 4: IMDA AI Testing Framework (AI Verify)."""

    def _eval(self, ctx, doc=None):
        if doc is None:
            doc = _base_doc()
        return mod.IMDATestingFilter().evaluate(ctx, doc)

    def test_high_risk_not_registered_requires_review(self):
        """HIGH risk + not model_registered → REQUIRES_HUMAN_REVIEW."""
        ctx = _high_ctx(model_registered=False)
        result = self._eval(ctx)
        assert result.decision == mod.SingaporeAIDecision.REQUIRES_HUMAN_REVIEW
        assert not result.is_denied

    def test_document_requires_human_decision_automated_no_review_denied(self):
        """Document requires human decision + automated + no human review → DENIED."""
        ctx = _base_ctx(
            ai_risk_level=mod.SingaporeAIRiskLevel.HIGH,
            is_automated_decision=True,
            human_review_available=False,
            has_ai_impact_assessment=True,
            explainability_available=True,
            audit_trail_enabled=True,
            bias_testing_done=True,
            model_registered=True,
        )
        doc = _base_doc(requires_human_decision=True)
        result = self._eval(ctx, doc)
        assert result.is_denied
        assert result.decision == mod.SingaporeAIDecision.DENIED

    def test_medium_risk_no_bias_testing_requires_review(self):
        """MEDIUM risk + no bias testing → REQUIRES_HUMAN_REVIEW."""
        ctx = _base_ctx(
            ai_risk_level=mod.SingaporeAIRiskLevel.MEDIUM,
            bias_testing_done=False,
            model_registered=True,
        )
        result = self._eval(ctx)
        assert result.decision == mod.SingaporeAIDecision.REQUIRES_HUMAN_REVIEW

    def test_low_risk_all_defaults_approved(self):
        """LOW risk + all defaults → APPROVED."""
        ctx = _base_ctx()
        result = self._eval(ctx)
        assert result.decision == mod.SingaporeAIDecision.APPROVED
        assert not result.is_denied

    def test_denied_is_denied_true(self):
        """is_denied is True only for DENIED decisions."""
        ctx = _base_ctx(
            ai_risk_level=mod.SingaporeAIRiskLevel.HIGH,
            is_automated_decision=True,
            human_review_available=False,
            has_ai_impact_assessment=True,
            explainability_available=True,
            audit_trail_enabled=True,
            bias_testing_done=True,
            model_registered=True,
        )
        doc = _base_doc(requires_human_decision=True)
        result = self._eval(ctx, doc)
        assert result.is_denied


# ===========================================================================
# TestSingaporeAIGovernanceReport
# ===========================================================================


class TestSingaporeAIGovernanceReport:
    """Aggregated SingaporeAIGovernanceReport via the orchestrator."""

    def _evaluate(self, ctx, doc=None):
        if doc is None:
            doc = _base_doc()
        orchestrator = mod.SingaporeAIGovernanceOrchestrator()
        results = orchestrator.evaluate(ctx, doc)
        return mod.SingaporeAIGovernanceReport(
            context=ctx, document=doc, filter_results=results
        )

    def test_any_filter_denied_overall_denied(self):
        """If any filter returns DENIED, overall_decision is DENIED."""
        ctx = _base_ctx(involves_personal_data=True, has_pdpa_consent=False)
        report = self._evaluate(ctx)
        assert report.overall_decision == mod.SingaporeAIDecision.DENIED

    def test_no_denial_but_review_required_overall_requires_review(self):
        """No DENIED but at least one REQUIRES_HUMAN_REVIEW → REQUIRES_HUMAN_REVIEW."""
        ctx = _base_ctx(
            ai_risk_level=mod.SingaporeAIRiskLevel.MEDIUM,
            audit_trail_enabled=False,
        )
        report = self._evaluate(ctx)
        assert report.overall_decision == mod.SingaporeAIDecision.REQUIRES_HUMAN_REVIEW

    def test_all_approved_overall_approved(self):
        """All filters APPROVED → overall_decision is APPROVED."""
        ctx = _base_ctx()
        report = self._evaluate(ctx)
        assert report.overall_decision == mod.SingaporeAIDecision.APPROVED

    def test_is_compliant_false_when_denied(self):
        """is_compliant is False when any filter is DENIED."""
        ctx = _base_ctx(involves_personal_data=True, has_pdpa_consent=False)
        report = self._evaluate(ctx)
        assert not report.is_compliant
