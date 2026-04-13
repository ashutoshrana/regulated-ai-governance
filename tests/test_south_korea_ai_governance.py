"""
Tests for 24_south_korea_ai_governance.py — Four-layer South Korea AI
governance framework covering Korea AI Framework Act (2024), PIPA 2020,
Korea Sectoral AI Regulations, and Korea Data Governance & AI Auditing.
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
    _name = "south_korea_ai_governance_24"
    spec = importlib.util.spec_from_file_location(
        _name,
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "examples",
            "24_south_korea_ai_governance.py",
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
    """Return a fully-compliant MINIMAL-risk GENERAL-sector context."""
    defaults = dict(
        user_id="u1",
        sector=mod.KoreaSector.GENERAL,
        ai_risk_level=mod.KoreaAIRiskLevel.MINIMAL,
        is_automated_decision=False,
        involves_personal_info=False,
        contains_sensitive_info=False,
        has_pipa_consent=True,
        has_sensitive_info_consent=True,
        processing_purpose="service_delivery",
        is_high_impact_ai=False,
        ai_transparency_disclosed=True,
        involves_prohibited_practice=False,
        is_automated_credit_decision=False,
        has_credit_explainability=True,
        is_automated_hiring_decision=False,
        has_hiring_human_review=True,
        is_medical_ai=False,
        has_mfds_approval=False,
        has_physician_oversight=False,
        cross_border_transfer=False,
        requester_jurisdiction="KR",
        has_pipa_transfer_mechanism=True,
        profiling_involved=False,
        has_profiling_consent=True,
        right_to_contest_provided=True,
        is_generative_ai=False,
        has_ai_output_label=True,
    )
    defaults.update(overrides)
    return mod.KoreaAIContext(**defaults)


def _base_doc(**overrides):
    """Return a minimal, non-sensitive document."""
    defaults = dict(
        document_id="d1",
        content_type="REPORT",
        contains_personal_info=False,
        risk_level="MINIMAL",
        requires_human_review=False,
        processing_timestamp="2024-06-01T09:00:00+09:00",
        jurisdiction="KR",
    )
    defaults.update(overrides)
    return mod.KoreaAIDocument(**defaults)


# ===========================================================================
# TestKoreaAIFrameworkActFilter
# ===========================================================================


class TestKoreaAIFrameworkActFilter:
    """Layer 1: Korea AI Framework Act (January 23, 2024)."""

    def _eval(self, ctx, doc=None):
        if doc is None:
            doc = _base_doc()
        return mod.KoreaAIFrameworkActFilter().evaluate(ctx, doc)

    def test_prohibited_practice_denied(self):
        """Prohibited AI practice (social scoring) → DENIED."""
        ctx = _base_ctx(involves_prohibited_practice=True)
        result = self._eval(ctx)
        assert result.is_denied
        assert result.decision == "DENIED"

    def test_prohibited_practice_cites_article_10(self):
        """Prohibited practice denial cites Korea AI Framework Act Article 10."""
        ctx = _base_ctx(involves_prohibited_practice=True)
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "Article 10" in combined or "10" in combined

    def test_high_impact_no_disclosure_requires_human_review(self):
        """High-impact AI + no transparency disclosure → REQUIRES_HUMAN_REVIEW."""
        ctx = _base_ctx(
            ai_risk_level=mod.KoreaAIRiskLevel.HIGH_IMPACT,
            ai_transparency_disclosed=False,
        )
        result = self._eval(ctx)
        assert result.decision == "REQUIRES_HUMAN_REVIEW"
        assert not result.is_denied

    def test_high_impact_no_disclosure_cites_article_6(self):
        """REQUIRES_HUMAN_REVIEW for missing disclosure cites Article 6."""
        ctx = _base_ctx(
            ai_risk_level=mod.KoreaAIRiskLevel.HIGH_IMPACT,
            ai_transparency_disclosed=False,
        )
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "Article 6" in combined or "6" in combined

    def test_high_impact_with_disclosure_approved(self):
        """High-impact AI + transparency disclosed → APPROVED."""
        ctx = _base_ctx(
            ai_risk_level=mod.KoreaAIRiskLevel.HIGH_IMPACT,
            ai_transparency_disclosed=True,
        )
        result = self._eval(ctx)
        assert result.decision == "APPROVED"
        assert not result.is_denied

    def test_non_high_impact_approved(self):
        """Non-high-impact AI → APPROVED (no Framework Act obligations triggered)."""
        ctx = _base_ctx(
            ai_risk_level=mod.KoreaAIRiskLevel.MINIMAL,
            involves_prohibited_practice=False,
        )
        result = self._eval(ctx)
        assert result.decision == "APPROVED"
        assert not result.is_denied

    def test_significant_risk_no_prohibited_approved(self):
        """SIGNIFICANT risk + no prohibited practice → APPROVED."""
        ctx = _base_ctx(
            ai_risk_level=mod.KoreaAIRiskLevel.SIGNIFICANT,
            ai_transparency_disclosed=True,
            involves_prohibited_practice=False,
        )
        result = self._eval(ctx)
        assert result.decision == "APPROVED"


# ===========================================================================
# TestKoreaPIPAFilter
# ===========================================================================


class TestKoreaPIPAFilter:
    """Layer 2: PIPA 2020 (Personal Information Protection Act)."""

    def _eval(self, ctx, doc=None):
        if doc is None:
            doc = _base_doc()
        return mod.KoreaPIPAFilter().evaluate(ctx, doc)

    def test_no_personal_info_approved(self):
        """No personal information involved → APPROVED."""
        ctx = _base_ctx(involves_personal_info=False)
        result = self._eval(ctx)
        assert result.decision == "APPROVED"
        assert not result.is_denied

    def test_no_personal_info_cites_no_pipa(self):
        """No personal info approval mentions PIPA not triggered."""
        ctx = _base_ctx(involves_personal_info=False)
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "PIPA" in combined or "personal" in combined.lower()

    def test_no_consent_no_lawful_basis_denied(self):
        """Personal info + no consent + no lawful basis → DENIED."""
        ctx = _base_ctx(
            involves_personal_info=True,
            has_pipa_consent=False,
            processing_purpose="marketing",
        )
        result = self._eval(ctx)
        assert result.is_denied
        assert result.decision == "DENIED"

    def test_no_consent_cites_article_15(self):
        """No consent denial cites PIPA Article 15."""
        ctx = _base_ctx(
            involves_personal_info=True,
            has_pipa_consent=False,
            processing_purpose="marketing",
        )
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "15" in combined

    def test_sensitive_info_no_consent_denied(self):
        """Sensitive information + no explicit consent → DENIED."""
        ctx = _base_ctx(
            involves_personal_info=True,
            has_pipa_consent=True,
            contains_sensitive_info=True,
            has_sensitive_info_consent=False,
        )
        result = self._eval(ctx)
        assert result.is_denied
        assert result.decision == "DENIED"

    def test_sensitive_info_no_consent_cites_article_23(self):
        """Sensitive info denial cites PIPA Article 23."""
        ctx = _base_ctx(
            involves_personal_info=True,
            has_pipa_consent=True,
            contains_sensitive_info=True,
            has_sensitive_info_consent=False,
        )
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "23" in combined

    def test_automated_decision_no_contest_requires_human_review(self):
        """Automated decision + no right to contest → REQUIRES_HUMAN_REVIEW."""
        ctx = _base_ctx(
            involves_personal_info=True,
            has_pipa_consent=True,
            is_automated_decision=True,
            right_to_contest_provided=False,
        )
        result = self._eval(ctx)
        assert result.decision == "REQUIRES_HUMAN_REVIEW"
        assert not result.is_denied

    def test_automated_decision_no_contest_cites_article_28_2(self):
        """REQUIRES_HUMAN_REVIEW for missing contest cites PIPA Article 28-2."""
        ctx = _base_ctx(
            involves_personal_info=True,
            has_pipa_consent=True,
            is_automated_decision=True,
            right_to_contest_provided=False,
        )
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "28" in combined

    def test_profiling_no_consent_requires_human_review(self):
        """Profiling + no profiling consent → REQUIRES_HUMAN_REVIEW."""
        ctx = _base_ctx(
            involves_personal_info=True,
            has_pipa_consent=True,
            profiling_involved=True,
            has_profiling_consent=False,
        )
        result = self._eval(ctx)
        assert result.decision == "REQUIRES_HUMAN_REVIEW"
        assert not result.is_denied

    def test_profiling_no_consent_cites_article_28_3(self):
        """REQUIRES_HUMAN_REVIEW for profiling cites PIPA Article 28-3."""
        ctx = _base_ctx(
            involves_personal_info=True,
            has_pipa_consent=True,
            profiling_involved=True,
            has_profiling_consent=False,
        )
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "28" in combined

    def test_cross_border_to_adequate_jurisdiction_approved(self):
        """Cross-border transfer to EU (adequate) → APPROVED."""
        ctx = _base_ctx(
            involves_personal_info=True,
            has_pipa_consent=True,
            cross_border_transfer=True,
            requester_jurisdiction="EU",
            has_pipa_transfer_mechanism=False,
        )
        result = self._eval(ctx)
        assert result.decision == "APPROVED"
        assert not result.is_denied

    def test_cross_border_no_mechanism_denied(self):
        """Cross-border to non-adequate jurisdiction + no mechanism → DENIED."""
        ctx = _base_ctx(
            involves_personal_info=True,
            has_pipa_consent=True,
            cross_border_transfer=True,
            requester_jurisdiction="BR",
            has_pipa_transfer_mechanism=False,
        )
        result = self._eval(ctx)
        assert result.is_denied
        assert result.decision == "DENIED"

    def test_cross_border_no_mechanism_cites_article_39_3(self):
        """Cross-border denial cites PIPA Article 39-3."""
        ctx = _base_ctx(
            involves_personal_info=True,
            has_pipa_consent=True,
            cross_border_transfer=True,
            requester_jurisdiction="BR",
            has_pipa_transfer_mechanism=False,
        )
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "39" in combined

    def test_legal_obligation_basis_approved_without_consent(self):
        """Legal obligation basis → APPROVED even without has_pipa_consent."""
        ctx = _base_ctx(
            involves_personal_info=True,
            has_pipa_consent=False,
            processing_purpose="legal_obligation",
        )
        result = self._eval(ctx)
        assert result.decision == "APPROVED"
        assert not result.is_denied


# ===========================================================================
# TestKoreaSectoralAIFilter
# ===========================================================================


class TestKoreaSectoralAIFilter:
    """Layer 3: Korea Sectoral AI Regulations."""

    def _eval(self, ctx, doc=None):
        if doc is None:
            doc = _base_doc()
        return mod.KoreaSectoralAIFilter().evaluate(ctx, doc)

    def test_financial_credit_no_explainability_requires_human_review(self):
        """Financial sector + automated credit + no explainability → REQUIRES_HUMAN_REVIEW."""
        ctx = _base_ctx(
            sector=mod.KoreaSector.FINANCIAL,
            is_automated_credit_decision=True,
            has_credit_explainability=False,
        )
        result = self._eval(ctx)
        assert result.decision == "REQUIRES_HUMAN_REVIEW"
        assert not result.is_denied

    def test_financial_credit_cites_credit_act_article_20(self):
        """Financial credit review cites Credit Information Act Article 20."""
        ctx = _base_ctx(
            sector=mod.KoreaSector.FINANCIAL,
            is_automated_credit_decision=True,
            has_credit_explainability=False,
        )
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "20" in combined or "Credit" in combined

    def test_employment_no_human_review_requires_human_review(self):
        """Employment sector + automated hiring + no human review → REQUIRES_HUMAN_REVIEW."""
        ctx = _base_ctx(
            sector=mod.KoreaSector.EMPLOYMENT,
            is_automated_hiring_decision=True,
            has_hiring_human_review=False,
        )
        result = self._eval(ctx)
        assert result.decision == "REQUIRES_HUMAN_REVIEW"
        assert not result.is_denied

    def test_employment_no_human_review_cites_employment_act(self):
        """Employment review cites Korea Employment Act."""
        ctx = _base_ctx(
            sector=mod.KoreaSector.EMPLOYMENT,
            is_automated_hiring_decision=True,
            has_hiring_human_review=False,
        )
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "Employment" in combined or "hiring" in combined.lower()

    def test_healthcare_no_mfds_denied(self):
        """Healthcare sector + medical AI + no MFDS approval → DENIED."""
        ctx = _base_ctx(
            sector=mod.KoreaSector.HEALTHCARE,
            is_medical_ai=True,
            has_mfds_approval=False,
        )
        result = self._eval(ctx)
        assert result.is_denied
        assert result.decision == "DENIED"

    def test_healthcare_no_mfds_cites_medical_devices_act(self):
        """Healthcare MFDS denial cites Korean Medical Devices Act."""
        ctx = _base_ctx(
            sector=mod.KoreaSector.HEALTHCARE,
            is_medical_ai=True,
            has_mfds_approval=False,
        )
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "MFDS" in combined or "Medical" in combined

    def test_healthcare_mfds_no_physician_requires_human_review(self):
        """Healthcare + MFDS approved + no physician oversight → REQUIRES_HUMAN_REVIEW."""
        ctx = _base_ctx(
            sector=mod.KoreaSector.HEALTHCARE,
            is_medical_ai=True,
            has_mfds_approval=True,
            has_physician_oversight=False,
        )
        result = self._eval(ctx)
        assert result.decision == "REQUIRES_HUMAN_REVIEW"
        assert not result.is_denied

    def test_healthcare_mfds_physician_approved(self):
        """Healthcare + MFDS approved + physician oversight → APPROVED."""
        ctx = _base_ctx(
            sector=mod.KoreaSector.HEALTHCARE,
            is_medical_ai=True,
            has_mfds_approval=True,
            has_physician_oversight=True,
        )
        result = self._eval(ctx)
        assert result.decision == "APPROVED"
        assert not result.is_denied

    def test_public_high_impact_requires_human_review(self):
        """Public sector + HIGH_IMPACT → REQUIRES_HUMAN_REVIEW (impact assessment)."""
        ctx = _base_ctx(
            sector=mod.KoreaSector.PUBLIC,
            ai_risk_level=mod.KoreaAIRiskLevel.HIGH_IMPACT,
            ai_transparency_disclosed=True,
        )
        result = self._eval(ctx)
        assert result.decision == "REQUIRES_HUMAN_REVIEW"
        assert not result.is_denied

    def test_public_high_impact_cites_article_7(self):
        """Public high-impact review cites Korea AI Framework Act Article 7."""
        ctx = _base_ctx(
            sector=mod.KoreaSector.PUBLIC,
            ai_risk_level=mod.KoreaAIRiskLevel.HIGH_IMPACT,
            ai_transparency_disclosed=True,
        )
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "7" in combined or "impact assessment" in combined.lower()

    def test_general_sector_approved(self):
        """GENERAL sector with no special AI types → APPROVED."""
        ctx = _base_ctx(
            sector=mod.KoreaSector.GENERAL,
            is_automated_credit_decision=False,
            is_automated_hiring_decision=False,
            is_medical_ai=False,
        )
        result = self._eval(ctx)
        assert result.decision == "APPROVED"
        assert not result.is_denied

    def test_education_sector_approved(self):
        """EDUCATION sector → APPROVED (no sector-specific AI rules triggered)."""
        ctx = _base_ctx(
            sector=mod.KoreaSector.EDUCATION,
        )
        result = self._eval(ctx)
        assert result.decision == "APPROVED"
        assert not result.is_denied


# ===========================================================================
# TestKoreaDataGovernanceFilter
# ===========================================================================


class TestKoreaDataGovernanceFilter:
    """Layer 4: Korea Data Governance & AI Auditing."""

    def _eval(self, ctx, doc=None):
        if doc is None:
            doc = _base_doc()
        return mod.KoreaDataGovernanceFilter().evaluate(ctx, doc)

    def test_high_impact_no_transparency_requires_human_review(self):
        """HIGH_IMPACT risk + no AI transparency → REQUIRES_HUMAN_REVIEW."""
        ctx = _base_ctx(
            ai_risk_level=mod.KoreaAIRiskLevel.HIGH_IMPACT,
            ai_transparency_disclosed=False,
        )
        result = self._eval(ctx)
        assert result.decision == "REQUIRES_HUMAN_REVIEW"
        assert not result.is_denied

    def test_significant_no_transparency_requires_human_review(self):
        """SIGNIFICANT risk + no AI transparency → REQUIRES_HUMAN_REVIEW."""
        ctx = _base_ctx(
            ai_risk_level=mod.KoreaAIRiskLevel.SIGNIFICANT,
            ai_transparency_disclosed=False,
        )
        result = self._eval(ctx)
        assert result.decision == "REQUIRES_HUMAN_REVIEW"

    def test_personal_info_automated_no_contest_requires_human_review(self):
        """Personal info + automated decision + no right to contest → REQUIRES_HUMAN_REVIEW."""
        ctx = _base_ctx(
            involves_personal_info=True,
            is_automated_decision=True,
            right_to_contest_provided=False,
            ai_transparency_disclosed=True,
        )
        result = self._eval(ctx)
        assert result.decision == "REQUIRES_HUMAN_REVIEW"
        assert not result.is_denied

    def test_compliant_minimal_approved(self):
        """Fully compliant MINIMAL risk context → APPROVED."""
        ctx = _base_ctx(
            ai_risk_level=mod.KoreaAIRiskLevel.MINIMAL,
            ai_transparency_disclosed=True,
            involves_personal_info=False,
            is_automated_decision=False,
        )
        result = self._eval(ctx)
        assert result.decision == "APPROVED"
        assert not result.is_denied

    def test_compliant_high_impact_with_disclosure_approved(self):
        """HIGH_IMPACT + transparency disclosed + no automated decision → APPROVED."""
        ctx = _base_ctx(
            ai_risk_level=mod.KoreaAIRiskLevel.HIGH_IMPACT,
            ai_transparency_disclosed=True,
            involves_personal_info=False,
            is_automated_decision=False,
        )
        result = self._eval(ctx)
        assert result.decision == "APPROVED"


# ===========================================================================
# TestOrchestrator
# ===========================================================================


class TestOrchestrator:
    """Integration tests across the full orchestrator."""

    def test_fully_compliant_context_all_approved(self):
        """Fully compliant MINIMAL-risk GENERAL context → all four filters APPROVED."""
        ctx = _base_ctx()
        doc = _base_doc()
        orchestrator = mod.KoreaAIGovernanceOrchestrator()
        results = orchestrator.evaluate(ctx, doc)
        assert len(results) == 4
        for r in results:
            assert r.decision == "APPROVED"
            assert not r.is_denied

    def test_orchestrator_returns_four_results(self):
        """Orchestrator always returns exactly four FilterResult objects."""
        ctx = _base_ctx()
        doc = _base_doc()
        orchestrator = mod.KoreaAIGovernanceOrchestrator()
        results = orchestrator.evaluate(ctx, doc)
        assert len(results) == 4

    def test_denied_path_produces_denied_result(self):
        """Prohibited practice → at least one filter result is DENIED."""
        ctx = _base_ctx(involves_prohibited_practice=True)
        doc = _base_doc()
        orchestrator = mod.KoreaAIGovernanceOrchestrator()
        results = orchestrator.evaluate(ctx, doc)
        assert any(r.is_denied for r in results)

    def test_all_filters_run_regardless_of_denial(self):
        """All four filters run even when first filter denies."""
        ctx = _base_ctx(involves_prohibited_practice=True)
        doc = _base_doc()
        orchestrator = mod.KoreaAIGovernanceOrchestrator()
        results = orchestrator.evaluate(ctx, doc)
        # All four filter results must be present
        assert len(results) == 4

    def test_denied_overrides_requires_human_review(self):
        """Scenario with both DENIED and REQUIRES_HUMAN_REVIEW → overall DENIED."""
        # prohibited practice = DENIED from filter 1
        # high-impact + no disclosure = REQUIRES_HUMAN_REVIEW from filter 1 normally,
        # but prohibited practice takes priority in filter 1
        # Trigger DENIED via prohibited practice and REQUIRES_HUMAN_REVIEW via
        # personal info + automated decision + no contest in PIPA filter
        ctx = _base_ctx(
            involves_prohibited_practice=True,
            involves_personal_info=True,
            has_pipa_consent=True,
            is_automated_decision=True,
            right_to_contest_provided=False,
        )
        doc = _base_doc()
        orchestrator = mod.KoreaAIGovernanceOrchestrator()
        results = orchestrator.evaluate(ctx, doc)
        report = mod.KoreaAIGovernanceReport(context=ctx, document=doc, filter_results=results)
        assert report.overall_decision == "DENIED"


# ===========================================================================
# TestReport
# ===========================================================================


class TestReport:
    """Tests for KoreaAIGovernanceReport aggregation properties."""

    def _make_report(self, ctx=None, doc=None):
        if ctx is None:
            ctx = _base_ctx()
        if doc is None:
            doc = _base_doc()
        orchestrator = mod.KoreaAIGovernanceOrchestrator()
        results = orchestrator.evaluate(ctx, doc)
        return mod.KoreaAIGovernanceReport(context=ctx, document=doc, filter_results=results)

    def test_overall_decision_approved_when_all_pass(self):
        """Fully compliant context → overall_decision is 'APPROVED'."""
        report = self._make_report()
        assert report.overall_decision == "APPROVED"

    def test_overall_decision_denied_when_any_denied(self):
        """Any DENIED result → overall_decision is 'DENIED'."""
        ctx = _base_ctx(involves_prohibited_practice=True)
        report = self._make_report(ctx=ctx)
        assert report.overall_decision == "DENIED"

    def test_overall_decision_requires_human_review_when_no_denial_but_review(self):
        """REQUIRES_HUMAN_REVIEW result (no denial) → overall_decision is 'REQUIRES_HUMAN_REVIEW'."""
        ctx = _base_ctx(
            ai_risk_level=mod.KoreaAIRiskLevel.HIGH_IMPACT,
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
        ctx = _base_ctx(involves_prohibited_practice=True)
        report = self._make_report(ctx=ctx)
        assert report.is_compliant is False

    def test_is_compliant_false_when_requires_human_review(self):
        """REQUIRES_HUMAN_REVIEW → is_compliant is False (not fully approved)."""
        ctx = _base_ctx(
            ai_risk_level=mod.KoreaAIRiskLevel.HIGH_IMPACT,
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
            mod.FilterResult(filter_name="F1", decision="APPROVED", reason="ok", regulation_citation="x"),
            mod.FilterResult(filter_name="F2", decision="DENIED", reason="fail", regulation_citation="y"),
            mod.FilterResult(
                filter_name="F3", decision="REQUIRES_HUMAN_REVIEW", reason="review", regulation_citation="z"
            ),  # noqa: E501
            mod.FilterResult(filter_name="F4", decision="APPROVED", reason="ok", regulation_citation="w"),
        ]
        report = mod.KoreaAIGovernanceReport(context=ctx, document=doc, filter_results=fake_results)
        assert report.overall_decision == "DENIED"
        assert report.is_compliant is False

    def test_mixed_results_no_denial_requires_human_review(self):
        """Mixed results with REQUIRES_HUMAN_REVIEW but no DENIED → REQUIRES_HUMAN_REVIEW."""
        ctx = _base_ctx()
        doc = _base_doc()
        fake_results = [
            mod.FilterResult(filter_name="F1", decision="APPROVED", reason="ok", regulation_citation="x"),
            mod.FilterResult(
                filter_name="F2", decision="REQUIRES_HUMAN_REVIEW", reason="review", regulation_citation="y"
            ),  # noqa: E501
            mod.FilterResult(filter_name="F3", decision="APPROVED", reason="ok", regulation_citation="z"),
            mod.FilterResult(filter_name="F4", decision="APPROVED", reason="ok", regulation_citation="w"),
        ]
        report = mod.KoreaAIGovernanceReport(context=ctx, document=doc, filter_results=fake_results)
        assert report.overall_decision == "REQUIRES_HUMAN_REVIEW"
        assert report.is_compliant is False

    def test_cross_border_to_japan_adequate_approved(self):
        """Cross-border transfer to Japan (adequate) + no SCC → APPROVED."""
        ctx = _base_ctx(
            involves_personal_info=True,
            has_pipa_consent=True,
            cross_border_transfer=True,
            requester_jurisdiction="JP",
            has_pipa_transfer_mechanism=False,
        )
        result = mod.KoreaPIPAFilter().evaluate(ctx, _base_doc())
        assert result.decision == "APPROVED"
        assert not result.is_denied

    def test_cross_border_with_mechanism_approved(self):
        """Cross-border to non-adequate jurisdiction + SCC in place → APPROVED."""
        ctx = _base_ctx(
            involves_personal_info=True,
            has_pipa_consent=True,
            cross_border_transfer=True,
            requester_jurisdiction="IN",
            has_pipa_transfer_mechanism=True,
        )
        result = mod.KoreaPIPAFilter().evaluate(ctx, _base_doc())
        assert result.decision == "APPROVED"
        assert not result.is_denied

    def test_context_is_frozen(self):
        """KoreaAIContext is frozen (immutable) — direct assignment raises."""
        ctx = _base_ctx()
        raised = False
        try:
            ctx.user_id = "changed"  # type: ignore[misc]
        except Exception:
            raised = True
        assert raised, "Expected frozen dataclass to raise on attribute assignment"

    def test_document_is_frozen(self):
        """KoreaAIDocument is frozen (immutable) — direct assignment raises."""
        doc = _base_doc()
        raised = False
        try:
            doc.document_id = "changed"  # type: ignore[misc]
        except Exception:
            raised = True
        assert raised, "Expected frozen dataclass to raise on attribute assignment"
