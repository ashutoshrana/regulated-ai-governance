"""
Tests for 15_public_sector_ai_governance.py

Four-layer public sector AI governance:
  Layer 1: OMB M-24-10 — Federal AI governance (CAIO, inventory, rights/safety)
  Layer 2: EO 14110   — Safe, Secure AI (red-team, TEVV, safety testing)
  Layer 3: NIST AI RMF — GOVERN / MAP / MEASURE / MANAGE maturity
  Layer 4: Section 508 / ADA — Accessibility and plain-language explanations
"""

import importlib.util
import sys
import types
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Module loading
# ---------------------------------------------------------------------------

_MOD_PATH = (
    Path(__file__).parent.parent / "examples" / "15_public_sector_ai_governance.py"
)


def _load_module():
    module_name = "public_sector_ai_governance"
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
# Helpers — default fully-compliant context
# ---------------------------------------------------------------------------


def _ctx(m, **kwargs):
    """
    Return a fully-compliant PublicSectorAIContext for a HIGH_RISK
    BENEFITS_DETERMINATION (rights-impacting) system. Override any field
    via kwargs.
    """
    defaults = dict(
        system_id="GOV-TEST-001",
        system_name="Benefits AI",
        use_case=m.FederalAIUseCase.BENEFITS_DETERMINATION,
        impact_level=m.AIImpactLevel.RIGHTS_IMPACTING,
        eo14110_risk_tier=m.EO14110RiskTier.HIGH_RISK,
        nist_rmf_level=m.NISTRMFLevel.FULL,
        deploying_agency="SSA",
        caio_designated=True,
        ai_inventory_maintained=True,
        human_review_available=True,
        appeal_mechanism_exists=True,
        pre_deployment_safety_testing_done=True,
        incident_reporting_active=True,
        red_team_assessment_completed=False,  # HIGH_RISK doesn't require red-team
        tevv_framework_applied=True,
        nist_govern_documented=True,
        nist_map_completed=True,
        nist_measure_quantified=True,
        nist_manage_plan_exists=True,
        section_508_compliant=True,
        plain_language_explanations=True,
    )
    defaults.update(kwargs)
    return m.PublicSectorAIContext(**defaults)


def _min_ctx(m, **kwargs):
    """Return a fully-compliant MINIMUM_IMPACT context."""
    defaults = dict(
        system_id="GOV-MIN-001",
        system_name="Internal Analytics",
        use_case=m.FederalAIUseCase.INTERNAL_ANALYTICS,
        impact_level=m.AIImpactLevel.MINIMUM_IMPACT,
        eo14110_risk_tier=m.EO14110RiskTier.STANDARD,
        nist_rmf_level=m.NISTRMFLevel.MINIMAL,
        deploying_agency="GSA",
        caio_designated=True,
        ai_inventory_maintained=True,
        human_review_available=False,
        appeal_mechanism_exists=False,
        pre_deployment_safety_testing_done=False,
        incident_reporting_active=False,
        red_team_assessment_completed=False,
        tevv_framework_applied=False,
        nist_govern_documented=False,
        nist_map_completed=False,
        nist_measure_quantified=False,
        nist_manage_plan_exists=False,
        section_508_compliant=True,
        plain_language_explanations=False,
    )
    defaults.update(kwargs)
    return m.PublicSectorAIContext(**defaults)


# ---------------------------------------------------------------------------
# Layer 1 — OMB M-24-10
# ---------------------------------------------------------------------------


