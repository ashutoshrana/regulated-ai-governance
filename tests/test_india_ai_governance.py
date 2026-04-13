"""
Tests for 23_india_ai_governance.py — Four-layer India AI governance
framework covering DPDP Act 2023, MEITY AI Advisory 2024, IT Act 2000 /
IT Rules 2011, and India Sectoral AI Requirements (RBI, IRDAI, CDSCO).
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
    _name = "india_ai_governance_23"
    spec = importlib.util.spec_from_file_location(
        _name,
        os.path.join(
            os.path.dirname(__file__), "..", "examples", "23_india_ai_governance.py"
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
        sector=mod.IndiaSector.GENERAL,
        ai_risk_level=mod.IndiaAIRiskLevel.LOW,
        # DPDP
        involves_personal_data=False,
        dpdp_legal_basis="legitimate_uses",
        has_dpdp_consent=True,
        involves_childrens_data=False,
        has_parental_consent=False,
        is_data_principal_access_request=False,
        involves_cross_border_transfer=False,
        destination_country="US",
        # MEITY
        can_generate_synthetic_media=False,
        has_ai_generated_label=True,
        is_election_related_ai=False,
        has_election_content_safeguards=True,
        is_generative_ai=False,
        has_bias_hallucination_testing=True,
        # IT Act
        is_body_corporate=True,
        handles_sensitive_personal_data=False,
        has_reasonable_security_practices=True,
        involves_sensitive_personal_data=False,
        has_written_consent=True,
        involves_third_party_disclosure=False,
        has_disclosure_consent=True,
        # Sectoral
        is_credit_ai=False,
        has_model_risk_management=True,
        is_automated_underwriting=False,
        human_review_available=True,
        is_clinical_decision_support=False,
        has_cdsco_approval=False,
    )
    defaults.update(overrides)
    return mod.IndiaAIContext(**defaults)


def _base_doc(**overrides):
    """Return a minimal, non-sensitive document."""
    defaults = dict(
        document_id="d1",
        document_type="REPORT",
        contains_personal_data=False,
        contains_sensitive_data=False,
        is_ai_output=False,
        classification="PUBLIC",
        data_subject_count=0,
    )
    defaults.update(overrides)
    return mod.IndiaAIDocument(**defaults)


# ===========================================================================
# TestDPDPDataProtectionFilter
# ===========================================================================


class TestDPDPDataProtectionFilter:
    """Layer 1: Digital Personal Data Protection Act 2023."""

    def _eval(self, ctx, doc=None):
        if doc is None:
            doc = _base_doc()
        return mod.DPDPDataProtectionFilter().evaluate(ctx, doc)

    def test_no_legal_basis_denied(self):
        """Personal data + no valid legal basis → DENIED."""
        ctx = _base_ctx(
            involves_personal_data=True,
            dpdp_legal_basis="none",
        )
        result = self._eval(ctx)
        assert result.is_denied
        assert result.decision == mod.IndiaAIDecision.DENIED

    def test_no_legal_basis_cites_dpdp_section_4(self):
        """Denial for missing legal basis cites DPDP §4."""
        ctx = _base_ctx(
            involves_personal_data=True,
            dpdp_legal_basis="none",
        )
        result = self._eval(ctx)
        assert "§4" in result.regulation_citation or "4" in result.regulation_citation

    def test_consent_basis_without_consent_denied(self):
        """Consent basis + no valid consent → DENIED."""
        ctx = _base_ctx(
            involves_personal_data=True,
            dpdp_legal_basis="consent",
            has_dpdp_consent=False,
        )
        result = self._eval(ctx)
        assert result.is_denied
        assert result.decision == mod.IndiaAIDecision.DENIED

    def test_consent_basis_without_consent_cites_section_6(self):
        """Denial for missing consent cites DPDP §6."""
        ctx = _base_ctx(
            involves_personal_data=True,
            dpdp_legal_basis="consent",
            has_dpdp_consent=False,
        )
        result = self._eval(ctx)
        assert "§6" in result.regulation_citation or "§6" in result.reason

    def test_childrens_data_without_parental_consent_denied(self):
        """Children's data + no parental consent → DENIED."""
        ctx = _base_ctx(
            involves_childrens_data=True,
            has_parental_consent=False,
        )
        result = self._eval(ctx)
        assert result.is_denied
        assert result.decision == mod.IndiaAIDecision.DENIED

    def test_childrens_data_cites_section_9(self):
        """Children's data denial cites DPDP §9."""
        ctx = _base_ctx(
            involves_childrens_data=True,
            has_parental_consent=False,
        )
        result = self._eval(ctx)
        assert "§9" in result.regulation_citation or "§9" in result.reason

    def test_data_principal_access_request_approved_immediately(self):
        """Data principal access request → APPROVED immediately."""
        ctx = _base_ctx(
            is_data_principal_access_request=True,
            # Even with no legal basis — access request takes precedence
            involves_personal_data=True,
            dpdp_legal_basis="none",
        )
        result = self._eval(ctx)
        assert result.decision == mod.IndiaAIDecision.APPROVED
        assert not result.is_denied

    def test_data_principal_access_cites_section_12(self):
        """Access request approval cites DPDP §12."""
        ctx = _base_ctx(is_data_principal_access_request=True)
        result = self._eval(ctx)
        assert "§12" in result.regulation_citation or "§12" in result.reason

    def test_cross_border_to_restricted_country_denied(self):
        """Cross-border transfer to restricted country (CN) → DENIED."""
        ctx = _base_ctx(
            involves_cross_border_transfer=True,
            destination_country="CN",
        )
        result = self._eval(ctx)
        assert result.is_denied
        assert result.decision == mod.IndiaAIDecision.DENIED

    def test_cross_border_restricted_cites_section_16(self):
        """Cross-border denial cites DPDP §16."""
        ctx = _base_ctx(
            involves_cross_border_transfer=True,
            destination_country="RU",
        )
        result = self._eval(ctx)
        assert "§16" in result.regulation_citation or "§16" in result.reason

    def test_state_function_legal_basis_approved_without_consent(self):
        """state_function legal basis → APPROVED even without has_dpdp_consent."""
        ctx = _base_ctx(
            involves_personal_data=True,
            dpdp_legal_basis="state_function",
            has_dpdp_consent=False,
        )
        result = self._eval(ctx)
        assert result.decision == mod.IndiaAIDecision.APPROVED
        assert not result.is_denied

    def test_cross_border_to_non_restricted_country_approved(self):
        """Cross-border transfer to non-restricted country (US) → APPROVED."""
        ctx = _base_ctx(
            involves_cross_border_transfer=True,
            destination_country="US",
        )
        result = self._eval(ctx)
        assert result.decision == mod.IndiaAIDecision.APPROVED
        assert not result.is_denied


