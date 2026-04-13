"""Tests for 12_medtech_ai_governance.py — FDA SaMD + IEC 62304 + ISO 14971 + EU MDR"""

from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Module loading
# ---------------------------------------------------------------------------


def _load_module(name: str):
    examples_dir = Path(__file__).parent.parent / "examples"
    spec = importlib.util.spec_from_file_location(name, examples_dir / "12_medtech_ai_governance.py")
    mod = types.ModuleType(name)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def m():
    return _load_module("medtech_governance")


# ---------------------------------------------------------------------------
# Helper: build a context
# ---------------------------------------------------------------------------


def _make_context(m, **overrides):
    defaults = dict(
        system_id="SYS-TEST-001",
        system_name="Test AI System",
        iec62304_safety_class=m.IEC62304SafetyClass.CLASS_B,
        fda_device_class=m.FDASaMDClass.CLASS_II,
        fda_clearance_pathway=m.FDAClearancePathway.K510_CLEARED,
        eu_mdr_class=m.EUMDRClass.CLASS_IIA,
        iso14971_residual_risk=m.ISO14971RiskLevel.ACCEPTABLE,
        intended_use="Test intended use",
        has_notified_body_certificate=True,
        has_pccp=True,
        lifecycle_documentation_complete=True,
        formal_verification_complete=True,
        risk_management_file_complete=True,
        clinical_validation_study_complete=True,
        change_type=None,
        intended_markets=("US", "EU"),
    )
    defaults.update(overrides)
    return m.MedicalAIRequestContext(**defaults)


# ---------------------------------------------------------------------------
# TestIEC62304SafetyFilter
# ---------------------------------------------------------------------------


class TestIEC62304SafetyFilter:
    def test_class_a_always_approved(self, m):
        f = m.IEC62304SafetyFilter()
        ctx = _make_context(
            m,
            iec62304_safety_class=m.IEC62304SafetyClass.CLASS_A,
            lifecycle_documentation_complete=False,
            formal_verification_complete=False,
        )
        result = f.evaluate(ctx)
        assert not result.is_denied
        assert result.decision == m.DeploymentDecision.APPROVED

    def test_class_b_incomplete_docs_denied(self, m):
        f = m.IEC62304SafetyFilter()
        ctx = _make_context(
            m, iec62304_safety_class=m.IEC62304SafetyClass.CLASS_B, lifecycle_documentation_complete=False
        )
        result = f.evaluate(ctx)
        assert result.is_denied
        assert any("62304" in v for v in result.violations)

    def test_class_b_complete_docs_approved(self, m):
        f = m.IEC62304SafetyFilter()
        ctx = _make_context(
            m, iec62304_safety_class=m.IEC62304SafetyClass.CLASS_B, lifecycle_documentation_complete=True
        )
        result = f.evaluate(ctx)
        assert not result.is_denied

    def test_class_c_missing_formal_verification_denied(self, m):
        f = m.IEC62304SafetyFilter()
        ctx = _make_context(
            m,
            iec62304_safety_class=m.IEC62304SafetyClass.CLASS_C,
            lifecycle_documentation_complete=True,
            formal_verification_complete=False,
        )
        result = f.evaluate(ctx)
        assert result.is_denied
        assert any("formal verification" in v.lower() for v in result.violations)

    def test_class_c_missing_lifecycle_docs_denied(self, m):
        f = m.IEC62304SafetyFilter()
        ctx = _make_context(
            m,
            iec62304_safety_class=m.IEC62304SafetyClass.CLASS_C,
            lifecycle_documentation_complete=False,
            formal_verification_complete=True,
        )
        result = f.evaluate(ctx)
        assert result.is_denied

    def test_class_c_full_compliance_approved_with_conditions(self, m):
        f = m.IEC62304SafetyFilter()
        ctx = _make_context(
            m,
            iec62304_safety_class=m.IEC62304SafetyClass.CLASS_C,
            lifecycle_documentation_complete=True,
            formal_verification_complete=True,
        )
        result = f.evaluate(ctx)
        assert not result.is_denied
        assert len(result.conditions) > 0

    def test_class_a_has_note(self, m):
        f = m.IEC62304SafetyFilter()
        ctx = _make_context(m, iec62304_safety_class=m.IEC62304SafetyClass.CLASS_A)
        result = f.evaluate(ctx)
        assert len(result.notes) > 0

    def test_layer_name(self, m):
        f = m.IEC62304SafetyFilter()
        ctx = _make_context(m, iec62304_safety_class=m.IEC62304SafetyClass.CLASS_B)
        result = f.evaluate(ctx)
        assert result.layer == "IEC 62304"

    def test_class_b_missing_both_lifecycle_and_fv_reports_violation(self, m):
        f = m.IEC62304SafetyFilter()
        ctx = _make_context(
            m,
            iec62304_safety_class=m.IEC62304SafetyClass.CLASS_B,
            lifecycle_documentation_complete=False,
            formal_verification_complete=False,
        )
        result = f.evaluate(ctx)
        assert result.is_denied
        # Class B: only lifecycle docs are required; FV not required
        # So only one violation expected
        assert len(result.violations) >= 1


