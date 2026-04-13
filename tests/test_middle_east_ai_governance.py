"""
Tests for 25_middle_east_ai_governance.py — Four-layer Middle East (GCC) AI
governance framework covering UAE PDPL + AI Ethics Principles (2019), Saudi
PDPL + NDMO + SAMA/SFDA, Qatar PDPA + National AI Strategy 2030, and GCC
Cross-Border Data Transfer Framework.
"""

from __future__ import annotations

import importlib.util
import os
import sys
import types

# ---------------------------------------------------------------------------
# Module loader
# ---------------------------------------------------------------------------


def _load():
    _name = "middle_east_ai_governance_25"
    spec = importlib.util.spec_from_file_location(
        _name,
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "examples",
            "25_middle_east_ai_governance.py",
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


def _base_ctx(**overrides):
    """Return a fully-compliant LOW-risk UAE GENERAL context."""
    defaults = dict(
        user_id="u1",
        jurisdiction=mod.MiddleEastJurisdiction.UAE,
        sector=mod.MiddleEastSector.GENERAL,
        ai_risk_level=mod.MiddleEastAIRiskLevel.LOW,
        is_automated_decision=False,
        involves_personal_data=False,
        has_data_subject_consent=True,
        processing_purpose="service_delivery",
        is_uae_pdpl_subject=True,
        has_uae_consent=True,
        uae_dpo_appointed=True,
        is_saudi_pdpl_subject=False,
        has_saudi_consent=False,
        saudi_data_classified=True,
        is_qatar_pdpa_subject=False,
        has_qatar_consent=False,
        is_cross_border_transfer=False,
        transfer_destination_jurisdiction="",
        is_high_impact_ai=False,
        ai_transparency_disclosed=True,
        involves_biometric_data=False,
        has_biometric_consent=False,
        is_financial_ai=False,
        has_cbuae_approval=False,
        has_sama_approval=False,
        is_medical_ai=False,
        has_doh_approval=False,
        has_sfda_approval=False,
        profiling_involved=False,
        right_to_explanation_provided=True,
    )
    defaults.update(overrides)
    return mod.MiddleEastAIContext(**defaults)


def _base_doc(**overrides):
    """Return a minimal, non-sensitive document."""
    defaults = dict(
        document_id="d1",
        content_type="REPORT",
        contains_personal_data=False,
        risk_level="LOW",
        requires_human_review=False,
        processing_timestamp="2025-06-01T10:00:00+04:00",
        jurisdiction="UAE",
    )
    defaults.update(overrides)
    return mod.MiddleEastAIDocument(**defaults)


# ===========================================================================
# TestUAEAIFilter
# ===========================================================================


class TestUAEAIFilter:
    """Layer 1: UAE PDPL Federal Decree-Law No. 45/2021 + UAE AI Ethics 2019."""

    def _eval(self, ctx, doc=None):
        if doc is None:
            doc = _base_doc()
        return mod.UAEAIFilter().evaluate(ctx, doc)

    def test_non_uae_jurisdiction_approved(self):
        """Non-UAE jurisdiction → APPROVED (filter not triggered)."""
        ctx = _base_ctx(
            jurisdiction=mod.MiddleEastJurisdiction.QATAR,
            is_uae_pdpl_subject=True,
        )
        result = self._eval(ctx)
        assert result.decision == "APPROVED"
        assert not result.is_denied

    def test_not_uae_pdpl_subject_approved(self):
        """Not UAE PDPL subject → APPROVED regardless of other fields."""
        ctx = _base_ctx(
            jurisdiction=mod.MiddleEastJurisdiction.UAE,
            is_uae_pdpl_subject=False,
            involves_personal_data=True,
            has_uae_consent=False,
        )
        result = self._eval(ctx)
        assert result.decision == "APPROVED"
        assert not result.is_denied

    def test_no_consent_no_lawful_basis_denied(self):
        """Personal data + no UAE consent + no lawful basis → DENIED."""
        ctx = _base_ctx(
            jurisdiction=mod.MiddleEastJurisdiction.UAE,
            is_uae_pdpl_subject=True,
            involves_personal_data=True,
            has_uae_consent=False,
            processing_purpose="marketing",
        )
        result = self._eval(ctx)
        assert result.is_denied
        assert result.decision == "DENIED"

    def test_no_consent_denied_cites_article_7(self):
        """No consent denial cites UAE PDPL Article 7."""
        ctx = _base_ctx(
            jurisdiction=mod.MiddleEastJurisdiction.UAE,
            is_uae_pdpl_subject=True,
            involves_personal_data=True,
            has_uae_consent=False,
            processing_purpose="marketing",
        )
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "7" in combined or "Article 7" in combined

    def test_biometric_no_consent_denied(self):
        """Biometric data + no biometric consent → DENIED."""
        ctx = _base_ctx(
            jurisdiction=mod.MiddleEastJurisdiction.UAE,
            is_uae_pdpl_subject=True,
            involves_biometric_data=True,
            has_biometric_consent=False,
        )
        result = self._eval(ctx)
        assert result.is_denied
        assert result.decision == "DENIED"

    def test_biometric_no_consent_cites_article_10(self):
        """Biometric denial cites UAE PDPL Article 10."""
        ctx = _base_ctx(
            jurisdiction=mod.MiddleEastJurisdiction.UAE,
            is_uae_pdpl_subject=True,
            involves_biometric_data=True,
            has_biometric_consent=False,
        )
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "10" in combined or "Article 10" in combined

    def test_high_impact_no_transparency_requires_human_review(self):
        """High-impact AI + no transparency → REQUIRES_HUMAN_REVIEW."""
        ctx = _base_ctx(
            jurisdiction=mod.MiddleEastJurisdiction.UAE,
            is_uae_pdpl_subject=True,
            is_high_impact_ai=True,
            ai_transparency_disclosed=False,
        )
        result = self._eval(ctx)
        assert result.decision == "REQUIRES_HUMAN_REVIEW"
        assert not result.is_denied

    def test_high_risk_no_dpo_requires_human_review(self):
        """HIGH risk level + no DPO appointed → REQUIRES_HUMAN_REVIEW."""
        ctx = _base_ctx(
            jurisdiction=mod.MiddleEastJurisdiction.UAE,
            is_uae_pdpl_subject=True,
            ai_risk_level=mod.MiddleEastAIRiskLevel.HIGH,
            uae_dpo_appointed=False,
        )
        result = self._eval(ctx)
        assert result.decision == "REQUIRES_HUMAN_REVIEW"
        assert not result.is_denied

    def test_compliant_uae_approved(self):
        """Fully compliant UAE context → APPROVED."""
        ctx = _base_ctx(
            jurisdiction=mod.MiddleEastJurisdiction.UAE,
            is_uae_pdpl_subject=True,
            involves_personal_data=True,
            has_uae_consent=True,
            involves_biometric_data=False,
            is_high_impact_ai=False,
            ai_risk_level=mod.MiddleEastAIRiskLevel.LOW,
            uae_dpo_appointed=True,
        )
        result = self._eval(ctx)
        assert result.decision == "APPROVED"
        assert not result.is_denied

    def test_legal_obligation_basis_approved_without_consent(self):
        """Legal obligation processing purpose → APPROVED without explicit consent."""
        ctx = _base_ctx(
            jurisdiction=mod.MiddleEastJurisdiction.UAE,
            is_uae_pdpl_subject=True,
            involves_personal_data=True,
            has_uae_consent=False,
            processing_purpose="legal_obligation",
        )
        result = self._eval(ctx)
        assert result.decision == "APPROVED"
        assert not result.is_denied


# ===========================================================================
# TestSaudiAIFilter
# ===========================================================================


class TestSaudiAIFilter:
    """Layer 2: Saudi PDPL Royal Decree M/19 + NDMO + SAMA/SFDA."""

    def _eval(self, ctx, doc=None):
        if doc is None:
            doc = _base_doc()
        return mod.SaudiAIFilter().evaluate(ctx, doc)

    def test_non_saudi_jurisdiction_approved(self):
        """Non-Saudi jurisdiction → APPROVED (filter not triggered)."""
        ctx = _base_ctx(
            jurisdiction=mod.MiddleEastJurisdiction.UAE,
            is_saudi_pdpl_subject=True,
        )
        result = self._eval(ctx)
        assert result.decision == "APPROVED"
        assert not result.is_denied

    def test_not_saudi_pdpl_subject_approved(self):
        """Not Saudi PDPL subject → APPROVED."""
        ctx = _base_ctx(
            jurisdiction=mod.MiddleEastJurisdiction.SAUDI_ARABIA,
            is_saudi_pdpl_subject=False,
            involves_personal_data=True,
            has_saudi_consent=False,
        )
        result = self._eval(ctx)
        assert result.decision == "APPROVED"
        assert not result.is_denied

    def test_no_saudi_consent_denied(self):
        """Personal data + no Saudi consent + no lawful basis → DENIED."""
        ctx = _base_ctx(
            jurisdiction=mod.MiddleEastJurisdiction.SAUDI_ARABIA,
            is_saudi_pdpl_subject=True,
            involves_personal_data=True,
            has_saudi_consent=False,
            processing_purpose="marketing",
        )
        result = self._eval(ctx)
        assert result.is_denied
        assert result.decision == "DENIED"

    def test_no_saudi_consent_cites_article_4(self):
        """Saudi consent denial cites Saudi PDPL Article 4."""
        ctx = _base_ctx(
            jurisdiction=mod.MiddleEastJurisdiction.SAUDI_ARABIA,
            is_saudi_pdpl_subject=True,
            involves_personal_data=True,
            has_saudi_consent=False,
            processing_purpose="marketing",
        )
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "4" in combined or "Article 4" in combined

    def test_unclassified_data_requires_human_review(self):
        """Personal data not classified per NDMO → REQUIRES_HUMAN_REVIEW."""
        ctx = _base_ctx(
            jurisdiction=mod.MiddleEastJurisdiction.SAUDI_ARABIA,
            is_saudi_pdpl_subject=True,
            involves_personal_data=True,
            has_saudi_consent=True,
            saudi_data_classified=False,
        )
        result = self._eval(ctx)
        assert result.decision == "REQUIRES_HUMAN_REVIEW"
        assert not result.is_denied

    def test_financial_ai_no_sama_denied(self):
        """Financial AI + no SAMA approval → DENIED."""
        ctx = _base_ctx(
            jurisdiction=mod.MiddleEastJurisdiction.SAUDI_ARABIA,
            is_saudi_pdpl_subject=True,
            involves_personal_data=True,
            has_saudi_consent=True,
            saudi_data_classified=True,
            is_financial_ai=True,
            has_sama_approval=False,
        )
        result = self._eval(ctx)
        assert result.is_denied
        assert result.decision == "DENIED"

    def test_financial_ai_no_sama_cites_sama_framework(self):
        """Financial AI denial cites SAMA framework."""
        ctx = _base_ctx(
            jurisdiction=mod.MiddleEastJurisdiction.SAUDI_ARABIA,
            is_saudi_pdpl_subject=True,
            involves_personal_data=True,
            has_saudi_consent=True,
            saudi_data_classified=True,
            is_financial_ai=True,
            has_sama_approval=False,
        )
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "SAMA" in combined

    def test_medical_ai_no_sfda_denied(self):
        """Medical AI + no SFDA approval → DENIED."""
        ctx = _base_ctx(
            jurisdiction=mod.MiddleEastJurisdiction.SAUDI_ARABIA,
            is_saudi_pdpl_subject=True,
            involves_personal_data=True,
            has_saudi_consent=True,
            saudi_data_classified=True,
            is_medical_ai=True,
            has_sfda_approval=False,
        )
        result = self._eval(ctx)
        assert result.is_denied
        assert result.decision == "DENIED"

    def test_medical_ai_no_sfda_cites_sfda(self):
        """Medical AI denial cites Saudi SFDA."""
        ctx = _base_ctx(
            jurisdiction=mod.MiddleEastJurisdiction.SAUDI_ARABIA,
            is_saudi_pdpl_subject=True,
            involves_personal_data=True,
            has_saudi_consent=True,
            saudi_data_classified=True,
            is_medical_ai=True,
            has_sfda_approval=False,
        )
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "SFDA" in combined

    def test_compliant_saudi_approved(self):
        """Fully compliant Saudi context → APPROVED."""
        ctx = _base_ctx(
            jurisdiction=mod.MiddleEastJurisdiction.SAUDI_ARABIA,
            is_saudi_pdpl_subject=True,
            involves_personal_data=True,
            has_saudi_consent=True,
            saudi_data_classified=True,
            is_financial_ai=False,
            is_medical_ai=False,
        )
        result = self._eval(ctx)
        assert result.decision == "APPROVED"
        assert not result.is_denied


# ===========================================================================
# TestQatarAIFilter
# ===========================================================================


class TestQatarAIFilter:
    """Layer 3: Qatar PDPA Law No. 13/2016 + Qatar National AI Strategy 2030."""

    def _eval(self, ctx, doc=None):
        if doc is None:
            doc = _base_doc()
        return mod.QatarAIFilter().evaluate(ctx, doc)

    def test_non_qatar_jurisdiction_approved(self):
        """Non-Qatar jurisdiction → APPROVED (filter not triggered)."""
        ctx = _base_ctx(
            jurisdiction=mod.MiddleEastJurisdiction.UAE,
            is_qatar_pdpa_subject=True,
        )
        result = self._eval(ctx)
        assert result.decision == "APPROVED"
        assert not result.is_denied

    def test_not_qatar_pdpa_subject_approved(self):
        """Not Qatar PDPA subject → APPROVED."""
        ctx = _base_ctx(
            jurisdiction=mod.MiddleEastJurisdiction.QATAR,
            is_qatar_pdpa_subject=False,
            involves_personal_data=True,
            has_qatar_consent=False,
        )
        result = self._eval(ctx)
        assert result.decision == "APPROVED"
        assert not result.is_denied

    def test_no_qatar_consent_denied(self):
        """Personal data + no Qatar consent → DENIED."""
        ctx = _base_ctx(
            jurisdiction=mod.MiddleEastJurisdiction.QATAR,
            is_qatar_pdpa_subject=True,
            involves_personal_data=True,
            has_qatar_consent=False,
        )
        result = self._eval(ctx)
        assert result.is_denied
        assert result.decision == "DENIED"

    def test_no_qatar_consent_cites_article_8(self):
        """Qatar consent denial cites Qatar PDPA Article 8."""
        ctx = _base_ctx(
            jurisdiction=mod.MiddleEastJurisdiction.QATAR,
            is_qatar_pdpa_subject=True,
            involves_personal_data=True,
            has_qatar_consent=False,
        )
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "8" in combined or "Article 8" in combined

    def test_automated_decision_no_explanation_requires_human_review(self):
        """Automated decision + no explanation → REQUIRES_HUMAN_REVIEW."""
        ctx = _base_ctx(
            jurisdiction=mod.MiddleEastJurisdiction.QATAR,
            is_qatar_pdpa_subject=True,
            is_automated_decision=True,
            right_to_explanation_provided=False,
        )
        result = self._eval(ctx)
        assert result.decision == "REQUIRES_HUMAN_REVIEW"
        assert not result.is_denied

    def test_automated_decision_no_explanation_cites_ai_strategy(self):
        """Automated decision review cites Qatar National AI Strategy."""
        ctx = _base_ctx(
            jurisdiction=mod.MiddleEastJurisdiction.QATAR,
            is_qatar_pdpa_subject=True,
            is_automated_decision=True,
            right_to_explanation_provided=False,
        )
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "Qatar" in combined or "AI Strategy" in combined or "2030" in combined

    def test_profiling_no_consent_requires_human_review(self):
        """Profiling + no data subject consent → REQUIRES_HUMAN_REVIEW."""
        ctx = _base_ctx(
            jurisdiction=mod.MiddleEastJurisdiction.QATAR,
            is_qatar_pdpa_subject=True,
            profiling_involved=True,
            has_data_subject_consent=False,
        )
        result = self._eval(ctx)
        assert result.decision == "REQUIRES_HUMAN_REVIEW"
        assert not result.is_denied

    def test_profiling_no_consent_cites_article_9(self):
        """Profiling review cites Qatar PDPA Article 9."""
        ctx = _base_ctx(
            jurisdiction=mod.MiddleEastJurisdiction.QATAR,
            is_qatar_pdpa_subject=True,
            profiling_involved=True,
            has_data_subject_consent=False,
        )
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "9" in combined or "Article 9" in combined

    def test_compliant_qatar_approved(self):
        """Fully compliant Qatar context → APPROVED."""
        ctx = _base_ctx(
            jurisdiction=mod.MiddleEastJurisdiction.QATAR,
            is_qatar_pdpa_subject=True,
            involves_personal_data=True,
            has_qatar_consent=True,
            is_automated_decision=False,
            profiling_involved=False,
            right_to_explanation_provided=True,
        )
        result = self._eval(ctx)
        assert result.decision == "APPROVED"
        assert not result.is_denied


# ===========================================================================
# TestGCCCrossBorderFilter
# ===========================================================================


class TestGCCCrossBorderFilter:
    """Layer 4: GCC Cross-Border Data Transfer Framework."""

    def _eval(self, ctx, doc=None):
        if doc is None:
            doc = _base_doc()
        return mod.GCCCrossBorderFilter().evaluate(ctx, doc)

    def test_no_transfer_approved(self):
        """No cross-border transfer → APPROVED."""
        ctx = _base_ctx(is_cross_border_transfer=False)
        result = self._eval(ctx)
        assert result.decision == "APPROVED"
        assert not result.is_denied

    def test_no_transfer_reason_mentions_no_transfer(self):
        """No transfer approval reason mentions no transfer involved."""
        ctx = _base_ctx(is_cross_border_transfer=False)
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "cross-border" in combined.lower() or "transfer" in combined.lower()

    def test_gcc_to_gcc_adequate_approved(self):
        """GCC-to-GCC transfer (UAE → SA) → APPROVED (adequate jurisdiction)."""
        ctx = _base_ctx(
            jurisdiction=mod.MiddleEastJurisdiction.UAE,
            is_uae_pdpl_subject=True,
            is_cross_border_transfer=True,
            transfer_destination_jurisdiction="SA",
            has_uae_consent=True,
        )
        result = self._eval(ctx)
        assert result.decision == "APPROVED"
        assert not result.is_denied

    def test_gcc_to_gcc_cites_adequate_framework(self):
        """GCC-to-GCC approval cites GCC adequate jurisdiction framework."""
        ctx = _base_ctx(
            jurisdiction=mod.MiddleEastJurisdiction.UAE,
            is_uae_pdpl_subject=True,
            is_cross_border_transfer=True,
            transfer_destination_jurisdiction="QA",
            has_uae_consent=True,
        )
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "GCC" in combined or "adequate" in combined.lower()

    def test_uae_to_non_gcc_no_consent_denied(self):
        """UAE to non-GCC (US) without UAE consent → DENIED."""
        ctx = _base_ctx(
            jurisdiction=mod.MiddleEastJurisdiction.UAE,
            is_uae_pdpl_subject=True,
            is_cross_border_transfer=True,
            transfer_destination_jurisdiction="US",
            has_uae_consent=False,
        )
        result = self._eval(ctx)
        assert result.is_denied
        assert result.decision == "DENIED"

    def test_uae_to_non_gcc_no_consent_cites_article_26(self):
        """UAE non-GCC transfer denial cites UAE PDPL Article 26."""
        ctx = _base_ctx(
            jurisdiction=mod.MiddleEastJurisdiction.UAE,
            is_uae_pdpl_subject=True,
            is_cross_border_transfer=True,
            transfer_destination_jurisdiction="US",
            has_uae_consent=False,
        )
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "26" in combined or "Article 26" in combined

    def test_saudi_to_non_gcc_requires_human_review(self):
        """Saudi Arabia to non-GCC (UK) → REQUIRES_HUMAN_REVIEW (SDAIA approval needed)."""
        ctx = _base_ctx(
            jurisdiction=mod.MiddleEastJurisdiction.SAUDI_ARABIA,
            is_saudi_pdpl_subject=True,
            is_cross_border_transfer=True,
            transfer_destination_jurisdiction="GB",
        )
        result = self._eval(ctx)
        assert result.decision == "REQUIRES_HUMAN_REVIEW"
        assert not result.is_denied

    def test_saudi_to_non_gcc_cites_article_29(self):
        """Saudi non-GCC transfer review cites Saudi PDPL Article 29."""
        ctx = _base_ctx(
            jurisdiction=mod.MiddleEastJurisdiction.SAUDI_ARABIA,
            is_saudi_pdpl_subject=True,
            is_cross_border_transfer=True,
            transfer_destination_jurisdiction="GB",
        )
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "29" in combined or "Article 29" in combined or "SDAIA" in combined

    def test_qatar_to_non_gcc_no_consent_denied(self):
        """Qatar to non-GCC (JP) without Qatar consent → DENIED."""
        ctx = _base_ctx(
            jurisdiction=mod.MiddleEastJurisdiction.QATAR,
            is_qatar_pdpa_subject=True,
            is_cross_border_transfer=True,
            transfer_destination_jurisdiction="JP",
            has_qatar_consent=False,
        )
        result = self._eval(ctx)
        assert result.is_denied
        assert result.decision == "DENIED"

    def test_qatar_to_non_gcc_no_consent_cites_article_12(self):
        """Qatar non-GCC transfer denial cites Qatar PDPA Article 12."""
        ctx = _base_ctx(
            jurisdiction=mod.MiddleEastJurisdiction.QATAR,
            is_qatar_pdpa_subject=True,
            is_cross_border_transfer=True,
            transfer_destination_jurisdiction="JP",
            has_qatar_consent=False,
        )
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "12" in combined or "Article 12" in combined or "MOTC" in combined


# ===========================================================================
# TestOrchestrator
# ===========================================================================


class TestOrchestrator:
    """Integration tests across the full orchestrator."""

    def test_fully_compliant_context_all_approved(self):
        """Fully compliant LOW-risk UAE GENERAL context → all four filters APPROVED."""
        ctx = _base_ctx()
        doc = _base_doc()
        orchestrator = mod.MiddleEastAIGovernanceOrchestrator()
        results = orchestrator.evaluate(ctx, doc)
        assert len(results) == 4
        for r in results:
            assert r.decision == "APPROVED"
            assert not r.is_denied

    def test_orchestrator_returns_four_results(self):
        """Orchestrator always returns exactly four FilterResult objects."""
        ctx = _base_ctx()
        doc = _base_doc()
        orchestrator = mod.MiddleEastAIGovernanceOrchestrator()
        results = orchestrator.evaluate(ctx, doc)
        assert len(results) == 4

    def test_all_filters_run_regardless_of_denial(self):
        """All four filters run even when first filter produces DENIED."""
        ctx = _base_ctx(
            jurisdiction=mod.MiddleEastJurisdiction.UAE,
            is_uae_pdpl_subject=True,
            involves_personal_data=True,
            has_uae_consent=False,
            processing_purpose="marketing",
        )
        doc = _base_doc()
        orchestrator = mod.MiddleEastAIGovernanceOrchestrator()
        results = orchestrator.evaluate(ctx, doc)
        assert len(results) == 4

    def test_denied_path_produces_denied_result(self):
        """Biometric data without consent → at least one filter result is DENIED."""
        ctx = _base_ctx(
            jurisdiction=mod.MiddleEastJurisdiction.UAE,
            is_uae_pdpl_subject=True,
            involves_biometric_data=True,
            has_biometric_consent=False,
        )
        doc = _base_doc()
        orchestrator = mod.MiddleEastAIGovernanceOrchestrator()
        results = orchestrator.evaluate(ctx, doc)
        assert any(r.is_denied for r in results)

    def test_denied_overrides_requires_human_review(self):
        """Scenario with both DENIED and REQUIRES_HUMAN_REVIEW → overall DENIED."""
        # UAE biometric without consent → DENIED from filter 1
        # high-impact without transparency → REQUIRES_HUMAN_REVIEW but biometric
        # takes precedence for DENIED in filter 1; combine with Qatar auto-decision
        # needing explanation to create a multi-signal scenario
        ctx = _base_ctx(
            jurisdiction=mod.MiddleEastJurisdiction.UAE,
            is_uae_pdpl_subject=True,
            involves_biometric_data=True,
            has_biometric_consent=False,
            is_high_impact_ai=True,
            ai_transparency_disclosed=False,
        )
        doc = _base_doc()
        orchestrator = mod.MiddleEastAIGovernanceOrchestrator()
        results = orchestrator.evaluate(ctx, doc)
        report = mod.MiddleEastAIGovernanceReport(context=ctx, document=doc, filter_results=results)
        assert report.overall_decision == "DENIED"


# ===========================================================================
# TestReport
# ===========================================================================


class TestReport:
    """Tests for MiddleEastAIGovernanceReport aggregation properties."""

    def _make_report(self, ctx=None, doc=None):
        if ctx is None:
            ctx = _base_ctx()
        if doc is None:
            doc = _base_doc()
        orchestrator = mod.MiddleEastAIGovernanceOrchestrator()
        results = orchestrator.evaluate(ctx, doc)
        return mod.MiddleEastAIGovernanceReport(context=ctx, document=doc, filter_results=results)

    def test_overall_decision_approved_when_all_pass(self):
        """Fully compliant context → overall_decision is 'APPROVED'."""
        report = self._make_report()
        assert report.overall_decision == "APPROVED"

    def test_overall_decision_denied_when_any_denied(self):
        """Any DENIED result → overall_decision is 'DENIED'."""
        ctx = _base_ctx(
            jurisdiction=mod.MiddleEastJurisdiction.UAE,
            is_uae_pdpl_subject=True,
            involves_biometric_data=True,
            has_biometric_consent=False,
        )
        report = self._make_report(ctx=ctx)
        assert report.overall_decision == "DENIED"

    def test_overall_decision_requires_human_review_when_no_denial_but_review(self):
        """REQUIRES_HUMAN_REVIEW result (no denial) → overall_decision is 'REQUIRES_HUMAN_REVIEW'."""
        ctx = _base_ctx(
            jurisdiction=mod.MiddleEastJurisdiction.UAE,
            is_uae_pdpl_subject=True,
            is_high_impact_ai=True,
            ai_transparency_disclosed=False,
        )
        report = self._make_report(ctx=ctx)
        assert report.overall_decision == "REQUIRES_HUMAN_REVIEW"

    def test_is_compliant_true_when_all_approved(self):
        """Fully compliant context → is_compliant is True."""
        report = self._make_report()
        assert report.is_compliant is True

    def test_is_compliant_false_when_denied(self):
        """DENIED result → is_compliant is False."""
        ctx = _base_ctx(
            jurisdiction=mod.MiddleEastJurisdiction.UAE,
            is_uae_pdpl_subject=True,
            involves_biometric_data=True,
            has_biometric_consent=False,
        )
        report = self._make_report(ctx=ctx)
        assert report.is_compliant is False

    def test_is_compliant_false_when_requires_human_review(self):
        """REQUIRES_HUMAN_REVIEW → is_compliant is False."""
        ctx = _base_ctx(
            jurisdiction=mod.MiddleEastJurisdiction.UAE,
            is_uae_pdpl_subject=True,
            is_high_impact_ai=True,
            ai_transparency_disclosed=False,
        )
        report = self._make_report(ctx=ctx)
        assert report.is_compliant is False

    def test_compliance_summary_contains_user_id(self):
        """compliance_summary includes the user_id."""
        report = self._make_report()
        assert "u1" in report.compliance_summary

    def test_compliance_summary_contains_overall_decision(self):
        """compliance_summary includes the overall decision string."""
        report = self._make_report()
        assert "APPROVED" in report.compliance_summary

    def test_compliance_summary_contains_sector(self):
        """compliance_summary includes the sector value."""
        report = self._make_report()
        assert "general" in report.compliance_summary.lower()


# ===========================================================================
# TestEdgeCases
# ===========================================================================


class TestEdgeCases:
    """Edge case and boundary tests."""

    def test_is_denied_property_false_for_approved(self):
        """FilterResult.is_denied returns False for APPROVED decision."""
        result = mod.FilterResult(
            filter_name="TEST",
            decision="APPROVED",
            reason="ok",
            regulation_citation="Test",
        )
        assert result.is_denied is False

    def test_is_denied_property_false_for_requires_human_review(self):
        """FilterResult.is_denied returns False for REQUIRES_HUMAN_REVIEW."""
        result = mod.FilterResult(
            filter_name="TEST",
            decision="REQUIRES_HUMAN_REVIEW",
            reason="review needed",
            regulation_citation="Test",
        )
        assert result.is_denied is False

    def test_is_denied_property_true_for_denied(self):
        """FilterResult.is_denied returns True only for DENIED."""
        result = mod.FilterResult(
            filter_name="TEST",
            decision="DENIED",
            reason="violation",
            regulation_citation="Test",
        )
        assert result.is_denied is True

    def test_mixed_results_overall_denied(self):
        """Mixed filter results with at least one DENIED → overall DENIED."""
        ctx = _base_ctx()
        doc = _base_doc()
        fake_results = [
            mod.FilterResult(
                filter_name="F1",
                decision="APPROVED",
                reason="ok",
                regulation_citation="x",
            ),
            mod.FilterResult(
                filter_name="F2",
                decision="DENIED",
                reason="fail",
                regulation_citation="y",
            ),
            mod.FilterResult(
                filter_name="F3",
                decision="REQUIRES_HUMAN_REVIEW",
                reason="review",
                regulation_citation="z",
            ),
            mod.FilterResult(
                filter_name="F4",
                decision="APPROVED",
                reason="ok",
                regulation_citation="w",
            ),
        ]
        report = mod.MiddleEastAIGovernanceReport(context=ctx, document=doc, filter_results=fake_results)
        assert report.overall_decision == "DENIED"
        assert report.is_compliant is False

    def test_mixed_results_no_denial_requires_human_review(self):
        """Mixed results with REQUIRES_HUMAN_REVIEW but no DENIED → REQUIRES_HUMAN_REVIEW."""
        ctx = _base_ctx()
        doc = _base_doc()
        fake_results = [
            mod.FilterResult(
                filter_name="F1",
                decision="APPROVED",
                reason="ok",
                regulation_citation="x",
            ),
            mod.FilterResult(
                filter_name="F2",
                decision="REQUIRES_HUMAN_REVIEW",
                reason="review",
                regulation_citation="y",
            ),
            mod.FilterResult(
                filter_name="F3",
                decision="APPROVED",
                reason="ok",
                regulation_citation="z",
            ),
            mod.FilterResult(
                filter_name="F4",
                decision="APPROVED",
                reason="ok",
                regulation_citation="w",
            ),
        ]
        report = mod.MiddleEastAIGovernanceReport(context=ctx, document=doc, filter_results=fake_results)
        assert report.overall_decision == "REQUIRES_HUMAN_REVIEW"
        assert report.is_compliant is False

    def test_bahrain_jurisdiction_passes_uae_filter(self):
        """Bahrain jurisdiction with UAE PDPL subject=True → APPROVED (non-UAE)."""
        ctx = _base_ctx(
            jurisdiction=mod.MiddleEastJurisdiction.BAHRAIN,
            is_uae_pdpl_subject=True,
        )
        result = mod.UAEAIFilter().evaluate(ctx, _base_doc())
        assert result.decision == "APPROVED"
        assert not result.is_denied

    def test_kuwait_jurisdiction_passes_saudi_filter(self):
        """Kuwait jurisdiction with Saudi PDPL subject=True → APPROVED (non-Saudi)."""
        ctx = _base_ctx(
            jurisdiction=mod.MiddleEastJurisdiction.KUWAIT,
            is_saudi_pdpl_subject=True,
        )
        result = mod.SaudiAIFilter().evaluate(ctx, _base_doc())
        assert result.decision == "APPROVED"
        assert not result.is_denied

    def test_context_is_frozen(self):
        """MiddleEastAIContext is frozen (immutable) — direct assignment raises."""
        ctx = _base_ctx()
        raised = False
        try:
            ctx.user_id = "changed"  # type: ignore[misc]
        except Exception:
            raised = True
        assert raised, "Expected frozen dataclass to raise on attribute assignment"

    def test_document_is_frozen(self):
        """MiddleEastAIDocument is frozen (immutable) — direct assignment raises."""
        doc = _base_doc()
        raised = False
        try:
            doc.document_id = "changed"  # type: ignore[misc]
        except Exception:
            raised = True
        assert raised, "Expected frozen dataclass to raise on attribute assignment"

    def test_uae_contract_basis_approved_without_explicit_consent(self):
        """UAE processing for contract purpose → APPROVED without explicit consent."""
        ctx = _base_ctx(
            jurisdiction=mod.MiddleEastJurisdiction.UAE,
            is_uae_pdpl_subject=True,
            involves_personal_data=True,
            has_uae_consent=False,
            processing_purpose="contract",
        )
        result = mod.UAEAIFilter().evaluate(ctx, _base_doc())
        assert result.decision == "APPROVED"
        assert not result.is_denied

    def test_gcc_to_bahrain_is_adequate(self):
        """UAE to Bahrain (BH) → GCC adequate, APPROVED."""
        ctx = _base_ctx(
            jurisdiction=mod.MiddleEastJurisdiction.UAE,
            is_uae_pdpl_subject=True,
            is_cross_border_transfer=True,
            transfer_destination_jurisdiction="BH",
            has_uae_consent=False,
        )
        result = mod.GCCCrossBorderFilter().evaluate(ctx, _base_doc())
        assert result.decision == "APPROVED"
        assert not result.is_denied

    def test_gcc_to_oman_is_adequate(self):
        """Qatar to Oman (OM) → GCC adequate, APPROVED."""
        ctx = _base_ctx(
            jurisdiction=mod.MiddleEastJurisdiction.QATAR,
            is_qatar_pdpa_subject=True,
            is_cross_border_transfer=True,
            transfer_destination_jurisdiction="OM",
            has_qatar_consent=False,
        )
        result = mod.GCCCrossBorderFilter().evaluate(ctx, _base_doc())
        assert result.decision == "APPROVED"
        assert not result.is_denied
