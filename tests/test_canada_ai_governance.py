"""
Tests for 18_canada_ai_governance.py — Four-layer Canadian AI governance framework.

Covers:
    - AIDAComplianceFilter        (Layer 1 — Bill C-27 AIDA)
    - CPPADataGovernanceFilter    (Layer 2 — Consumer Privacy Protection Act)
    - OPCGuidelinesFilter         (Layer 3 — OPC AI Guidelines 2023)
    - QuebecLaw25Filter           (Layer 4 — Québec Law 25)
    - CanadaAIGovernanceOrchestrator (four-layer orchestrator)
"""

from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path

import pytest

_MOD_PATH = Path(__file__).parent.parent / "examples" / "18_canada_ai_governance.py"


def _load_module():
    module_name = "canada_ai_governance_18"
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
    """Fully compliant Québec HIGH_IMPACT system."""
    defaults = dict(
        system_id="CA-TEST-001",
        system_name="Test AI System",
        risk_level=m.CanadianAIRiskLevel.HIGH_IMPACT,
        deploying_province="QC",
        is_high_impact_system=True,
        impact_assessment_completed=True,
        transparency_notice_provided=True,
        ministerial_order_compliant=True,
        meaningful_consent_obtained=True,
        purpose_limitation_documented=True,
        data_minimization_applied=True,
        cross_border_transfer_safeguards=True,
        human_oversight_available=True,
        accuracy_measures_in_place=True,
        accountability_framework_exists=True,
        privacy_impact_assessment_done=True,
        algorithmic_transparency_published=True,
        data_governance_officer_designated=True,
    )
    defaults.update(kwargs)
    return m.CanadaAIContext(**defaults)


def _non_qc_ctx(m, **kwargs):
    """Fully compliant Ontario LOW_IMPACT system."""
    defaults = dict(
        system_id="CA-ON-001",
        system_name="Ontario AI System",
        risk_level=m.CanadianAIRiskLevel.LOW_IMPACT,
        deploying_province="ON",
        is_high_impact_system=False,
        impact_assessment_completed=True,
        transparency_notice_provided=True,
        ministerial_order_compliant=True,
        meaningful_consent_obtained=True,
        purpose_limitation_documented=True,
        data_minimization_applied=True,
        cross_border_transfer_safeguards=True,
        human_oversight_available=True,
        accuracy_measures_in_place=True,
        accountability_framework_exists=True,
        privacy_impact_assessment_done=True,
        algorithmic_transparency_published=True,
        data_governance_officer_designated=True,
    )
    defaults.update(kwargs)
    return m.CanadaAIContext(**defaults)


# ---------------------------------------------------------------------------
# TestAIDAComplianceFilter
# ---------------------------------------------------------------------------