# ---------------------------------------------------------------------------
# TestISO14971RiskFilter
# ---------------------------------------------------------------------------


class TestISO14971RiskFilter:
    def test_unacceptable_risk_denied(self, m):
        f = m.ISO14971RiskFilter()
        ctx = _make_context(m, iso14971_residual_risk=m.ISO14971RiskLevel.UNACCEPTABLE)
        result = f.evaluate(ctx)
        assert result.is_denied
        assert any("14971" in v for v in result.violations)

    def test_acceptable_risk_approved(self, m):
        f = m.ISO14971RiskFilter()
        ctx = _make_context(m, iso14971_residual_risk=m.ISO14971RiskLevel.ACCEPTABLE)
        result = f.evaluate(ctx)
        assert not result.is_denied
        assert result.decision == m.DeploymentDecision.APPROVED

    def test_alarp_approved_with_conditions(self, m):
        f = m.ISO14971RiskFilter()
        ctx = _make_context(m, iso14971_residual_risk=m.ISO14971RiskLevel.ALARP)
        result = f.evaluate(ctx)
        assert not result.is_denied
        assert result.decision == m.DeploymentDecision.APPROVED_WITH_CONDITIONS
        assert any("ALARP" in c for c in result.conditions)

    def test_incomplete_risk_file_denied(self, m):
        f = m.ISO14971RiskFilter()
        ctx = _make_context(
            m, iso14971_residual_risk=m.ISO14971RiskLevel.ACCEPTABLE, risk_management_file_complete=False
        )
        result = f.evaluate(ctx)
        assert result.is_denied

    def test_unacceptable_risk_has_specific_violation(self, m):
        f = m.ISO14971RiskFilter()
        ctx = _make_context(m, iso14971_residual_risk=m.ISO14971RiskLevel.UNACCEPTABLE)
        result = f.evaluate(ctx)
        assert any("risk control" in v.lower() or "residual risk" in v.lower() for v in result.violations)

    def test_layer_name(self, m):
        f = m.ISO14971RiskFilter()
        ctx = _make_context(m)
        result = f.evaluate(ctx)
        assert result.layer == "ISO 14971"

    def test_alarp_notes_include_pms(self, m):
        f = m.ISO14971RiskFilter()
        ctx = _make_context(m, iso14971_residual_risk=m.ISO14971RiskLevel.ALARP)
        result = f.evaluate(ctx)
        assert any("surveillance" in n.lower() or "PMS" in n for n in result.notes)


# ---------------------------------------------------------------------------
# TestFDASaMDFilter
# ---------------------------------------------------------------------------