# ===========================================================================
# TestMEITYAIAdvisoryFilter
# ===========================================================================


class TestMEITYAIAdvisoryFilter:
    """Layer 2: MEITY AI Advisory 2024."""

    def _eval(self, ctx, doc=None):
        if doc is None:
            doc = _base_doc()
        return mod.MEITYAIAdvisoryFilter().evaluate(ctx, doc)

    def test_synthetic_media_without_label_requires_human_review(self):
        """Synthetic media capability + no label → REQUIRES_HUMAN_REVIEW."""
        ctx = _base_ctx(
            can_generate_synthetic_media=True,
            has_ai_generated_label=False,
        )
        result = self._eval(ctx)
        assert result.decision == mod.IndiaAIDecision.REQUIRES_HUMAN_REVIEW
        assert not result.is_denied

    def test_synthetic_media_without_label_cites_meity(self):
        """REQUIRES_HUMAN_REVIEW for unlabelled synthetic media cites MEITY."""
        ctx = _base_ctx(
            can_generate_synthetic_media=True,
            has_ai_generated_label=False,
        )
        result = self._eval(ctx)
        assert "MEITY" in result.regulation_citation

    def test_election_ai_without_safeguards_denied(self):
        """Election-related AI + no safeguards → DENIED."""
        ctx = _base_ctx(
            is_election_related_ai=True,
            has_election_content_safeguards=False,
        )
        result = self._eval(ctx)
        assert result.is_denied
        assert result.decision == mod.IndiaAIDecision.DENIED

    def test_election_ai_denial_cites_meity(self):
        """Election AI denial cites MEITY in regulation_citation."""
        ctx = _base_ctx(
            is_election_related_ai=True,
            has_election_content_safeguards=False,
        )
        result = self._eval(ctx)
        assert "MEITY" in result.regulation_citation

    def test_generative_high_risk_without_testing_requires_review(self):
        """Generative AI + HIGH risk + no testing → REQUIRES_HUMAN_REVIEW."""
        ctx = _base_ctx(
            is_generative_ai=True,
            ai_risk_level=mod.IndiaAIRiskLevel.HIGH,
            has_bias_hallucination_testing=False,
        )
        result = self._eval(ctx)
        assert result.decision == mod.IndiaAIDecision.REQUIRES_HUMAN_REVIEW
        assert not result.is_denied

    def test_generative_medium_risk_without_testing_requires_review(self):
        """Generative AI + MEDIUM risk + no testing → REQUIRES_HUMAN_REVIEW."""
        ctx = _base_ctx(
            is_generative_ai=True,
            ai_risk_level=mod.IndiaAIRiskLevel.MEDIUM,
            has_bias_hallucination_testing=False,
        )
        result = self._eval(ctx)
        assert result.decision == mod.IndiaAIDecision.REQUIRES_HUMAN_REVIEW

    def test_generative_low_risk_without_testing_approved(self):
        """Generative AI + LOW risk + no testing → APPROVED (low risk exempt)."""
        ctx = _base_ctx(
            is_generative_ai=True,
            ai_risk_level=mod.IndiaAIRiskLevel.LOW,
            has_bias_hallucination_testing=False,
        )
        result = self._eval(ctx)
        assert result.decision == mod.IndiaAIDecision.APPROVED
        assert not result.is_denied

    def test_generative_high_risk_with_testing_approved(self):
        """Generative AI + HIGH risk + testing done → APPROVED."""
        ctx = _base_ctx(
            is_generative_ai=True,
            ai_risk_level=mod.IndiaAIRiskLevel.HIGH,
            has_bias_hallucination_testing=True,
        )
        result = self._eval(ctx)
        assert result.decision == mod.IndiaAIDecision.APPROVED
        assert not result.is_denied


