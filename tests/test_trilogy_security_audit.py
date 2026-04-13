"""Tests for 41_trilogy_security_audit.py — TrilogyAuditOrchestrator."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Load the module under test
# ---------------------------------------------------------------------------
_EXAMPLES_DIR = Path(__file__).parent.parent / "examples"
_MODULE_PATH = _EXAMPLES_DIR / "41_trilogy_security_audit.py"

spec = importlib.util.spec_from_file_location("trilogy_security_audit", _MODULE_PATH)
mod = importlib.util.module_from_spec(spec)
sys.modules["trilogy_security_audit"] = mod
spec.loader.exec_module(mod)

TrilogySystemProfile = mod.TrilogySystemProfile
TrilogyCrossGap = mod.TrilogyCrossGap
TrilogyAuditResult = mod.TrilogyAuditResult
TrilogyAuditOrchestrator = mod.TrilogyAuditOrchestrator


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _audit(profile: TrilogySystemProfile) -> TrilogyAuditResult:
    return TrilogyAuditOrchestrator().audit(profile)


def _all_enabled() -> TrilogySystemProfile:
    return TrilogySystemProfile(
        system_id="production-ai",
        rag_query_injection_detection_enabled=True,
        rag_namespace_isolation_enforced=True,
        rag_cross_tenant_isolation=True,
        rag_dlp_scan_on_output=True,
        rag_action_gating_enabled=True,
        rag_query_logging_enabled=True,
        rag_vector_store_access_control=True,
        rag_document_integrity_checksums=True,
        rag_pre_filter_placement="pre",
        rag_output_schema_validation=True,
        rag_hallucination_detection_enabled=True,
        rag_retrieval_audit_logging=True,
        agent_tool_permission_model="rbac",
        agent_unsafe_tool_calls_blocked=True,
        agent_agent_identity_enforced=True,
        agent_privilege_escalation_prevented=True,
        agent_prompt_context_sanitized=True,
        agent_mcp_enabled=True,
        agent_mcp_source_allowlisted=True,
        agent_hitl_for_high_risk_actions=True,
        agent_multi_agent_enabled=True,
        agent_agent_trust_boundaries_defined=True,
        agent_tool_invocation_logging=True,
        gov_owasp_llm_prompt_injection_controls=True,
        gov_owasp_llm_sensitive_info_controls=True,
        gov_owasp_llm_data_poisoning_controls=True,
        gov_owasp_asi_goal_hijack_controls=True,
        gov_owasp_asi_tool_misuse_controls=True,
        gov_nist_govern_function_implemented=True,
        gov_iso_ai_policy_defined=True,
        gov_iso_ai_risk_assessment=True,
        gov_mitre_prompt_injection_detection=True,
        gov_mitre_poisoning_detection=True,
        gov_csa_atf_sandbox_controls=True,
        gov_csa_atf_continuous_assessment=True,
    )


# ---------------------------------------------------------------------------
# TrilogySystemProfile
# ---------------------------------------------------------------------------

class TestTrilogySystemProfile:
    def test_defaults_system_id(self):
        p = TrilogySystemProfile()
        assert p.system_id == "enterprise-ai-system"

    def test_all_rag_defaults_false(self):
        p = TrilogySystemProfile()
        assert p.rag_query_injection_detection_enabled is False
        assert p.rag_namespace_isolation_enforced is False
        assert p.rag_dlp_scan_on_output is False

    def test_agent_defaults(self):
        p = TrilogySystemProfile()
        assert p.agent_tool_permission_model == "none"
        assert p.agent_unsafe_tool_calls_blocked is False

    def test_gov_defaults_false(self):
        p = TrilogySystemProfile()
        assert p.gov_owasp_llm_prompt_injection_controls is False
        assert p.gov_nist_govern_function_implemented is False


# ---------------------------------------------------------------------------
# TrilogyCrossGap
# ---------------------------------------------------------------------------

class TestTrilogyCrossGap:
    def test_fields(self):
        gap = TrilogyCrossGap(
            gap_id="XG-001",
            title="Test Gap",
            description="desc",
            affected_auditors=["RAG", "Governance"],
            severity="HIGH",
            remediation="Fix it",
        )
        assert gap.gap_id == "XG-001"
        assert "RAG" in gap.affected_auditors
        assert gap.severity == "HIGH"


# ---------------------------------------------------------------------------
# All-defaults audit (Sandbox)
# ---------------------------------------------------------------------------

class TestAllDefaultsAudit:
    def setup_method(self):
        self.result = _audit(TrilogySystemProfile())

    def test_combined_maturity_is_sandbox(self):
        assert self.result.combined_maturity == "Sandbox"

    def test_rag_score_is_low(self):
        assert self.result.rag_score < 50

    def test_agent_score_is_low(self):
        assert self.result.agent_score < 85

    def test_governance_score_is_low(self):
        assert self.result.governance_score < 50

    def test_combined_score_formula(self):
        expected = (
            self.result.rag_score * 0.35
            + self.result.agent_score * 0.35
            + self.result.governance_score * 0.30
        )
        assert abs(self.result.combined_score - expected) < 0.01

    def test_cross_gaps_present(self):
        assert len(self.result.cross_gaps) > 0

    def test_xg_002_data_exfiltration_detected(self):
        gap_ids = {g.gap_id for g in self.result.cross_gaps}
        assert "XG-002" in gap_ids

    def test_xg_007_hitl_gap_detected(self):
        gap_ids = {g.gap_id for g in self.result.cross_gaps}
        assert "XG-007" in gap_ids

    def test_system_id_preserved(self):
        assert self.result.system_id == "enterprise-ai-system"


# ---------------------------------------------------------------------------
# All-enabled audit (Autonomous)
# ---------------------------------------------------------------------------

class TestAllEnabledAudit:
    def setup_method(self):
        self.result = _audit(_all_enabled())

    def test_combined_maturity_is_autonomous(self):
        assert self.result.combined_maturity == "Autonomous"

    def test_rag_score_is_100(self):
        assert self.result.rag_score == 100.0

    def test_agent_score_is_100(self):
        assert self.result.agent_score == 100

    def test_governance_score_is_100(self):
        assert self.result.governance_score == 100

    def test_combined_score_is_100(self):
        assert self.result.combined_score == 100.0

    def test_no_cross_gaps(self):
        assert len(self.result.cross_gaps) == 0

    def test_rag_critical_count_zero(self):
        assert self.result.rag_critical_count == 0

    def test_agent_critical_count_zero(self):
        assert self.result.agent_critical_count == 0

    def test_gov_critical_count_zero(self):
        assert self.result.gov_critical_count == 0


# ---------------------------------------------------------------------------
# Combined score formula
# ---------------------------------------------------------------------------

class TestCombinedScoreFormula:
    def test_combined_score_is_weighted_average(self):
        result = _audit(_all_enabled())
        expected = result.rag_score * 0.35 + result.agent_score * 0.35 + result.governance_score * 0.30
        assert abs(result.combined_score - expected) < 0.01

    def test_combined_maturity_is_minimum_of_three(self):
        # With all defaults, all three are Sandbox → combined is Sandbox
        result = _audit(TrilogySystemProfile())
        maturity_order = {"Sandbox": 0, "Controlled": 1, "Trusted": 2, "Autonomous": 3}
        combined_rank = maturity_order.get(result.combined_maturity, -1)
        rag_rank = maturity_order.get(result.rag_maturity, -1)
        agent_rank = maturity_order.get(result.agent_maturity, -1)
        gov_rank = maturity_order.get(result.governance_maturity, -1)
        assert combined_rank <= rag_rank
        assert combined_rank <= agent_rank
        assert combined_rank <= gov_rank


# ---------------------------------------------------------------------------
# Cross-gap XG-001: injection policy mismatch
# ---------------------------------------------------------------------------

class TestXG001InjectionMismatch:
    def test_xg_001_triggered_when_governance_has_control_but_rag_does_not(self):
        profile = TrilogySystemProfile(
            rag_query_injection_detection_enabled=False,
            gov_owasp_llm_prompt_injection_controls=True,
        )
        result = _audit(profile)
        gap_ids = {g.gap_id for g in result.cross_gaps}
        assert "XG-001" in gap_ids

    def test_xg_001_not_triggered_when_both_consistent(self):
        # Both enabled = no mismatch
        profile = TrilogySystemProfile(
            rag_query_injection_detection_enabled=True,
            gov_owasp_llm_prompt_injection_controls=True,
        )
        result = _audit(profile)
        gap_ids = {g.gap_id for g in result.cross_gaps}
        assert "XG-001" not in gap_ids


# ---------------------------------------------------------------------------
# Cross-gap XG-004: audit trail
# ---------------------------------------------------------------------------

class TestXG004AuditTrail:
    def test_xg_004_triggered_when_no_logging(self):
        profile = TrilogySystemProfile(
            rag_retrieval_audit_logging=False,
            agent_tool_invocation_logging=False,
        )
        result = _audit(profile)
        gap_ids = {g.gap_id for g in result.cross_gaps}
        assert "XG-004" in gap_ids

    def test_xg_004_not_triggered_when_both_enabled(self):
        profile = _all_enabled()
        result = _audit(profile)
        gap_ids = {g.gap_id for g in result.cross_gaps}
        assert "XG-004" not in gap_ids


# ---------------------------------------------------------------------------
# Cross-gap XG-007: HITL gap
# ---------------------------------------------------------------------------

class TestXG007HITLGap:
    def test_xg_007_triggered_when_no_hitl_no_action_gating(self):
        profile = TrilogySystemProfile(
            agent_hitl_for_high_risk_actions=False,
            rag_action_gating_enabled=False,
        )
        result = _audit(profile)
        gap_ids = {g.gap_id for g in result.cross_gaps}
        assert "XG-007" in gap_ids

    def test_xg_007_not_triggered_when_hitl_and_gating_enabled(self):
        profile = _all_enabled()
        result = _audit(profile)
        gap_ids = {g.gap_id for g in result.cross_gaps}
        assert "XG-007" not in gap_ids


# ---------------------------------------------------------------------------
# TrilogyAuditResult.summary()
# ---------------------------------------------------------------------------

class TestTrilogyAuditResultSummary:
    def test_summary_returns_string(self):
        result = _audit(TrilogySystemProfile())
        assert isinstance(result.summary(), str)

    def test_summary_contains_system_id(self):
        result = _audit(TrilogySystemProfile(system_id="my-system"))
        assert "my-system" in result.summary()

    def test_summary_contains_combined_score(self):
        result = _audit(_all_enabled())
        assert "100" in result.summary()

    def test_summary_contains_combined_maturity(self):
        result = _audit(TrilogySystemProfile())
        assert "Sandbox" in result.summary()

    def test_summary_contains_auditor_names(self):
        result = _audit(TrilogySystemProfile())
        s = result.summary()
        assert "RAG" in s
        assert "Agent" in s


# ---------------------------------------------------------------------------
# Score bounds
# ---------------------------------------------------------------------------

class TestScoreBounds:
    def test_combined_score_not_negative(self):
        result = _audit(TrilogySystemProfile())
        assert result.combined_score >= 0.0

    def test_combined_score_not_above_100(self):
        result = _audit(_all_enabled())
        assert result.combined_score <= 100.0

    def test_rag_score_not_negative(self):
        result = _audit(TrilogySystemProfile())
        assert result.rag_score >= 0.0

    def test_agent_score_not_negative(self):
        result = _audit(TrilogySystemProfile())
        assert result.agent_score >= 0.0

    def test_governance_score_not_negative(self):
        result = _audit(TrilogySystemProfile())
        assert result.governance_score >= 0.0
