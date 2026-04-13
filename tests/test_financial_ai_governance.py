"""Tests for 13_financial_ai_governance.py — FRB SR 11-7 + Basel III/IV + EU DORA + OCC 2011-12"""
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
    spec = importlib.util.spec_from_file_location(name, examples_dir / "13_financial_ai_governance.py")
    mod = types.ModuleType(name)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def m():
    return _load_module("financial_ai_governance")


# ---------------------------------------------------------------------------
# Test helpers
# ---------------------------------------------------------------------------


def _ctx(m, **kwargs):
    """Build a FinancialModelContext with sensible defaults (all passes)."""
    defaults = dict(
        model_id="MDL-TEST-001",
        model_name="Test Model",
        tier=m.ModelTier.TIER_2,
        is_validated_independently=True,
        validation_findings_resolved=True,
        ongoing_monitoring_active=True,
        last_performance_review_days_ago=100,
        model_approval_status=m.ModelApprovalStatus.NOT_REQUIRED,
        is_capital_model=False,
        bcbs239_lineage_verified=True,
        frtb_backtesting_passed=True,
        dora_classification=m.DORAClassification.NON_CRITICAL,
        dora_resilience_documented=True,
        dora_incident_reporting_active=True,
        is_third_party=False,
        third_party_risk_level=m.ThirdPartyRiskLevel.LOW,
        third_party_due_diligence_complete=True,
        third_party_contract_has_audit_rights=True,
        intended_jurisdiction=("US",),
        model_inventory_registered=True,
    )
    defaults.update(kwargs)
    return m.FinancialModelContext(**defaults)


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------


class TestEnumerations:
    def test_model_tiers(self, m):
        assert m.ModelTier.TIER_1.value == "TIER_1"
        assert m.ModelTier.TIER_2.value == "TIER_2"
        assert m.ModelTier.TIER_3.value == "TIER_3"

    def test_dora_classifications(self, m):
        types_ = [m.DORAClassification.CRITICAL_ICT, m.DORAClassification.IMPORTANT_ICT,
                  m.DORAClassification.NON_CRITICAL]
        assert len(set(types_)) == 3

    def test_third_party_risk_levels(self, m):
        levels = [m.ThirdPartyRiskLevel.CRITICAL, m.ThirdPartyRiskLevel.HIGH,
                  m.ThirdPartyRiskLevel.MODERATE, m.ThirdPartyRiskLevel.LOW]
        assert len(set(levels)) == 4

    def test_governance_decisions(self, m):
        decisions = [m.FinancialGovernanceDecision.APPROVED,
                     m.FinancialGovernanceDecision.APPROVED_WITH_CONDITIONS,
                     m.FinancialGovernanceDecision.DENIED]
        assert len(set(decisions)) == 3


# ---------------------------------------------------------------------------
# SR117Filter — Layer 1
# ---------------------------------------------------------------------------