# ===========================================================================
# TestIndiaITActFilter
# ===========================================================================


class TestIndiaITActFilter:
    """Layer 3: IT Act 2000 + IT Rules 2011."""

    def _eval(self, ctx, doc=None):
        if doc is None:
            doc = _base_doc()
        return mod.IndiaITActFilter().evaluate(ctx, doc)

    def test_body_corporate_without_security_practices_requires_review(self):
        """Body corporate + SPDI + no security practices → REQUIRES_HUMAN_REVIEW."""
        ctx = _base_ctx(
            is_body_corporate=True,
            handles_sensitive_personal_data=True,
            has_reasonable_security_practices=False,
        )
        result = self._eval(ctx)
        assert result.decision == mod.IndiaAIDecision.REQUIRES_HUMAN_REVIEW
        assert not result.is_denied

    def test_body_corporate_security_cites_it_act_43a(self):
        """REQUIRES_HUMAN_REVIEW for missing security cites IT Act §43A."""
        ctx = _base_ctx(
            is_body_corporate=True,
            handles_sensitive_personal_data=True,
            has_reasonable_security_practices=False,
        )
        result = self._eval(ctx)
        assert "43A" in result.regulation_citation or "43A" in result.reason

    def test_sensitive_data_without_written_consent_denied(self):
        """Sensitive personal data + no written consent → DENIED."""
        ctx = _base_ctx(
            involves_sensitive_personal_data=True,
            has_written_consent=False,
        )
        result = self._eval(ctx)
        assert result.is_denied
        assert result.decision == mod.IndiaAIDecision.DENIED

    def test_sensitive_data_denial_cites_rule_5(self):
        """Denial for missing written consent cites Rule 5(1)."""
        ctx = _base_ctx(
            involves_sensitive_personal_data=True,
            has_written_consent=False,
        )
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "Rule 5" in combined or "5(1)" in combined

    def test_third_party_disclosure_without_consent_denied(self):
        """Third-party disclosure + SPDI + no disclosure consent → DENIED."""
        ctx = _base_ctx(
            involves_third_party_disclosure=True,
            involves_sensitive_personal_data=True,
            has_written_consent=True,
            has_disclosure_consent=False,
        )
        result = self._eval(ctx)
        assert result.is_denied
        assert result.decision == mod.IndiaAIDecision.DENIED

    def test_third_party_disclosure_cites_rule_6(self):
        """Third-party disclosure denial cites Rule 6."""
        ctx = _base_ctx(
            involves_third_party_disclosure=True,
            involves_sensitive_personal_data=True,
            has_written_consent=True,
            has_disclosure_consent=False,
        )
        result = self._eval(ctx)
        assert "Rule 6" in result.regulation_citation or "Rule 6" in result.reason

    def test_non_sensitive_data_passes_it_act(self):
        """No SPDI involved → APPROVED (IT Act controls not triggered)."""
        ctx = _base_ctx(
            involves_sensitive_personal_data=False,
            handles_sensitive_personal_data=False,
            involves_third_party_disclosure=True,
            has_disclosure_consent=False,
        )
        result = self._eval(ctx)
        assert result.decision == mod.IndiaAIDecision.APPROVED
        assert not result.is_denied


