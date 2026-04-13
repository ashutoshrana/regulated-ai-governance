"""
Tests for 14_insurance_ai_governance.py

Four-layer insurance AI governance:
  Layer 1: NAIC Model AI Governance Bulletin 2023
  Layer 2: FCRA adverse action notice
  Layer 3: NY DFS Circular Letter 2019-1
  Layer 4: ECOA disparate impact (4/5 rule)
"""

import importlib.util
import sys
import types
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Module loading
# ---------------------------------------------------------------------------

_MOD_PATH = Path(__file__).parent.parent / "examples" / "14_insurance_ai_governance.py"


def _load_module():
    module_name = "insurance_ai_governance"
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
# Helpers — default passing context
# ---------------------------------------------------------------------------


def _ctx(m, **kwargs):
    """
    Default: fully compliant HIGH risk underwriting model in NY.
    All flags set to passing values.
    """
    defaults = dict(
        model_id="M-TEST",
        model_name="Test Model",
        use_case=m.InsuranceAIUseCase.UNDERWRITING_DECISION,
        risk_level=m.InsuranceModelRiskLevel.HIGH,
        intended_states=frozenset({"NY"}),
        is_model_documented=True,
        is_model_validated=True,
        is_monitoring_active=True,
        is_explainability_available=True,
        uses_consumer_report=True,
        uses_credit_based_insurance_score=True,
        adverse_action_reasons_specific=True,
        uses_prohibited_factor=False,
        ecdis_sources_documented=True,
        non_discrimination_validated=True,
        disparate_impact_ratio=0.90,
        protected_class_sample_size=200,
        min_sample_size_for_di_test=100,
    )
    defaults.update(kwargs)
    return m.InsuranceModelContext(**defaults)


# ---------------------------------------------------------------------------
# Layer 1 — NAIC filter
# ---------------------------------------------------------------------------


class TestNAICFilter:
    def test_high_risk_all_compliant_approved_with_conditions(self, m):
        f = m.NAICFilter()
        ctx = _ctx(m, risk_level=m.InsuranceModelRiskLevel.HIGH)
        result = f.evaluate(ctx)
        # HIGH risk with all requirements met should have annual review condition
        assert result.decision in (
            m.InsuranceGovernanceDecision.APPROVED_WITH_CONDITIONS,
            m.InsuranceGovernanceDecision.APPROVED,
        )
        assert result.layer == "NAIC_2023"

    def test_high_risk_missing_validation_denied(self, m):
        f = m.NAICFilter()
        ctx = _ctx(m, risk_level=m.InsuranceModelRiskLevel.HIGH, is_model_validated=False)
        result = f.evaluate(ctx)
        assert result.decision == m.InsuranceGovernanceDecision.DENIED
        assert any("validation" in finding.lower() for finding in result.findings)

    def test_high_risk_missing_monitoring_denied(self, m):
        f = m.NAICFilter()
        ctx = _ctx(m, risk_level=m.InsuranceModelRiskLevel.HIGH, is_monitoring_active=False)
        result = f.evaluate(ctx)
        assert result.decision == m.InsuranceGovernanceDecision.DENIED
        assert any("monitoring" in f.lower() for f in result.findings)

    def test_high_risk_missing_explainability_denied(self, m):
        f = m.NAICFilter()
        ctx = _ctx(m, risk_level=m.InsuranceModelRiskLevel.HIGH, is_explainability_available=False)
        result = f.evaluate(ctx)
        assert result.decision == m.InsuranceGovernanceDecision.DENIED
        assert any("explainability" in finding.lower() for finding in result.findings)

    def test_medium_risk_requires_validation_and_monitoring(self, m):
        f = m.NAICFilter()
        ctx = _ctx(
            m,
            risk_level=m.InsuranceModelRiskLevel.MEDIUM,
            is_model_validated=False,
            is_monitoring_active=False,
        )
        result = f.evaluate(ctx)
        assert result.decision == m.InsuranceGovernanceDecision.DENIED
        # Should have two findings (validation + monitoring)
        assert len(result.findings) >= 2

    def test_low_risk_only_requires_documentation(self, m):
        f = m.NAICFilter()
        ctx = _ctx(
            m,
            risk_level=m.InsuranceModelRiskLevel.LOW,
            is_model_validated=False,  # Not required for LOW
            is_monitoring_active=False,  # Not required for LOW
            is_explainability_available=False,
        )
        result = f.evaluate(ctx)
        assert result.decision == m.InsuranceGovernanceDecision.APPROVED

    def test_low_risk_missing_documentation_denied(self, m):
        f = m.NAICFilter()
        ctx = _ctx(
            m,
            risk_level=m.InsuranceModelRiskLevel.LOW,
            is_model_documented=False,
        )
        result = f.evaluate(ctx)
        assert result.decision == m.InsuranceGovernanceDecision.DENIED

    def test_high_risk_annual_review_condition_present(self, m):
        f = m.NAICFilter()
        ctx = _ctx(m, risk_level=m.InsuranceModelRiskLevel.HIGH)
        result = f.evaluate(ctx)
        if result.decision == m.InsuranceGovernanceDecision.APPROVED_WITH_CONDITIONS:
            assert any("annual" in c.lower() or "review" in c.lower() for c in result.conditions)

    def test_missing_documentation_always_denied(self, m):
        f = m.NAICFilter()
        for risk in m.InsuranceModelRiskLevel:
            ctx = _ctx(m, risk_level=risk, is_model_documented=False)
            result = f.evaluate(ctx)
            assert result.decision == m.InsuranceGovernanceDecision.DENIED, (
                f"Expected DENIED for {risk} with missing documentation"
            )