class TestSR117Filter:
    def test_tier1_fully_compliant_approved(self, m):
        f = m.SR117Filter()
        ctx = _ctx(m, tier=m.ModelTier.TIER_1,
                   is_validated_independently=True,
                   validation_findings_resolved=True,
                   ongoing_monitoring_active=True,
                   last_performance_review_days_ago=180)
        result = f.evaluate(ctx)
        assert not result.is_denied

    def test_tier1_no_independent_validation_denied(self, m):
        f = m.SR117Filter()
        ctx = _ctx(m, tier=m.ModelTier.TIER_1,
                   is_validated_independently=False)
        result = f.evaluate(ctx)
        assert result.is_denied
        assert any("independent" in v.lower() or "SR 11-7" in v for v in result.violations)

    def test_tier1_unresolved_findings_denied(self, m):
        f = m.SR117Filter()
        ctx = _ctx(m, tier=m.ModelTier.TIER_1,
                   is_validated_independently=True,
                   validation_findings_resolved=False)
        result = f.evaluate(ctx)
        assert result.is_denied
        assert any("findings" in v.lower() for v in result.violations)

    def test_tier1_no_ongoing_monitoring_denied(self, m):
        f = m.SR117Filter()
        ctx = _ctx(m, tier=m.ModelTier.TIER_1,
                   is_validated_independently=True,
                   validation_findings_resolved=True,
                   ongoing_monitoring_active=False)
        result = f.evaluate(ctx)
        assert result.is_denied
        assert any("monitoring" in v.lower() for v in result.violations)

    def test_tier1_review_overdue_denied(self, m):
        f = m.SR117Filter()
        ctx = _ctx(m, tier=m.ModelTier.TIER_1,
                   last_performance_review_days_ago=400)  # Over 365 limit
        result = f.evaluate(ctx)
        assert result.is_denied
        assert any("365" in v for v in result.violations)

    def test_tier2_no_independent_validation_denied(self, m):
        f = m.SR117Filter()
        ctx = _ctx(m, tier=m.ModelTier.TIER_2,
                   is_validated_independently=False)
        result = f.evaluate(ctx)
        assert result.is_denied

    def test_tier2_review_overdue_denied(self, m):
        f = m.SR117Filter()
        ctx = _ctx(m, tier=m.ModelTier.TIER_2,
                   last_performance_review_days_ago=800)  # Over 730 limit
        result = f.evaluate(ctx)
        assert result.is_denied

    def test_tier3_no_validation_not_denied(self, m):
        """Tier 3 does not require independent validation."""
        f = m.SR117Filter()
        ctx = _ctx(m, tier=m.ModelTier.TIER_3,
                   is_validated_independently=False,
                   ongoing_monitoring_active=False,
                   last_performance_review_days_ago=300)
        result = f.evaluate(ctx)
        assert not result.is_denied

    def test_tier3_review_overdue_denied(self, m):
        """Tier 3 still has a 1095-day review limit."""
        f = m.SR117Filter()
        ctx = _ctx(m, tier=m.ModelTier.TIER_3,
                   last_performance_review_days_ago=1200)  # Over 1095
        result = f.evaluate(ctx)
        assert result.is_denied

    def test_not_in_model_inventory_denied(self, m):
        f = m.SR117Filter()
        ctx = _ctx(m, model_inventory_registered=False)
        result = f.evaluate(ctx)
        assert result.is_denied
        assert any("inventory" in v.lower() for v in result.violations)

    def test_tier3_note_present(self, m):
        f = m.SR117Filter()
        ctx = _ctx(m, tier=m.ModelTier.TIER_3)
        result = f.evaluate(ctx)
        assert any("Tier 3" in n for n in result.notes)

    def test_tier1_approved_has_condition(self, m):
        f = m.SR117Filter()
        ctx = _ctx(m, tier=m.ModelTier.TIER_1,
                   is_validated_independently=True,
                   validation_findings_resolved=True,
                   ongoing_monitoring_active=True,
                   last_performance_review_days_ago=90)
        result = f.evaluate(ctx)
        assert not result.is_denied
        assert len(result.conditions) > 0

    def test_max_review_age_values(self, m):
        f = m.SR117Filter()
        assert f._MAX_REVIEW_AGE[m.ModelTier.TIER_1] == 365
        assert f._MAX_REVIEW_AGE[m.ModelTier.TIER_2] == 730
        assert f._MAX_REVIEW_AGE[m.ModelTier.TIER_3] == 1095

    def test_is_denied_property(self, m):
        result = m.FinancialFilterResult(
            layer="SR 11-7",
            decision=m.FinancialGovernanceDecision.DENIED,
            violations=["test violation"],
        )
        assert result.is_denied

    def test_is_not_denied_when_approved(self, m):
        result = m.FinancialFilterResult(
            layer="SR 11-7",
            decision=m.FinancialGovernanceDecision.APPROVED,
        )
        assert not result.is_denied


# ---------------------------------------------------------------------------
# Basel3Filter — Layer 2
# ---------------------------------------------------------------------------