class TestAIDAComplianceFilter:
    """Layer 1 — Bill C-27 AIDA Compliance."""

    def test_fully_compliant_high_impact_approved_with_conditions(self, m):
        """Fully compliant HIGH_IMPACT system → APPROVED_WITH_CONDITIONS."""
        ctx = _ctx(m)
        result = m.AIDAComplianceFilter().evaluate(ctx)
        assert result.has_conditions, (
            f"Expected APPROVED_WITH_CONDITIONS for compliant HIGH_IMPACT; got decision={result.decision}"
        )

    def test_missing_impact_assessment_denied(self, m):
        """HIGH_IMPACT system with no impact assessment → DENIED; finding references s.6."""
        ctx = _ctx(m, impact_assessment_completed=False)
        result = m.AIDAComplianceFilter().evaluate(ctx)
        assert result.is_denied, "Expected DENIED when impact_assessment_completed=False"
        combined = " ".join(result.findings).lower()
        assert "s.6" in combined or "impact assessment" in combined, (
            f"Finding should reference s.6 or 'impact assessment'; findings={result.findings}"
        )

    def test_missing_transparency_notice_denied(self, m):
        """HIGH_IMPACT system with no transparency notice → DENIED; finding references s.9."""
        ctx = _ctx(m, transparency_notice_provided=False)
        result = m.AIDAComplianceFilter().evaluate(ctx)
        assert result.is_denied, "Expected DENIED when transparency_notice_provided=False"
        combined = " ".join(result.findings).lower()
        assert "s.9" in combined or "transparency" in combined, (
            f"Finding should reference s.9 or 'transparency'; findings={result.findings}"
        )

    def test_ministerial_order_non_compliant_denied(self, m):
        """HIGH_IMPACT system non-compliant with ministerial order → DENIED; finding references s.35."""
        ctx = _ctx(m, ministerial_order_compliant=False)
        result = m.AIDAComplianceFilter().evaluate(ctx)
        assert result.is_denied, "Expected DENIED when ministerial_order_compliant=False"
        combined = " ".join(result.findings).lower()
        assert "s.35" in combined or "ministerial" in combined, (
            f"Finding should reference s.35 or 'ministerial'; findings={result.findings}"
        )

    def test_exempt_system_approved_with_conditions(self, m):
        """EXEMPT system → APPROVED_WITH_CONDITIONS; condition references 'exempt' or 'AIDA'."""
        ctx = _ctx(
            m,
            risk_level=m.CanadianAIRiskLevel.EXEMPT,
            is_high_impact_system=False,
            impact_assessment_completed=False,
            transparency_notice_provided=False,
        )
        result = m.AIDAComplianceFilter().evaluate(ctx)
        assert result.has_conditions, f"Expected APPROVED_WITH_CONDITIONS for EXEMPT system; got {result.decision}"
        combined = " ".join(result.conditions).lower()
        assert "exempt" in combined or "aida" in combined, (
            f"Condition should reference 'exempt' or 'AIDA'; conditions={result.conditions}"
        )

    def test_low_impact_not_high_impact_approved_with_conditions(self, m):
        """LOW_IMPACT, is_high_impact_system=False → not DENIED."""
        ctx = _ctx(
            m,
            risk_level=m.CanadianAIRiskLevel.LOW_IMPACT,
            is_high_impact_system=False,
        )
        result = m.AIDAComplianceFilter().evaluate(ctx)
        assert not result.is_denied, f"Expected not DENIED for LOW_IMPACT non-high-impact system; got {result.decision}"

    def test_conditions_reference_aida(self, m):
        """Compliant HIGH_IMPACT system → conditions contain 'AIDA', 's.10', or 's.11'."""
        ctx = _ctx(m)
        result = m.AIDAComplianceFilter().evaluate(ctx)
        combined = " ".join(result.conditions)
        assert "AIDA" in combined or "s.10" in combined or "s.11" in combined, (
            f"Conditions should reference AIDA, s.10, or s.11; conditions={result.conditions}"
        )


# ---------------------------------------------------------------------------
# TestCPPADataGovernanceFilter
# ---------------------------------------------------------------------------


class TestCPPADataGovernanceFilter:
    """Layer 2 — CPPA Data Governance."""

    def test_all_compliant_approved_with_conditions(self, m):
        """All CPPA fields True → APPROVED_WITH_CONDITIONS."""
        ctx = _ctx(m)
        result = m.CPPADataGovernanceFilter().evaluate(ctx)
        assert result.has_conditions, (
            f"Expected APPROVED_WITH_CONDITIONS when all CPPA fields pass; got {result.decision}"
        )

    def test_no_consent_denied(self, m):
        """meaningful_consent_obtained=False → DENIED; finding references s.15 or 'consent'."""
        ctx = _ctx(m, meaningful_consent_obtained=False)
        result = m.CPPADataGovernanceFilter().evaluate(ctx)
        assert result.is_denied, "Expected DENIED when meaningful_consent_obtained=False"
        combined = " ".join(result.findings).lower()
        assert "s.15" in combined or "consent" in combined, (
            f"Finding should reference s.15 or 'consent'; findings={result.findings}"
        )

    def test_no_purpose_limitation_denied(self, m):
        """purpose_limitation_documented=False → DENIED; finding references s.12 or 'purpose'."""
        ctx = _ctx(m, purpose_limitation_documented=False)
        result = m.CPPADataGovernanceFilter().evaluate(ctx)
        assert result.is_denied, "Expected DENIED when purpose_limitation_documented=False"
        combined = " ".join(result.findings).lower()
        assert "s.12" in combined or "purpose" in combined, (
            f"Finding should reference s.12 or 'purpose'; findings={result.findings}"
        )

    def test_no_data_minimization_denied(self, m):
        """data_minimization_applied=False → DENIED; finding references s.13, 'minimization', or 'proportionality'."""
        ctx = _ctx(m, data_minimization_applied=False)
        result = m.CPPADataGovernanceFilter().evaluate(ctx)
        assert result.is_denied, "Expected DENIED when data_minimization_applied=False"
        combined = " ".join(result.findings).lower()
        assert (
            "s.13" in combined
            or "minimization" in combined
            or "minimisation" in combined
            or "proportionality" in combined
            or "necessary" in combined
        ), f"Finding should reference s.13, minimization, or proportionality; findings={result.findings}"

    def test_no_cross_border_safeguards_denied(self, m):
        """cross_border_transfer_safeguards=False → DENIED; finding references s.24 or 'cross-border'."""
        ctx = _ctx(m, cross_border_transfer_safeguards=False)
        result = m.CPPADataGovernanceFilter().evaluate(ctx)
        assert result.is_denied, "Expected DENIED when cross_border_transfer_safeguards=False"
        combined = " ".join(result.findings).lower()
        assert (
            "s.24" in combined or "cross-border" in combined or "cross border" in combined or "transfer" in combined
        ), f"Finding should reference s.24, cross-border, or transfer; findings={result.findings}"

    def test_conditions_reference_cppa_rights(self, m):
        """Compliant system → conditions contain 's.62', 's.63', 'portability', or 'withdraw'."""
        ctx = _ctx(m)
        result = m.CPPADataGovernanceFilter().evaluate(ctx)
        combined = " ".join(result.conditions)
        assert "s.62" in combined or "s.63" in combined or "portability" in combined or "withdraw" in combined, (
            f"Conditions should reference s.62, s.63, portability, or withdraw; conditions={result.conditions}"
        )

    def test_layer_name_correct(self, m):
        """Result layer name == 'CPPA_DATA_GOVERNANCE'."""
        ctx = _ctx(m)
        result = m.CPPADataGovernanceFilter().evaluate(ctx)
        assert result.layer == "CPPA_DATA_GOVERNANCE", f"Expected layer='CPPA_DATA_GOVERNANCE'; got '{result.layer}'"