class TestOMBM2410Filter:

    def test_compliant_rights_impacting_approved_with_conditions(self, m):
        f = m.OMBM2410Filter()
        ctx = _ctx(m)
        result = f.evaluate(ctx)
        assert result.decision == m.PublicSectorGovernanceDecision.APPROVED_WITH_CONDITIONS
        assert len(result.conditions) > 0

    def test_no_caio_denied(self, m):
        f = m.OMBM2410Filter()
        ctx = _ctx(m, caio_designated=False)
        result = f.evaluate(ctx)
        assert result.decision == m.PublicSectorGovernanceDecision.DENIED
        assert any("CAIO" in finding or "Chief AI Officer" in finding for finding in result.findings)

    def test_no_inventory_denied(self, m):
        f = m.OMBM2410Filter()
        ctx = _ctx(m, ai_inventory_maintained=False)
        result = f.evaluate(ctx)
        assert result.decision == m.PublicSectorGovernanceDecision.DENIED
        assert any("inventory" in finding.lower() for finding in result.findings)

    def test_no_human_review_for_rights_impacting_denied(self, m):
        f = m.OMBM2410Filter()
        ctx = _ctx(m, human_review_available=False)
        result = f.evaluate(ctx)
        assert result.decision == m.PublicSectorGovernanceDecision.DENIED
        assert any("human review" in finding.lower() for finding in result.findings)

    def test_no_appeal_mechanism_for_rights_impacting_denied(self, m):
        f = m.OMBM2410Filter()
        ctx = _ctx(m, appeal_mechanism_exists=False)
        result = f.evaluate(ctx)
        assert result.decision == m.PublicSectorGovernanceDecision.DENIED
        assert any("appeal" in finding.lower() for finding in result.findings)

    def test_safety_impacting_no_safety_testing_denied(self, m):
        f = m.OMBM2410Filter()
        ctx = _ctx(
            m,
            use_case=m.FederalAIUseCase.CRITICAL_INFRASTRUCTURE,
            impact_level=m.AIImpactLevel.SAFETY_IMPACTING,
            pre_deployment_safety_testing_done=False,
        )
        result = f.evaluate(ctx)
        assert result.decision == m.PublicSectorGovernanceDecision.DENIED
        assert any("safety testing" in finding.lower() for finding in result.findings)

    def test_safety_impacting_no_incident_reporting_denied(self, m):
        f = m.OMBM2410Filter()
        ctx = _ctx(
            m,
            use_case=m.FederalAIUseCase.CRITICAL_INFRASTRUCTURE,
            impact_level=m.AIImpactLevel.SAFETY_IMPACTING,
            incident_reporting_active=False,
        )
        result = f.evaluate(ctx)
        assert result.decision == m.PublicSectorGovernanceDecision.DENIED

    def test_minimum_impact_only_requires_inventory(self, m):
        f = m.OMBM2410Filter()
        ctx = _min_ctx(m)
        result = f.evaluate(ctx)
        # No CAIO required for minimum-impact; only inventory
        assert result.decision == m.PublicSectorGovernanceDecision.APPROVED

    def test_minimum_impact_without_inventory_denied(self, m):
        f = m.OMBM2410Filter()
        ctx = _min_ctx(m, ai_inventory_maintained=False)
        result = f.evaluate(ctx)
        assert result.decision == m.PublicSectorGovernanceDecision.DENIED

    def test_safety_impacting_compliant_approved_with_conditions(self, m):
        f = m.OMBM2410Filter()
        ctx = _ctx(
            m,
            use_case=m.FederalAIUseCase.CRITICAL_INFRASTRUCTURE,
            impact_level=m.AIImpactLevel.SAFETY_IMPACTING,
        )
        result = f.evaluate(ctx)
        assert result.decision == m.PublicSectorGovernanceDecision.APPROVED_WITH_CONDITIONS
        assert any("monitoring" in c.lower() for c in result.conditions)


# ---------------------------------------------------------------------------
# Layer 2 — EO 14110
# ---------------------------------------------------------------------------