class TestBasel3Filter:
    def test_non_capital_model_passes_through(self, m):
        f = m.Basel3Filter()
        ctx = _ctx(m, is_capital_model=False)
        result = f.evaluate(ctx)
        assert not result.is_denied
        assert result.decision == m.FinancialGovernanceDecision.APPROVED
        assert any("not a capital model" in n.lower() for n in result.notes)

    def test_capital_model_needs_regulatory_approval(self, m):
        f = m.Basel3Filter()
        ctx = _ctx(m, is_capital_model=True,
                   model_approval_status=m.ModelApprovalStatus.PENDING_REVIEW,
                   bcbs239_lineage_verified=True,
                   frtb_backtesting_passed=True,
                   tier=m.ModelTier.TIER_2)
        result = f.evaluate(ctx)
        assert result.is_denied
        assert any("regulatory" in v.lower() or "approval" in v.lower() for v in result.violations)

    def test_capital_model_rejected_status_denied(self, m):
        f = m.Basel3Filter()
        ctx = _ctx(m, is_capital_model=True,
                   model_approval_status=m.ModelApprovalStatus.REJECTED,
                   bcbs239_lineage_verified=True,
                   frtb_backtesting_passed=True,
                   tier=m.ModelTier.TIER_2)
        result = f.evaluate(ctx)
        assert result.is_denied

    def test_capital_model_missing_bcbs239_lineage_denied(self, m):
        f = m.Basel3Filter()
        ctx = _ctx(m, is_capital_model=True,
                   model_approval_status=m.ModelApprovalStatus.APPROVED,
                   bcbs239_lineage_verified=False,
                   frtb_backtesting_passed=True,
                   tier=m.ModelTier.TIER_2)
        result = f.evaluate(ctx)
        assert result.is_denied
        assert any("BCBS 239" in v for v in result.violations)

    def test_tier1_capital_model_frtb_backtesting_required(self, m):
        f = m.Basel3Filter()
        ctx = _ctx(m, is_capital_model=True,
                   tier=m.ModelTier.TIER_1,
                   model_approval_status=m.ModelApprovalStatus.APPROVED,
                   bcbs239_lineage_verified=True,
                   frtb_backtesting_passed=False)
        result = f.evaluate(ctx)
        assert result.is_denied
        assert any("FRTB" in v for v in result.violations)

    def test_tier1_capital_fully_compliant_approved(self, m):
        f = m.Basel3Filter()
        ctx = _ctx(m, is_capital_model=True,
                   tier=m.ModelTier.TIER_1,
                   model_approval_status=m.ModelApprovalStatus.APPROVED,
                   bcbs239_lineage_verified=True,
                   frtb_backtesting_passed=True)
        result = f.evaluate(ctx)
        assert not result.is_denied

    def test_conditional_approval_generates_condition(self, m):
        f = m.Basel3Filter()
        ctx = _ctx(m, is_capital_model=True,
                   tier=m.ModelTier.TIER_2,
                   model_approval_status=m.ModelApprovalStatus.CONDITIONAL_APPROVAL,
                   bcbs239_lineage_verified=True,
                   frtb_backtesting_passed=True)
        result = f.evaluate(ctx)
        assert not result.is_denied
        assert any("conditional" in c.lower() for c in result.conditions)


# ---------------------------------------------------------------------------
# DORAFilter — Layer 3
# ---------------------------------------------------------------------------