class TestFDASaMDFilter:
    def test_class_ii_not_cleared_denied(self, m):
        f = m.FDASaMDFilter()
        ctx = _make_context(
            m,
            fda_device_class=m.FDASaMDClass.CLASS_II,
            fda_clearance_pathway=m.FDAClearancePathway.NOT_CLEARED,
            intended_markets=("US",),
        )
        result = f.evaluate(ctx)
        assert result.is_denied
        assert any("510(k)" in v for v in result.violations)

    def test_class_ii_cleared_approved(self, m):
        f = m.FDASaMDFilter()
        ctx = _make_context(
            m,
            fda_device_class=m.FDASaMDClass.CLASS_II,
            fda_clearance_pathway=m.FDAClearancePathway.K510_CLEARED,
            intended_markets=("US",),
        )
        result = f.evaluate(ctx)
        assert not result.is_denied

    def test_class_iii_requires_pma(self, m):
        f = m.FDASaMDFilter()
        ctx = _make_context(
            m,
            fda_device_class=m.FDASaMDClass.CLASS_III,
            fda_clearance_pathway=m.FDAClearancePathway.K510_CLEARED,
            intended_markets=("US",),
        )
        result = f.evaluate(ctx)
        assert result.is_denied
        assert any("PMA" in v for v in result.violations)

    def test_class_iii_pma_approved_approved(self, m):
        f = m.FDASaMDFilter()
        ctx = _make_context(
            m,
            fda_device_class=m.FDASaMDClass.CLASS_III,
            fda_clearance_pathway=m.FDAClearancePathway.PMA_APPROVED,
            intended_markets=("US",),
        )
        result = f.evaluate(ctx)
        assert not result.is_denied

    def test_class_i_exempt(self, m):
        f = m.FDASaMDFilter()
        ctx = _make_context(
            m,
            fda_device_class=m.FDASaMDClass.CLASS_I,
            fda_clearance_pathway=m.FDAClearancePathway.EXEMPT,
            intended_markets=("US",),
        )
        result = f.evaluate(ctx)
        assert not result.is_denied
        assert result.decision == m.DeploymentDecision.APPROVED_WITH_CONDITIONS

    def test_intended_use_change_requires_new_clearance(self, m):
        f = m.FDASaMDFilter()
        ctx = _make_context(
            m,
            fda_device_class=m.FDASaMDClass.CLASS_II,
            fda_clearance_pathway=m.FDAClearancePathway.K510_CLEARED,
            change_type=m.SaMDChangeType.INTENDED_USE_CHANGE,
            intended_markets=("US",),
        )
        result = f.evaluate(ctx)
        assert result.is_denied
        assert any("INTENDED_USE_CHANGE" in v for v in result.violations)

    def test_non_us_market_skips_fda(self, m):
        f = m.FDASaMDFilter()
        ctx = _make_context(m, fda_clearance_pathway=m.FDAClearancePathway.NOT_CLEARED, intended_markets=("EU",))
        result = f.evaluate(ctx)
        assert not result.is_denied

    def test_missing_validation_study_denied_class_ii(self, m):
        f = m.FDASaMDFilter()
        ctx = _make_context(
            m,
            fda_device_class=m.FDASaMDClass.CLASS_II,
            fda_clearance_pathway=m.FDAClearancePathway.K510_CLEARED,
            clinical_validation_study_complete=False,
            intended_markets=("US",),
        )
        result = f.evaluate(ctx)
        assert result.is_denied

    def test_no_pccp_adds_condition(self, m):
        f = m.FDASaMDFilter()
        ctx = _make_context(
            m,
            fda_device_class=m.FDASaMDClass.CLASS_II,
            fda_clearance_pathway=m.FDAClearancePathway.K510_CLEARED,
            has_pccp=False,
            intended_markets=("US",),
        )
        result = f.evaluate(ctx)
        assert not result.is_denied
        assert any("PCCP" in c for c in result.conditions)


# ---------------------------------------------------------------------------
# TestMDCGEUFilter
# ---------------------------------------------------------------------------


class TestMDCGEUFilter:
    def test_class_i_self_certification(self, m):
        f = m.MDCGEUFilter()
        ctx = _make_context(m, eu_mdr_class=m.EUMDRClass.CLASS_I, intended_markets=("EU",))
        result = f.evaluate(ctx)
        assert not result.is_denied
        assert result.decision == m.DeploymentDecision.APPROVED_WITH_CONDITIONS
        assert any("self-certification" in c.lower() or "Declaration" in c for c in result.conditions)

    def test_class_iia_without_nb_denied(self, m):
        f = m.MDCGEUFilter()
        ctx = _make_context(
            m, eu_mdr_class=m.EUMDRClass.CLASS_IIA, has_notified_body_certificate=False, intended_markets=("EU",)
        )
        result = f.evaluate(ctx)
        assert result.is_denied
        assert any("Notified Body" in v for v in result.violations)

    def test_class_iia_with_nb_approved(self, m):
        f = m.MDCGEUFilter()
        ctx = _make_context(
            m, eu_mdr_class=m.EUMDRClass.CLASS_IIA, has_notified_body_certificate=True, intended_markets=("EU",)
        )
        result = f.evaluate(ctx)
        assert not result.is_denied

    def test_class_iii_without_validation_denied(self, m):
        f = m.MDCGEUFilter()
        ctx = _make_context(
            m,
            eu_mdr_class=m.EUMDRClass.CLASS_III,
            has_notified_body_certificate=True,
            clinical_validation_study_complete=False,
            intended_markets=("EU",),
        )
        result = f.evaluate(ctx)
        assert result.is_denied

    def test_class_iii_notes_eu_ai_act(self, m):
        f = m.MDCGEUFilter()
        ctx = _make_context(
            m,
            eu_mdr_class=m.EUMDRClass.CLASS_III,
            has_notified_body_certificate=True,
            clinical_validation_study_complete=True,
            formal_verification_complete=True,
            intended_markets=("EU",),
        )
        result = f.evaluate(ctx)
        assert any("EU AI Act" in n for n in result.notes)

    def test_non_eu_market_skips_mdcg(self, m):
        f = m.MDCGEUFilter()
        ctx = _make_context(m, has_notified_body_certificate=False, intended_markets=("US",))
        result = f.evaluate(ctx)
        assert not result.is_denied

    def test_class_iib_adds_pms_condition(self, m):
        f = m.MDCGEUFilter()
        ctx = _make_context(
            m,
            eu_mdr_class=m.EUMDRClass.CLASS_IIB,
            has_notified_body_certificate=True,
            clinical_validation_study_complete=True,
            intended_markets=("EU",),
        )
        result = f.evaluate(ctx)
        assert not result.is_denied
        assert any("surveillance" in c.lower() or "PSUR" in c for c in result.conditions)