class TestEO14110Filter:

    def test_standard_approved_with_conditions(self, m):
        f = m.EO14110Filter()
        ctx = _ctx(m, eo14110_risk_tier=m.EO14110RiskTier.STANDARD)
        result = f.evaluate(ctx)
        assert result.decision == m.PublicSectorGovernanceDecision.APPROVED_WITH_CONDITIONS
        assert any("STANDARD" in c for c in result.conditions)

    def test_high_risk_no_safety_testing_denied(self, m):
        f = m.EO14110Filter()
        ctx = _ctx(m, eo14110_risk_tier=m.EO14110RiskTier.HIGH_RISK, pre_deployment_safety_testing_done=False)
        result = f.evaluate(ctx)
        assert result.decision == m.PublicSectorGovernanceDecision.DENIED
        assert any("safety" in finding.lower() for finding in result.findings)

    def test_high_risk_with_safety_testing_approved_with_conditions(self, m):
        f = m.EO14110Filter()
        ctx = _ctx(m, eo14110_risk_tier=m.EO14110RiskTier.HIGH_RISK)
        result = f.evaluate(ctx)
        assert result.decision == m.PublicSectorGovernanceDecision.APPROVED_WITH_CONDITIONS
        assert any("quarterly" in c.lower() for c in result.conditions)

    def test_dual_use_no_red_team_denied(self, m):
        f = m.EO14110Filter()
        ctx = _ctx(m, eo14110_risk_tier=m.EO14110RiskTier.DUAL_USE_FOUNDATION, red_team_assessment_completed=False)
        result = f.evaluate(ctx)
        assert result.decision == m.PublicSectorGovernanceDecision.DENIED
        assert any("red-team" in finding.lower() for finding in result.findings)

    def test_dual_use_no_tevv_denied(self, m):
        f = m.EO14110Filter()
        ctx = _ctx(m, eo14110_risk_tier=m.EO14110RiskTier.DUAL_USE_FOUNDATION, red_team_assessment_completed=True, tevv_framework_applied=False)
        result = f.evaluate(ctx)
        assert result.decision == m.PublicSectorGovernanceDecision.DENIED
        assert any("TEVV" in finding for finding in result.findings)

    def test_dual_use_fully_compliant_approved(self, m):
        f = m.EO14110Filter()
        ctx = _ctx(m, eo14110_risk_tier=m.EO14110RiskTier.DUAL_USE_FOUNDATION,
                   red_team_assessment_completed=True, tevv_framework_applied=True)
        result = f.evaluate(ctx)
        assert result.decision == m.PublicSectorGovernanceDecision.APPROVED

    def test_safety_critical_no_tevv_denied(self, m):
        f = m.EO14110Filter()
        ctx = _ctx(m, eo14110_risk_tier=m.EO14110RiskTier.SAFETY_CRITICAL, tevv_framework_applied=False)
        result = f.evaluate(ctx)
        assert result.decision == m.PublicSectorGovernanceDecision.DENIED

    def test_safety_critical_no_safety_testing_denied(self, m):
        f = m.EO14110Filter()
        ctx = _ctx(m, eo14110_risk_tier=m.EO14110RiskTier.SAFETY_CRITICAL, pre_deployment_safety_testing_done=False)
        result = f.evaluate(ctx)
        assert result.decision == m.PublicSectorGovernanceDecision.DENIED

    def test_safety_critical_fully_compliant_approved(self, m):
        f = m.EO14110Filter()
        ctx = _ctx(m, eo14110_risk_tier=m.EO14110RiskTier.SAFETY_CRITICAL,
                   tevv_framework_applied=True, pre_deployment_safety_testing_done=True)
        result = f.evaluate(ctx)
        assert result.decision == m.PublicSectorGovernanceDecision.APPROVED


# ---------------------------------------------------------------------------
# Layer 3 — NIST AI RMF
# ---------------------------------------------------------------------------