class TestDORAFilter:
    def test_non_eu_jurisdiction_passes_through(self, m):
        f = m.DORAFilter()
        ctx = _ctx(m, intended_jurisdiction=("US",))
        result = f.evaluate(ctx)
        assert not result.is_denied
        assert any("EU not in" in n or "DORA not applicable" in n for n in result.notes)

    def test_uk_only_jurisdiction_passes_through(self, m):
        f = m.DORAFilter()
        ctx = _ctx(m, intended_jurisdiction=("UK",))
        result = f.evaluate(ctx)
        assert not result.is_denied

    def test_eu_jurisdiction_non_critical_approved(self, m):
        f = m.DORAFilter()
        ctx = _ctx(m, intended_jurisdiction=("EU",),
                   dora_classification=m.DORAClassification.NON_CRITICAL)
        result = f.evaluate(ctx)
        assert not result.is_denied

    def test_eu_important_ict_no_resilience_docs_denied(self, m):
        f = m.DORAFilter()
        ctx = _ctx(m, intended_jurisdiction=("EU",),
                   dora_classification=m.DORAClassification.IMPORTANT_ICT,
                   dora_resilience_documented=False,
                   dora_incident_reporting_active=True)
        result = f.evaluate(ctx)
        assert result.is_denied
        assert any("Art. 11" in v or "resilience" in v.lower() for v in result.violations)

    def test_eu_important_ict_no_incident_reporting_denied(self, m):
        f = m.DORAFilter()
        ctx = _ctx(m, intended_jurisdiction=("EU",),
                   dora_classification=m.DORAClassification.IMPORTANT_ICT,
                   dora_resilience_documented=True,
                   dora_incident_reporting_active=False)
        result = f.evaluate(ctx)
        assert result.is_denied
        assert any("Art. 19" in v or "incident" in v.lower() for v in result.violations)

    def test_eu_critical_ict_fully_compliant_approved_with_condition(self, m):
        f = m.DORAFilter()
        ctx = _ctx(m, intended_jurisdiction=("EU",),
                   dora_classification=m.DORAClassification.CRITICAL_ICT,
                   dora_resilience_documented=True,
                   dora_incident_reporting_active=True,
                   is_third_party=False)
        result = f.evaluate(ctx)
        assert not result.is_denied
        # CRITICAL ICT requires TLPT condition
        assert any("TLPT" in c or "Art. 26" in c for c in result.conditions)

    def test_eu_critical_ict_third_party_no_audit_rights_denied(self, m):
        f = m.DORAFilter()
        ctx = _ctx(m, intended_jurisdiction=("EU",),
                   dora_classification=m.DORAClassification.CRITICAL_ICT,
                   dora_resilience_documented=True,
                   dora_incident_reporting_active=True,
                   is_third_party=True,
                   third_party_contract_has_audit_rights=False)
        result = f.evaluate(ctx)
        assert result.is_denied
        assert any("Art. 28" in v for v in result.violations)

    def test_eu_critical_ict_third_party_with_audit_rights_approved(self, m):
        f = m.DORAFilter()
        ctx = _ctx(m, intended_jurisdiction=("EU",),
                   dora_classification=m.DORAClassification.CRITICAL_ICT,
                   dora_resilience_documented=True,
                   dora_incident_reporting_active=True,
                   is_third_party=True,
                   third_party_contract_has_audit_rights=True)
        result = f.evaluate(ctx)
        assert not result.is_denied


# ---------------------------------------------------------------------------
# OCC2011Filter — Layer 4
# ---------------------------------------------------------------------------


class TestOCC2011Filter:
    def test_internal_model_passes_through(self, m):
        f = m.OCC2011Filter()
        ctx = _ctx(m, is_third_party=False)
        result = f.evaluate(ctx)
        assert not result.is_denied
        assert any("internally developed" in n.lower() for n in result.notes)

    def test_critical_third_party_no_due_diligence_denied(self, m):
        f = m.OCC2011Filter()
        ctx = _ctx(m, is_third_party=True,
                   third_party_risk_level=m.ThirdPartyRiskLevel.CRITICAL,
                   third_party_due_diligence_complete=False,
                   third_party_contract_has_audit_rights=True)
        result = f.evaluate(ctx)
        assert result.is_denied
        assert any("due diligence" in v.lower() for v in result.violations)

    def test_critical_third_party_no_audit_rights_denied(self, m):
        f = m.OCC2011Filter()
        ctx = _ctx(m, is_third_party=True,
                   third_party_risk_level=m.ThirdPartyRiskLevel.CRITICAL,
                   third_party_due_diligence_complete=True,
                   third_party_contract_has_audit_rights=False)
        result = f.evaluate(ctx)
        assert result.is_denied
        assert any("audit" in v.lower() for v in result.violations)

    def test_high_third_party_no_audit_rights_denied(self, m):
        f = m.OCC2011Filter()
        ctx = _ctx(m, is_third_party=True,
                   third_party_risk_level=m.ThirdPartyRiskLevel.HIGH,
                   third_party_due_diligence_complete=True,
                   third_party_contract_has_audit_rights=False)
        result = f.evaluate(ctx)
        assert result.is_denied

    def test_moderate_third_party_needs_due_diligence(self, m):
        f = m.OCC2011Filter()
        ctx = _ctx(m, is_third_party=True,
                   third_party_risk_level=m.ThirdPartyRiskLevel.MODERATE,
                   third_party_due_diligence_complete=False)
        result = f.evaluate(ctx)
        assert result.is_denied

    def test_moderate_third_party_no_audit_rights_still_passes(self, m):
        """MODERATE risk doesn't require audit rights — only CRITICAL/HIGH."""
        f = m.OCC2011Filter()
        ctx = _ctx(m, is_third_party=True,
                   third_party_risk_level=m.ThirdPartyRiskLevel.MODERATE,
                   third_party_due_diligence_complete=True,
                   third_party_contract_has_audit_rights=False)
        result = f.evaluate(ctx)
        assert not result.is_denied

    def test_low_third_party_minimal_requirements(self, m):
        f = m.OCC2011Filter()
        ctx = _ctx(m, is_third_party=True,
                   third_party_risk_level=m.ThirdPartyRiskLevel.LOW,
                   third_party_due_diligence_complete=False,
                   third_party_contract_has_audit_rights=False)
        result = f.evaluate(ctx)
        assert not result.is_denied

    def test_critical_third_party_fully_compliant_has_condition(self, m):
        f = m.OCC2011Filter()
        ctx = _ctx(m, is_third_party=True,
                   third_party_risk_level=m.ThirdPartyRiskLevel.CRITICAL,
                   third_party_due_diligence_complete=True,
                   third_party_contract_has_audit_rights=True)
        result = f.evaluate(ctx)
        assert not result.is_denied
        assert any("annual" in c.lower() for c in result.conditions)

    def test_dd_required_levels(self, m):
        f = m.OCC2011Filter()
        assert m.ThirdPartyRiskLevel.CRITICAL in f._DD_REQUIRED_LEVELS
        assert m.ThirdPartyRiskLevel.HIGH in f._DD_REQUIRED_LEVELS
        assert m.ThirdPartyRiskLevel.MODERATE in f._DD_REQUIRED_LEVELS
        assert m.ThirdPartyRiskLevel.LOW not in f._DD_REQUIRED_LEVELS

    def test_audit_rights_required_levels(self, m):
        f = m.OCC2011Filter()
        assert m.ThirdPartyRiskLevel.CRITICAL in f._AUDIT_RIGHTS_REQUIRED_LEVELS
        assert m.ThirdPartyRiskLevel.HIGH in f._AUDIT_RIGHTS_REQUIRED_LEVELS
        assert m.ThirdPartyRiskLevel.MODERATE not in f._AUDIT_RIGHTS_REQUIRED_LEVELS


