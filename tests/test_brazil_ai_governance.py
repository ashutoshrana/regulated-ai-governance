"""
Tests for 22_brazil_ai_governance.py — Four-layer Brazil AI governance
framework covering LGPD, Brazil AI Bill PL 2338/2023, ANPD Guidelines,
and Brazilian Sectoral Requirements.
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
    _name = "brazil_ai_governance_22"
    spec = importlib.util.spec_from_file_location(
        _name,
        os.path.join(
            os.path.dirname(__file__), "..", "examples", "22_brazil_ai_governance.py"
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
    """Return a fully-compliant LOW-risk GENERAL-sector context."""
    defaults = dict(
        user_id="u1",
        sector=mod.BrazilSector.GENERAL,
        ai_risk_level=mod.BrazilAIRiskLevel.LOW,
        # LGPD
        involves_personal_data=False,
        involves_sensitive_personal_data=False,
        lgpd_legal_basis="none",
        has_lgpd_explicit_consent=False,
        involves_cross_border_transfer=False,
        has_lgpd_transfer_mechanism=False,
        has_processing_records=True,
        # AI Bill
        is_high_risk_ai=False,
        has_conformity_assessment=False,
        is_automated_decision_making=False,
        affects_fundamental_rights=False,
        human_review_available=True,
        has_incident_reporting=False,
        is_prohibited_ai_practice=False,
        # ANPD
        is_large_scale_processing=False,
        has_privacy_by_design=True,
        involves_excessive_data_collection=False,
        has_dpo_appointed=True,
        # Sectoral
        is_clinical_ai=False,
        physician_oversight_available=False,
        is_credit_scoring_ai=False,
        explainability_available=True,
        is_employment_decision_ai=False,
        bias_audit_completed=False,
    )
    defaults.update(overrides)
    return mod.BrazilAIContext(**defaults)


def _base_doc(**overrides):
    """Return a minimal non-sensitive document."""
    defaults = dict(
        document_id="d1",
        document_type="REPORT",
        contains_personal_data=False,
        contains_sensitive_data=False,
        data_subject_count=0,
        is_ai_model_output=False,
        classification="PUBLIC",
    )
    defaults.update(overrides)
    return mod.BrazilAIDocument(**defaults)


def _personal_data_ctx(**overrides):
    """Fully-compliant context that handles personal data."""
    base = dict(
        involves_personal_data=True,
        lgpd_legal_basis="consent",
        has_lgpd_explicit_consent=True,
        has_processing_records=True,
    )
    base.update(overrides)
    return _base_ctx(**base)


def _high_risk_compliant_ctx(**overrides):
    """Fully-compliant HIGH-risk context."""
    base = dict(
        ai_risk_level=mod.BrazilAIRiskLevel.HIGH,
        is_high_risk_ai=True,
        has_conformity_assessment=True,
        has_incident_reporting=True,
        involves_personal_data=True,
        lgpd_legal_basis="consent",
        has_lgpd_explicit_consent=True,
        has_processing_records=True,
        is_automated_decision_making=True,
        affects_fundamental_rights=True,
        human_review_available=True,
    )
    base.update(overrides)
    return _base_ctx(**base)


# ===========================================================================
# TestLGPDDataProtectionFilter
# ===========================================================================


class TestLGPDDataProtectionFilter:
    """Layer 1: LGPD — Lei Geral de Proteção de Dados."""

    def _eval(self, ctx, doc=None):
        if doc is None:
            doc = _base_doc()
        return mod.LGPDDataProtectionFilter().evaluate(ctx, doc)

    def test_valid_legal_basis_approved(self):
        """Personal data with valid legal basis 'consent' → APPROVED."""
        ctx = _personal_data_ctx()
        result = self._eval(ctx)
        assert result.decision == mod.BrazilAIDecision.APPROVED
        assert not result.is_denied

    def test_invalid_legal_basis_denied(self):
        """Personal data with lgpd_legal_basis='none' → DENIED."""
        ctx = _base_ctx(involves_personal_data=True, lgpd_legal_basis="none")
        result = self._eval(ctx)
        assert result.is_denied
        assert result.decision == mod.BrazilAIDecision.DENIED

    def test_invalid_legal_basis_cites_lgpd_art7(self):
        """Denial for invalid legal basis cites LGPD Art. 7."""
        ctx = _base_ctx(involves_personal_data=True, lgpd_legal_basis="none")
        result = self._eval(ctx)
        assert "LGPD Art. 7" in result.regulation_citation

    def test_sensitive_data_without_consent_denied(self):
        """Sensitive personal data + no explicit consent + not legal_obligation → DENIED."""
        ctx = _personal_data_ctx(
            involves_sensitive_personal_data=True,
            has_lgpd_explicit_consent=False,
            lgpd_legal_basis="consent",
        )
        result = self._eval(ctx)
        assert result.is_denied
        assert result.decision == mod.BrazilAIDecision.DENIED

    def test_sensitive_data_without_consent_cites_art11(self):
        """LGPD Art. 11 must appear in regulation_citation for sensitive data denial."""
        ctx = _personal_data_ctx(
            involves_sensitive_personal_data=True,
            has_lgpd_explicit_consent=False,
            lgpd_legal_basis="consent",
        )
        result = self._eval(ctx)
        assert "LGPD Art. 11" in result.regulation_citation

    def test_sensitive_data_legal_obligation_approved(self):
        """Sensitive data with legal_obligation basis (no explicit consent) → APPROVED."""
        ctx = _personal_data_ctx(
            involves_sensitive_personal_data=True,
            has_lgpd_explicit_consent=False,
            lgpd_legal_basis="legal_obligation",
        )
        result = self._eval(ctx)
        assert result.decision == mod.BrazilAIDecision.APPROVED

    def test_cross_border_without_mechanism_denied(self):
        """Cross-border transfer + no transfer mechanism → DENIED."""
        ctx = _personal_data_ctx(
            involves_cross_border_transfer=True,
            has_lgpd_transfer_mechanism=False,
        )
        result = self._eval(ctx)
        assert result.is_denied
        assert result.decision == mod.BrazilAIDecision.DENIED

    def test_cross_border_denial_cites_art33(self):
        """LGPD Art. 33 must appear in regulation_citation for cross-border denial."""
        ctx = _personal_data_ctx(
            involves_cross_border_transfer=True,
            has_lgpd_transfer_mechanism=False,
        )
        result = self._eval(ctx)
        assert "LGPD Art. 33" in result.regulation_citation

    def test_missing_processing_records_requires_human_review(self):
        """Personal data + no processing records → REQUIRES_HUMAN_REVIEW."""
        ctx = _personal_data_ctx(has_processing_records=False)
        result = self._eval(ctx)
        assert result.decision == mod.BrazilAIDecision.REQUIRES_HUMAN_REVIEW
        assert not result.is_denied

    def test_missing_processing_records_cites_art37(self):
        """LGPD Art. 37 must appear in regulation_citation for missing records."""
        ctx = _personal_data_ctx(has_processing_records=False)
        result = self._eval(ctx)
        assert "LGPD Art. 37" in result.regulation_citation


# ===========================================================================
# TestBrazilAIBillFilter
# ===========================================================================


class TestBrazilAIBillFilter:
    """Layer 2: Brazil AI Bill PL 2338/2023."""

    def _eval(self, ctx, doc=None):
        if doc is None:
            doc = _base_doc()
        return mod.BrazilAIBillFilter().evaluate(ctx, doc)

    def test_high_risk_without_conformity_assessment_denied(self):
        """High-risk AI + no conformity assessment → DENIED."""
        ctx = _base_ctx(
            is_high_risk_ai=True,
            has_conformity_assessment=False,
            has_incident_reporting=True,
        )
        result = self._eval(ctx)
        assert result.is_denied
        assert result.decision == mod.BrazilAIDecision.DENIED

    def test_high_risk_no_conformity_cites_art3(self):
        """Denial for missing conformity assessment cites Brazil AI Bill Art. 3."""
        ctx = _base_ctx(
            is_high_risk_ai=True,
            has_conformity_assessment=False,
            has_incident_reporting=True,
        )
        result = self._eval(ctx)
        assert "Art. 3" in result.regulation_citation

    def test_automated_decisions_affecting_rights_without_human_review_requires_review(self):
        """Automated decisions affecting fundamental rights without human review → REQUIRES_HUMAN_REVIEW."""
        ctx = _base_ctx(
            is_automated_decision_making=True,
            affects_fundamental_rights=True,
            human_review_available=False,
        )
        result = self._eval(ctx)
        assert result.decision == mod.BrazilAIDecision.REQUIRES_HUMAN_REVIEW
        assert not result.is_denied

    def test_automated_decisions_cites_art14(self):
        """REQUIRES_HUMAN_REVIEW for automated decisions cites Brazil AI Bill Art. 14."""
        ctx = _base_ctx(
            is_automated_decision_making=True,
            affects_fundamental_rights=True,
            human_review_available=False,
        )
        result = self._eval(ctx)
        assert "Art. 14" in result.regulation_citation

    def test_high_risk_without_incident_reporting_requires_review(self):
        """High-risk AI + conformity assessment present but no incident reporting → REQUIRES_HUMAN_REVIEW."""
        ctx = _base_ctx(
            is_high_risk_ai=True,
            has_conformity_assessment=True,
            has_incident_reporting=False,
        )
        result = self._eval(ctx)
        assert result.decision == mod.BrazilAIDecision.REQUIRES_HUMAN_REVIEW
        assert not result.is_denied

    def test_incident_reporting_required_cites_art16(self):
        """REQUIRES_HUMAN_REVIEW for missing incident reporting cites Brazil AI Bill Art. 16."""
        ctx = _base_ctx(
            is_high_risk_ai=True,
            has_conformity_assessment=True,
            has_incident_reporting=False,
        )
        result = self._eval(ctx)
        assert "Art. 16" in result.regulation_citation

    def test_prohibited_ai_practice_denied(self):
        """is_prohibited_ai_practice=True → DENIED."""
        ctx = _base_ctx(is_prohibited_ai_practice=True)
        result = self._eval(ctx)
        assert result.is_denied
        assert result.decision == mod.BrazilAIDecision.DENIED

    def test_prohibited_practice_cites_art22(self):
        """Denial for prohibited practice cites Brazil AI Bill Art. 22."""
        ctx = _base_ctx(is_prohibited_ai_practice=True)
        result = self._eval(ctx)
        assert "Art. 22" in result.regulation_citation

    def test_low_risk_no_issues_approved(self):
        """LOW-risk AI with no prohibited practice → APPROVED."""
        ctx = _base_ctx()
        result = self._eval(ctx)
        assert result.decision == mod.BrazilAIDecision.APPROVED
        assert not result.is_denied


# ===========================================================================
# TestANPDGuidelinesFilter
# ===========================================================================


class TestANPDGuidelinesFilter:
    """Layer 3: ANPD Guidelines."""

    def _eval(self, ctx, doc=None):
        if doc is None:
            doc = _base_doc()
        return mod.ANPDGuidelinesFilter().evaluate(ctx, doc)

    def test_large_scale_without_privacy_by_design_requires_review(self):
        """Large-scale processing + no privacy by design → REQUIRES_HUMAN_REVIEW."""
        ctx = _base_ctx(
            is_large_scale_processing=True,
            has_privacy_by_design=False,
            has_dpo_appointed=True,
        )
        result = self._eval(ctx)
        assert result.decision == mod.BrazilAIDecision.REQUIRES_HUMAN_REVIEW
        assert not result.is_denied

    def test_privacy_by_design_cites_anpd_orientation(self):
        """REQUIRES_HUMAN_REVIEW for missing privacy by design cites ANPD Orientation 1/2023."""
        ctx = _base_ctx(
            is_large_scale_processing=True,
            has_privacy_by_design=False,
            has_dpo_appointed=True,
        )
        result = self._eval(ctx)
        assert "ANPD Orientation 1/2023" in result.regulation_citation

    def test_excessive_data_collection_denied(self):
        """involves_excessive_data_collection=True → DENIED."""
        ctx = _base_ctx(involves_excessive_data_collection=True)
        result = self._eval(ctx)
        assert result.is_denied
        assert result.decision == mod.BrazilAIDecision.DENIED

    def test_data_minimization_violation_cites_art6(self):
        """DENIED for excessive data collection cites LGPD Art. 6 VI."""
        ctx = _base_ctx(involves_excessive_data_collection=True)
        result = self._eval(ctx)
        assert "Art. 6 VI" in result.regulation_citation

    def test_large_scale_without_dpo_requires_review(self):
        """Large-scale processing + no DPO → REQUIRES_HUMAN_REVIEW."""
        ctx = _base_ctx(
            is_large_scale_processing=True,
            has_privacy_by_design=True,
            has_dpo_appointed=False,
        )
        result = self._eval(ctx)
        assert result.decision == mod.BrazilAIDecision.REQUIRES_HUMAN_REVIEW
        assert not result.is_denied

    def test_dpo_requirement_cites_art41(self):
        """REQUIRES_HUMAN_REVIEW for missing DPO cites LGPD Art. 41."""
        ctx = _base_ctx(
            is_large_scale_processing=True,
            has_privacy_by_design=True,
            has_dpo_appointed=False,
        )
        result = self._eval(ctx)
        assert "Art. 41" in result.regulation_citation

    def test_small_scale_no_issues_approved(self):
        """Non-large-scale processing + no excessive data collection → APPROVED."""
        ctx = _base_ctx()
        result = self._eval(ctx)
        assert result.decision == mod.BrazilAIDecision.APPROVED
        assert not result.is_denied


# ===========================================================================
# TestBrazilSectoralFilter
# ===========================================================================


class TestBrazilSectoralFilter:
    """Layer 4: Brazilian Sectoral Requirements."""

    def _eval(self, ctx, doc=None):
        if doc is None:
            doc = _base_doc()
        return mod.BrazilSectoralFilter().evaluate(ctx, doc)

    def test_healthcare_clinical_ai_without_physician_oversight_denied(self):
        """HEALTHCARE sector + is_clinical_ai + no physician oversight → DENIED."""
        ctx = _base_ctx(
            sector=mod.BrazilSector.HEALTHCARE,
            is_clinical_ai=True,
            physician_oversight_available=False,
        )
        result = self._eval(ctx)
        assert result.is_denied
        assert result.decision == mod.BrazilAIDecision.DENIED

    def test_healthcare_denial_cites_cfm_resolution(self):
        """Denial for missing physician oversight cites CFM Resolution 2299/2021."""
        ctx = _base_ctx(
            sector=mod.BrazilSector.HEALTHCARE,
            is_clinical_ai=True,
            physician_oversight_available=False,
        )
        result = self._eval(ctx)
        assert "CFM Resolution 2299/2021" in result.regulation_citation

    def test_healthcare_with_physician_oversight_approved(self):
        """HEALTHCARE sector + is_clinical_ai + physician oversight present → APPROVED."""
        ctx = _base_ctx(
            sector=mod.BrazilSector.HEALTHCARE,
            is_clinical_ai=True,
            physician_oversight_available=True,
        )
        result = self._eval(ctx)
        assert result.decision == mod.BrazilAIDecision.APPROVED
        assert not result.is_denied

    def test_financial_credit_scoring_without_explainability_requires_review(self):
        """FINANCIAL sector + is_credit_scoring_ai + no explainability → REQUIRES_HUMAN_REVIEW."""
        ctx = _base_ctx(
            sector=mod.BrazilSector.FINANCIAL,
            is_credit_scoring_ai=True,
            explainability_available=False,
        )
        result = self._eval(ctx)
        assert result.decision == mod.BrazilAIDecision.REQUIRES_HUMAN_REVIEW
        assert not result.is_denied

    def test_financial_credit_scoring_cites_bcb_circular(self):
        """REQUIRES_HUMAN_REVIEW for missing explainability cites BCB Circular 3.978/2020."""
        ctx = _base_ctx(
            sector=mod.BrazilSector.FINANCIAL,
            is_credit_scoring_ai=True,
            explainability_available=False,
        )
        result = self._eval(ctx)
        assert "BCB Circular 3.978/2020" in result.regulation_citation

    def test_employment_ai_without_bias_audit_requires_review(self):
        """EMPLOYMENT sector + is_employment_decision_ai + no bias audit → REQUIRES_HUMAN_REVIEW."""
        ctx = _base_ctx(
            sector=mod.BrazilSector.EMPLOYMENT,
            is_employment_decision_ai=True,
            bias_audit_completed=False,
        )
        result = self._eval(ctx)
        assert result.decision == mod.BrazilAIDecision.REQUIRES_HUMAN_REVIEW
        assert not result.is_denied

    def test_employment_bias_audit_cites_clt_mpt(self):
        """REQUIRES_HUMAN_REVIEW for missing bias audit cites CLT + MPT Guidance."""
        ctx = _base_ctx(
            sector=mod.BrazilSector.EMPLOYMENT,
            is_employment_decision_ai=True,
            bias_audit_completed=False,
        )
        result = self._eval(ctx)
        assert "CLT" in result.regulation_citation or "MPT" in result.regulation_citation

    def test_general_sector_no_sectoral_triggers_approved(self):
        """GENERAL sector + no clinical/credit/employment AI → APPROVED (sectoral not applicable)."""
        ctx = _base_ctx(sector=mod.BrazilSector.GENERAL)
        result = self._eval(ctx)
        assert result.decision == mod.BrazilAIDecision.APPROVED
        assert not result.is_denied


# ===========================================================================
# TestFullPipeline
# ===========================================================================


class TestFullPipeline:
    """Integration tests using the full orchestrator pipeline."""

    def _evaluate(self, ctx, doc=None):
        if doc is None:
            doc = _base_doc()
        orchestrator = mod.BrazilAIGovernanceOrchestrator()
        results = orchestrator.evaluate(ctx, doc)
        return mod.BrazilAIGovernanceReport(
            context=ctx, document=doc, filter_results=results
        )

    def test_fully_compliant_approved_path(self):
        """All filters pass for a fully compliant HIGH-risk healthcare AI → APPROVED."""
        ctx = mod.BrazilAIContext(
            user_id="pipeline-test-01",
            sector=mod.BrazilSector.HEALTHCARE,
            ai_risk_level=mod.BrazilAIRiskLevel.HIGH,
            involves_personal_data=True,
            involves_sensitive_personal_data=True,
            lgpd_legal_basis="consent",
            has_lgpd_explicit_consent=True,
            involves_cross_border_transfer=False,
            has_lgpd_transfer_mechanism=False,
            has_processing_records=True,
            is_high_risk_ai=True,
            has_conformity_assessment=True,
            is_automated_decision_making=True,
            affects_fundamental_rights=True,
            human_review_available=True,
            has_incident_reporting=True,
            is_prohibited_ai_practice=False,
            is_large_scale_processing=True,
            has_privacy_by_design=True,
            involves_excessive_data_collection=False,
            has_dpo_appointed=True,
            is_clinical_ai=True,
            physician_oversight_available=True,
            is_credit_scoring_ai=False,
            explainability_available=True,
            is_employment_decision_ai=False,
            bias_audit_completed=False,
        )
        report = self._evaluate(ctx)
        assert report.overall_decision == mod.BrazilAIDecision.APPROVED
        assert report.is_compliant

    def test_prohibited_practice_pipeline_denied(self):
        """Prohibited AI practice → overall DENIED pipeline result."""
        ctx = _base_ctx(is_prohibited_ai_practice=True)
        report = self._evaluate(ctx)
        assert report.overall_decision == mod.BrazilAIDecision.DENIED
        assert not report.is_compliant

    def test_denial_takes_priority_over_review(self):
        """DENIED in one filter + REQUIRES_HUMAN_REVIEW in another → overall DENIED."""
        ctx = _base_ctx(
            # triggers LGPD denial
            involves_personal_data=True,
            lgpd_legal_basis="none",
            # also triggers ANPD review (but denial should win)
            is_large_scale_processing=True,
            has_privacy_by_design=False,
            has_dpo_appointed=True,
        )
        report = self._evaluate(ctx)
        assert report.overall_decision == mod.BrazilAIDecision.DENIED


# ===========================================================================
# TestBrazilAIGovernanceReport
# ===========================================================================


class TestBrazilAIGovernanceReport:
    """Tests for BrazilAIGovernanceReport properties."""

    def _report(self, ctx, doc=None):
        if doc is None:
            doc = _base_doc()
        orchestrator = mod.BrazilAIGovernanceOrchestrator()
        results = orchestrator.evaluate(ctx, doc)
        return mod.BrazilAIGovernanceReport(
            context=ctx, document=doc, filter_results=results
        )

    def test_overall_decision_denied_when_any_filter_denied(self):
        """If any filter returns DENIED, overall_decision is DENIED."""
        ctx = _base_ctx(involves_personal_data=True, lgpd_legal_basis="none")
        report = self._report(ctx)
        assert report.overall_decision == mod.BrazilAIDecision.DENIED

    def test_overall_decision_requires_review_when_no_denial(self):
        """No DENIED + at least one REQUIRES_HUMAN_REVIEW → REQUIRES_HUMAN_REVIEW."""
        ctx = _base_ctx(
            is_large_scale_processing=True,
            has_privacy_by_design=False,
            has_dpo_appointed=True,
        )
        report = self._report(ctx)
        assert report.overall_decision == mod.BrazilAIDecision.REQUIRES_HUMAN_REVIEW

    def test_overall_decision_approved_when_all_pass(self):
        """All filters APPROVED → overall_decision APPROVED."""
        ctx = _base_ctx()
        report = self._report(ctx)
        assert report.overall_decision == mod.BrazilAIDecision.APPROVED

    def test_is_compliant_false_when_denied(self):
        """is_compliant is False when overall_decision is DENIED."""
        ctx = _base_ctx(involves_personal_data=True, lgpd_legal_basis="none")
        report = self._report(ctx)
        assert not report.is_compliant

    def test_is_compliant_false_when_requires_review(self):
        """is_compliant is False when overall_decision is REQUIRES_HUMAN_REVIEW."""
        ctx = _base_ctx(
            is_large_scale_processing=True,
            has_privacy_by_design=False,
            has_dpo_appointed=True,
        )
        report = self._report(ctx)
        assert not report.is_compliant

    def test_is_compliant_true_when_approved(self):
        """is_compliant is True when overall_decision is APPROVED."""
        ctx = _base_ctx()
        report = self._report(ctx)
        assert report.is_compliant

    def test_compliance_summary_mentions_overall_decision(self):
        """compliance_summary string contains the overall decision value."""
        ctx = _base_ctx(involves_personal_data=True, lgpd_legal_basis="none")
        report = self._report(ctx)
        assert "DENIED" in report.compliance_summary

    def test_compliance_summary_all_approved(self):
        """compliance_summary for fully compliant system mentions COMPLIANT."""
        ctx = _base_ctx()
        report = self._report(ctx)
        assert "COMPLIANT" in report.compliance_summary


# ===========================================================================
# Edge Cases
# ===========================================================================


class TestEdgeCases:
    """Edge case and boundary condition tests."""

    def test_general_sector_no_sectoral_checks(self):
        """GENERAL sector skips all sectoral-specific checks → APPROVED in Layer 4."""
        ctx = _base_ctx(
            sector=mod.BrazilSector.GENERAL,
            is_clinical_ai=True,           # would trigger denial in HEALTHCARE
            physician_oversight_available=False,
            is_credit_scoring_ai=True,      # would trigger review in FINANCIAL
            explainability_available=False,
            is_employment_decision_ai=True, # would trigger review in EMPLOYMENT
            bias_audit_completed=False,
        )
        result = mod.BrazilSectoralFilter().evaluate(ctx, _base_doc())
        assert result.decision == mod.BrazilAIDecision.APPROVED
        assert not result.is_denied

    def test_low_risk_ai_passes_ai_bill_gate(self):
        """LOW-risk AI with no prohibited practice passes the AI Bill filter."""
        ctx = _base_ctx(
            ai_risk_level=mod.BrazilAIRiskLevel.LOW,
            is_high_risk_ai=False,
            is_prohibited_ai_practice=False,
        )
        result = mod.BrazilAIBillFilter().evaluate(ctx, _base_doc())
        assert result.decision == mod.BrazilAIDecision.APPROVED
        assert not result.is_denied

    def test_is_denied_false_for_requires_human_review(self):
        """is_denied is False for REQUIRES_HUMAN_REVIEW decisions."""
        ctx = _base_ctx(
            is_large_scale_processing=True,
            has_privacy_by_design=False,
            has_dpo_appointed=True,
        )
        result = mod.ANPDGuidelinesFilter().evaluate(ctx, _base_doc())
        assert result.decision == mod.BrazilAIDecision.REQUIRES_HUMAN_REVIEW
        assert not result.is_denied

    def test_is_denied_true_only_for_denied(self):
        """is_denied is True only for DENIED, not APPROVED."""
        ctx_approved = _base_ctx()
        result_approved = mod.LGPDDataProtectionFilter().evaluate(ctx_approved, _base_doc())
        assert not result_approved.is_denied

        ctx_denied = _base_ctx(involves_personal_data=True, lgpd_legal_basis="none")
        result_denied = mod.LGPDDataProtectionFilter().evaluate(ctx_denied, _base_doc())
        assert result_denied.is_denied