# ---------------------------------------------------------------------------
# TestOPCGuidelinesFilter
# ---------------------------------------------------------------------------


class TestOPCGuidelinesFilter:
    """Layer 3 — OPC AI Guidelines 2023."""

    def test_all_compliant_approved_with_conditions(self, m):
        """All OPC fields True → APPROVED_WITH_CONDITIONS."""
        ctx = _ctx(m)
        result = m.OPCGuidelinesFilter().evaluate(ctx)
        assert result.has_conditions, (
            f"Expected APPROVED_WITH_CONDITIONS when all OPC fields pass; got {result.decision}"
        )

    def test_no_human_oversight_denied(self, m):
        """human_oversight_available=False → DENIED; finding references Guideline 3, 'oversight', or 'human oversight'."""  # noqa: E501
        ctx = _ctx(m, human_oversight_available=False)
        result = m.OPCGuidelinesFilter().evaluate(ctx)
        assert result.is_denied, "Expected DENIED when human_oversight_available=False"
        combined = " ".join(result.findings).lower()
        assert "guideline 3" in combined or "oversight" in combined or "human oversight" in combined, (
            f"Finding should reference Guideline 3 or oversight; findings={result.findings}"
        )

    def test_no_accuracy_measures_denied(self, m):
        """accuracy_measures_in_place=False → DENIED; finding references Guideline 4 or 'accuracy'."""
        ctx = _ctx(m, accuracy_measures_in_place=False)
        result = m.OPCGuidelinesFilter().evaluate(ctx)
        assert result.is_denied, "Expected DENIED when accuracy_measures_in_place=False"
        combined = " ".join(result.findings).lower()
        assert "guideline 4" in combined or "accuracy" in combined, (
            f"Finding should reference Guideline 4 or 'accuracy'; findings={result.findings}"
        )

    def test_no_accountability_framework_denied(self, m):
        """accountability_framework_exists=False → DENIED; finding references Guideline 5 or 'accountability'."""
        ctx = _ctx(m, accountability_framework_exists=False)
        result = m.OPCGuidelinesFilter().evaluate(ctx)
        assert result.is_denied, "Expected DENIED when accountability_framework_exists=False"
        combined = " ".join(result.findings).lower()
        assert "guideline 5" in combined or "accountability" in combined, (
            f"Finding should reference Guideline 5 or 'accountability'; findings={result.findings}"
        )

    def test_no_consent_also_denied_by_opc(self, m):
        """meaningful_consent_obtained=False → OPC independently produces DENIED."""
        ctx = _ctx(m, meaningful_consent_obtained=False)
        result = m.OPCGuidelinesFilter().evaluate(ctx)
        assert result.is_denied, "OPC layer should independently deny when meaningful_consent_obtained=False"

    def test_conditions_reference_opc(self, m):
        """Compliant system → conditions reference 'OPC', 'audit', or 'Guideline'."""
        ctx = _ctx(m)
        result = m.OPCGuidelinesFilter().evaluate(ctx)
        combined = " ".join(result.conditions)
        assert "OPC" in combined or "audit" in combined.lower() or "Guideline" in combined, (
            f"Conditions should reference OPC, audit, or Guideline; conditions={result.conditions}"
        )