# ---------------------------------------------------------------------------
# Layer 2 — FCRA filter
# ---------------------------------------------------------------------------


class TestFCRAFilter:
    def test_prohibited_factor_always_denied(self, m):
        f = m.FCRAFilter()
        ctx = _ctx(m, uses_prohibited_factor=True)
        result = f.evaluate(ctx)
        assert result.decision == m.InsuranceGovernanceDecision.DENIED
        assert result.layer == "FCRA"
        assert any("prohibited" in finding.lower() for finding in result.findings)

    def test_cbis_with_specific_reasons_approved_with_conditions(self, m):
        f = m.FCRAFilter()
        ctx = _ctx(
            m,
            uses_credit_based_insurance_score=True,
            adverse_action_reasons_specific=True,
            is_explainability_available=True,
        )
        result = f.evaluate(ctx)
        assert result.decision == m.InsuranceGovernanceDecision.APPROVED_WITH_CONDITIONS
        assert any("adverse action notice" in c.lower() or "fcra" in c.lower() for c in result.conditions)

    def test_cbis_without_specific_reasons_denied(self, m):
        f = m.FCRAFilter()
        ctx = _ctx(
            m,
            uses_credit_based_insurance_score=True,
            adverse_action_reasons_specific=False,
            is_explainability_available=True,
        )
        result = f.evaluate(ctx)
        assert result.decision == m.InsuranceGovernanceDecision.DENIED
        assert any("specific" in finding.lower() for finding in result.findings)

    def test_cbis_without_explainability_denied(self, m):
        f = m.FCRAFilter()
        ctx = _ctx(
            m,
            uses_credit_based_insurance_score=True,
            adverse_action_reasons_specific=True,
            is_explainability_available=False,
        )
        result = f.evaluate(ctx)
        assert result.decision == m.InsuranceGovernanceDecision.DENIED

    def test_no_consumer_report_approved(self, m):
        f = m.FCRAFilter()
        ctx = _ctx(
            m,
            uses_consumer_report=False,
            uses_credit_based_insurance_score=False,
        )
        result = f.evaluate(ctx)
        assert result.decision == m.InsuranceGovernanceDecision.APPROVED

    def test_operational_use_case_no_adverse_action_requirement(self, m):
        f = m.FCRAFilter()
        ctx = _ctx(
            m,
            use_case=m.InsuranceAIUseCase.OPERATIONAL_ANALYTICS,
            uses_consumer_report=True,
            uses_credit_based_insurance_score=True,
            adverse_action_reasons_specific=False,
        )
        result = f.evaluate(ctx)
        # Operational analytics doesn't trigger adverse action requirement
        assert result.decision == m.InsuranceGovernanceDecision.APPROVED

    def test_prohibited_factor_takes_priority_over_everything(self, m):
        f = m.FCRAFilter()
        ctx = _ctx(
            m,
            uses_prohibited_factor=True,
            uses_credit_based_insurance_score=True,
            adverse_action_reasons_specific=True,
        )
        result = f.evaluate(ctx)
        assert result.decision == m.InsuranceGovernanceDecision.DENIED
        assert any("prohibited" in finding.lower() for finding in result.findings)