class TestNISTAIRMFFilter:

    def test_full_maturity_approved_with_conditions(self, m):
        f = m.NISTAIRMFFilter()
        ctx = _ctx(m, nist_rmf_level=m.NISTRMFLevel.FULL)
        result = f.evaluate(ctx)
        assert result.decision == m.PublicSectorGovernanceDecision.APPROVED_WITH_CONDITIONS
        assert any("annual review" in c.lower() for c in result.conditions)

    def test_none_for_non_minimum_denied(self, m):
        f = m.NISTAIRMFFilter()
        ctx = _ctx(m, nist_rmf_level=m.NISTRMFLevel.NONE)
        result = f.evaluate(ctx)
        assert result.decision == m.PublicSectorGovernanceDecision.DENIED

    def test_minimal_for_non_minimum_denied(self, m):
        f = m.NISTAIRMFFilter()
        ctx = _ctx(m, nist_rmf_level=m.NISTRMFLevel.MINIMAL)
        result = f.evaluate(ctx)
        assert result.decision == m.PublicSectorGovernanceDecision.DENIED
        assert any("MINIMAL" in finding for finding in result.findings)

    def test_partial_with_missing_functions_approved_with_conditions(self, m):
        f = m.NISTAIRMFFilter()
        ctx = _ctx(m, nist_rmf_level=m.NISTRMFLevel.PARTIAL, nist_measure_quantified=False, nist_manage_plan_exists=False)
        result = f.evaluate(ctx)
        assert result.decision == m.PublicSectorGovernanceDecision.APPROVED_WITH_CONDITIONS
        assert any("MEASURE" in c and "MANAGE" in c for c in result.conditions)

    def test_partial_all_functions_documented_approved_with_conditions(self, m):
        """PARTIAL maturity but all four fields True → update-maturity condition."""
        f = m.NISTAIRMFFilter()
        ctx = _ctx(m, nist_rmf_level=m.NISTRMFLevel.PARTIAL)
        result = f.evaluate(ctx)
        assert result.decision == m.PublicSectorGovernanceDecision.APPROVED_WITH_CONDITIONS
        assert any("PARTIAL" in c or "update maturity" in c.lower() for c in result.conditions)

    def test_minimum_impact_none_denied(self, m):
        f = m.NISTAIRMFFilter()
        ctx = _min_ctx(m, nist_rmf_level=m.NISTRMFLevel.NONE)
        result = f.evaluate(ctx)
        assert result.decision == m.PublicSectorGovernanceDecision.DENIED

    def test_minimum_impact_minimal_accepted(self, m):
        f = m.NISTAIRMFFilter()
        ctx = _min_ctx(m, nist_rmf_level=m.NISTRMFLevel.MINIMAL)
        result = f.evaluate(ctx)
        assert result.decision == m.PublicSectorGovernanceDecision.APPROVED_WITH_CONDITIONS

    def test_partial_missing_govern_listed_in_conditions(self, m):
        f = m.NISTAIRMFFilter()
        ctx = _ctx(m, nist_rmf_level=m.NISTRMFLevel.PARTIAL, nist_govern_documented=False)
        result = f.evaluate(ctx)
        assert result.decision == m.PublicSectorGovernanceDecision.APPROVED_WITH_CONDITIONS
        assert any("GOVERN" in c for c in result.conditions)


# ---------------------------------------------------------------------------
# Layer 4 — Section 508 / ADA
# ---------------------------------------------------------------------------


class TestSection508Filter:

    def test_compliant_rights_impacting_approved_with_conditions(self, m):
        f = m.Section508Filter()
        ctx = _ctx(m)
        result = f.evaluate(ctx)
        assert result.decision == m.PublicSectorGovernanceDecision.APPROVED_WITH_CONDITIONS
        assert any("WCAG" in c or "508" in c for c in result.conditions)

    def test_not_508_compliant_denied(self, m):
        f = m.Section508Filter()
        ctx = _ctx(m, section_508_compliant=False)
        result = f.evaluate(ctx)
        assert result.decision == m.PublicSectorGovernanceDecision.DENIED
        assert any("Section 508" in finding for finding in result.findings)

    def test_no_plain_language_for_rights_impacting_denied(self, m):
        f = m.Section508Filter()
        ctx = _ctx(m, plain_language_explanations=False)
        result = f.evaluate(ctx)
        assert result.decision == m.PublicSectorGovernanceDecision.DENIED
        assert any("plain language" in finding.lower() for finding in result.findings)

    def test_citizen_services_requires_plain_language(self, m):
        f = m.Section508Filter()
        ctx = _ctx(
            m,
            use_case=m.FederalAIUseCase.CITIZEN_SERVICES_CHAT,
            impact_level=m.AIImpactLevel.LOW_IMPACT,
            plain_language_explanations=False,
        )
        result = f.evaluate(ctx)
        assert result.decision == m.PublicSectorGovernanceDecision.DENIED

    def test_minimum_impact_always_approved_with_conditions(self, m):
        f = m.Section508Filter()
        ctx = _min_ctx(m, section_508_compliant=False)
        result = f.evaluate(ctx)
        # Minimum-impact returns APPROVED_WITH_CONDITIONS early (employee accessibility only)
        assert result.decision == m.PublicSectorGovernanceDecision.APPROVED_WITH_CONDITIONS

    def test_internal_analytics_no_plain_language_needed(self, m):
        """Non-rights/safety/citizen use case skips plain-language check."""
        f = m.Section508Filter()
        ctx = _ctx(
            m,
            use_case=m.FederalAIUseCase.INTERNAL_ANALYTICS,
            impact_level=m.AIImpactLevel.LOW_IMPACT,
            plain_language_explanations=False,
        )
        result = f.evaluate(ctx)
        # Only 508 compliance needed; plain-language not required for INTERNAL_ANALYTICS
        assert result.decision != m.PublicSectorGovernanceDecision.DENIED or any(
            "plain language" not in f.lower() for f in result.findings
        )

    def test_safety_impacting_no_plain_language_denied(self, m):
        f = m.Section508Filter()
        ctx = _ctx(
            m,
            use_case=m.FederalAIUseCase.CRITICAL_INFRASTRUCTURE,
            impact_level=m.AIImpactLevel.SAFETY_IMPACTING,
            plain_language_explanations=False,
        )
        result = f.evaluate(ctx)
        assert result.decision == m.PublicSectorGovernanceDecision.DENIED