# ===========================================================================
# TestIndiaSectoralFilter
# ===========================================================================


class TestIndiaSectoralFilter:
    """Layer 4: India Sectoral AI Requirements."""

    def _eval(self, ctx, doc=None):
        if doc is None:
            doc = _base_doc()
        return mod.IndiaSectoralFilter().evaluate(ctx, doc)

    def test_banking_credit_ai_without_model_risk_management_requires_review(self):
        """Banking sector + credit AI + no MRM framework → REQUIRES_HUMAN_REVIEW."""
        ctx = _base_ctx(
            sector=mod.IndiaSector.BANKING,
            is_credit_ai=True,
            has_model_risk_management=False,
        )
        result = self._eval(ctx)
        assert result.decision == mod.IndiaAIDecision.REQUIRES_HUMAN_REVIEW
        assert not result.is_denied

    def test_banking_credit_ai_cites_rbi(self):
        """Banking credit AI review cites RBI guidance."""
        ctx = _base_ctx(
            sector=mod.IndiaSector.BANKING,
            is_credit_ai=True,
            has_model_risk_management=False,
        )
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "RBI" in combined or "Reserve Bank of India" in combined

    def test_insurance_automated_underwriting_without_human_review_requires_review(self):
        """Insurance + automated underwriting + no human review → REQUIRES_HUMAN_REVIEW."""
        ctx = _base_ctx(
            sector=mod.IndiaSector.INSURANCE,
            is_automated_underwriting=True,
            human_review_available=False,
        )
        result = self._eval(ctx)
        assert result.decision == mod.IndiaAIDecision.REQUIRES_HUMAN_REVIEW
        assert not result.is_denied

    def test_insurance_underwriting_cites_irdai(self):
        """Insurance underwriting review cites IRDAI."""
        ctx = _base_ctx(
            sector=mod.IndiaSector.INSURANCE,
            is_automated_underwriting=True,
            human_review_available=False,
        )
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "IRDAI" in combined or "Insurance Regulatory" in combined

    def test_healthcare_clinical_ai_without_cdsco_denied(self):
        """Healthcare + clinical decision support + no CDSCO approval → DENIED."""
        ctx = _base_ctx(
            sector=mod.IndiaSector.HEALTHCARE,
            is_clinical_decision_support=True,
            has_cdsco_approval=False,
        )
        result = self._eval(ctx)
        assert result.is_denied
        assert result.decision == mod.IndiaAIDecision.DENIED

    def test_healthcare_clinical_ai_cites_cdsco(self):
        """Healthcare clinical AI denial cites CDSCO."""
        ctx = _base_ctx(
            sector=mod.IndiaSector.HEALTHCARE,
            is_clinical_decision_support=True,
            has_cdsco_approval=False,
        )
        result = self._eval(ctx)
        assert "CDSCO" in result.regulation_citation

    def test_general_sector_passes_all_sectoral(self):
        """GENERAL sector with no special AI types → APPROVED."""
        ctx = _base_ctx(
            sector=mod.IndiaSector.GENERAL,
            is_credit_ai=False,
            is_automated_underwriting=False,
            is_clinical_decision_support=False,
        )
        result = self._eval(ctx)
        assert result.decision == mod.IndiaAIDecision.APPROVED
        assert not result.is_denied


