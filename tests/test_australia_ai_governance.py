"""
Tests for 19_australia_ai_governance.py — Four-layer Australian AI governance
framework covering DIIS Ethics, Privacy Act APPs, DTA ADM, and AHRC guidelines.
"""

from __future__ import annotations

import dataclasses
import importlib.util
import sys
import types
from pathlib import Path

import pytest

_MOD_PATH = (
    Path(__file__).parent.parent / "examples" / "19_australia_ai_governance.py"
)


def _load_module():
    module_name = "australia_ai_governance_19"
    if module_name in sys.modules:
        return sys.modules[module_name]
    spec = importlib.util.spec_from_file_location(module_name, _MOD_PATH)
    mod = types.ModuleType(module_name)
    sys.modules[module_name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def m():
    return _load_module()


# ---------------------------------------------------------------------------
# Helper factories
# ---------------------------------------------------------------------------


def _ctx(m, **kwargs):
    """Fully compliant government HIGH_RISK system."""
    defaults = dict(
        system_id="AU-TEST-001",
        system_name="Test AI System",
        risk_level=m.AustralianAIRiskLevel.HIGH_RISK,
        deploying_sector=m.AustralianSector.GOVERNMENT,
        human_societal_wellbeing_assessed=True,
        human_centred_design_applied=True,
        privacy_protection_in_place=True,
        reliability_safety_validated=True,
        transparency_explainability_provided=True,
        contestability_mechanism_available=True,
        accountability_governance_exists=True,
        app1_privacy_policy_published=True,
        app3_collection_consent_valid=True,
        app6_use_disclosure_limited=True,
        app11_security_safeguards=True,
        human_review_right_provided=True,
        explanation_obligation_met=True,
        adm_record_keeping_current=True,
        non_discrimination_assessment_done=True,
        accessible_design_verified=True,
    )
    defaults.update(kwargs)
    return m.AustraliaAIContext(**defaults)


def _private_ctx(m, **kwargs):
    """Fully compliant private sector MEDIUM_RISK system."""
    base = _ctx(
        m,
        deploying_sector=m.AustralianSector.PRIVATE_SECTOR,
        risk_level=m.AustralianAIRiskLevel.MEDIUM_RISK,
    )
    d = dataclasses.asdict(base)
    d.update(kwargs)
    return m.AustraliaAIContext(**d)


# ===========================================================================
# TestAustralianAIEthicsFilter
# ===========================================================================


class TestAustralianAIEthicsFilter:
    """Tests for Layer 1: Australian AI Ethics Framework (DIIS 8 Principles)."""

    def test_fully_compliant_approved_with_conditions(self, m):
        """All ethics fields True → has_conditions (APPROVED_WITH_CONDITIONS)."""
        ctx = _ctx(m)
        f = m.AustralianAIEthicsFilter()
        result = f.evaluate(ctx)
        assert result.has_conditions
        assert not result.is_denied

    def test_missing_wellbeing_assessment_denied(self, m):
        """human_societal_wellbeing_assessed=False → is_denied, finding mentions Principle 1 or wellbeing."""
        ctx = _ctx(m, human_societal_wellbeing_assessed=False)
        f = m.AustralianAIEthicsFilter()
        result = f.evaluate(ctx)
        assert result.is_denied
        combined = " ".join(result.findings).lower()
        assert "principle 1" in combined or "wellbeing" in combined

    def test_missing_reliability_denied(self, m):
        """reliability_safety_validated=False → is_denied, finding mentions Principle 4 or reliability/safety."""
        ctx = _ctx(m, reliability_safety_validated=False)
        f = m.AustralianAIEthicsFilter()
        result = f.evaluate(ctx)
        assert result.is_denied
        combined = " ".join(result.findings).lower()
        assert "principle 4" in combined or "reliability" in combined or "safety" in combined

    def test_missing_transparency_denied(self, m):
        """transparency_explainability_provided=False → is_denied, finding mentions Principle 5 or transparency."""
        ctx = _ctx(m, transparency_explainability_provided=False)
        f = m.AustralianAIEthicsFilter()
        result = f.evaluate(ctx)
        assert result.is_denied
        combined = " ".join(result.findings).lower()
        assert "principle 5" in combined or "transparency" in combined

    def test_missing_contestability_denied(self, m):
        """contestability_mechanism_available=False → is_denied, finding mentions Principle 6 or contestability."""
        ctx = _ctx(m, contestability_mechanism_available=False)
        f = m.AustralianAIEthicsFilter()
        result = f.evaluate(ctx)
        assert result.is_denied
        combined = " ".join(result.findings).lower()
        assert "principle 6" in combined or "contestability" in combined

    def test_exempt_system_approved_with_conditions(self, m):
        """risk_level=EXEMPT → has_conditions (APPROVED_WITH_CONDITIONS), not is_denied."""
        ctx = _ctx(m, risk_level=m.AustralianAIRiskLevel.EXEMPT)
        f = m.AustralianAIEthicsFilter()
        result = f.evaluate(ctx)
        assert result.has_conditions
        assert not result.is_denied

    def test_conditions_reference_ethics_framework(self, m):
        """Compliant system → conditions reference AI Ethics, DIIS, or Principle."""
        ctx = _ctx(m)
        f = m.AustralianAIEthicsFilter()
        result = f.evaluate(ctx)
        combined = " ".join(result.conditions).lower()
        assert "ai ethics" in combined or "diis" in combined or "principle" in combined


# ===========================================================================
# TestPrivacyActAPPsFilter
# ===========================================================================


class TestPrivacyActAPPsFilter:
    """Tests for Layer 2: Privacy Act 1988 Australian Privacy Principles."""

    def test_all_compliant_approved_with_conditions(self, m):
        """All APP fields True → has_conditions (APPROVED_WITH_CONDITIONS)."""
        ctx = _ctx(m)
        f = m.PrivacyActAPPsFilter()
        result = f.evaluate(ctx)
        assert result.has_conditions
        assert not result.is_denied

    def test_missing_privacy_policy_denied(self, m):
        """app1_privacy_policy_published=False → is_denied, finding mentions APP 1 or privacy policy."""
        ctx = _ctx(m, app1_privacy_policy_published=False)
        f = m.PrivacyActAPPsFilter()
        result = f.evaluate(ctx)
        assert result.is_denied
        combined = " ".join(result.findings).lower()
        assert "app 1" in combined or "privacy policy" in combined

    def test_missing_collection_consent_denied(self, m):
        """app3_collection_consent_valid=False → is_denied, finding mentions APP 3 or collection."""
        ctx = _ctx(m, app3_collection_consent_valid=False)
        f = m.PrivacyActAPPsFilter()
        result = f.evaluate(ctx)
        assert result.is_denied
        combined = " ".join(result.findings).lower()
        assert "app 3" in combined or "collection" in combined

    def test_missing_use_disclosure_denied(self, m):
        """app6_use_disclosure_limited=False → is_denied, finding mentions APP 6 or disclosure."""
        ctx = _ctx(m, app6_use_disclosure_limited=False)
        f = m.PrivacyActAPPsFilter()
        result = f.evaluate(ctx)
        assert result.is_denied
        combined = " ".join(result.findings).lower()
        assert "app 6" in combined or "disclosure" in combined

    def test_missing_security_safeguards_denied(self, m):
        """app11_security_safeguards=False → is_denied, finding mentions APP 11 or security."""
        ctx = _ctx(m, app11_security_safeguards=False)
        f = m.PrivacyActAPPsFilter()
        result = f.evaluate(ctx)
        assert result.is_denied
        combined = " ".join(result.findings).lower()
        assert "app 11" in combined or "security" in combined

    def test_conditions_reference_ndb_scheme(self, m):
        """Compliant system → conditions reference APP 12, APP 13, NDB, or breach."""
        ctx = _ctx(m)
        f = m.PrivacyActAPPsFilter()
        result = f.evaluate(ctx)
        combined = " ".join(result.conditions).lower()
        assert (
            "app 12" in combined
            or "app 13" in combined
            or "ndb" in combined
            or "breach" in combined
        )


# ===========================================================================
# TestDTAADMFilter
# ===========================================================================


class TestDTAADMFilter:
    """Tests for Layer 3: DTA Automated Decision-Making Framework."""

    def test_private_sector_not_applicable(self, m):
        """PRIVATE_SECTOR → not is_denied, condition references government, DTA, or private sector."""
        ctx = _private_ctx(m)
        f = m.DTAADMFilter()
        result = f.evaluate(ctx)
        assert not result.is_denied
        combined = " ".join(result.conditions).lower()
        assert "government" in combined or "dta" in combined or "private sector" in combined

    def test_government_all_compliant_approved_with_conditions(self, m):
        """GOVERNMENT sector, all ADM fields True → has_conditions."""
        ctx = _ctx(m)
        f = m.DTAADMFilter()
        result = f.evaluate(ctx)
        assert result.has_conditions
        assert not result.is_denied

    def test_government_missing_human_review_denied(self, m):
        """GOVERNMENT, human_review_right_provided=False → is_denied, finding mentions human review or DTA."""
        ctx = _ctx(m, human_review_right_provided=False)
        f = m.DTAADMFilter()
        result = f.evaluate(ctx)
        assert result.is_denied
        combined = " ".join(result.findings).lower()
        assert "human review" in combined or "dta" in combined

    def test_government_missing_explanation_denied(self, m):
        """GOVERNMENT, explanation_obligation_met=False → is_denied, finding mentions explanation or DTA."""
        ctx = _ctx(m, explanation_obligation_met=False)
        f = m.DTAADMFilter()
        result = f.evaluate(ctx)
        assert result.is_denied
        combined = " ".join(result.findings).lower()
        assert "explanation" in combined or "dta" in combined

    def test_government_missing_record_keeping_denied(self, m):
        """GOVERNMENT, adm_record_keeping_current=False → is_denied, finding mentions record, FOI, or DTA."""
        ctx = _ctx(m, adm_record_keeping_current=False)
        f = m.DTAADMFilter()
        result = f.evaluate(ctx)
        assert result.is_denied
        combined = " ".join(result.findings).lower()
        assert "record" in combined or "foi" in combined or "dta" in combined

    def test_conditions_reference_foi(self, m):
        """GOVERNMENT compliant → conditions reference FOI, DTA, or review."""
        ctx = _ctx(m)
        f = m.DTAADMFilter()
        result = f.evaluate(ctx)
        combined = " ".join(result.conditions).lower()
        assert "foi" in combined or "dta" in combined or "review" in combined


# ===========================================================================
# TestAHRCAIGuidelinesFilter
# ===========================================================================


class TestAHRCAIGuidelinesFilter:
    """Tests for Layer 4: AHRC AI Human Rights Guidelines."""

    def test_all_compliant_approved_with_conditions(self, m):
        """All AHRC fields True → has_conditions (APPROVED_WITH_CONDITIONS)."""
        ctx = _ctx(m)
        f = m.AHRCAIGuidelinesFilter()
        result = f.evaluate(ctx)
        assert result.has_conditions
        assert not result.is_denied

    def test_missing_non_discrimination_assessment_denied(self, m):
        """non_discrimination_assessment_done=False → is_denied, finding mentions discrimination or AHRC."""
        ctx = _ctx(m, non_discrimination_assessment_done=False)
        f = m.AHRCAIGuidelinesFilter()
        result = f.evaluate(ctx)
        assert result.is_denied
        combined = " ".join(result.findings).lower()
        assert "discrimination" in combined or "ahrc" in combined

    def test_high_risk_missing_accessible_design_denied(self, m):
        """risk_level=HIGH_RISK, accessible_design_verified=False → is_denied, finding mentions accessible, Disability, or AHRC."""
        ctx = _ctx(
            m,
            risk_level=m.AustralianAIRiskLevel.HIGH_RISK,
            accessible_design_verified=False,
        )
        f = m.AHRCAIGuidelinesFilter()
        result = f.evaluate(ctx)
        assert result.is_denied
        combined = " ".join(result.findings).lower()
        assert "accessib" in combined or "disability" in combined or "ahrc" in combined

    def test_low_risk_missing_accessible_design_not_denied(self, m):
        """risk_level=LOW_RISK, accessible_design_verified=False → not is_denied."""
        ctx = _ctx(
            m,
            risk_level=m.AustralianAIRiskLevel.LOW_RISK,
            accessible_design_verified=False,
        )
        f = m.AHRCAIGuidelinesFilter()
        result = f.evaluate(ctx)
        assert not result.is_denied

    def test_conditions_reference_first_nations(self, m):
        """Compliant system → conditions reference First Nations, communities, or intersectional."""
        ctx = _ctx(m)
        f = m.AHRCAIGuidelinesFilter()
        result = f.evaluate(ctx)
        combined = " ".join(result.conditions).lower()
        assert (
            "first nations" in combined
            or "communities" in combined
            or "intersectional" in combined
        )

    def test_layer_name_correct(self, m):
        """result.layer == 'AHRC_AI_HUMAN_RIGHTS'."""
        ctx = _ctx(m)
        f = m.AHRCAIGuidelinesFilter()
        result = f.evaluate(ctx)
        assert result.layer == "AHRC_AI_HUMAN_RIGHTS"


# ===========================================================================
# TestAustraliaAIGovernanceOrchestrator
# ===========================================================================


class TestAustraliaAIGovernanceOrchestrator:
    """Tests for the four-layer orchestrator and aggregated AustraliaAIGovernanceReport."""

    def test_fully_compliant_government_system_approved_with_conditions(self, m):
        """Compliant GOVERNMENT HIGH_RISK system → APPROVED_WITH_CONDITIONS."""
        ctx = _ctx(m)
        orch = m.AustraliaAIGovernanceOrchestrator()
        report = orch.evaluate(ctx)
        assert report.final_decision == m.AustralianAIDecision.APPROVED_WITH_CONDITIONS

    def test_missing_human_review_denied(self, m):
        """human_review_right_provided=False → final_decision DENIED."""
        ctx = _ctx(m, human_review_right_provided=False)
        orch = m.AustraliaAIGovernanceOrchestrator()
        report = orch.evaluate(ctx)
        assert report.final_decision == m.AustralianAIDecision.DENIED

    def test_all_four_layers_evaluated(self, m):
        """layer_results has exactly 4 entries regardless of compliance."""
        ctx = _ctx(m)
        orch = m.AustraliaAIGovernanceOrchestrator()
        report = orch.evaluate(ctx)
        assert len(report.layer_results) == 4

    def test_layer_order(self, m):
        """Layer names appear in the correct order across all four layers."""
        ctx = _ctx(m)
        orch = m.AustraliaAIGovernanceOrchestrator()
        report = orch.evaluate(ctx)
        names = [r.layer for r in report.layer_results]
        assert names == [
            "AUSTRALIAN_AI_ETHICS_FRAMEWORK",
            "PRIVACY_ACT_1988_APPs",
            "DTA_ADM_FRAMEWORK",
            "AHRC_AI_HUMAN_RIGHTS",
        ]

    def test_report_summary_structure(self, m):
        """summary() contains expected top-level keys with correct values."""
        ctx = _ctx(m)
        orch = m.AustraliaAIGovernanceOrchestrator()
        report = orch.evaluate(ctx)
        summary = report.summary()
        assert summary["system_id"] == "AU-TEST-001"
        assert summary["system_name"] == "Test AI System"
        assert "risk_level" in summary
        assert "deploying_sector" in summary
        assert "final_decision" in summary
        assert len(summary["layers"]) == 4

    def test_private_sector_approved_with_conditions(self, m):
        """PRIVATE_SECTOR compliant MEDIUM_RISK system → APPROVED_WITH_CONDITIONS."""
        ctx = _private_ctx(m)
        orch = m.AustraliaAIGovernanceOrchestrator()
        report = orch.evaluate(ctx)
        assert report.final_decision == m.AustralianAIDecision.APPROVED_WITH_CONDITIONS

    def test_non_discrimination_missing_denied(self, m):
        """non_discrimination_assessment_done=False → final_decision DENIED."""
        ctx = _ctx(m, non_discrimination_assessment_done=False)
        orch = m.AustraliaAIGovernanceOrchestrator()
        report = orch.evaluate(ctx)
        assert report.final_decision == m.AustralianAIDecision.DENIED