# ---------------------------------------------------------------------------
# FinancialModelGovernanceOrchestrator
# ---------------------------------------------------------------------------


class TestFinancialModelGovernanceOrchestrator:
    def test_scenario_a_tier1_irb_approved_with_conditions(self, m):
        """Tier 1 IRB model fully compliant — APPROVED_WITH_CONDITIONS (Tier 1 conditions)."""
        orch = m.FinancialModelGovernanceOrchestrator()
        ctx = _ctx(m,
                   model_id="MDL-IRB-001",
                   model_name="Credit IRB Model",
                   tier=m.ModelTier.TIER_1,
                   is_validated_independently=True,
                   validation_findings_resolved=True,
                   ongoing_monitoring_active=True,
                   last_performance_review_days_ago=180,
                   model_approval_status=m.ModelApprovalStatus.APPROVED,
                   is_capital_model=True,
                   bcbs239_lineage_verified=True,
                   frtb_backtesting_passed=True,
                   dora_classification=m.DORAClassification.IMPORTANT_ICT,
                   dora_resilience_documented=True,
                   dora_incident_reporting_active=True,
                   is_third_party=True,
                   third_party_risk_level=m.ThirdPartyRiskLevel.HIGH,
                   third_party_due_diligence_complete=True,
                   third_party_contract_has_audit_rights=True,
                   intended_jurisdiction=("US", "EU"))
        result = orch.evaluate(ctx)
        assert result.final_decision != m.FinancialGovernanceDecision.DENIED

    def test_scenario_b_tier1_unresolved_findings_denied(self, m):
        """Tier 1 with unresolved validation findings → DENIED."""
        orch = m.FinancialModelGovernanceOrchestrator()
        ctx = _ctx(m,
                   tier=m.ModelTier.TIER_1,
                   is_validated_independently=True,
                   validation_findings_resolved=False,
                   ongoing_monitoring_active=True,
                   last_performance_review_days_ago=90)
        result = orch.evaluate(ctx)
        assert result.final_decision == m.FinancialGovernanceDecision.DENIED
        assert len(result.all_violations) > 0

    def test_scenario_c_third_party_aml_dora_critical_denied(self, m):
        """Third-party AML with DORA Critical ICT, no resilience docs → DENIED."""
        orch = m.FinancialModelGovernanceOrchestrator()
        ctx = _ctx(m,
                   tier=m.ModelTier.TIER_1,
                   is_validated_independently=True,
                   validation_findings_resolved=True,
                   ongoing_monitoring_active=True,
                   last_performance_review_days_ago=45,
                   is_capital_model=False,
                   dora_classification=m.DORAClassification.CRITICAL_ICT,
                   dora_resilience_documented=False,
                   dora_incident_reporting_active=False,
                   is_third_party=True,
                   third_party_risk_level=m.ThirdPartyRiskLevel.CRITICAL,
                   third_party_due_diligence_complete=True,
                   third_party_contract_has_audit_rights=False,
                   intended_jurisdiction=("EU",))
        result = orch.evaluate(ctx)
        assert result.final_decision == m.FinancialGovernanceDecision.DENIED

    def test_scenario_d_tier3_internal_approved(self, m):
        """Tier 3 internal operational model with minimal requirements → APPROVED."""
        orch = m.FinancialModelGovernanceOrchestrator()
        ctx = _ctx(m,
                   tier=m.ModelTier.TIER_3,
                   is_validated_independently=False,
                   ongoing_monitoring_active=False,
                   last_performance_review_days_ago=300,
                   is_capital_model=False,
                   dora_classification=m.DORAClassification.NON_CRITICAL,
                   is_third_party=False,
                   intended_jurisdiction=("US",))
        result = orch.evaluate(ctx)
        assert result.final_decision == m.FinancialGovernanceDecision.APPROVED

    def test_any_denied_layer_causes_overall_denial(self, m):
        orch = m.FinancialModelGovernanceOrchestrator()
        ctx = _ctx(m, model_inventory_registered=False)  # SR 11-7 violation
        result = orch.evaluate(ctx)
        assert result.final_decision == m.FinancialGovernanceDecision.DENIED

    def test_four_layer_results_always_present(self, m):
        orch = m.FinancialModelGovernanceOrchestrator()
        ctx = _ctx(m)
        result = orch.evaluate(ctx)
        assert len(result.layer_results) == 4

    def test_violations_aggregated_from_all_layers(self, m):
        orch = m.FinancialModelGovernanceOrchestrator()
        # Create context that violates multiple layers
        ctx = _ctx(m,
                   tier=m.ModelTier.TIER_1,
                   is_validated_independently=False,  # SR 11-7 violation
                   intended_jurisdiction=("EU",),
                   dora_classification=m.DORAClassification.CRITICAL_ICT,
                   dora_resilience_documented=False,  # DORA violation
                   dora_incident_reporting_active=True)
        result = orch.evaluate(ctx)
        assert len(result.all_violations) >= 2

    def test_review_id_is_generated(self, m):
        orch = m.FinancialModelGovernanceOrchestrator()
        ctx = _ctx(m)
        result = orch.evaluate(ctx)
        assert result.review_id
        assert len(result.review_id) > 0

    def test_summary_method_returns_string(self, m):
        orch = m.FinancialModelGovernanceOrchestrator()
        ctx = _ctx(m)
        result = orch.evaluate(ctx)
        summary = result.summary()
        assert isinstance(summary, str)
        assert result.model_name in summary
        assert result.final_decision.value in summary

    def test_conditions_aggregated_from_layers(self, m):
        """Approved models may have conditions from multiple layers."""
        orch = m.FinancialModelGovernanceOrchestrator()
        ctx = _ctx(m,
                   tier=m.ModelTier.TIER_1,
                   is_validated_independently=True,
                   validation_findings_resolved=True,
                   ongoing_monitoring_active=True,
                   last_performance_review_days_ago=90,
                   is_capital_model=True,
                   model_approval_status=m.ModelApprovalStatus.CONDITIONAL_APPROVAL,
                   bcbs239_lineage_verified=True,
                   frtb_backtesting_passed=True,
                   intended_jurisdiction=("EU",),
                   dora_classification=m.DORAClassification.CRITICAL_ICT,
                   dora_resilience_documented=True,
                   dora_incident_reporting_active=True,
                   is_third_party=True,
                   third_party_risk_level=m.ThirdPartyRiskLevel.HIGH,
                   third_party_due_diligence_complete=True,
                   third_party_contract_has_audit_rights=True)
        result = orch.evaluate(ctx)
        assert len(result.all_conditions) > 0
