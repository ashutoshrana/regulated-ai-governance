"""
Tests for 17_uk_ai_governance.py

Four-layer UK AI governance framework:
  1. UKGDPRAutomatedDecisionFilter — Article 22 ADM safeguards
  2. ICOAIAuditingFilter — bias testing, explainability, accuracy
  3. UKEqualityActFilter — disparate impact + reasonable adjustments + PSED
  4. DSITAISafetyPrinciplesFilter — Safety/Security/Accountability/Transparency/Contestability
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
    Path(__file__).parent.parent / "examples" / "17_uk_ai_governance.py"
)


def _load_module():
    module_name = "uk_ai_governance"
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
    """Fully compliant HIGH_RISK public sector context."""
    defaults = dict(
        system_id="UK-TEST-001",
        system_name="Test HR System",
        risk_tier=m.UKAIRiskTier.HIGH_RISK,
        deploying_sector="public_sector",
        is_solely_automated=True,
        decision_has_legal_effect=True,
        processes_sensitive_categories=False,
        lawful_basis_documented=True,
        explicit_consent_obtained=True,
        human_review_available=True,
        opt_out_mechanism_provided=True,
        bias_testing_completed=True,
        explainability_mechanism_in_place=True,
        accuracy_validated=True,
        disparate_impact_assessment_done=True,
        reasonable_adjustments_supported=True,
        public_sector_equality_duty=True,
        equality_impact_documented=True,
        safety_testing_completed=True,
        adversarial_testing_done=True,
        responsible_officer_designated=True,
        stakeholder_disclosure_made=True,
        contestability_mechanism_provided=True,
    )
    defaults.update(kwargs)
    return m.UKAIContext(**defaults)


def _non_auto_ctx(m, **kwargs):
    """LOW_RISK, non-solely-automated context."""
    defaults = dict(
        system_id="UK-LOW-001",
        system_name="Spam Filter",
        risk_tier=m.UKAIRiskTier.LOW_RISK,
        deploying_sector="retail",
        is_solely_automated=False,
        decision_has_legal_effect=False,
        processes_sensitive_categories=False,
        lawful_basis_documented=True,
        explicit_consent_obtained=False,
        human_review_available=True,
        opt_out_mechanism_provided=True,
        bias_testing_completed=True,
        explainability_mechanism_in_place=True,
        accuracy_validated=True,
        disparate_impact_assessment_done=True,
        reasonable_adjustments_supported=True,
        public_sector_equality_duty=False,
        equality_impact_documented=False,
        safety_testing_completed=True,
        adversarial_testing_done=True,
        responsible_officer_designated=True,
        stakeholder_disclosure_made=True,
        contestability_mechanism_provided=True,
    )
    defaults.update(kwargs)
    return m.UKAIContext(**defaults)


# ---------------------------------------------------------------------------
# Layer 1 — UKGDPRAutomatedDecisionFilter
# ---------------------------------------------------------------------------


class TestUKGDPRAutomatedDecisionFilter:

    def test_not_solely_automated_approved_with_conditions(self, m):
        f = m.UKGDPRAutomatedDecisionFilter()
        ctx = _ctx(m, is_solely_automated=False)
        result = f.evaluate(ctx)
        assert result.has_conditions

    def test_solely_automated_non_legal_effect_approved_with_conditions(self, m):
        f = m.UKGDPRAutomatedDecisionFilter()
        ctx = _ctx(m, is_solely_automated=True, decision_has_legal_effect=False)
        result = f.evaluate(ctx)
        assert result.has_conditions

    def test_solely_automated_legal_effect_compliant_approved_with_conditions(self, m):
        f = m.UKGDPRAutomatedDecisionFilter()
        ctx = _ctx(m)  # fully compliant
        result = f.evaluate(ctx)
        assert not result.is_denied

    def test_no_lawful_basis_denied(self, m):
        f = m.UKGDPRAutomatedDecisionFilter()
        ctx = _ctx(m, lawful_basis_documented=False)
        result = f.evaluate(ctx)
        assert result.is_denied
        assert any("Article 22" in finding for finding in result.findings)

    def test_no_human_review_denied(self, m):
        f = m.UKGDPRAutomatedDecisionFilter()
        ctx = _ctx(m, human_review_available=False)
        result = f.evaluate(ctx)
        assert result.is_denied
        assert any("Article 22" in finding for finding in result.findings)

    def test_no_opt_out_denied(self, m):
        f = m.UKGDPRAutomatedDecisionFilter()
        ctx = _ctx(m, opt_out_mechanism_provided=False)
        result = f.evaluate(ctx)
        assert result.is_denied

    def test_sensitive_categories_no_explicit_consent_denied(self, m):
        f = m.UKGDPRAutomatedDecisionFilter()
        ctx = _ctx(m, processes_sensitive_categories=True, explicit_consent_obtained=False)
        result = f.evaluate(ctx)
        assert result.is_denied
        assert any("special category" in finding.lower() or "Article 22(4)" in finding
                   for finding in result.findings)


# ---------------------------------------------------------------------------
# Layer 2 — ICOAIAuditingFilter
# ---------------------------------------------------------------------------


class TestICOAIAuditingFilter:

    def test_all_compliant_approved_with_conditions(self, m):
        f = m.ICOAIAuditingFilter()
        ctx = _ctx(m)
        result = f.evaluate(ctx)
        assert result.has_conditions

    def test_no_bias_testing_denied(self, m):
        f = m.ICOAIAuditingFilter()
        ctx = _ctx(m, bias_testing_completed=False)
        result = f.evaluate(ctx)
        assert result.is_denied
        assert any("bias" in finding.lower() for finding in result.findings)

    def test_no_explainability_denied(self, m):
        f = m.ICOAIAuditingFilter()
        ctx = _ctx(m, explainability_mechanism_in_place=False)
        result = f.evaluate(ctx)
        assert result.is_denied
        assert any("explainab" in finding.lower() or "Article 13" in finding
                   for finding in result.findings)

    def test_no_accuracy_validation_denied(self, m):
        f = m.ICOAIAuditingFilter()
        ctx = _ctx(m, accuracy_validated=False)
        result = f.evaluate(ctx)
        assert result.is_denied
        assert any("accuracy" in finding.lower() for finding in result.findings)

    def test_conditions_reference_annual_reaudit(self, m):
        f = m.ICOAIAuditingFilter()
        ctx = _ctx(m)
        result = f.evaluate(ctx)
        assert any("re-audit" in c or "annual" in c.lower() for c in result.conditions)


# ---------------------------------------------------------------------------
# Layer 3 — UKEqualityActFilter
# ---------------------------------------------------------------------------


class TestUKEqualityActFilter:

    def test_all_compliant_approved_with_conditions(self, m):
        f = m.UKEqualityActFilter()
        ctx = _ctx(m)
        result = f.evaluate(ctx)
        assert result.has_conditions

    def test_no_disparate_impact_assessment_denied(self, m):
        f = m.UKEqualityActFilter()
        ctx = _ctx(m, disparate_impact_assessment_done=False)
        result = f.evaluate(ctx)
        assert result.is_denied
        assert any("s.19" in finding or "disparate" in finding.lower()
                   for finding in result.findings)

    def test_no_reasonable_adjustments_denied(self, m):
        f = m.UKEqualityActFilter()
        ctx = _ctx(m, reasonable_adjustments_supported=False)
        result = f.evaluate(ctx)
        assert result.is_denied
        assert any("s.20" in finding or "adjustment" in finding.lower()
                   for finding in result.findings)

    def test_public_sector_no_eia_denied(self, m):
        f = m.UKEqualityActFilter()
        ctx = _ctx(m, public_sector_equality_duty=True, equality_impact_documented=False)
        result = f.evaluate(ctx)
        assert result.is_denied
        assert any("s.149" in finding or "PSED" in finding or "equality impact" in finding.lower()
                   for finding in result.findings)

    def test_non_public_sector_no_eia_still_passes(self, m):
        f = m.UKEqualityActFilter()
        ctx = _ctx(m, public_sector_equality_duty=False, equality_impact_documented=False)
        result = f.evaluate(ctx)
        assert not result.is_denied

    def test_conditions_reference_protected_characteristics(self, m):
        f = m.UKEqualityActFilter()
        ctx = _ctx(m)
        result = f.evaluate(ctx)
        assert result.has_conditions
        all_text = " ".join(result.conditions)
        assert "s.19" in all_text or "protected" in all_text.lower() or "disparate" in all_text.lower()


# ---------------------------------------------------------------------------
# Layer 4 — DSITAISafetyPrinciplesFilter
# ---------------------------------------------------------------------------


class TestDSITAISafetyPrinciplesFilter:

    def test_all_compliant_approved_with_conditions(self, m):
        f = m.DSITAISafetyPrinciplesFilter()
        ctx = _ctx(m)
        result = f.evaluate(ctx)
        assert result.has_conditions

    def test_no_safety_testing_denied(self, m):
        f = m.DSITAISafetyPrinciplesFilter()
        ctx = _ctx(m, safety_testing_completed=False)
        result = f.evaluate(ctx)
        assert result.is_denied
        assert any("safety" in finding.lower() or "Safety" in finding
                   for finding in result.findings)

    def test_no_adversarial_testing_denied(self, m):
        f = m.DSITAISafetyPrinciplesFilter()
        ctx = _ctx(m, adversarial_testing_done=False)
        result = f.evaluate(ctx)
        assert result.is_denied
        assert any("security" in finding.lower() or "adversarial" in finding.lower()
                   for finding in result.findings)

    def test_no_responsible_officer_denied(self, m):
        f = m.DSITAISafetyPrinciplesFilter()
        ctx = _ctx(m, responsible_officer_designated=False)
        result = f.evaluate(ctx)
        assert result.is_denied
        assert any("accountability" in finding.lower() or "responsible officer" in finding.lower()
                   for finding in result.findings)

    def test_no_stakeholder_disclosure_denied(self, m):
        f = m.DSITAISafetyPrinciplesFilter()
        ctx = _ctx(m, stakeholder_disclosure_made=False)
        result = f.evaluate(ctx)
        assert result.is_denied
        assert any("transparency" in finding.lower() or "disclosure" in finding.lower()
                   for finding in result.findings)

    def test_no_contestability_denied(self, m):
        f = m.DSITAISafetyPrinciplesFilter()
        ctx = _ctx(m, contestability_mechanism_provided=False)
        result = f.evaluate(ctx)
        assert result.is_denied
        assert any("contestab" in finding.lower() or "challenge" in finding.lower()
                   for finding in result.findings)

    def test_conditions_reference_dsit_principles(self, m):
        f = m.DSITAISafetyPrinciplesFilter()
        ctx = _ctx(m)
        result = f.evaluate(ctx)
        assert result.has_conditions
        all_text = " ".join(result.conditions)
        assert "DSIT" in all_text or "White Paper" in all_text or "principle" in all_text.lower()


# ---------------------------------------------------------------------------
# UKAIGovernanceOrchestrator
# ---------------------------------------------------------------------------


class TestUKAIGovernanceOrchestrator:

    def test_fully_compliant_approved_with_conditions(self, m):
        orch = m.UKAIGovernanceOrchestrator()
        ctx = _ctx(m)
        report = orch.evaluate(ctx)
        assert report.final_decision == m.UKAIDecision.APPROVED_WITH_CONDITIONS

    def test_automated_loan_no_human_review_denied(self, m):
        orch = m.UKAIGovernanceOrchestrator()
        ctx = _ctx(m, human_review_available=False)
        report = orch.evaluate(ctx)
        assert report.final_decision == m.UKAIDecision.DENIED

    def test_all_four_layers_evaluated(self, m):
        orch = m.UKAIGovernanceOrchestrator()
        ctx = _ctx(m)
        report = orch.evaluate(ctx)
        layer_names = {lr.layer for lr in report.layer_results}
        assert "UK_GDPR_AUTOMATED_DECISION" in layer_names
        assert "ICO_AI_AUDITING" in layer_names
        assert "UK_EQUALITY_ACT" in layer_names
        assert "DSIT_AI_SAFETY_PRINCIPLES" in layer_names

    def test_layer_order(self, m):
        orch = m.UKAIGovernanceOrchestrator()
        ctx = _ctx(m)
        report = orch.evaluate(ctx)
        order = [lr.layer for lr in report.layer_results]
        assert order == [
            "UK_GDPR_AUTOMATED_DECISION",
            "ICO_AI_AUDITING",
            "UK_EQUALITY_ACT",
            "DSIT_AI_SAFETY_PRINCIPLES",
        ]

    def test_report_summary_structure(self, m):
        orch = m.UKAIGovernanceOrchestrator()
        ctx = _ctx(m)
        report = orch.evaluate(ctx)
        s = report.summary()
        assert s["system_id"] == ctx.system_id
        assert s["system_name"] == ctx.system_name
        assert "final_decision" in s
        assert len(s["layers"]) == 4

    def test_is_denied_property(self, m):
        result = m.UKAIGovernanceResult(layer="TEST")
        result.decision = m.UKAIDecision.DENIED
        assert result.is_denied
        result.decision = m.UKAIDecision.APPROVED
        assert not result.is_denied

    def test_has_conditions_property(self, m):
        result = m.UKAIGovernanceResult(layer="TEST")
        result.decision = m.UKAIDecision.APPROVED_WITH_CONDITIONS
        assert result.has_conditions
        result.decision = m.UKAIDecision.APPROVED
        assert not result.has_conditions