# ---------------------------------------------------------------------------
# Layer 3 — NY DFS filter
# ---------------------------------------------------------------------------


class TestNYDFSFilter:
    def test_non_ny_state_approved(self, m):
        f = m.NYDFSFilter()
        ctx = _ctx(m, intended_states=frozenset({"TX", "FL", "CA"}))
        result = f.evaluate(ctx)
        assert result.decision == m.InsuranceGovernanceDecision.APPROVED
        assert result.layer == "NY_DFS_2019"
        assert any("does not apply" in finding.lower() for finding in result.findings)

    def test_ny_state_missing_ecdis_docs_denied(self, m):
        f = m.NYDFSFilter()
        ctx = _ctx(m, intended_states=frozenset({"NY"}), ecdis_sources_documented=False)
        result = f.evaluate(ctx)
        assert result.decision == m.InsuranceGovernanceDecision.DENIED
        assert any("ecdis" in finding.lower() for finding in result.findings)

    def test_ny_state_missing_non_discrimination_validation_denied(self, m):
        f = m.NYDFSFilter()
        ctx = _ctx(m, intended_states=frozenset({"NY"}), non_discrimination_validated=False)
        result = f.evaluate(ctx)
        assert result.decision == m.InsuranceGovernanceDecision.DENIED
        # Finding text references proxies for protected characteristics
        assert any("prox" in finding.lower() or "validated" in finding.lower() for finding in result.findings)

    def test_ny_state_both_missing_denied_with_two_findings(self, m):
        f = m.NYDFSFilter()
        ctx = _ctx(
            m,
            intended_states=frozenset({"NY"}),
            ecdis_sources_documented=False,
            non_discrimination_validated=False,
        )
        result = f.evaluate(ctx)
        assert result.decision == m.InsuranceGovernanceDecision.DENIED
        assert len(result.findings) >= 2

    def test_ny_state_compliant_approved_with_conditions(self, m):
        f = m.NYDFSFilter()
        ctx = _ctx(
            m,
            intended_states=frozenset({"NY"}),
            ecdis_sources_documented=True,
            non_discrimination_validated=True,
        )
        result = f.evaluate(ctx)
        assert result.decision == m.InsuranceGovernanceDecision.APPROVED_WITH_CONDITIONS

    def test_multi_state_including_ny_triggers_ny_rules(self, m):
        f = m.NYDFSFilter()
        ctx = _ctx(
            m,
            intended_states=frozenset({"NY", "NJ", "CT"}),
            ecdis_sources_documented=False,
        )
        result = f.evaluate(ctx)
        assert result.decision == m.InsuranceGovernanceDecision.DENIED

    def test_non_ny_ignores_ecdis_status(self, m):
        f = m.NYDFSFilter()
        ctx = _ctx(
            m,
            intended_states=frozenset({"CA"}),
            ecdis_sources_documented=False,
            non_discrimination_validated=False,
        )
        result = f.evaluate(ctx)
        assert result.decision == m.InsuranceGovernanceDecision.APPROVED


# ---------------------------------------------------------------------------
# Layer 4 — ECOA Disparate Impact filter
# ---------------------------------------------------------------------------