# ---------------------------------------------------------------------------
# TestQuebecLaw25Filter
# ---------------------------------------------------------------------------


class TestQuebecLaw25Filter:
    """Layer 4 — Québec Law 25."""

    def test_non_qc_province_not_applicable(self, m):
        """deploying_province='ON' → not DENIED; condition references 'Québec', 'Law 25', or 'does not apply'."""
        ctx = _non_qc_ctx(m, deploying_province="ON")
        result = m.QuebecLaw25Filter().evaluate(ctx)
        assert not result.is_denied, f"Expected not DENIED for non-QC province; got {result.decision}"
        combined = " ".join(result.conditions).lower()
        assert "québec" in combined or "quebec" in combined or "law 25" in combined or "does not apply" in combined, (
            f"Condition should mention Québec/Law 25/does not apply; conditions={result.conditions}"
        )

    def test_qc_all_compliant_approved_with_conditions(self, m):
        """deploying_province='QC', all Law 25 fields True → APPROVED_WITH_CONDITIONS."""
        ctx = _ctx(m, deploying_province="QC")
        result = m.QuebecLaw25Filter().evaluate(ctx)
        assert result.has_conditions, (
            f"Expected APPROVED_WITH_CONDITIONS for compliant QC system; got {result.decision}"
        )

    def test_qc_missing_pia_denied(self, m):
        """QC deployment, privacy_impact_assessment_done=False → DENIED; finding references s.63.3 or 'PIA'."""
        ctx = _ctx(m, deploying_province="QC", privacy_impact_assessment_done=False)
        result = m.QuebecLaw25Filter().evaluate(ctx)
        assert result.is_denied, "Expected DENIED when QC deployment with privacy_impact_assessment_done=False"
        combined = " ".join(result.findings).lower()
        assert "s.63.3" in combined or "pia" in combined or "privacy impact" in combined, (
            f"Finding should reference s.63.3, PIA, or privacy impact; findings={result.findings}"
        )

    def test_qc_missing_algorithmic_transparency_denied(self, m):
        """QC deployment, algorithmic_transparency_published=False → DENIED; finding references s.12 or 'algorithmic'."""  # noqa: E501
        ctx = _ctx(m, deploying_province="QC", algorithmic_transparency_published=False)
        result = m.QuebecLaw25Filter().evaluate(ctx)
        assert result.is_denied, "Expected DENIED when QC deployment with algorithmic_transparency_published=False"
        combined = " ".join(result.findings).lower()
        assert "s.12" in combined or "algorithmic" in combined or "transparency" in combined, (
            f"Finding should reference s.12, algorithmic, or transparency; findings={result.findings}"
        )

    def test_qc_missing_data_governance_officer_denied(self, m):
        """QC deployment, data_governance_officer_designated=False → DENIED; finding references s.3.1, CPO, Privacy Officer, or governance officer."""  # noqa: E501
        ctx = _ctx(m, deploying_province="QC", data_governance_officer_designated=False)
        result = m.QuebecLaw25Filter().evaluate(ctx)
        assert result.is_denied, "Expected DENIED when QC deployment with data_governance_officer_designated=False"
        combined = " ".join(result.findings).lower()
        assert (
            "s.3.1" in combined
            or "cpo" in combined
            or "privacy officer" in combined
            or "governance officer" in combined
            or "responsible" in combined
        ), f"Finding should reference s.3.1, CPO, Privacy Officer, or governance officer; findings={result.findings}"

    def test_qc_conditions_reference_law_25(self, m):
        """QC compliant system → conditions reference 'Law 25', 'Québec', or 'Commission'."""
        ctx = _ctx(m, deploying_province="QC")
        result = m.QuebecLaw25Filter().evaluate(ctx)
        combined = " ".join(result.conditions)
        assert "Law 25" in combined or "Québec" in combined or "Quebec" in combined or "Commission" in combined, (
            f"Conditions should reference Law 25, Québec, or Commission; conditions={result.conditions}"
        )

    def test_bc_province_not_applicable(self, m):
        """deploying_province='BC' → not DENIED (Law 25 does not apply)."""
        ctx = _non_qc_ctx(
            m,
            deploying_province="BC",
            # Law 25 fields intentionally incomplete — should not matter outside QC
            privacy_impact_assessment_done=False,
            algorithmic_transparency_published=False,
            data_governance_officer_designated=False,
        )
        result = m.QuebecLaw25Filter().evaluate(ctx)
        assert not result.is_denied, f"Expected not DENIED for BC deployment; got {result.decision}"


