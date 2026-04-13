"""
Tests for 27_iso42001_compliance.py — ISO 42001:2023 AI Management System
compliance framework covering Clause 5 (Leadership), Clause 6 (Planning),
Clause 8 (Operations), and Clause 9 (Performance Evaluation).
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
    _name = "iso42001_compliance_27"
    spec = importlib.util.spec_from_file_location(
        _name,
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "examples",
            "27_iso42001_compliance.py",
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
    """Return a fully-conforming enterprise decision-support context (limited risk)."""
    defaults = dict(
        user_id="u1",
        organization_type="enterprise",
        ai_system_type="decision_support",
        risk_level="limited",
        has_aims_policy=True,
        has_risk_assessment=True,
        has_impact_assessment=True,
        has_human_oversight=True,
        has_data_governance=True,
        has_transparency_docs=True,
        has_incident_process=True,
        has_audit_trail=True,
        is_third_party_ai=False,
        has_supplier_assessment=False,
        deployment_stage="production",
    )
    defaults.update(overrides)
    return mod.ISO42001Context(**defaults)


def _base_doc(**overrides):
    """Return a minimal document."""
    defaults = dict(
        content="test document content",
        document_id="d1",
        doc_type="ai_system_record",
    )
    defaults.update(overrides)
    return mod.ISO42001Document(**defaults)


# ===========================================================================
# TestISO42001PolicyFilter (Clause 5 — Leadership)
# ===========================================================================


class TestISO42001PolicyFilter:
    """Layer 1: ISO 42001:2023 Clause 5 — Leadership."""

    def _eval(self, ctx, doc=None):
        if doc is None:
            doc = _base_doc()
        return mod.ISO42001PolicyFilter().evaluate(ctx, doc)

    # --- Clause 5.2: production without AI policy → REQUIRES_HUMAN_REVIEW ---

    def test_production_no_policy_requires_review(self):
        """Production deployment + no AI policy → REQUIRES_HUMAN_REVIEW."""
        ctx = _base_ctx(
            risk_level="minimal",
            has_aims_policy=False,
            deployment_stage="production",
        )
        result = self._eval(ctx)
        assert result.decision == "REQUIRES_HUMAN_REVIEW"
        assert not result.is_denied

    def test_production_no_policy_cites_clause_52(self):
        """REQUIRES_HUMAN_REVIEW for missing policy cites Clause 5.2."""
        ctx = _base_ctx(
            risk_level="minimal",
            has_aims_policy=False,
            deployment_stage="production",
        )
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "5.2" in combined

    def test_production_with_policy_approved(self):
        """Production deployment WITH AI policy → APPROVED."""
        ctx = _base_ctx(has_aims_policy=True, deployment_stage="production")
        result = self._eval(ctx)
        assert result.decision == "APPROVED"

    def test_development_no_policy_approved(self):
        """Development stage + no AI policy → APPROVED (Clause 5.2 not triggered)."""
        ctx = _base_ctx(
            risk_level="minimal",
            has_aims_policy=False,
            deployment_stage="development",
        )
        result = self._eval(ctx)
        assert result.decision == "APPROVED"

    # --- Clause 5.1: high-risk without AI policy → DENIED ---

    def test_high_risk_no_policy_denied(self):
        """High-risk system + no AI policy → DENIED."""
        ctx = _base_ctx(risk_level="high", has_aims_policy=False)
        result = self._eval(ctx)
        assert result.decision == "DENIED"
        assert result.is_denied

    def test_high_risk_no_policy_cites_clause_51(self):
        """DENIED for high-risk without policy cites Clause 5.1."""
        ctx = _base_ctx(risk_level="high", has_aims_policy=False)
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "5.1" in combined

    def test_high_risk_with_policy_approved(self):
        """High-risk system WITH AI policy → APPROVED (Clause 5 satisfied)."""
        ctx = _base_ctx(risk_level="high", has_aims_policy=True)
        result = self._eval(ctx)
        assert result.decision == "APPROVED"

    # --- Minimal risk approved ---

    def test_minimal_risk_with_policy_approved(self):
        """Minimal-risk system WITH AI policy → APPROVED."""
        ctx = _base_ctx(risk_level="minimal", has_aims_policy=True)
        result = self._eval(ctx)
        assert result.decision == "APPROVED"
        assert not result.is_denied

    def test_compliant_result_not_requires_logging(self):
        """Compliant approval should set requires_logging=False."""
        ctx = _base_ctx()
        result = self._eval(ctx)
        assert result.requires_logging is False

    def test_denied_requires_logging(self):
        """DENIED result should set requires_logging=True."""
        ctx = _base_ctx(risk_level="high", has_aims_policy=False)
        result = self._eval(ctx)
        assert result.requires_logging is True


# ===========================================================================
# TestISO42001RiskFilter (Clause 6 — Planning)
# ===========================================================================


class TestISO42001RiskFilter:
    """Layer 2: ISO 42001:2023 Clause 6 — Planning."""

    def _eval(self, ctx, doc=None):
        if doc is None:
            doc = _base_doc()
        return mod.ISO42001RiskFilter().evaluate(ctx, doc)

    # --- Clause 6.1: high-risk without risk assessment → DENIED ---

    def test_high_risk_no_assessment_denied(self):
        """High-risk system + no risk assessment → DENIED."""
        ctx = _base_ctx(risk_level="high", has_risk_assessment=False)
        result = self._eval(ctx)
        assert result.decision == "DENIED"
        assert result.is_denied

    def test_high_risk_no_assessment_cites_clause_61(self):
        """DENIED for missing risk assessment cites Clause 6.1."""
        ctx = _base_ctx(risk_level="high", has_risk_assessment=False)
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "6.1" in combined

    def test_limited_risk_no_assessment_denied(self):
        """Limited-risk system + no risk assessment → DENIED."""
        ctx = _base_ctx(risk_level="limited", has_risk_assessment=False)
        result = self._eval(ctx)
        assert result.decision == "DENIED"
        assert result.is_denied

    def test_minimal_risk_no_assessment_approved(self):
        """Minimal-risk system + no risk assessment → APPROVED (Clause 6.1 not triggered)."""
        ctx = _base_ctx(risk_level="minimal", has_risk_assessment=False)
        result = self._eval(ctx)
        assert result.decision == "APPROVED"

    # --- Annex B: high-risk without impact assessment → REQUIRES_HUMAN_REVIEW ---

    def test_high_risk_no_impact_assessment_requires_review(self):
        """High-risk system + risk assessment present + no impact assessment → REQUIRES_HUMAN_REVIEW."""
        ctx = _base_ctx(
            risk_level="high",
            has_risk_assessment=True,
            has_impact_assessment=False,
        )
        result = self._eval(ctx)
        assert result.decision == "REQUIRES_HUMAN_REVIEW"
        assert not result.is_denied

    def test_high_risk_no_impact_assessment_cites_annex_b(self):
        """REQUIRES_HUMAN_REVIEW for missing impact assessment cites Annex B."""
        ctx = _base_ctx(
            risk_level="high",
            has_risk_assessment=True,
            has_impact_assessment=False,
        )
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "Annex B" in combined or "Annex" in combined

    def test_limited_risk_no_impact_assessment_approved(self):
        """Limited-risk + no impact assessment → APPROVED (Annex B not required)."""
        ctx = _base_ctx(risk_level="limited", has_impact_assessment=False)
        result = self._eval(ctx)
        assert result.decision == "APPROVED"

    # --- Clause 6.1.2: unacceptable risk → DENIED ---

    def test_unacceptable_risk_denied(self):
        """Unacceptable risk system → DENIED."""
        ctx = _base_ctx(risk_level="unacceptable")
        result = self._eval(ctx)
        assert result.decision == "DENIED"
        assert result.is_denied

    def test_unacceptable_risk_cites_clause_612(self):
        """DENIED for unacceptable risk cites Clause 6.1.2."""
        ctx = _base_ctx(risk_level="unacceptable")
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "6.1.2" in combined

    # --- Minimal risk approved ---

    def test_minimal_risk_approved(self):
        """Minimal-risk system with all controls → APPROVED."""
        ctx = _base_ctx(risk_level="minimal")
        result = self._eval(ctx)
        assert result.decision == "APPROVED"
        assert not result.is_denied

    def test_compliant_cites_clause_6(self):
        """Compliant approval cites ISO 42001:2023 Clause 6."""
        ctx = _base_ctx()
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "6" in combined


# ===========================================================================
# TestISO42001OperationsFilter (Clause 8 — Operations)
# ===========================================================================


class TestISO42001OperationsFilter:
    """Layer 3: ISO 42001:2023 Clause 8 — Operations."""

    def _eval(self, ctx, doc=None):
        if doc is None:
            doc = _base_doc()
        return mod.ISO42001OperationsFilter().evaluate(ctx, doc)

    # --- Clause 8.4: autonomous without human oversight → DENIED ---

    def test_autonomous_no_oversight_denied(self):
        """Autonomous AI system + no human oversight → DENIED."""
        ctx = _base_ctx(
            ai_system_type="autonomous",
            has_human_oversight=False,
        )
        result = self._eval(ctx)
        assert result.decision == "DENIED"
        assert result.is_denied

    def test_autonomous_no_oversight_cites_clause_84(self):
        """DENIED for autonomous without oversight cites Clause 8.4."""
        ctx = _base_ctx(
            ai_system_type="autonomous",
            has_human_oversight=False,
        )
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "8.4" in combined

    def test_autonomous_with_oversight_approved(self):
        """Autonomous AI system WITH human oversight → APPROVED."""
        ctx = _base_ctx(
            ai_system_type="autonomous",
            has_human_oversight=True,
        )
        result = self._eval(ctx)
        assert result.decision == "APPROVED"

    def test_non_autonomous_no_oversight_approved(self):
        """Non-autonomous system + no human oversight → APPROVED (Clause 8.4 not triggered)."""
        ctx = _base_ctx(
            ai_system_type="generative",
            has_human_oversight=False,
        )
        result = self._eval(ctx)
        assert result.decision == "APPROVED"

    # --- Clause 8.3: production without data governance → REQUIRES_HUMAN_REVIEW ---

    def test_production_no_data_governance_requires_review(self):
        """Production deployment + no data governance → REQUIRES_HUMAN_REVIEW."""
        ctx = _base_ctx(
            has_data_governance=False,
            deployment_stage="production",
        )
        result = self._eval(ctx)
        assert result.decision == "REQUIRES_HUMAN_REVIEW"
        assert not result.is_denied

    def test_production_no_data_governance_cites_clause_83(self):
        """REQUIRES_HUMAN_REVIEW for missing data governance cites Clause 8.3."""
        ctx = _base_ctx(
            has_data_governance=False,
            deployment_stage="production",
        )
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "8.3" in combined

    def test_testing_no_data_governance_approved(self):
        """Testing stage + no data governance → APPROVED (Clause 8.3 not triggered)."""
        ctx = _base_ctx(
            has_data_governance=False,
            deployment_stage="testing",
        )
        result = self._eval(ctx)
        assert result.decision == "APPROVED"

    def test_production_with_data_governance_approved(self):
        """Production + data governance present → APPROVED."""
        ctx = _base_ctx(has_data_governance=True, deployment_stage="production")
        result = self._eval(ctx)
        assert result.decision == "APPROVED"

    # --- Clause 8.6: third-party AI without supplier assessment → REQUIRES_HUMAN_REVIEW ---

    def test_third_party_no_supplier_assessment_requires_review(self):
        """Third-party AI + no supplier assessment → REQUIRES_HUMAN_REVIEW."""
        ctx = _base_ctx(
            is_third_party_ai=True,
            has_supplier_assessment=False,
        )
        result = self._eval(ctx)
        assert result.decision == "REQUIRES_HUMAN_REVIEW"
        assert not result.is_denied

    def test_third_party_no_supplier_assessment_cites_clause_86(self):
        """REQUIRES_HUMAN_REVIEW for missing supplier assessment cites Clause 8.6."""
        ctx = _base_ctx(
            is_third_party_ai=True,
            has_supplier_assessment=False,
        )
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "8.6" in combined

    def test_third_party_with_supplier_assessment_approved(self):
        """Third-party AI WITH supplier assessment → APPROVED."""
        ctx = _base_ctx(
            is_third_party_ai=True,
            has_supplier_assessment=True,
        )
        result = self._eval(ctx)
        assert result.decision == "APPROVED"

    def test_non_third_party_no_supplier_assessment_approved(self):
        """Non-third-party AI + no supplier assessment → APPROVED (Clause 8.6 not triggered)."""
        ctx = _base_ctx(
            is_third_party_ai=False,
            has_supplier_assessment=False,
        )
        result = self._eval(ctx)
        assert result.decision == "APPROVED"

    # --- Compliant baseline ---

    def test_fully_compliant_approved(self):
        """Fully compliant operations context → APPROVED."""
        ctx = _base_ctx()
        result = self._eval(ctx)
        assert result.decision == "APPROVED"
        assert not result.is_denied

    def test_compliant_result_not_requires_logging(self):
        """Compliant approval should set requires_logging=False."""
        ctx = _base_ctx()
        result = self._eval(ctx)
        assert result.requires_logging is False


# ===========================================================================
# TestISO42001PerformanceFilter (Clause 9 — Performance Evaluation)
# ===========================================================================


class TestISO42001PerformanceFilter:
    """Layer 4: ISO 42001:2023 Clause 9 — Performance Evaluation."""

    def _eval(self, ctx, doc=None):
        if doc is None:
            doc = _base_doc()
        return mod.ISO42001PerformanceFilter().evaluate(ctx, doc)

    # --- Clause 9.1: high-risk without audit trail → DENIED ---

    def test_high_risk_no_audit_trail_denied(self):
        """High-risk system + no audit trail → DENIED."""
        ctx = _base_ctx(risk_level="high", has_audit_trail=False)
        result = self._eval(ctx)
        assert result.decision == "DENIED"
        assert result.is_denied

    def test_high_risk_no_audit_trail_cites_clause_91(self):
        """DENIED for missing audit trail cites Clause 9.1."""
        ctx = _base_ctx(risk_level="high", has_audit_trail=False)
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "9.1" in combined

    def test_limited_risk_no_audit_trail_denied(self):
        """Limited-risk system + no audit trail → DENIED."""
        ctx = _base_ctx(risk_level="limited", has_audit_trail=False)
        result = self._eval(ctx)
        assert result.decision == "DENIED"
        assert result.is_denied

    def test_minimal_risk_no_audit_trail_approved(self):
        """Minimal-risk system + no audit trail → APPROVED (Clause 9.1 not triggered)."""
        ctx = _base_ctx(risk_level="minimal", has_audit_trail=False)
        result = self._eval(ctx)
        assert result.decision == "APPROVED"

    # --- Clause 7.5: production without transparency docs → REQUIRES_HUMAN_REVIEW ---

    def test_production_no_transparency_docs_requires_review(self):
        """Production deployment + no transparency docs → REQUIRES_HUMAN_REVIEW."""
        ctx = _base_ctx(
            has_transparency_docs=False,
            deployment_stage="production",
        )
        result = self._eval(ctx)
        assert result.decision == "REQUIRES_HUMAN_REVIEW"
        assert not result.is_denied

    def test_production_no_transparency_docs_cites_clause_75(self):
        """REQUIRES_HUMAN_REVIEW for missing transparency docs cites Clause 7.5."""
        ctx = _base_ctx(
            has_transparency_docs=False,
            deployment_stage="production",
        )
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "7.5" in combined

    def test_development_no_transparency_docs_approved(self):
        """Development stage + no transparency docs → APPROVED (Clause 7.5 not triggered)."""
        ctx = _base_ctx(
            has_transparency_docs=False,
            deployment_stage="development",
        )
        result = self._eval(ctx)
        assert result.decision == "APPROVED"

    # --- Clause 10.1: high-risk without incident process → REQUIRES_HUMAN_REVIEW ---

    def test_high_risk_no_incident_process_requires_review(self):
        """High-risk system + no incident process → REQUIRES_HUMAN_REVIEW."""
        ctx = _base_ctx(
            risk_level="high",
            has_audit_trail=True,
            has_transparency_docs=True,
            has_incident_process=False,
        )
        result = self._eval(ctx)
        assert result.decision == "REQUIRES_HUMAN_REVIEW"
        assert not result.is_denied

    def test_high_risk_no_incident_process_cites_clause_101(self):
        """REQUIRES_HUMAN_REVIEW for missing incident process cites Clause 10.1."""
        ctx = _base_ctx(
            risk_level="high",
            has_audit_trail=True,
            has_transparency_docs=True,
            has_incident_process=False,
        )
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "10.1" in combined

    def test_limited_risk_no_incident_process_approved(self):
        """Limited-risk + no incident process → APPROVED (Clause 10.1 not triggered)."""
        ctx = _base_ctx(
            risk_level="limited",
            has_incident_process=False,
        )
        result = self._eval(ctx)
        assert result.decision == "APPROVED"

    # --- Compliant baseline ---

    def test_fully_compliant_approved(self):
        """Fully compliant performance evaluation context → APPROVED."""
        ctx = _base_ctx()
        result = self._eval(ctx)
        assert result.decision == "APPROVED"
        assert not result.is_denied

    def test_compliant_result_not_requires_logging(self):
        """Compliant approval should set requires_logging=False."""
        ctx = _base_ctx()
        result = self._eval(ctx)
        assert result.requires_logging is False

    def test_compliant_cites_clause_9(self):
        """Compliant approval cites ISO 42001:2023 Clause 9."""
        ctx = _base_ctx()
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "9" in combined


# ===========================================================================
# TestISO42001GovernanceOrchestrator
# ===========================================================================


class TestISO42001GovernanceOrchestrator:
    """Full orchestrator pipeline tests."""

    def _run(self, ctx, doc=None):
        if doc is None:
            doc = _base_doc()
        return mod.ISO42001GovernanceOrchestrator().evaluate(ctx, doc)

    def test_returns_four_results(self):
        """Orchestrator always returns exactly four FilterResult objects."""
        ctx = _base_ctx()
        results = self._run(ctx)
        assert len(results) == 4

    def test_all_four_filters_run_even_on_denial(self):
        """All four filters run regardless of earlier DENIED results."""
        ctx = _base_ctx(risk_level="high", has_aims_policy=False)
        results = self._run(ctx)
        assert len(results) == 4

    def test_filter_names_present(self):
        """Each result carries a non-empty filter_name."""
        ctx = _base_ctx()
        results = self._run(ctx)
        for r in results:
            assert r.filter_name

    def test_fully_compliant_all_approved(self):
        """Fully compliant context → all four results APPROVED."""
        ctx = _base_ctx()
        results = self._run(ctx)
        for r in results:
            assert r.decision == "APPROVED", f"{r.filter_name}: {r.decision}"

    def test_policy_denial_appears_in_first_result(self):
        """Policy DENIED appears in first result for high-risk without policy."""
        ctx = _base_ctx(risk_level="high", has_aims_policy=False)
        results = self._run(ctx)
        assert results[0].decision == "DENIED"

    def test_risk_denial_appears_in_second_result(self):
        """Risk DENIED appears in second result for unacceptable risk system."""
        ctx = _base_ctx(risk_level="unacceptable")
        results = self._run(ctx)
        assert results[1].decision == "DENIED"

    def test_operations_denial_appears_in_third_result(self):
        """Operations DENIED appears in third result for autonomous without oversight."""
        ctx = _base_ctx(
            ai_system_type="autonomous",
            has_human_oversight=False,
        )
        results = self._run(ctx)
        assert results[2].decision == "DENIED"

    def test_performance_denial_appears_in_fourth_result(self):
        """Performance DENIED appears in fourth result for limited-risk without audit trail."""
        ctx = _base_ctx(risk_level="limited", has_audit_trail=False)
        results = self._run(ctx)
        assert results[3].decision == "DENIED"

    def test_operations_requires_review_propagates(self):
        """Operations REQUIRES_HUMAN_REVIEW for production without data governance."""
        ctx = _base_ctx(
            has_data_governance=False,
            deployment_stage="production",
        )
        results = self._run(ctx)
        assert results[2].decision == "REQUIRES_HUMAN_REVIEW"

    def test_performance_requires_review_propagates(self):
        """Performance REQUIRES_HUMAN_REVIEW for production without transparency docs."""
        ctx = _base_ctx(
            has_transparency_docs=False,
            deployment_stage="production",
        )
        results = self._run(ctx)
        assert results[3].decision == "REQUIRES_HUMAN_REVIEW"


# ===========================================================================
# TestISO42001ComplianceReport
# ===========================================================================


class TestISO42001ComplianceReport:
    """Report aggregation, overall_decision, is_compliant, and conformity_level tests."""

    def _make_report(self, ctx, doc=None):
        if doc is None:
            doc = _base_doc()
        orchestrator = mod.ISO42001GovernanceOrchestrator()
        results = orchestrator.evaluate(ctx, doc)
        return mod.ISO42001ComplianceReport(
            context=ctx,
            document=doc,
            filter_results=results,
        )

    # --- overall_decision aggregation ---

    def test_all_approved_overall_approved(self):
        """All filters APPROVED → overall_decision == APPROVED."""
        report = self._make_report(_base_ctx())
        assert report.overall_decision == "APPROVED"

    def test_all_approved_is_compliant(self):
        """All filters APPROVED → is_compliant == True."""
        report = self._make_report(_base_ctx())
        assert report.is_compliant is True

    def test_one_denied_overall_denied(self):
        """One DENIED filter → overall_decision == DENIED."""
        ctx = _base_ctx(risk_level="high", has_aims_policy=False)
        report = self._make_report(ctx)
        assert report.overall_decision == "DENIED"

    def test_one_denied_not_compliant(self):
        """One DENIED filter → is_compliant == False."""
        ctx = _base_ctx(risk_level="high", has_aims_policy=False)
        report = self._make_report(ctx)
        assert report.is_compliant is False

    def test_requires_human_review_overall_requires_review(self):
        """REQUIRES_HUMAN_REVIEW (no DENIED) → overall_decision == REQUIRES_HUMAN_REVIEW."""
        ctx = _base_ctx(
            risk_level="minimal",
            has_aims_policy=False,
            deployment_stage="production",
        )
        report = self._make_report(ctx)
        assert report.overall_decision == "REQUIRES_HUMAN_REVIEW"

    def test_requires_human_review_is_compliant(self):
        """REQUIRES_HUMAN_REVIEW without DENIED → is_compliant == True."""
        ctx = _base_ctx(
            risk_level="minimal",
            has_aims_policy=False,
            deployment_stage="production",
        )
        report = self._make_report(ctx)
        assert report.is_compliant is True

    def test_denied_takes_priority_over_requires_review(self):
        """DENIED takes priority over REQUIRES_HUMAN_REVIEW in overall_decision."""
        # Policy: high-risk without policy → DENIED
        # Performance: production without transparency docs → REQUIRES_HUMAN_REVIEW
        ctx = _base_ctx(
            risk_level="high",
            has_aims_policy=False,
            has_transparency_docs=False,
            deployment_stage="production",
        )
        report = self._make_report(ctx)
        assert report.overall_decision == "DENIED"

    # --- conformity_level ---

    def test_all_approved_conformity_level_full(self):
        """All APPROVED → conformity_level == FULL."""
        report = self._make_report(_base_ctx())
        assert report.conformity_level == "FULL"

    def test_requires_review_conformity_level_partial(self):
        """Any REQUIRES_HUMAN_REVIEW (no DENIED) → conformity_level == PARTIAL."""
        ctx = _base_ctx(
            risk_level="minimal",
            has_aims_policy=False,
            deployment_stage="production",
        )
        report = self._make_report(ctx)
        assert report.conformity_level == "PARTIAL"

    def test_denied_conformity_level_non_conforming(self):
        """Any DENIED → conformity_level == NON_CONFORMING."""
        ctx = _base_ctx(risk_level="unacceptable")
        report = self._make_report(ctx)
        assert report.conformity_level == "NON_CONFORMING"

    # --- compliance_summary content ---

    def test_compliance_summary_contains_user_id(self):
        """compliance_summary includes the user_id."""
        ctx = _base_ctx(user_id="test-user-iso-42")
        report = self._make_report(ctx)
        assert "test-user-iso-42" in report.compliance_summary

    def test_compliance_summary_contains_overall_decision(self):
        """compliance_summary includes the overall decision string."""
        ctx = _base_ctx()
        report = self._make_report(ctx)
        assert report.overall_decision in report.compliance_summary

    def test_compliance_summary_contains_all_filter_names(self):
        """compliance_summary lists all four filter names."""
        ctx = _base_ctx()
        report = self._make_report(ctx)
        summary = report.compliance_summary
        assert "ISO42001_POLICY_FILTER" in summary
        assert "ISO42001_RISK_FILTER" in summary
        assert "ISO42001_OPERATIONS_FILTER" in summary
        assert "ISO42001_PERFORMANCE_FILTER" in summary

    def test_compliance_summary_contains_conformity_level(self):
        """compliance_summary includes the conformity level."""
        ctx = _base_ctx()
        report = self._make_report(ctx)
        assert report.conformity_level in report.compliance_summary

    # --- FilterResult.is_denied semantics ---

    def test_filter_result_is_denied_false_for_approved(self):
        """FilterResult.is_denied is False for APPROVED decision."""
        result = mod.FilterResult(
            filter_name="TEST",
            decision="APPROVED",
            reason="ok",
            regulation_citation="",
        )
        assert result.is_denied is False

    def test_filter_result_is_denied_false_for_requires_review(self):
        """FilterResult.is_denied is False for REQUIRES_HUMAN_REVIEW decision."""
        result = mod.FilterResult(
            filter_name="TEST",
            decision="REQUIRES_HUMAN_REVIEW",
            reason="needs review",
            regulation_citation="",
        )
        assert result.is_denied is False

    def test_filter_result_is_denied_true_for_denied(self):
        """FilterResult.is_denied is True only for DENIED decision."""
        result = mod.FilterResult(
            filter_name="TEST",
            decision="DENIED",
            reason="denied",
            regulation_citation="",
        )
        assert result.is_denied is True
