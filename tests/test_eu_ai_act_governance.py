"""
Tests for 16_eu_ai_act_governance.py

Four-layer EU AI Act governance framework:
  1. EURiskClassificationFilter — prohibited/high-risk/limited-transparency/minimal
  2. EUConformityAssessmentFilter — RMS + conformity assessment + CE marking
  3. EUDataGovernanceFilter — training data quality + bias examination + monitoring
  4. EUTransparencyHumanOversightFilter — instructions + oversight + logs + incident reporting
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
    Path(__file__).parent.parent / "examples" / "16_eu_ai_act_governance.py"
)


def _load_module():
    module_name = "eu_ai_act_governance_16"
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
# Helpers
# ---------------------------------------------------------------------------


def _ctx(m, **kwargs):
    """Fully compliant HIGH_RISK EMPLOYMENT_WORKERS context (baseline)."""
    defaults = dict(
        system_id="EU-TEST-001",
        system_name="Test CV Screener",
        risk_level=m.EUAIActRiskLevel.HIGH_RISK,
        annex_iii_category=m.AnnexIIICategory.EMPLOYMENT_WORKERS,
        conformity_assessment_route=m.EUConformityAssessmentRoute.INTERNAL_CONTROL,
        deploying_country="DE",
        provider_name="Test GmbH",
        is_prohibited_practice=False,
        risk_management_system_established=True,
        residual_risks_acceptable=True,
        post_market_monitoring_plan=True,
        training_data_quality_documented=True,
        bias_examination_completed=True,
        data_monitoring_active=True,
        conformity_assessment_completed=True,
        ce_marking_affixed=True,
        instructions_for_use_complete=True,
        disclosure_obligation_met=True,
        human_oversight_measures_designed=True,
        override_capability_available=True,
        deployer_logs_maintained=True,
        serious_incident_reporting_active=True,
    )
    defaults.update(kwargs)
    return m.EUAIActContext(**defaults)


def _limited_ctx(m, **kwargs):
    """Compliant LIMITED_TRANSPARENCY chatbot context."""
    defaults = dict(
        system_id="EU-LT-001",
        system_name="Test Chatbot",
        risk_level=m.EUAIActRiskLevel.LIMITED_TRANSPARENCY,
        annex_iii_category=None,
        conformity_assessment_route=m.EUConformityAssessmentRoute.NOT_REQUIRED,
        deploying_country="FR",
        provider_name="ChatCo",
        is_prohibited_practice=False,
        risk_management_system_established=False,
        residual_risks_acceptable=True,
        post_market_monitoring_plan=False,
        training_data_quality_documented=False,
        bias_examination_completed=False,
        data_monitoring_active=False,
        conformity_assessment_completed=False,
        ce_marking_affixed=False,
        instructions_for_use_complete=True,
        disclosure_obligation_met=True,
        human_oversight_measures_designed=True,
        override_capability_available=True,
        deployer_logs_maintained=True,
        serious_incident_reporting_active=False,
    )
    defaults.update(kwargs)
    return m.EUAIActContext(**defaults)


def _minimal_ctx(m, **kwargs):
    """MINIMAL_RISK context."""
    defaults = dict(
        system_id="EU-MIN-001",
        system_name="Spam Filter",
        risk_level=m.EUAIActRiskLevel.MINIMAL_RISK,
        annex_iii_category=None,
        conformity_assessment_route=m.EUConformityAssessmentRoute.NOT_REQUIRED,
        deploying_country="NL",
        provider_name="SpamCo",
        is_prohibited_practice=False,
        risk_management_system_established=False,
        residual_risks_acceptable=True,
        post_market_monitoring_plan=False,
        training_data_quality_documented=False,
        bias_examination_completed=False,
        data_monitoring_active=False,
        conformity_assessment_completed=False,
        ce_marking_affixed=False,
        instructions_for_use_complete=True,
        disclosure_obligation_met=False,
        human_oversight_measures_designed=False,
        override_capability_available=False,
        deployer_logs_maintained=False,
        serious_incident_reporting_active=False,
    )
    defaults.update(kwargs)
    return m.EUAIActContext(**defaults)


# ---------------------------------------------------------------------------
# Layer 1 — EURiskClassificationFilter
# ---------------------------------------------------------------------------


class TestEURiskClassificationFilter:

    def test_prohibited_practice_denied(self, m):
        f = m.EURiskClassificationFilter()
        ctx = _ctx(m, risk_level=m.EUAIActRiskLevel.PROHIBITED, is_prohibited_practice=True)
        result = f.evaluate(ctx)
        assert result.is_denied
        assert any("Article 5" in finding for finding in result.findings)

    def test_is_prohibited_flag_alone_denies(self, m):
        f = m.EURiskClassificationFilter()
        ctx = _ctx(m, is_prohibited_practice=True)
        result = f.evaluate(ctx)
        assert result.is_denied

    def test_high_risk_with_annex_iii_approved_with_conditions(self, m):
        f = m.EURiskClassificationFilter()
        ctx = _ctx(m)  # HIGH_RISK + EMPLOYMENT_WORKERS
        result = f.evaluate(ctx)
        assert result.has_conditions
        assert any("HIGH_RISK" in c or "EMPLOYMENT_WORKERS" in c for c in result.conditions)

    def test_high_risk_without_annex_iii_denied(self, m):
        f = m.EURiskClassificationFilter()
        ctx = _ctx(m, annex_iii_category=None)
        result = f.evaluate(ctx)
        assert result.is_denied
        assert any("Article 6" in finding for finding in result.findings)

    def test_limited_transparency_with_disclosure_approved_with_conditions(self, m):
        f = m.EURiskClassificationFilter()
        ctx = _limited_ctx(m)
        result = f.evaluate(ctx)
        assert result.has_conditions
        assert any("Article 50" in c for c in result.conditions)

    def test_limited_transparency_no_disclosure_denied(self, m):
        f = m.EURiskClassificationFilter()
        ctx = _limited_ctx(m, disclosure_obligation_met=False)
        result = f.evaluate(ctx)
        assert result.is_denied
        assert any("Article 50" in finding for finding in result.findings)

    def test_minimal_risk_approved_with_conditions(self, m):
        f = m.EURiskClassificationFilter()
        ctx = _minimal_ctx(m)
        result = f.evaluate(ctx)
        assert result.has_conditions
        assert any("MINIMAL_RISK" in c or "Recital 97" in c for c in result.conditions)


# ---------------------------------------------------------------------------
# Layer 2 — EUConformityAssessmentFilter
# ---------------------------------------------------------------------------


class TestEUConformityAssessmentFilter:

    def test_compliant_high_risk_approved_with_conditions(self, m):
        f = m.EUConformityAssessmentFilter()
        ctx = _ctx(m)
        result = f.evaluate(ctx)
        assert result.has_conditions

    def test_no_risk_management_system_denied(self, m):
        f = m.EUConformityAssessmentFilter()
        ctx = _ctx(m, risk_management_system_established=False)
        result = f.evaluate(ctx)
        assert result.is_denied
        assert any("Article 9" in finding for finding in result.findings)

    def test_residual_risks_not_acceptable_denied(self, m):
        f = m.EUConformityAssessmentFilter()
        ctx = _ctx(m, residual_risks_acceptable=False)
        result = f.evaluate(ctx)
        assert result.is_denied
        assert any("Article 9(4)" in finding for finding in result.findings)

    def test_no_post_market_plan_denied(self, m):
        f = m.EUConformityAssessmentFilter()
        ctx = _ctx(m, post_market_monitoring_plan=False)
        result = f.evaluate(ctx)
        assert result.is_denied
        assert any("Article 72" in finding for finding in result.findings)

    def test_conformity_assessment_not_completed_denied(self, m):
        f = m.EUConformityAssessmentFilter()
        ctx = _ctx(m, conformity_assessment_completed=False)
        result = f.evaluate(ctx)
        assert result.is_denied
        assert any("Article 43" in finding for finding in result.findings)

    def test_no_ce_marking_denied(self, m):
        f = m.EUConformityAssessmentFilter()
        ctx = _ctx(m, ce_marking_affixed=False)
        result = f.evaluate(ctx)
        assert result.is_denied
        assert any("Article 49" in finding for finding in result.findings)

    def test_non_high_risk_passes_with_approved(self, m):
        f = m.EUConformityAssessmentFilter()
        ctx = _limited_ctx(m)
        result = f.evaluate(ctx)
        assert not result.is_denied
        assert result.decision == m.EUGovernanceDecision.APPROVED

    def test_compliant_conditions_reference_reassessment(self, m):
        f = m.EUConformityAssessmentFilter()
        ctx = _ctx(m)
        result = f.evaluate(ctx)
        assert any("re-assessment" in c or "Article 43" in c for c in result.conditions)


# ---------------------------------------------------------------------------
# Layer 3 — EUDataGovernanceFilter
# ---------------------------------------------------------------------------


class TestEUDataGovernanceFilter:

    def test_compliant_high_risk_approved_with_conditions(self, m):
        f = m.EUDataGovernanceFilter()
        ctx = _ctx(m)
        result = f.evaluate(ctx)
        assert result.has_conditions
        assert any("Article 10(5)" in c for c in result.conditions)

    def test_no_training_data_quality_docs_denied(self, m):
        f = m.EUDataGovernanceFilter()
        ctx = _ctx(m, training_data_quality_documented=False)
        result = f.evaluate(ctx)
        assert result.is_denied
        assert any("Article 10(2)" in finding for finding in result.findings)

    def test_no_bias_examination_denied(self, m):
        f = m.EUDataGovernanceFilter()
        ctx = _ctx(m, bias_examination_completed=False)
        result = f.evaluate(ctx)
        assert result.is_denied
        assert any("Article 10(5)" in finding for finding in result.findings)

    def test_data_monitoring_inactive_denied(self, m):
        f = m.EUDataGovernanceFilter()
        ctx = _ctx(m, data_monitoring_active=False)
        result = f.evaluate(ctx)
        assert result.is_denied

    def test_non_high_risk_gets_best_practice_condition(self, m):
        f = m.EUDataGovernanceFilter()
        ctx = _limited_ctx(m)
        result = f.evaluate(ctx)
        assert result.has_conditions
        assert any("best practice" in c or "Article 10" in c for c in result.conditions)

    def test_minimal_risk_also_gets_best_practice(self, m):
        f = m.EUDataGovernanceFilter()
        ctx = _minimal_ctx(m)
        result = f.evaluate(ctx)
        assert result.has_conditions

    def test_bias_condition_references_article(self, m):
        f = m.EUDataGovernanceFilter()
        ctx = _ctx(m)
        result = f.evaluate(ctx)
        assert any("bias" in c.lower() or "Article 10(5)" in c for c in result.conditions)


# ---------------------------------------------------------------------------
# Layer 4 — EUTransparencyHumanOversightFilter
# ---------------------------------------------------------------------------


class TestEUTransparencyHumanOversightFilter:

    def test_compliant_high_risk_approved_with_conditions(self, m):
        f = m.EUTransparencyHumanOversightFilter()
        ctx = _ctx(m)
        result = f.evaluate(ctx)
        assert result.has_conditions
        assert any("Article 13" in c for c in result.conditions)

    def test_no_instructions_denied(self, m):
        f = m.EUTransparencyHumanOversightFilter()
        ctx = _ctx(m, instructions_for_use_complete=False)
        result = f.evaluate(ctx)
        assert result.is_denied
        assert any("Article 13" in finding for finding in result.findings)

    def test_no_human_oversight_high_risk_denied(self, m):
        f = m.EUTransparencyHumanOversightFilter()
        ctx = _ctx(m, human_oversight_measures_designed=False)
        result = f.evaluate(ctx)
        assert result.is_denied
        assert any("Article 14" in finding for finding in result.findings)

    def test_no_override_capability_high_risk_denied(self, m):
        f = m.EUTransparencyHumanOversightFilter()
        ctx = _ctx(m, override_capability_available=False)
        result = f.evaluate(ctx)
        assert result.is_denied
        assert any("Article 14(4)" in finding for finding in result.findings)

    def test_no_deployer_logs_high_risk_denied(self, m):
        f = m.EUTransparencyHumanOversightFilter()
        ctx = _ctx(m, deployer_logs_maintained=False)
        result = f.evaluate(ctx)
        assert result.is_denied
        assert any("Article 26" in finding for finding in result.findings)

    def test_no_incident_reporting_high_risk_denied(self, m):
        f = m.EUTransparencyHumanOversightFilter()
        ctx = _ctx(m, serious_incident_reporting_active=False)
        result = f.evaluate(ctx)
        assert result.is_denied
        assert any("Article 73" in finding for finding in result.findings)

    def test_no_incident_reporting_limited_transparency_not_denied(self, m):
        """Article 73 incident reporting is HIGH_RISK only — not required for LIMITED_TRANSPARENCY."""
        f = m.EUTransparencyHumanOversightFilter()
        ctx = _limited_ctx(m, serious_incident_reporting_active=False)
        result = f.evaluate(ctx)
        assert not result.is_denied

    def test_minimal_risk_early_return_approved_with_conditions(self, m):
        f = m.EUTransparencyHumanOversightFilter()
        ctx = _minimal_ctx(m)
        result = f.evaluate(ctx)
        assert result.has_conditions
        assert any("Article 13" in c for c in result.conditions)

    def test_limited_transparency_compliant_approved_with_conditions(self, m):
        f = m.EUTransparencyHumanOversightFilter()
        ctx = _limited_ctx(m)
        result = f.evaluate(ctx)
        assert result.has_conditions


# ---------------------------------------------------------------------------
# EUAIActGovernanceOrchestrator
# ---------------------------------------------------------------------------


class TestEUAIActGovernanceOrchestrator:

    def test_fully_compliant_high_risk_approved_with_conditions(self, m):
        orch = m.EUAIActGovernanceOrchestrator()
        ctx = _ctx(m)
        report = orch.evaluate(ctx)
        assert report.final_decision == m.EUGovernanceDecision.APPROVED_WITH_CONDITIONS

    def test_prohibited_practice_final_denied(self, m):
        orch = m.EUAIActGovernanceOrchestrator()
        ctx = _ctx(m, risk_level=m.EUAIActRiskLevel.PROHIBITED, is_prohibited_practice=True)
        report = orch.evaluate(ctx)
        assert report.final_decision == m.EUGovernanceDecision.DENIED

    def test_all_four_layers_evaluated(self, m):
        orch = m.EUAIActGovernanceOrchestrator()
        ctx = _ctx(m)
        report = orch.evaluate(ctx)
        layer_names = {lr.layer for lr in report.layer_results}
        assert "EU_RISK_CLASSIFICATION" in layer_names
        assert "EU_CONFORMITY_ASSESSMENT" in layer_names
        assert "EU_DATA_GOVERNANCE" in layer_names
        assert "EU_TRANSPARENCY_OVERSIGHT" in layer_names

    def test_layer_order(self, m):
        orch = m.EUAIActGovernanceOrchestrator()
        ctx = _ctx(m)
        report = orch.evaluate(ctx)
        order = [lr.layer for lr in report.layer_results]
        assert order == [
            "EU_RISK_CLASSIFICATION",
            "EU_CONFORMITY_ASSESSMENT",
            "EU_DATA_GOVERNANCE",
            "EU_TRANSPARENCY_OVERSIGHT",
        ]

    def test_report_summary_structure(self, m):
        orch = m.EUAIActGovernanceOrchestrator()
        ctx = _ctx(m)
        report = orch.evaluate(ctx)
        s = report.summary()
        assert s["system_id"] == ctx.system_id
        assert s["system_name"] == ctx.system_name
        assert s["risk_level"] == "HIGH_RISK"
        assert "final_decision" in s
        assert len(s["layers"]) == 4

    def test_missing_conformity_assessment_denied(self, m):
        orch = m.EUAIActGovernanceOrchestrator()
        ctx = _ctx(m, conformity_assessment_completed=False, ce_marking_affixed=False)
        report = orch.evaluate(ctx)
        assert report.final_decision == m.EUGovernanceDecision.DENIED

    def test_limited_transparency_compliant_approved_with_conditions(self, m):
        orch = m.EUAIActGovernanceOrchestrator()
        ctx = _limited_ctx(m)
        report = orch.evaluate(ctx)
        assert report.final_decision == m.EUGovernanceDecision.APPROVED_WITH_CONDITIONS

    def test_minimal_risk_approved_with_conditions(self, m):
        orch = m.EUAIActGovernanceOrchestrator()
        ctx = _minimal_ctx(m)
        report = orch.evaluate(ctx)
        assert report.final_decision == m.EUGovernanceDecision.APPROVED_WITH_CONDITIONS

    def test_is_denied_property(self, m):
        result = m.EUGovernanceResult(layer="TEST")
        result.decision = m.EUGovernanceDecision.DENIED
        assert result.is_denied
        result.decision = m.EUGovernanceDecision.APPROVED
        assert not result.is_denied

    def test_has_conditions_property(self, m):
        result = m.EUGovernanceResult(layer="TEST")
        result.decision = m.EUGovernanceDecision.APPROVED_WITH_CONDITIONS
        assert result.has_conditions
        result.decision = m.EUGovernanceDecision.APPROVED
        assert not result.has_conditions
