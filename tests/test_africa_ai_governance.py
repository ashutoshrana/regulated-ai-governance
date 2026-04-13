"""
Tests for 26_africa_ai_governance.py — Africa AI governance framework covering
Kenya DPA 2019, Nigeria NDPA 2023, South Africa POPIA 2013, and the AU
cross-border transfer rules under the AU Data Policy Framework 2022.
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
    _name = "africa_ai_governance_26"
    spec = importlib.util.spec_from_file_location(
        _name,
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "examples",
            "26_africa_ai_governance.py",
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
    """Return a fully-compliant general-sector Kenya context."""
    defaults = dict(
        user_id="u1",
        jurisdiction="KE",
        sector="general",
        is_automated_decision=False,
        is_significant_decision=False,
        is_high_risk=False,
        is_high_risk_ai=False,
        has_human_review=True,
        has_explicit_consent=True,
        has_sensitive_data=False,
        involves_profiling=False,
        has_profiling_notice=True,
        has_dpia=True,
        has_nitda_registration=True,
        is_research_purpose=False,
        has_fsca_approval=True,
        source_jurisdiction="KE",
        destination_jurisdiction="KE",
        has_transfer_safeguards=False,
    )
    defaults.update(overrides)
    return mod.AfricaAIContext(**defaults)


def _base_doc(**overrides):
    """Return a minimal document."""
    defaults = dict(
        document_id="d1",
        content="test document content",
    )
    defaults.update(overrides)
    return mod.AfricaAIDocument(**defaults)


# ===========================================================================
# TestKenyaAIFilter
# ===========================================================================


class TestKenyaAIFilter:
    """Layer 1: Kenya Data Protection Act 2019."""

    def _eval(self, ctx, doc=None):
        if doc is None:
            doc = _base_doc()
        return mod.KenyaAIFilter().evaluate(ctx, doc)

    # --- Section 30: automated decision requiring human review ---

    def test_automated_significant_no_human_review_requires_review(self):
        """Significant automated decision + no human review → REQUIRES_HUMAN_REVIEW."""
        ctx = _base_ctx(
            is_automated_decision=True,
            is_significant_decision=True,
            has_human_review=False,
        )
        result = self._eval(ctx)
        assert result.decision == "REQUIRES_HUMAN_REVIEW"
        assert not result.is_denied

    def test_automated_significant_no_human_review_cites_section_30(self):
        """REQUIRES_HUMAN_REVIEW for significant automated decision cites §30."""
        ctx = _base_ctx(
            is_automated_decision=True,
            is_significant_decision=True,
            has_human_review=False,
        )
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "30" in combined

    def test_automated_not_significant_with_no_human_review_approved(self):
        """Automated but NOT significant decision, no human review → APPROVED (§30 not triggered)."""
        ctx = _base_ctx(
            is_automated_decision=True,
            is_significant_decision=False,
            has_human_review=False,
        )
        result = self._eval(ctx)
        assert result.decision == "APPROVED"

    def test_automated_significant_with_human_review_approved(self):
        """Significant automated decision WITH human review → APPROVED."""
        ctx = _base_ctx(
            is_automated_decision=True,
            is_significant_decision=True,
            has_human_review=True,
        )
        result = self._eval(ctx)
        assert result.decision == "APPROVED"

    # --- Section 25: sensitive data ---

    def test_sensitive_data_no_consent_denied(self):
        """Sensitive data + no explicit consent → DENIED."""
        ctx = _base_ctx(
            has_sensitive_data=True,
            has_explicit_consent=False,
        )
        result = self._eval(ctx)
        assert result.decision == "DENIED"
        assert result.is_denied

    def test_sensitive_data_no_consent_cites_section_25(self):
        """DENIED for sensitive data without consent cites §25."""
        ctx = _base_ctx(
            has_sensitive_data=True,
            has_explicit_consent=False,
        )
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "25" in combined

    def test_sensitive_data_with_consent_approved(self):
        """Sensitive data WITH explicit consent → APPROVED."""
        ctx = _base_ctx(
            has_sensitive_data=True,
            has_explicit_consent=True,
        )
        result = self._eval(ctx)
        assert result.decision == "APPROVED"

    # --- Section 31: profiling ---

    def test_profiling_no_notice_denied(self):
        """Profiling + no prior notice → DENIED."""
        ctx = _base_ctx(
            involves_profiling=True,
            has_profiling_notice=False,
        )
        result = self._eval(ctx)
        assert result.decision == "DENIED"
        assert result.is_denied

    def test_profiling_no_notice_cites_section_31(self):
        """DENIED for profiling without notice cites §31."""
        ctx = _base_ctx(
            involves_profiling=True,
            has_profiling_notice=False,
        )
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "31" in combined

    def test_profiling_with_notice_approved(self):
        """Profiling WITH prior notice → APPROVED."""
        ctx = _base_ctx(
            involves_profiling=True,
            has_profiling_notice=True,
        )
        result = self._eval(ctx)
        assert result.decision == "APPROVED"

    # --- Compliant baseline ---

    def test_fully_compliant_approved(self):
        """Fully compliant Kenya context → APPROVED."""
        ctx = _base_ctx()
        result = self._eval(ctx)
        assert result.decision == "APPROVED"
        assert not result.is_denied

    def test_compliant_result_not_requires_logging(self):
        """Compliant approval should set requires_logging=False."""
        ctx = _base_ctx()
        result = self._eval(ctx)
        assert result.requires_logging is False

    def test_non_compliant_requires_logging(self):
        """DENIED result should set requires_logging=True."""
        ctx = _base_ctx(has_sensitive_data=True, has_explicit_consent=False)
        result = self._eval(ctx)
        assert result.requires_logging is True


# ===========================================================================
# TestNigeriaAIFilter
# ===========================================================================


class TestNigeriaAIFilter:
    """Layer 2: Nigeria Data Protection Act 2023 + NITDA AI Policy."""

    def _eval(self, ctx, doc=None):
        if doc is None:
            doc = _base_doc()
        return mod.NigeriaAIFilter().evaluate(ctx, doc)

    # --- Section 34: high-risk automated processing without DPIA ---

    def test_high_risk_automated_no_dpia_requires_review(self):
        """High-risk automated processing + no DPIA → REQUIRES_HUMAN_REVIEW."""
        ctx = _base_ctx(
            is_automated_decision=True,
            is_high_risk=True,
            has_dpia=False,
        )
        result = self._eval(ctx)
        assert result.decision == "REQUIRES_HUMAN_REVIEW"
        assert not result.is_denied

    def test_high_risk_automated_no_dpia_cites_section_34(self):
        """REQUIRES_HUMAN_REVIEW for missing DPIA cites NDPA §34."""
        ctx = _base_ctx(
            is_automated_decision=True,
            is_high_risk=True,
            has_dpia=False,
        )
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "34" in combined

    def test_high_risk_automated_with_dpia_approved(self):
        """High-risk automated processing WITH DPIA → APPROVED."""
        ctx = _base_ctx(
            is_automated_decision=True,
            is_high_risk=True,
            has_dpia=True,
        )
        result = self._eval(ctx)
        assert result.decision == "APPROVED"

    def test_not_high_risk_automated_no_dpia_approved(self):
        """Automated but NOT high-risk + no DPIA → APPROVED (§34 not triggered)."""
        ctx = _base_ctx(
            is_automated_decision=True,
            is_high_risk=False,
            has_dpia=False,
        )
        result = self._eval(ctx)
        assert result.decision == "APPROVED"

    # --- Section 25: sensitive data ---

    def test_sensitive_data_no_consent_denied(self):
        """Sensitive data + no explicit consent → DENIED."""
        ctx = _base_ctx(
            has_sensitive_data=True,
            has_explicit_consent=False,
        )
        result = self._eval(ctx)
        assert result.decision == "DENIED"
        assert result.is_denied

    def test_sensitive_data_no_consent_cites_section_25(self):
        """DENIED for sensitive data without consent cites NDPA §25."""
        ctx = _base_ctx(
            has_sensitive_data=True,
            has_explicit_consent=False,
        )
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "25" in combined

    def test_sensitive_data_with_consent_approved(self):
        """Sensitive data WITH explicit consent → APPROVED."""
        ctx = _base_ctx(
            has_sensitive_data=True,
            has_explicit_consent=True,
        )
        result = self._eval(ctx)
        assert result.decision == "APPROVED"

    # --- NITDA AI Policy §3.2: high-risk AI registration ---

    def test_high_risk_ai_no_nitda_registration_requires_review(self):
        """High-risk AI system + no NITDA registration → REQUIRES_HUMAN_REVIEW."""
        ctx = _base_ctx(
            is_high_risk_ai=True,
            has_nitda_registration=False,
        )
        result = self._eval(ctx)
        assert result.decision == "REQUIRES_HUMAN_REVIEW"
        assert not result.is_denied

    def test_high_risk_ai_no_nitda_cites_policy(self):
        """REQUIRES_HUMAN_REVIEW for missing NITDA registration cites policy §3.2."""
        ctx = _base_ctx(
            is_high_risk_ai=True,
            has_nitda_registration=False,
        )
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "3.2" in combined or "NITDA" in combined

    def test_high_risk_ai_with_nitda_registration_approved(self):
        """High-risk AI WITH NITDA registration → APPROVED."""
        ctx = _base_ctx(
            is_high_risk_ai=True,
            has_nitda_registration=True,
        )
        result = self._eval(ctx)
        assert result.decision == "APPROVED"

    # --- Compliant baseline ---

    def test_fully_compliant_approved(self):
        """Fully compliant Nigeria context → APPROVED."""
        ctx = _base_ctx(jurisdiction="NG")
        result = self._eval(ctx)
        assert result.decision == "APPROVED"
        assert not result.is_denied

    def test_compliant_cites_ndpa(self):
        """Compliant approval cites Nigeria Data Protection Act 2023."""
        ctx = _base_ctx(jurisdiction="NG")
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "Nigeria" in combined or "NDPA" in combined or "2023" in combined


# ===========================================================================
# TestSouthAfricaAIFilter
# ===========================================================================


class TestSouthAfricaAIFilter:
    """Layer 3: South Africa POPIA 2013 + FSCA AI Guidance 2023."""

    def _eval(self, ctx, doc=None):
        if doc is None:
            doc = _base_doc()
        return mod.SouthAfricaAIFilter().evaluate(ctx, doc)

    # --- Section 71: automated decision without human review ---

    def test_automated_no_human_review_requires_review(self):
        """Automated decision + no human review → REQUIRES_HUMAN_REVIEW."""
        ctx = _base_ctx(
            is_automated_decision=True,
            has_human_review=False,
        )
        result = self._eval(ctx)
        assert result.decision == "REQUIRES_HUMAN_REVIEW"
        assert not result.is_denied

    def test_automated_no_human_review_cites_section_71(self):
        """REQUIRES_HUMAN_REVIEW for automated decision without review cites §71."""
        ctx = _base_ctx(
            is_automated_decision=True,
            has_human_review=False,
        )
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "71" in combined

    def test_automated_with_human_review_approved(self):
        """Automated decision WITH human review → APPROVED (§71 satisfied)."""
        ctx = _base_ctx(
            is_automated_decision=True,
            has_human_review=True,
        )
        result = self._eval(ctx)
        assert result.decision == "APPROVED"

    # --- Section 26: special personal information ---

    def test_special_info_no_consent_no_research_denied(self):
        """Special personal info + no consent + not research → DENIED."""
        ctx = _base_ctx(
            has_sensitive_data=True,
            has_explicit_consent=False,
            is_research_purpose=False,
        )
        result = self._eval(ctx)
        assert result.decision == "DENIED"
        assert result.is_denied

    def test_special_info_no_consent_no_research_cites_section_26(self):
        """DENIED for special info without consent cites POPIA §26."""
        ctx = _base_ctx(
            has_sensitive_data=True,
            has_explicit_consent=False,
            is_research_purpose=False,
        )
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "26" in combined

    def test_special_info_with_explicit_consent_approved(self):
        """Special personal info WITH explicit consent → APPROVED."""
        ctx = _base_ctx(
            has_sensitive_data=True,
            has_explicit_consent=True,
            is_research_purpose=False,
        )
        result = self._eval(ctx)
        assert result.decision == "APPROVED"

    def test_special_info_research_exemption_approved(self):
        """Special personal info for research purpose → APPROVED (§26 research exemption)."""
        ctx = _base_ctx(
            has_sensitive_data=True,
            has_explicit_consent=False,
            is_research_purpose=True,
        )
        result = self._eval(ctx)
        assert result.decision == "APPROVED"

    # --- FSCA AI Guidance 2023 ---

    def test_financial_sector_no_fsca_approval_requires_review(self):
        """Financial services AI + no FSCA approval → REQUIRES_HUMAN_REVIEW."""
        ctx = _base_ctx(
            sector="financial_services",
            has_fsca_approval=False,
        )
        result = self._eval(ctx)
        assert result.decision == "REQUIRES_HUMAN_REVIEW"
        assert not result.is_denied

    def test_financial_sector_no_fsca_cites_guidance(self):
        """REQUIRES_HUMAN_REVIEW for financial AI without FSCA cites FSCA guidance."""
        ctx = _base_ctx(
            sector="financial_services",
            has_fsca_approval=False,
        )
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "FSCA" in combined

    def test_financial_sector_with_fsca_approval_approved(self):
        """Financial services AI WITH FSCA approval → APPROVED."""
        ctx = _base_ctx(
            sector="financial_services",
            has_fsca_approval=True,
        )
        result = self._eval(ctx)
        assert result.decision == "APPROVED"

    def test_non_financial_no_fsca_approval_approved(self):
        """Non-financial sector + no FSCA approval → APPROVED (FSCA not applicable)."""
        ctx = _base_ctx(
            sector="healthcare",
            has_fsca_approval=False,
        )
        result = self._eval(ctx)
        assert result.decision == "APPROVED"

    # --- Compliant baseline ---

    def test_fully_compliant_approved(self):
        """Fully compliant South Africa context → APPROVED."""
        ctx = _base_ctx(jurisdiction="ZA")
        result = self._eval(ctx)
        assert result.decision == "APPROVED"
        assert not result.is_denied

    def test_compliant_cites_popia(self):
        """Compliant approval cites POPIA 2013."""
        ctx = _base_ctx(jurisdiction="ZA")
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "POPIA" in combined or "2013" in combined or "South Africa" in combined


# ===========================================================================
# TestAfricaCrossBorderFilter
# ===========================================================================


class TestAfricaCrossBorderFilter:
    """Layer 4: Africa Cross-Border Transfer Filter."""

    def _eval(self, ctx, doc=None):
        if doc is None:
            doc = _base_doc()
        return mod.AfricaCrossBorderFilter().evaluate(ctx, doc)

    # --- Adequate-to-adequate transfers ---

    def test_ke_to_ng_adequate_approved(self):
        """KE → NG (both adequate) → APPROVED."""
        ctx = _base_ctx(source_jurisdiction="KE", destination_jurisdiction="NG")
        result = self._eval(ctx)
        assert result.decision == "APPROVED"

    def test_za_to_ke_adequate_approved(self):
        """ZA → KE (both adequate) → APPROVED."""
        ctx = _base_ctx(source_jurisdiction="ZA", destination_jurisdiction="KE")
        result = self._eval(ctx)
        assert result.decision == "APPROVED"

    def test_ng_to_gh_adequate_approved(self):
        """NG → GH (both adequate) → APPROVED."""
        ctx = _base_ctx(source_jurisdiction="NG", destination_jurisdiction="GH")
        result = self._eval(ctx)
        assert result.decision == "APPROVED"

    def test_adequate_transfer_cites_au_framework(self):
        """Adequate jurisdiction transfer cites AU Data Policy Framework 2022."""
        ctx = _base_ctx(source_jurisdiction="KE", destination_jurisdiction="ZA")
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "AU" in combined or "adequate" in combined.lower()

    # --- Non-adequate destination without safeguards ---

    def test_ke_to_us_no_safeguards_denied(self):
        """KE → US (non-adequate) + no safeguards → DENIED."""
        ctx = _base_ctx(
            source_jurisdiction="KE",
            destination_jurisdiction="US",
            has_transfer_safeguards=False,
        )
        result = self._eval(ctx)
        assert result.decision == "DENIED"
        assert result.is_denied

    def test_ke_to_us_no_safeguards_cites_ke_dpa_48(self):
        """DENIED for KE source cites Kenya DPA 2019 §48."""
        ctx = _base_ctx(
            source_jurisdiction="KE",
            destination_jurisdiction="US",
            has_transfer_safeguards=False,
        )
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "48" in combined or "Kenya" in combined

    def test_ng_to_cn_no_safeguards_denied(self):
        """NG → CN (non-adequate) + no safeguards → DENIED."""
        ctx = _base_ctx(
            source_jurisdiction="NG",
            destination_jurisdiction="CN",
            has_transfer_safeguards=False,
        )
        result = self._eval(ctx)
        assert result.decision == "DENIED"
        assert result.is_denied

    def test_ng_to_cn_no_safeguards_cites_ndpa_43(self):
        """DENIED for NG source cites Nigeria NDPA 2023 §43."""
        ctx = _base_ctx(
            source_jurisdiction="NG",
            destination_jurisdiction="CN",
            has_transfer_safeguards=False,
        )
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "43" in combined or "Nigeria" in combined

    def test_za_to_ru_no_safeguards_denied(self):
        """ZA → RU (non-adequate) + no safeguards → DENIED."""
        ctx = _base_ctx(
            source_jurisdiction="ZA",
            destination_jurisdiction="RU",
            has_transfer_safeguards=False,
        )
        result = self._eval(ctx)
        assert result.decision == "DENIED"
        assert result.is_denied

    def test_za_to_ru_no_safeguards_cites_popia_72(self):
        """DENIED for ZA source cites POPIA 2013 §72."""
        ctx = _base_ctx(
            source_jurisdiction="ZA",
            destination_jurisdiction="RU",
            has_transfer_safeguards=False,
        )
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "72" in combined or "POPIA" in combined or "South Africa" in combined

    def test_unknown_source_to_non_adequate_no_safeguards_denied(self):
        """Unknown source jurisdiction → non-adequate destination + no safeguards → DENIED."""
        ctx = _base_ctx(
            source_jurisdiction="XX",
            destination_jurisdiction="US",
            has_transfer_safeguards=False,
        )
        result = self._eval(ctx)
        assert result.decision == "DENIED"

    # --- Non-adequate destination WITH safeguards ---

    def test_ke_to_us_with_safeguards_approved(self):
        """KE → US (non-adequate) WITH safeguards → APPROVED."""
        ctx = _base_ctx(
            source_jurisdiction="KE",
            destination_jurisdiction="US",
            has_transfer_safeguards=True,
        )
        result = self._eval(ctx)
        assert result.decision == "APPROVED"

    def test_ng_to_cn_with_safeguards_approved(self):
        """NG → CN (non-adequate) WITH safeguards → APPROVED."""
        ctx = _base_ctx(
            source_jurisdiction="NG",
            destination_jurisdiction="CN",
            has_transfer_safeguards=True,
        )
        result = self._eval(ctx)
        assert result.decision == "APPROVED"

    def test_safeguards_approved_cites_contractual_safeguards(self):
        """Approved with safeguards mentions contractual safeguards."""
        ctx = _base_ctx(
            source_jurisdiction="ZA",
            destination_jurisdiction="US",
            has_transfer_safeguards=True,
        )
        result = self._eval(ctx)
        combined = result.regulation_citation + " " + result.reason
        assert "safeguard" in combined.lower() or "contractual" in combined.lower()


# ===========================================================================
# TestAfricaAIGovernanceOrchestrator
# ===========================================================================


class TestAfricaAIGovernanceOrchestrator:
    """Full orchestrator pipeline tests."""

    def _run(self, ctx, doc=None):
        if doc is None:
            doc = _base_doc()
        return mod.AfricaAIGovernanceOrchestrator().evaluate(ctx, doc)

    def test_returns_four_results(self):
        """Orchestrator always returns exactly four FilterResult objects."""
        ctx = _base_ctx()
        results = self._run(ctx)
        assert len(results) == 4

    def test_all_four_filters_run_even_on_denial(self):
        """All four filters run regardless of earlier results."""
        ctx = _base_ctx(
            has_sensitive_data=True,
            has_explicit_consent=False,
        )
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

    def test_kenya_denial_propagates_to_results(self):
        """Kenya DENIED appears in first result when profiling has no notice."""
        ctx = _base_ctx(involves_profiling=True, has_profiling_notice=False)
        results = self._run(ctx)
        assert results[0].decision == "DENIED"

    def test_nigeria_requires_review_propagates(self):
        """Nigeria REQUIRES_HUMAN_REVIEW appears in second result for missing DPIA."""
        ctx = _base_ctx(
            is_automated_decision=True,
            is_high_risk=True,
            has_dpia=False,
        )
        results = self._run(ctx)
        assert results[1].decision == "REQUIRES_HUMAN_REVIEW"

    def test_south_africa_requires_review_propagates(self):
        """South Africa REQUIRES_HUMAN_REVIEW for automated decision without review."""
        ctx = _base_ctx(
            is_automated_decision=True,
            has_human_review=False,
        )
        results = self._run(ctx)
        assert results[2].decision == "REQUIRES_HUMAN_REVIEW"

    def test_cross_border_denial_propagates(self):
        """Cross-border DENIED appears in fourth result for non-adequate transfer."""
        ctx = _base_ctx(
            source_jurisdiction="KE",
            destination_jurisdiction="US",
            has_transfer_safeguards=False,
        )
        results = self._run(ctx)
        assert results[3].decision == "DENIED"


# ===========================================================================
# TestAfricaAIGovernanceReport
# ===========================================================================


class TestAfricaAIGovernanceReport:
    """Report aggregation and overall_decision / is_compliant tests."""

    def _make_report(self, ctx, doc=None):
        if doc is None:
            doc = _base_doc()
        orchestrator = mod.AfricaAIGovernanceOrchestrator()
        results = orchestrator.evaluate(ctx, doc)
        return mod.AfricaAIGovernanceReport(
            context=ctx,
            document=doc,
            filter_results=results,
        )

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
        ctx = _base_ctx(has_sensitive_data=True, has_explicit_consent=False)
        report = self._make_report(ctx)
        assert report.overall_decision == "DENIED"

    def test_one_denied_not_compliant(self):
        """One DENIED filter → is_compliant == False."""
        ctx = _base_ctx(has_sensitive_data=True, has_explicit_consent=False)
        report = self._make_report(ctx)
        assert report.is_compliant is False

    def test_requires_human_review_not_denied(self):
        """REQUIRES_HUMAN_REVIEW without DENIED → is_compliant == True."""
        ctx = _base_ctx(
            is_automated_decision=True,
            is_significant_decision=True,
            has_human_review=False,
        )
        report = self._make_report(ctx)
        assert report.overall_decision == "REQUIRES_HUMAN_REVIEW"
        assert report.is_compliant is True

    def test_denied_takes_priority_over_requires_review(self):
        """DENIED takes priority over REQUIRES_HUMAN_REVIEW in overall_decision."""
        # Kenya: profiling without notice → DENIED
        # South Africa: automated without human review → REQUIRES_HUMAN_REVIEW
        ctx = _base_ctx(
            involves_profiling=True,
            has_profiling_notice=False,
            is_automated_decision=True,
            has_human_review=False,
        )
        report = self._make_report(ctx)
        assert report.overall_decision == "DENIED"

    def test_compliance_summary_contains_user_id(self):
        """compliance_summary includes the user_id."""
        ctx = _base_ctx(user_id="test-user-42")
        report = self._make_report(ctx)
        assert "test-user-42" in report.compliance_summary

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
        assert "KENYA_AI_FILTER" in summary
        assert "NIGERIA_AI_FILTER" in summary
        assert "SOUTH_AFRICA_AI_FILTER" in summary
        assert "AFRICA_CROSS_BORDER_FILTER" in summary

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