# ---------------------------------------------------------------------------
# Orchestrator — full four-layer
# ---------------------------------------------------------------------------


class TestPublicSectorGovernanceOrchestrator:

    def test_all_layers_approved_with_conditions_when_compliant(self, m):
        orch = m.PublicSectorGovernanceOrchestrator()
        ctx = _ctx(m)
        report = orch.evaluate(ctx)
        assert report.final_decision == m.PublicSectorGovernanceDecision.APPROVED_WITH_CONDITIONS
        assert len(report.layer_results) == 4

    def test_denied_if_any_layer_denied(self, m):
        orch = m.PublicSectorGovernanceOrchestrator()
        ctx = _ctx(m, human_review_available=False)
        report = orch.evaluate(ctx)
        assert report.final_decision == m.PublicSectorGovernanceDecision.DENIED

    def test_all_layers_evaluated_even_on_denial(self, m):
        orch = m.PublicSectorGovernanceOrchestrator()
        ctx = _ctx(m, human_review_available=False, section_508_compliant=False)
        report = orch.evaluate(ctx)
        assert len(report.layer_results) == 4

    def test_report_summary_contains_all_fields(self, m):
        orch = m.PublicSectorGovernanceOrchestrator()
        ctx = _ctx(m)
        report = orch.evaluate(ctx)
        summary = report.summary()
        assert summary["system_id"] == "GOV-TEST-001"
        assert summary["use_case"] == m.FederalAIUseCase.BENEFITS_DETERMINATION.value
        assert len(summary["layers"]) == 4

    def test_layer_order_omb_eo_nist_508(self, m):
        orch = m.PublicSectorGovernanceOrchestrator()
        ctx = _ctx(m)
        report = orch.evaluate(ctx)
        layers = [lr.layer for lr in report.layer_results]
        assert layers == ["OMB_M24_10", "EO_14110", "NIST_AI_RMF", "SECTION_508_ADA"]

    def test_minimum_impact_system_approved_with_conditions(self, m):
        orch = m.PublicSectorGovernanceOrchestrator()
        ctx = _min_ctx(m)
        report = orch.evaluate(ctx)
        assert report.final_decision != m.PublicSectorGovernanceDecision.DENIED

    def test_dual_use_no_red_team_denied(self, m):
        orch = m.PublicSectorGovernanceOrchestrator()
        ctx = _ctx(m, eo14110_risk_tier=m.EO14110RiskTier.DUAL_USE_FOUNDATION, red_team_assessment_completed=False)
        report = orch.evaluate(ctx)
        assert report.final_decision == m.PublicSectorGovernanceDecision.DENIED
        eo_layer = next(lr for lr in report.layer_results if lr.layer == "EO_14110")
        assert eo_layer.is_denied

    def test_nist_none_denied_regardless_of_other_layers(self, m):
        orch = m.PublicSectorGovernanceOrchestrator()
        ctx = _ctx(m, nist_rmf_level=m.NISTRMFLevel.NONE)
        report = orch.evaluate(ctx)
        assert report.final_decision == m.PublicSectorGovernanceDecision.DENIED

    def test_report_is_denied_property(self, m):
        orch = m.PublicSectorGovernanceOrchestrator()
        ctx = _ctx(m, human_review_available=False)
        report = orch.evaluate(ctx)
        omb = next(lr for lr in report.layer_results if lr.layer == "OMB_M24_10")
        assert omb.is_denied is True

    def test_report_has_conditions_property(self, m):
        orch = m.PublicSectorGovernanceOrchestrator()
        ctx = _ctx(m)
        report = orch.evaluate(ctx)
        for lr in report.layer_results:
            if lr.decision == m.PublicSectorGovernanceDecision.APPROVED_WITH_CONDITIONS:
                assert lr.has_conditions is True