# ---------------------------------------------------------------------------
# TestCanadaAIGovernanceOrchestrator
# ---------------------------------------------------------------------------


class TestCanadaAIGovernanceOrchestrator:
    """Four-layer orchestrator: CanadaAIGovernanceOrchestrator."""

    def test_fully_compliant_qc_approved_with_conditions(self, m):
        """Fully compliant QC HIGH_IMPACT system → final_decision == APPROVED_WITH_CONDITIONS."""
        ctx = _ctx(m)
        report = m.CanadaAIGovernanceOrchestrator().evaluate(ctx)
        assert report.final_decision == m.CanadianAIDecision.APPROVED_WITH_CONDITIONS, (
            f"Expected APPROVED_WITH_CONDITIONS; got {report.final_decision}"
        )

    def test_missing_consent_denied(self, m):
        """meaningful_consent_obtained=False → final_decision == DENIED."""
        ctx = _ctx(m, meaningful_consent_obtained=False)
        report = m.CanadaAIGovernanceOrchestrator().evaluate(ctx)
        assert report.final_decision == m.CanadianAIDecision.DENIED, (
            f"Expected DENIED when consent missing; got {report.final_decision}"
        )

    def test_qc_missing_pia_denied(self, m):
        """QC system, privacy_impact_assessment_done=False → final_decision == DENIED."""
        ctx = _ctx(m, deploying_province="QC", privacy_impact_assessment_done=False)
        report = m.CanadaAIGovernanceOrchestrator().evaluate(ctx)
        assert report.final_decision == m.CanadianAIDecision.DENIED, (
            f"Expected DENIED when QC PIA missing; got {report.final_decision}"
        )

    def test_all_four_layers_evaluated(self, m):
        """Orchestrator always evaluates all four layers regardless of earlier results."""
        ctx = _ctx(m)
        report = m.CanadaAIGovernanceOrchestrator().evaluate(ctx)
        assert len(report.layer_results) == 4, f"Expected 4 layer results; got {len(report.layer_results)}"

    def test_layer_order(self, m):
        """Layer names appear in correct order: AIDA → CPPA → OPC → QUEBEC."""
        ctx = _ctx(m)
        report = m.CanadaAIGovernanceOrchestrator().evaluate(ctx)
        layer_names = [r.layer for r in report.layer_results]
        assert layer_names == [
            "AIDA_COMPLIANCE",
            "CPPA_DATA_GOVERNANCE",
            "OPC_AI_GUIDELINES",
            "QUEBEC_LAW_25",
        ], f"Expected layers in order AIDA→CPPA→OPC→QUEBEC; got {layer_names}"

    def test_report_summary_structure(self, m):
        """summary() contains required keys and correct layer count."""
        ctx = _ctx(m)
        report = m.CanadaAIGovernanceOrchestrator().evaluate(ctx)
        s = report.summary()
        for key in ("system_id", "system_name", "risk_level", "deploying_province", "final_decision", "layers"):
            assert key in s, f"summary() missing key '{key}'"
        assert len(s["layers"]) == 4, f"Expected 4 layers in summary; got {len(s['layers'])}"

    def test_non_qc_fully_compliant_approved_with_conditions(self, m):
        """Ontario LOW_IMPACT system, all fields True → final_decision == APPROVED_WITH_CONDITIONS."""
        ctx = _non_qc_ctx(m)
        report = m.CanadaAIGovernanceOrchestrator().evaluate(ctx)
        assert report.final_decision == m.CanadianAIDecision.APPROVED_WITH_CONDITIONS, (
            f"Expected APPROVED_WITH_CONDITIONS for compliant ON system; got {report.final_decision}"
        )