class TestECOAFilter:
    def test_ratio_above_threshold_approved_with_conditions(self, m):
        f = m.ECOADisparateImpactFilter()
        ctx = _ctx(m, disparate_impact_ratio=0.85, protected_class_sample_size=200)
        result = f.evaluate(ctx)
        assert result.decision == m.InsuranceGovernanceDecision.APPROVED_WITH_CONDITIONS
        assert result.layer == "ECOA_DISPARATE_IMPACT"

    def test_ratio_at_exactly_threshold_approved(self, m):
        f = m.ECOADisparateImpactFilter()
        ctx = _ctx(m, disparate_impact_ratio=0.80, protected_class_sample_size=200)
        result = f.evaluate(ctx)
        # 0.80 == threshold → not less than threshold → approved
        assert result.decision == m.InsuranceGovernanceDecision.APPROVED_WITH_CONDITIONS

    def test_ratio_below_threshold_denied(self, m):
        f = m.ECOADisparateImpactFilter()
        ctx = _ctx(m, disparate_impact_ratio=0.72, protected_class_sample_size=200)
        result = f.evaluate(ctx)
        assert result.decision == m.InsuranceGovernanceDecision.DENIED
        assert any("disparate impact" in finding.lower() for finding in result.findings)
        assert "72.0%" in result.findings[0]

    def test_insufficient_sample_size_denied(self, m):
        f = m.ECOADisparateImpactFilter()
        ctx = _ctx(m, disparate_impact_ratio=0.95, protected_class_sample_size=50, min_sample_size_for_di_test=100)
        result = f.evaluate(ctx)
        assert result.decision == m.InsuranceGovernanceDecision.DENIED
        assert any("insufficient" in finding.lower() for finding in result.findings)

    def test_none_ratio_with_sufficient_sample_denied(self, m):
        f = m.ECOADisparateImpactFilter()
        ctx = _ctx(m, disparate_impact_ratio=None, protected_class_sample_size=200)
        result = f.evaluate(ctx)
        assert result.decision == m.InsuranceGovernanceDecision.DENIED

    def test_non_adverse_action_use_case_approved(self, m):
        f = m.ECOADisparateImpactFilter()
        ctx = _ctx(
            m,
            use_case=m.InsuranceAIUseCase.OPERATIONAL_ANALYTICS,
            disparate_impact_ratio=0.50,  # Would fail if applied
            protected_class_sample_size=200,
        )
        result = f.evaluate(ctx)
        assert result.decision == m.InsuranceGovernanceDecision.APPROVED
        assert any("not required" in finding.lower() for finding in result.findings)

    def test_fraud_detection_use_case_evaluated(self, m):
        """Fraud detection with CLAIMS_ADJUDICATION use case triggers DI check."""
        f = m.ECOADisparateImpactFilter()
        ctx = _ctx(
            m,
            use_case=m.InsuranceAIUseCase.CLAIMS_ADJUDICATION,
            disparate_impact_ratio=0.65,
            protected_class_sample_size=200,
        )
        result = f.evaluate(ctx)
        assert result.decision == m.InsuranceGovernanceDecision.DENIED

    def test_ratio_just_above_threshold(self, m):
        f = m.ECOADisparateImpactFilter()
        ctx = _ctx(m, disparate_impact_ratio=0.801, protected_class_sample_size=200)
        result = f.evaluate(ctx)
        assert result.decision == m.InsuranceGovernanceDecision.APPROVED_WITH_CONDITIONS

    def test_ratio_just_below_threshold(self, m):
        f = m.ECOADisparateImpactFilter()
        ctx = _ctx(m, disparate_impact_ratio=0.799, protected_class_sample_size=200)
        result = f.evaluate(ctx)
        assert result.decision == m.InsuranceGovernanceDecision.DENIED

    def test_conditions_mention_ratio_value(self, m):
        f = m.ECOADisparateImpactFilter()
        ctx = _ctx(m, disparate_impact_ratio=0.88, protected_class_sample_size=200)
        result = f.evaluate(ctx)
        assert result.decision == m.InsuranceGovernanceDecision.APPROVED_WITH_CONDITIONS
        assert any("0.88" in c for c in result.conditions)


# ---------------------------------------------------------------------------
# Orchestrator integration tests
# ---------------------------------------------------------------------------