# ---------------------------------------------------------------------------
# TestMedicalDeviceAIOrchestrator
# ---------------------------------------------------------------------------


class TestMedicalDeviceAIOrchestrator:
    def test_fully_compliant_us_system_approved(self, m):
        orch = m.MedicalDeviceAIOrchestrator()
        ctx = _make_context(
            m,
            iec62304_safety_class=m.IEC62304SafetyClass.CLASS_B,
            fda_device_class=m.FDASaMDClass.CLASS_II,
            fda_clearance_pathway=m.FDAClearancePathway.K510_CLEARED,
            eu_mdr_class=m.EUMDRClass.CLASS_IIA,
            iso14971_residual_risk=m.ISO14971RiskLevel.ACCEPTABLE,
            has_notified_body_certificate=True,
            lifecycle_documentation_complete=True,
            formal_verification_complete=True,
            risk_management_file_complete=True,
            clinical_validation_study_complete=True,
            intended_markets=("US", "EU"),
        )
        result = orch.evaluate(ctx)
        assert not result.final_decision == m.DeploymentDecision.DENIED

    def test_unacceptable_residual_risk_denied(self, m):
        orch = m.MedicalDeviceAIOrchestrator()
        ctx = _make_context(m, iso14971_residual_risk=m.ISO14971RiskLevel.UNACCEPTABLE)
        result = orch.evaluate(ctx)
        assert result.final_decision == m.DeploymentDecision.DENIED
        assert len(result.all_violations) > 0

    def test_class_iii_no_pma_denied(self, m):
        orch = m.MedicalDeviceAIOrchestrator()
        ctx = _make_context(
            m,
            fda_device_class=m.FDASaMDClass.CLASS_III,
            fda_clearance_pathway=m.FDAClearancePathway.NOT_CLEARED,
            iec62304_safety_class=m.IEC62304SafetyClass.CLASS_C,
            formal_verification_complete=True,
            intended_markets=("US",),
        )
        result = orch.evaluate(ctx)
        assert result.final_decision == m.DeploymentDecision.DENIED

    def test_result_has_four_layer_results(self, m):
        orch = m.MedicalDeviceAIOrchestrator()
        ctx = _make_context(m)
        result = orch.evaluate(ctx)
        assert len(result.layer_results) == 4

    def test_layer_names_correct(self, m):
        orch = m.MedicalDeviceAIOrchestrator()
        ctx = _make_context(m)
        result = orch.evaluate(ctx)
        layer_names = {lr.layer for lr in result.layer_results}
        assert "IEC 62304" in layer_names
        assert "ISO 14971" in layer_names
        assert "FDA SaMD" in layer_names
        assert "EU MDR" in layer_names

    def test_summary_method_works(self, m):
        orch = m.MedicalDeviceAIOrchestrator()
        ctx = _make_context(m)
        result = orch.evaluate(ctx)
        summary = result.summary()
        assert ctx.system_name in summary
        assert "Final Decision" in summary

    def test_all_violations_aggregated_from_layers(self, m):
        orch = m.MedicalDeviceAIOrchestrator()
        ctx = _make_context(
            m,
            iso14971_residual_risk=m.ISO14971RiskLevel.UNACCEPTABLE,
            fda_device_class=m.FDASaMDClass.CLASS_III,
            fda_clearance_pathway=m.FDAClearancePathway.NOT_CLEARED,
            intended_markets=("US",),
        )
        result = orch.evaluate(ctx)
        # Both ISO 14971 and FDA layers have violations
        assert len(result.all_violations) >= 2


# ---------------------------------------------------------------------------
# TestScenarios (smoke tests)
# ---------------------------------------------------------------------------


class TestScenarios:
    def test_scenario_a_imaging_assistant(self, m):
        m.scenario_a_diagnostic_imaging_assistant()

    def test_scenario_b_admin_scheduler(self, m):
        m.scenario_b_administrative_scheduler()

    def test_scenario_c_autonomous_treatment(self, m):
        m.scenario_c_autonomous_treatment_recommendation()

    def test_scenario_d_monitoring_pending_study(self, m):
        m.scenario_d_monitoring_pending_study()