# ===========================================================================
# TestIntegration
# ===========================================================================


class TestIntegration:
    """Integration tests across the full orchestrator."""

    def test_fully_compliant_context_all_approved(self):
        """Fully compliant LOW-risk GENERAL context → all four filters APPROVED."""
        ctx = _base_ctx()
        doc = _base_doc()
        orchestrator = mod.IndiaAIGovernanceOrchestrator()
        results = orchestrator.evaluate(ctx, doc)
        assert len(results) == 4
        for r in results:
            assert r.decision == mod.IndiaAIDecision.APPROVED
            assert not r.is_denied

    def test_denied_path_produces_denied_result(self):
        """DPDP §4 violation → at least one filter result is DENIED."""
        ctx = _base_ctx(
            involves_personal_data=True,
            dpdp_legal_basis="none",
        )
        doc = _base_doc()
        orchestrator = mod.IndiaAIGovernanceOrchestrator()
        results = orchestrator.evaluate(ctx, doc)
        assert any(r.is_denied for r in results)

    def test_orchestrator_returns_four_results(self):
        """Orchestrator always returns exactly four FilterResult objects."""
        ctx = _base_ctx()
        doc = _base_doc()
        orchestrator = mod.IndiaAIGovernanceOrchestrator()
        results = orchestrator.evaluate(ctx, doc)
        assert len(results) == 4


# ===========================================================================
# TestIndiaAIGovernanceReport
# ===========================================================================


class TestIndiaAIGovernanceReport:
    """Tests for IndiaAIGovernanceReport aggregation properties."""

    def _make_report(self, ctx=None, doc=None):
        if ctx is None:
            ctx = _base_ctx()
        if doc is None:
            doc = _base_doc()
        orchestrator = mod.IndiaAIGovernanceOrchestrator()
        results = orchestrator.evaluate(ctx, doc)
        return mod.IndiaAIGovernanceReport(
            context=ctx, document=doc, filter_results=results
        )

    def test_overall_decision_approved_when_all_pass(self):
        """Fully compliant context → overall_decision is APPROVED."""
        report = self._make_report()
        assert report.overall_decision == mod.IndiaAIDecision.APPROVED

    def test_overall_decision_denied_when_any_denied(self):
        """Any DENIED result → overall_decision is DENIED."""
        ctx = _base_ctx(
            involves_personal_data=True,
            dpdp_legal_basis="none",
        )
        report = self._make_report(ctx=ctx)
        assert report.overall_decision == mod.IndiaAIDecision.DENIED

    def test_overall_decision_requires_human_review_when_no_denial_but_review(self):
        """REQUIRES_HUMAN_REVIEW result (no denial) → overall_decision is REQUIRES_HUMAN_REVIEW."""
        ctx = _base_ctx(
            is_body_corporate=True,
            handles_sensitive_personal_data=True,
            has_reasonable_security_practices=False,
        )
        report = self._make_report(ctx=ctx)
        assert report.overall_decision == mod.IndiaAIDecision.REQUIRES_HUMAN_REVIEW

    def test_is_compliant_true_when_no_denial(self):
        """Fully compliant context → is_compliant is True."""
        report = self._make_report()
        assert report.is_compliant is True

    def test_is_compliant_false_when_denied(self):
        """DENIED result → is_compliant is False."""
        ctx = _base_ctx(
            involves_personal_data=True,
            dpdp_legal_basis="none",
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