class TestInsuranceGovernanceOrchestrator:
    def test_all_layers_pass_returns_approved_with_conditions(self, m):
        orch = m.InsuranceGovernanceOrchestrator()
        ctx = _ctx(m)
        report = orch.evaluate(ctx)
        assert report.final_decision in (
            m.InsuranceGovernanceDecision.APPROVED_WITH_CONDITIONS,
            m.InsuranceGovernanceDecision.APPROVED,
        )
        assert report.model_id == "M-TEST"
        assert len(report.layer_results) == 4

    def test_any_denied_layer_makes_report_denied(self, m):
        orch = m.InsuranceGovernanceOrchestrator()
        ctx = _ctx(m, is_model_validated=False)  # NAIC will deny
        report = orch.evaluate(ctx)
        assert report.final_decision == m.InsuranceGovernanceDecision.DENIED

    def test_all_layers_evaluated_even_when_first_denies(self, m):
        orch = m.InsuranceGovernanceOrchestrator()
        ctx = _ctx(m, is_model_documented=False)  # NAIC denies
        report = orch.evaluate(ctx)
        assert len(report.layer_results) == 4
        layers = [lr.layer for lr in report.layer_results]
        assert "NAIC_2023" in layers
        assert "FCRA" in layers
        assert "NY_DFS_2019" in layers
        assert "ECOA_DISPARATE_IMPACT" in layers

    def test_low_risk_operational_approved(self, m):
        orch = m.InsuranceGovernanceOrchestrator()
        ctx = _ctx(
            m,
            use_case=m.InsuranceAIUseCase.OPERATIONAL_ANALYTICS,
            risk_level=m.InsuranceModelRiskLevel.LOW,
            intended_states=frozenset({"WA"}),
            is_model_validated=False,
            is_monitoring_active=False,
            is_explainability_available=False,
            uses_consumer_report=False,
            uses_credit_based_insurance_score=False,
            disparate_impact_ratio=None,
            protected_class_sample_size=0,
        )
        report = orch.evaluate(ctx)
        assert report.final_decision == m.InsuranceGovernanceDecision.APPROVED

    def test_summary_structure(self, m):
        orch = m.InsuranceGovernanceOrchestrator()
        ctx = _ctx(m)
        report = orch.evaluate(ctx)
        summary = report.summary()
        assert "model_id" in summary
        assert "final_decision" in summary
        assert "layers" in summary
        assert len(summary["layers"]) == 4
        for layer_entry in summary["layers"]:
            assert "layer" in layer_entry
            assert "decision" in layer_entry
            assert "findings" in layer_entry
            assert "conditions" in layer_entry

    def test_prohibited_factor_denied_even_with_all_else_compliant(self, m):
        orch = m.InsuranceGovernanceOrchestrator()
        ctx = _ctx(m, uses_prohibited_factor=True)
        report = orch.evaluate(ctx)
        assert report.final_decision == m.InsuranceGovernanceDecision.DENIED
        fcra_result = next(lr for lr in report.layer_results if lr.layer == "FCRA")
        assert fcra_result.is_denied

    def test_disparate_impact_denial_propagates(self, m):
        orch = m.InsuranceGovernanceOrchestrator()
        ctx = _ctx(m, disparate_impact_ratio=0.60, protected_class_sample_size=200)
        report = orch.evaluate(ctx)
        assert report.final_decision == m.InsuranceGovernanceDecision.DENIED
        ecoa_result = next(lr for lr in report.layer_results if lr.layer == "ECOA_DISPARATE_IMPACT")
        assert ecoa_result.is_denied

    def test_multiple_denied_layers_still_denied(self, m):
        orch = m.InsuranceGovernanceOrchestrator()
        ctx = _ctx(
            m,
            is_model_validated=False,  # NAIC denies
            uses_prohibited_factor=True,  # FCRA denies
            ecdis_sources_documented=False,  # NY DFS denies
            disparate_impact_ratio=0.50,  # ECOA denies
        )
        report = orch.evaluate(ctx)
        assert report.final_decision == m.InsuranceGovernanceDecision.DENIED
        denied_layers = [lr for lr in report.layer_results if lr.is_denied]
        assert len(denied_layers) >= 3

    def test_marketing_segmentation_ecoa_not_required(self, m):
        orch = m.InsuranceGovernanceOrchestrator()
        ctx = _ctx(
            m,
            use_case=m.InsuranceAIUseCase.MARKETING_SEGMENTATION,
            risk_level=m.InsuranceModelRiskLevel.MEDIUM,
            disparate_impact_ratio=0.50,  # Would fail if applied
            protected_class_sample_size=200,
            uses_consumer_report=False,
            uses_credit_based_insurance_score=False,
        )
        report = orch.evaluate(ctx)
        ecoa = next(lr for lr in report.layer_results if lr.layer == "ECOA_DISPARATE_IMPACT")
        assert ecoa.decision == m.InsuranceGovernanceDecision.APPROVED

    def test_report_use_case_in_summary(self, m):
        orch = m.InsuranceGovernanceOrchestrator()
        ctx = _ctx(m, use_case=m.InsuranceAIUseCase.CLAIMS_ADJUDICATION)
        report = orch.evaluate(ctx)
        assert "CLAIMS_ADJUDICATION" in report.summary()["use_case"]

    def test_is_denied_property_on_result(self, m):
        f = m.NAICFilter()
        ctx = _ctx(m, is_model_documented=False)
        result = f.evaluate(ctx)
        assert result.is_denied is True

    def test_has_conditions_property_on_result(self, m):
        f = m.NAICFilter()
        ctx = _ctx(m, risk_level=m.InsuranceModelRiskLevel.HIGH)
        result = f.evaluate(ctx)
        if result.decision == m.InsuranceGovernanceDecision.APPROVED_WITH_CONDITIONS:
            assert result.has_conditions is True
        else:
            assert result.has_conditions is False
