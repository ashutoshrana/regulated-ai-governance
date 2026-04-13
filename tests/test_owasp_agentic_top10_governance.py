"""
Tests for 39_owasp_agentic_top10_governance.py — OWASP Top 10 for Agentic
Applications 2026

Covers:
  1. OWASPAgenticInjectionFilter    — ASI01 Goal Hijack + ASI04 Data Poisoning
  2. OWASPAgenticToolSafetyFilter   — ASI02 Unsafe Tool Use + ASI05 Privilege
                                       Misuse + ASI06 Supply Chain
  3. OWASPAgenticDataLeakageFilter  — ASI03 Data Leakage + ASI07 Human-Agent
                                       Trust Exploitation
  4. OWASPAgenticGovernanceFilter   — ASI08 Cascading Failures + ASI09
                                       Monitoring + ASI10 Composition
  5. FilterResult.is_denied property
  6. OWASP_AGENTIC_TOP10_2026 constant completeness (10 entries)
  7. Eight ecosystem wrappers (LangChain, CrewAI, AutoGen, SK, LlamaIndex,
     Haystack, DSPy, MAF)
  8. Edge cases: missing keys, empty dict, boundary values
"""

from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Module loader — use importlib per task specification
# ---------------------------------------------------------------------------

_MOD_NAME = "mod_owasp_agentic_top10"

spec = importlib.util.spec_from_file_location(
    _MOD_NAME,
    str(Path(__file__).parent.parent / "examples" / "39_owasp_agentic_top10_governance.py"),
)
mod = types.ModuleType(_MOD_NAME)
sys.modules[_MOD_NAME] = mod
spec.loader.exec_module(mod)


# ===========================================================================
# TestFilterResult — is_denied property and field defaults
# ===========================================================================


class TestFilterResult:
    """FilterResult.is_denied must be True only for decision == 'DENIED'."""

    def test_is_denied_true_for_denied(self):
        r = mod.FilterResult(decision="DENIED", regulation="X", reason="Y", filter_name="F")
        assert r.is_denied is True

    def test_is_denied_false_for_permitted(self):
        r = mod.FilterResult(decision="PERMITTED", regulation="X", reason="Y", filter_name="F")
        assert r.is_denied is False

    def test_is_denied_false_for_requires_human_review(self):
        r = mod.FilterResult(
            decision="REQUIRES_HUMAN_REVIEW",
            regulation="X",
            reason="Y",
            filter_name="F",
        )
        assert r.is_denied is False

    def test_is_denied_false_for_other_value(self):
        r = mod.FilterResult(decision="PENDING", regulation="X", reason="Y", filter_name="F")
        assert r.is_denied is False

    def test_filter_result_has_required_fields(self):
        r = mod.FilterResult(decision="DENIED", regulation="R", reason="Reason", filter_name="FN")
        assert r.decision == "DENIED"
        assert r.regulation == "R"
        assert r.reason == "Reason"
        assert r.filter_name == "FN"

    def test_filter_result_fields_stored_correctly(self):
        r = mod.FilterResult(
            decision="PERMITTED",
            regulation="OWASP ASI01",
            reason="compliant",
            filter_name="OWASP_FILTER",
        )
        assert r.decision == "PERMITTED"
        assert r.regulation == "OWASP ASI01"
        assert r.reason == "compliant"
        assert r.filter_name == "OWASP_FILTER"


# ===========================================================================
# TestOWASPAgenticTop10Constant — completeness check
# ===========================================================================


class TestOWASPAgenticTop10Constant:
    """OWASP_AGENTIC_TOP10_2026 must have exactly 10 entries, ASI01-ASI10."""

    def test_constant_has_ten_entries(self):
        assert len(mod.OWASP_AGENTIC_TOP10_2026) == 10

    def test_constant_has_asi01(self):
        assert "ASI01" in mod.OWASP_AGENTIC_TOP10_2026

    def test_constant_has_asi02(self):
        assert "ASI02" in mod.OWASP_AGENTIC_TOP10_2026

    def test_constant_has_asi03(self):
        assert "ASI03" in mod.OWASP_AGENTIC_TOP10_2026

    def test_constant_has_asi04(self):
        assert "ASI04" in mod.OWASP_AGENTIC_TOP10_2026

    def test_constant_has_asi05(self):
        assert "ASI05" in mod.OWASP_AGENTIC_TOP10_2026

    def test_constant_has_asi06(self):
        assert "ASI06" in mod.OWASP_AGENTIC_TOP10_2026

    def test_constant_has_asi07(self):
        assert "ASI07" in mod.OWASP_AGENTIC_TOP10_2026

    def test_constant_has_asi08(self):
        assert "ASI08" in mod.OWASP_AGENTIC_TOP10_2026

    def test_constant_has_asi09(self):
        assert "ASI09" in mod.OWASP_AGENTIC_TOP10_2026

    def test_constant_has_asi10(self):
        assert "ASI10" in mod.OWASP_AGENTIC_TOP10_2026

    def test_asi01_name(self):
        assert "Goal Hijack" in mod.OWASP_AGENTIC_TOP10_2026["ASI01"]

    def test_asi02_name(self):
        assert "Tool" in mod.OWASP_AGENTIC_TOP10_2026["ASI02"]

    def test_asi03_name(self):
        assert "Leakage" in mod.OWASP_AGENTIC_TOP10_2026["ASI03"]

    def test_asi04_name(self):
        assert "Poisoning" in mod.OWASP_AGENTIC_TOP10_2026["ASI04"]

    def test_asi05_name(self):
        assert "Privilege" in mod.OWASP_AGENTIC_TOP10_2026["ASI05"]

    def test_asi06_name(self):
        assert "Supply" in mod.OWASP_AGENTIC_TOP10_2026["ASI06"]

    def test_asi07_name(self):
        assert "Trust" in mod.OWASP_AGENTIC_TOP10_2026["ASI07"]

    def test_asi08_name(self):
        assert "Cascading" in mod.OWASP_AGENTIC_TOP10_2026["ASI08"]

    def test_asi09_name(self):
        assert "Monitor" in mod.OWASP_AGENTIC_TOP10_2026["ASI09"]

    def test_asi10_name(self):
        assert "Composition" in mod.OWASP_AGENTIC_TOP10_2026["ASI10"]


# ===========================================================================
# TestOWASPAgenticInjectionFilter — ASI01 + ASI04
# ===========================================================================


class TestOWASPAgenticInjectionFilter:
    """ASI01 Goal Hijack and ASI04 Data Poisoning controls."""

    def _eval(self, **kwargs):
        return mod.OWASPAgenticInjectionFilter().filter(kwargs)

    # --- ASI01 — External input without injection detection: DENIED ---

    def test_external_input_no_injection_detection_denied(self):
        r = self._eval(external_input=True, injection_detection_enabled=False)
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_external_input_no_injection_detection_cites_asi01(self):
        r = self._eval(external_input=True, injection_detection_enabled=False)
        assert "ASI01" in r.regulation

    def test_external_input_no_injection_detection_filter_name(self):
        r = self._eval(external_input=True, injection_detection_enabled=False)
        assert r.filter_name == "OWASP_AGENTIC_INJECTION_FILTER"

    def test_external_input_with_injection_detection_permitted(self):
        r = self._eval(external_input=True, injection_detection_enabled=True)
        assert r.decision == "PERMITTED"

    def test_no_external_input_no_trigger(self):
        r = self._eval(external_input=False, injection_detection_enabled=False)
        assert r.decision == "PERMITTED"

    def test_missing_external_input_key_permitted(self):
        r = self._eval(injection_detection_enabled=False)
        assert r.decision == "PERMITTED"

    # --- ASI04 — Retrieved document without integrity verification: DENIED ---

    def test_retrieved_doc_no_integrity_denied(self):
        r = self._eval(retrieved_document=True, document_integrity_verified=False)
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_retrieved_doc_no_integrity_cites_asi04(self):
        r = self._eval(retrieved_document=True, document_integrity_verified=False)
        assert "ASI04" in r.regulation

    def test_retrieved_doc_no_integrity_filter_name(self):
        r = self._eval(retrieved_document=True, document_integrity_verified=False)
        assert r.filter_name == "OWASP_AGENTIC_INJECTION_FILTER"

    def test_retrieved_doc_with_integrity_permitted(self):
        r = self._eval(retrieved_document=True, document_integrity_verified=True)
        assert r.decision == "PERMITTED"

    def test_no_retrieved_doc_permitted(self):
        r = self._eval(retrieved_document=False, document_integrity_verified=False)
        assert r.decision == "PERMITTED"

    # --- ASI01 indirect — tool output without sanitisation: DENIED ---

    def test_tool_output_no_sanitization_denied(self):
        r = self._eval(tool_output=True, output_sanitized=False)
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_tool_output_no_sanitization_cites_asi01(self):
        r = self._eval(tool_output=True, output_sanitized=False)
        assert "ASI01" in r.regulation

    def test_tool_output_with_sanitization_permitted(self):
        r = self._eval(tool_output=True, output_sanitized=True)
        assert r.decision == "PERMITTED"

    def test_no_tool_output_permitted(self):
        r = self._eval(tool_output=False, output_sanitized=False)
        assert r.decision == "PERMITTED"

    # --- ASI04 anomaly — score above threshold: REQUIRES_HUMAN_REVIEW ---

    def test_high_anomaly_score_requires_human_review(self):
        r = self._eval(anomaly_score=0.85)
        assert r.decision == "REQUIRES_HUMAN_REVIEW"
        assert not r.is_denied

    def test_anomaly_score_at_threshold_boundary_permitted(self):
        # exactly at threshold 0.7 should NOT trigger (requires > 0.7)
        r = self._eval(anomaly_score=0.7)
        assert r.decision == "PERMITTED"

    def test_anomaly_score_just_above_threshold_rhr(self):
        r = self._eval(anomaly_score=0.71)
        assert r.decision == "REQUIRES_HUMAN_REVIEW"

    def test_anomaly_score_below_threshold_permitted(self):
        r = self._eval(anomaly_score=0.5)
        assert r.decision == "PERMITTED"

    def test_anomaly_score_zero_permitted(self):
        r = self._eval(anomaly_score=0.0)
        assert r.decision == "PERMITTED"

    def test_anomaly_score_1_rhr(self):
        r = self._eval(anomaly_score=1.0)
        assert r.decision == "REQUIRES_HUMAN_REVIEW"

    def test_rhr_cites_asi04(self):
        r = self._eval(anomaly_score=0.9)
        assert "ASI04" in r.regulation

    # --- Empty dict / fully compliant ---

    def test_empty_doc_permitted(self):
        r = self._eval()
        assert r.decision == "PERMITTED"

    def test_all_controls_satisfied_permitted(self):
        r = self._eval(
            external_input=True,
            injection_detection_enabled=True,
            retrieved_document=True,
            document_integrity_verified=True,
            tool_output=True,
            output_sanitized=True,
            anomaly_score=0.2,
        )
        assert r.decision == "PERMITTED"


# ===========================================================================
# TestOWASPAgenticToolSafetyFilter — ASI02 + ASI05 + ASI06
# ===========================================================================


class TestOWASPAgenticToolSafetyFilter:
    """ASI02 Unsafe Tool Use, ASI05 Privilege Misuse, ASI06 Supply Chain."""

    def _eval(self, **kwargs):
        return mod.OWASPAgenticToolSafetyFilter().filter(kwargs)

    # --- ASI02 — Tool invocation without allowlist verification: DENIED ---

    def test_tool_invocation_no_allowlist_denied(self):
        r = self._eval(tool_invocation=True, tool_allowlist_verified=False)
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_tool_invocation_no_allowlist_cites_asi02(self):
        r = self._eval(tool_invocation=True, tool_allowlist_verified=False)
        assert "ASI02" in r.regulation

    def test_tool_invocation_no_allowlist_filter_name(self):
        r = self._eval(tool_invocation=True, tool_allowlist_verified=False)
        assert r.filter_name == "OWASP_AGENTIC_TOOL_SAFETY_FILTER"

    def test_tool_invocation_with_allowlist_permitted(self):
        r = self._eval(tool_invocation=True, tool_allowlist_verified=True)
        assert r.decision == "PERMITTED"

    def test_no_tool_invocation_permitted(self):
        r = self._eval(tool_invocation=False, tool_allowlist_verified=False)
        assert r.decision == "PERMITTED"

    # --- ASI05 — Cross-session privileges: DENIED ---

    def test_cross_session_privileges_denied(self):
        r = self._eval(cross_session_privileges=True)
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_cross_session_privileges_cites_asi05(self):
        r = self._eval(cross_session_privileges=True)
        assert "ASI05" in r.regulation

    def test_cross_session_privileges_false_permitted(self):
        r = self._eval(cross_session_privileges=False)
        assert r.decision == "PERMITTED"

    def test_missing_cross_session_privileges_key_permitted(self):
        r = self._eval()
        assert r.decision == "PERMITTED"

    # --- ASI06 — Tool plugin without signature verification: DENIED ---

    def test_tool_plugin_no_signature_denied(self):
        r = self._eval(tool_plugin_loaded=True, tool_signature_verified=False)
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_tool_plugin_no_signature_cites_asi06(self):
        r = self._eval(tool_plugin_loaded=True, tool_signature_verified=False)
        assert "ASI06" in r.regulation

    def test_tool_plugin_with_signature_permitted(self):
        r = self._eval(tool_plugin_loaded=True, tool_signature_verified=True)
        assert r.decision == "PERMITTED"

    def test_no_tool_plugin_permitted(self):
        r = self._eval(tool_plugin_loaded=False, tool_signature_verified=False)
        assert r.decision == "PERMITTED"

    # --- ASI02 approval gate — requires approval without confirmation: RHR ---

    def test_requires_approval_no_human_rhr(self):
        r = self._eval(requires_approval=True, human_approved=False)
        assert r.decision == "REQUIRES_HUMAN_REVIEW"
        assert not r.is_denied

    def test_requires_approval_rhr_cites_asi02(self):
        r = self._eval(requires_approval=True, human_approved=False)
        assert "ASI02" in r.regulation

    def test_requires_approval_with_human_approved_permitted(self):
        r = self._eval(requires_approval=True, human_approved=True)
        assert r.decision == "PERMITTED"

    def test_requires_approval_false_permitted(self):
        r = self._eval(requires_approval=False, human_approved=False)
        assert r.decision == "PERMITTED"

    # --- Empty dict / fully compliant ---

    def test_empty_doc_permitted(self):
        r = self._eval()
        assert r.decision == "PERMITTED"

    def test_all_controls_satisfied_permitted(self):
        r = self._eval(
            tool_invocation=True,
            tool_allowlist_verified=True,
            cross_session_privileges=False,
            tool_plugin_loaded=True,
            tool_signature_verified=True,
            requires_approval=False,
        )
        assert r.decision == "PERMITTED"


# ===========================================================================
# TestOWASPAgenticDataLeakageFilter — ASI03 + ASI07
# ===========================================================================


class TestOWASPAgenticDataLeakageFilter:
    """ASI03 Data Leakage and ASI07 Human-Agent Trust Exploitation."""

    def _eval(self, **kwargs):
        return mod.OWASPAgenticDataLeakageFilter().filter(kwargs)

    # --- ASI03 — Agent output without DLP scan: DENIED ---

    def test_agent_output_no_dlp_scan_denied(self):
        r = self._eval(agent_output=True, dlp_scan_passed=False)
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_agent_output_no_dlp_scan_cites_asi03(self):
        r = self._eval(agent_output=True, dlp_scan_passed=False)
        assert "ASI03" in r.regulation

    def test_agent_output_no_dlp_scan_filter_name(self):
        r = self._eval(agent_output=True, dlp_scan_passed=False)
        assert r.filter_name == "OWASP_AGENTIC_DATA_LEAKAGE_FILTER"

    def test_agent_output_with_dlp_scan_permitted(self):
        r = self._eval(agent_output=True, dlp_scan_passed=True)
        assert r.decision == "PERMITTED"

    def test_no_agent_output_permitted(self):
        r = self._eval(agent_output=False, dlp_scan_passed=False)
        assert r.decision == "PERMITTED"

    # --- ASI03 — Memory not session-scoped: DENIED ---

    def test_memory_not_session_scoped_denied(self):
        r = self._eval(agent_memory_access=True, session_scoped_memory=False)
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_memory_not_session_scoped_cites_asi03(self):
        r = self._eval(agent_memory_access=True, session_scoped_memory=False)
        assert "ASI03" in r.regulation

    def test_memory_session_scoped_permitted(self):
        r = self._eval(agent_memory_access=True, session_scoped_memory=True)
        assert r.decision == "PERMITTED"

    def test_no_memory_access_permitted(self):
        r = self._eval(agent_memory_access=False, session_scoped_memory=False)
        assert r.decision == "PERMITTED"

    # --- ASI07 — Agent claims capabilities beyond actual scope: DENIED ---

    def test_claimed_capabilities_exceed_actual_denied(self):
        r = self._eval(claimed_capabilities_exceed_actual=True)
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_claimed_capabilities_exceed_actual_cites_asi07(self):
        r = self._eval(claimed_capabilities_exceed_actual=True)
        assert "ASI07" in r.regulation

    def test_claimed_capabilities_within_scope_permitted(self):
        r = self._eval(claimed_capabilities_exceed_actual=False)
        assert r.decision == "PERMITTED"

    def test_missing_claimed_capabilities_key_permitted(self):
        r = self._eval()
        assert r.decision == "PERMITTED"

    # --- ASI07 — Low confidence without disclosure: REQUIRES_HUMAN_REVIEW ---

    def test_low_confidence_no_disclosure_rhr(self):
        r = self._eval(confidence_score=0.45, confidence_disclosed=False)
        assert r.decision == "REQUIRES_HUMAN_REVIEW"
        assert not r.is_denied

    def test_low_confidence_rhr_cites_asi07(self):
        r = self._eval(confidence_score=0.45, confidence_disclosed=False)
        assert "ASI07" in r.regulation

    def test_low_confidence_with_disclosure_permitted(self):
        r = self._eval(confidence_score=0.45, confidence_disclosed=True)
        assert r.decision == "PERMITTED"

    def test_confidence_at_threshold_permitted(self):
        # exactly at threshold 0.6 should NOT trigger (requires < 0.6)
        r = self._eval(confidence_score=0.6, confidence_disclosed=False)
        assert r.decision == "PERMITTED"

    def test_confidence_just_below_threshold_rhr(self):
        r = self._eval(confidence_score=0.59, confidence_disclosed=False)
        assert r.decision == "REQUIRES_HUMAN_REVIEW"

    def test_high_confidence_permitted(self):
        r = self._eval(confidence_score=0.95, confidence_disclosed=False)
        assert r.decision == "PERMITTED"

    def test_confidence_1_0_permitted(self):
        r = self._eval(confidence_score=1.0, confidence_disclosed=False)
        assert r.decision == "PERMITTED"

    def test_default_confidence_no_rhr(self):
        # No confidence_score key — defaults to 1.0, should be PERMITTED
        r = self._eval(confidence_disclosed=False)
        assert r.decision == "PERMITTED"

    # --- Empty dict / fully compliant ---

    def test_empty_doc_permitted(self):
        r = self._eval()
        assert r.decision == "PERMITTED"

    def test_all_controls_satisfied_permitted(self):
        r = self._eval(
            agent_output=True,
            dlp_scan_passed=True,
            agent_memory_access=True,
            session_scoped_memory=True,
            claimed_capabilities_exceed_actual=False,
            confidence_score=0.9,
            confidence_disclosed=True,
        )
        assert r.decision == "PERMITTED"


# ===========================================================================
# TestOWASPAgenticGovernanceFilter — ASI08 + ASI09 + ASI10
# ===========================================================================


class TestOWASPAgenticGovernanceFilter:
    """ASI08 Cascading Failures, ASI09 Monitoring & Audit, ASI10 Composition."""

    def _eval(self, **kwargs):
        return mod.OWASPAgenticGovernanceFilter().filter(kwargs)

    # --- ASI08 — Irreversible action without rollback: DENIED ---

    def test_irreversible_action_no_rollback_denied(self):
        r = self._eval(action_irreversible=True, rollback_available=False)
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_irreversible_action_no_rollback_cites_asi08(self):
        r = self._eval(action_irreversible=True, rollback_available=False)
        assert "ASI08" in r.regulation

    def test_irreversible_action_no_rollback_filter_name(self):
        r = self._eval(action_irreversible=True, rollback_available=False)
        assert r.filter_name == "OWASP_AGENTIC_GOVERNANCE_FILTER"

    def test_irreversible_action_with_rollback_permitted(self):
        r = self._eval(action_irreversible=True, rollback_available=True)
        assert r.decision == "PERMITTED"

    def test_reversible_action_no_rollback_permitted(self):
        r = self._eval(action_irreversible=False, rollback_available=False)
        assert r.decision == "PERMITTED"

    def test_missing_irreversible_key_permitted(self):
        r = self._eval(rollback_available=False)
        assert r.decision == "PERMITTED"

    # --- ASI09 — Agent action without audit trail: DENIED ---

    def test_agent_action_no_audit_trail_denied(self):
        r = self._eval(agent_action=True, audit_trail_enabled=False)
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_agent_action_no_audit_trail_cites_asi09(self):
        r = self._eval(agent_action=True, audit_trail_enabled=False)
        assert "ASI09" in r.regulation

    def test_agent_action_with_audit_trail_permitted(self):
        r = self._eval(agent_action=True, audit_trail_enabled=True)
        assert r.decision == "PERMITTED"

    def test_no_agent_action_permitted(self):
        r = self._eval(agent_action=False, audit_trail_enabled=False)
        assert r.decision == "PERMITTED"

    # --- ASI10 — Multi-agent message without sender verification: DENIED ---

    def test_multi_agent_message_unverified_sender_denied(self):
        r = self._eval(multi_agent_message=True, sender_verified=False)
        assert r.decision == "DENIED"
        assert r.is_denied

    def test_multi_agent_message_unverified_cites_asi10(self):
        r = self._eval(multi_agent_message=True, sender_verified=False)
        assert "ASI10" in r.regulation

    def test_multi_agent_message_verified_sender_permitted(self):
        r = self._eval(multi_agent_message=True, sender_verified=True)
        assert r.decision == "PERMITTED"

    def test_no_multi_agent_message_permitted(self):
        r = self._eval(multi_agent_message=False, sender_verified=False)
        assert r.decision == "PERMITTED"

    # --- ASI08 HITL — High-impact action without human-in-the-loop: RHR ---

    def test_high_impact_no_hitl_rhr(self):
        r = self._eval(action_impact="high", human_in_loop=False)
        assert r.decision == "REQUIRES_HUMAN_REVIEW"
        assert not r.is_denied

    def test_high_impact_no_hitl_cites_asi08(self):
        r = self._eval(action_impact="high", human_in_loop=False)
        assert "ASI08" in r.regulation

    def test_high_impact_with_hitl_permitted(self):
        r = self._eval(action_impact="high", human_in_loop=True)
        assert r.decision == "PERMITTED"

    def test_low_impact_no_hitl_permitted(self):
        r = self._eval(action_impact="low", human_in_loop=False)
        assert r.decision == "PERMITTED"

    def test_medium_impact_no_hitl_permitted(self):
        r = self._eval(action_impact="medium", human_in_loop=False)
        assert r.decision == "PERMITTED"

    def test_missing_action_impact_permitted(self):
        r = self._eval(human_in_loop=False)
        assert r.decision == "PERMITTED"

    # --- Empty dict / fully compliant ---

    def test_empty_doc_permitted(self):
        r = self._eval()
        assert r.decision == "PERMITTED"

    def test_all_controls_satisfied_permitted(self):
        r = self._eval(
            action_irreversible=True,
            rollback_available=True,
            agent_action=True,
            audit_trail_enabled=True,
            multi_agent_message=True,
            sender_verified=True,
            action_impact="low",
            human_in_loop=True,
        )
        assert r.decision == "PERMITTED"


# ===========================================================================
# TestOWASPLangChainPolicyGuard — LangChain wrapper
# ===========================================================================


class TestOWASPLangChainPolicyGuard:
    """LangChain wrapper enforces OWASP Agentic governance via invoke()."""

    def test_invoke_denied_raises_permission_error(self):
        guard = mod.OWASPLangChainPolicyGuard(filter_instance=mod.OWASPAgenticInjectionFilter())
        with pytest.raises(PermissionError):
            guard.invoke({"external_input": True, "injection_detection_enabled": False})

    def test_invoke_permitted_returns_results(self):
        guard = mod.OWASPLangChainPolicyGuard(filter_instance=mod.OWASPAgenticInjectionFilter())
        results = guard.invoke({})
        assert isinstance(results, list)
        assert len(results) == 1
        assert results[0].decision == "PERMITTED"

    def test_ainvoke_denied_raises_permission_error(self):
        guard = mod.OWASPLangChainPolicyGuard(filter_instance=mod.OWASPAgenticInjectionFilter())
        with pytest.raises(PermissionError):
            guard.ainvoke({"external_input": True, "injection_detection_enabled": False})

    def test_process_denied_raises_permission_error(self):
        guard = mod.OWASPLangChainPolicyGuard(filter_instance=mod.OWASPAgenticInjectionFilter())
        with pytest.raises(PermissionError):
            guard.process({"external_input": True, "injection_detection_enabled": False})

    def test_process_permitted_returns_doc(self):
        guard = mod.OWASPLangChainPolicyGuard(filter_instance=mod.OWASPAgenticInjectionFilter())
        doc = {"something": "safe"}
        result = guard.process(doc)
        assert result == doc

    def test_multi_filter_mode_denied_raises(self):
        # No filter_instance → uses all four filters
        guard = mod.OWASPLangChainPolicyGuard()
        with pytest.raises(PermissionError):
            guard.invoke({"external_input": True, "injection_detection_enabled": False})

    def test_multi_filter_mode_permitted_returns_four_results(self):
        guard = mod.OWASPLangChainPolicyGuard()
        results = guard.invoke({})
        assert len(results) == 4
        assert all(r.decision == "PERMITTED" for r in results)

    def test_permission_error_contains_regulation(self):
        guard = mod.OWASPLangChainPolicyGuard(filter_instance=mod.OWASPAgenticInjectionFilter())
        with pytest.raises(PermissionError) as exc:
            guard.invoke({"external_input": True, "injection_detection_enabled": False})
        assert "ASI01" in str(exc.value)


# ===========================================================================
# TestOWASPCrewAIGovernanceGuard — CrewAI wrapper
# ===========================================================================


class TestOWASPCrewAIGovernanceGuard:
    """CrewAI wrapper enforces OWASP Agentic governance via _run()."""

    def test_run_denied_raises_permission_error(self):
        guard = mod.OWASPCrewAIGovernanceGuard(filter_instance=mod.OWASPAgenticToolSafetyFilter())
        with pytest.raises(PermissionError):
            guard._run({"tool_invocation": True, "tool_allowlist_verified": False})

    def test_run_permitted_returns_doc(self):
        guard = mod.OWASPCrewAIGovernanceGuard(filter_instance=mod.OWASPAgenticToolSafetyFilter())
        doc = {}
        assert guard._run(doc) == doc

    def test_run_permission_error_contains_asi02(self):
        guard = mod.OWASPCrewAIGovernanceGuard(filter_instance=mod.OWASPAgenticToolSafetyFilter())
        with pytest.raises(PermissionError) as exc:
            guard._run({"tool_invocation": True, "tool_allowlist_verified": False})
        assert "ASI02" in str(exc.value)

    def test_guard_has_name_attribute(self):
        guard = mod.OWASPCrewAIGovernanceGuard(filter_instance=mod.OWASPAgenticToolSafetyFilter())
        assert hasattr(guard, "name")
        assert isinstance(guard.name, str)

    def test_guard_has_description_attribute(self):
        guard = mod.OWASPCrewAIGovernanceGuard(filter_instance=mod.OWASPAgenticToolSafetyFilter())
        assert hasattr(guard, "description")
        assert isinstance(guard.description, str)


# ===========================================================================
# TestOWASPAutoGenGovernedAgent — AutoGen wrapper
# ===========================================================================


class TestOWASPAutoGenGovernedAgent:
    """AutoGen wrapper enforces OWASP Agentic governance via generate_reply()."""

    def test_generate_reply_denied_raises_permission_error(self):
        agent = mod.OWASPAutoGenGovernedAgent(filter_instance=mod.OWASPAgenticDataLeakageFilter())
        with pytest.raises(PermissionError):
            agent.generate_reply({"agent_output": True, "dlp_scan_passed": False})

    def test_generate_reply_permitted_returns_doc(self):
        agent = mod.OWASPAutoGenGovernedAgent(filter_instance=mod.OWASPAgenticDataLeakageFilter())
        doc = {}
        result = agent.generate_reply(doc)
        assert result == doc

    def test_generate_reply_none_messages_permitted(self):
        agent = mod.OWASPAutoGenGovernedAgent(filter_instance=mod.OWASPAgenticDataLeakageFilter())
        # messages=None should default to empty dict
        result = agent.generate_reply(None)
        assert result == {}

    def test_generate_reply_permission_error_contains_asi03(self):
        agent = mod.OWASPAutoGenGovernedAgent(filter_instance=mod.OWASPAgenticDataLeakageFilter())
        with pytest.raises(PermissionError) as exc:
            agent.generate_reply({"agent_output": True, "dlp_scan_passed": False})
        assert "ASI03" in str(exc.value)


# ===========================================================================
# TestOWASPSemanticKernelPlugin — Semantic Kernel wrapper
# ===========================================================================


class TestOWASPSemanticKernelPlugin:
    """Semantic Kernel wrapper enforces OWASP Agentic governance via enforce_governance()."""

    def test_enforce_governance_denied_raises_permission_error(self):
        plugin = mod.OWASPSemanticKernelPlugin(filter_instance=mod.OWASPAgenticGovernanceFilter())
        with pytest.raises(PermissionError):
            plugin.enforce_governance({"agent_action": True, "audit_trail_enabled": False})

    def test_enforce_governance_permitted_returns_doc(self):
        plugin = mod.OWASPSemanticKernelPlugin(filter_instance=mod.OWASPAgenticGovernanceFilter())
        doc = {}
        assert plugin.enforce_governance(doc) == doc

    def test_enforce_governance_permission_error_contains_asi09(self):
        plugin = mod.OWASPSemanticKernelPlugin(filter_instance=mod.OWASPAgenticGovernanceFilter())
        with pytest.raises(PermissionError) as exc:
            plugin.enforce_governance({"agent_action": True, "audit_trail_enabled": False})
        assert "ASI09" in str(exc.value)


# ===========================================================================
# TestOWASPLlamaIndexWorkflowGuard — LlamaIndex wrapper
# ===========================================================================


class TestOWASPLlamaIndexWorkflowGuard:
    """LlamaIndex wrapper enforces OWASP Agentic governance via process_event()."""

    def test_process_event_denied_raises_permission_error(self):
        guard = mod.OWASPLlamaIndexWorkflowGuard(filter_instance=mod.OWASPAgenticInjectionFilter())
        with pytest.raises(PermissionError):
            guard.process_event({"retrieved_document": True, "document_integrity_verified": False})

    def test_process_event_permitted_returns_doc(self):
        guard = mod.OWASPLlamaIndexWorkflowGuard(filter_instance=mod.OWASPAgenticInjectionFilter())
        doc = {}
        assert guard.process_event(doc) == doc

    def test_process_event_permission_error_contains_asi04(self):
        guard = mod.OWASPLlamaIndexWorkflowGuard(filter_instance=mod.OWASPAgenticInjectionFilter())
        with pytest.raises(PermissionError) as exc:
            guard.process_event({"retrieved_document": True, "document_integrity_verified": False})
        assert "ASI04" in str(exc.value)


# ===========================================================================
# TestOWASPHaystackGovernanceComponent — Haystack wrapper
# ===========================================================================


class TestOWASPHaystackGovernanceComponent:
    """Haystack wrapper filters denied documents; does not raise."""

    def test_run_filters_denied_documents(self):
        component = mod.OWASPHaystackGovernanceComponent(filter_instance=mod.OWASPAgenticToolSafetyFilter())
        docs = [
            {"tool_invocation": True, "tool_allowlist_verified": False},  # DENIED
            {},  # PERMITTED
        ]
        result = component.run(docs)
        assert len(result["documents"]) == 1
        assert result["documents"][0] == {}

    def test_run_all_permitted_returns_all(self):
        component = mod.OWASPHaystackGovernanceComponent(filter_instance=mod.OWASPAgenticToolSafetyFilter())
        docs = [{}, {}, {}]
        result = component.run(docs)
        assert len(result["documents"]) == 3

    def test_run_all_denied_returns_empty(self):
        component = mod.OWASPHaystackGovernanceComponent(filter_instance=mod.OWASPAgenticToolSafetyFilter())
        docs = [
            {"tool_invocation": True, "tool_allowlist_verified": False},
            {"tool_invocation": True, "tool_allowlist_verified": False},
        ]
        result = component.run(docs)
        assert result["documents"] == []

    def test_run_empty_list_returns_empty(self):
        component = mod.OWASPHaystackGovernanceComponent(filter_instance=mod.OWASPAgenticToolSafetyFilter())
        result = component.run([])
        assert result["documents"] == []

    def test_run_returns_documents_key(self):
        component = mod.OWASPHaystackGovernanceComponent(filter_instance=mod.OWASPAgenticToolSafetyFilter())
        result = component.run([{}])
        assert "documents" in result


# ===========================================================================
# TestOWASPDSPyGovernanceModule — DSPy wrapper
# ===========================================================================


class TestOWASPDSPyGovernanceModule:
    """DSPy wrapper enforces OWASP Agentic governance via forward()."""

    def _make_module(self):
        """Simple callable module for testing."""

        def _module(doc, **kwargs):
            return {"processed": True, "input": doc}

        return _module

    def test_forward_denied_raises_permission_error(self):
        dspy_mod = mod.OWASPDSPyGovernanceModule(
            filter_instance=mod.OWASPAgenticDataLeakageFilter(),
            module=self._make_module(),
        )
        with pytest.raises(PermissionError):
            dspy_mod.forward({"agent_output": True, "dlp_scan_passed": False})

    def test_forward_permitted_delegates_to_module(self):
        dspy_mod = mod.OWASPDSPyGovernanceModule(
            filter_instance=mod.OWASPAgenticDataLeakageFilter(),
            module=self._make_module(),
        )
        doc = {"safe": True}
        result = dspy_mod.forward(doc)
        assert result["processed"] is True
        assert result["input"] == doc

    def test_forward_permission_error_contains_regulation(self):
        dspy_mod = mod.OWASPDSPyGovernanceModule(
            filter_instance=mod.OWASPAgenticDataLeakageFilter(),
            module=self._make_module(),
        )
        with pytest.raises(PermissionError) as exc:
            dspy_mod.forward({"agent_output": True, "dlp_scan_passed": False})
        assert "ASI03" in str(exc.value)


# ===========================================================================
# TestOWASPMAFPolicyMiddleware — MAF wrapper
# ===========================================================================


class TestOWASPMAFPolicyMiddleware:
    """MAF middleware enforces OWASP Agentic governance via process()."""

    def _next(self, message):
        return {"forwarded": True, "message": message}

    def test_process_denied_raises_permission_error(self):
        middleware = mod.OWASPMAFPolicyMiddleware(filter_instance=mod.OWASPAgenticGovernanceFilter())
        with pytest.raises(PermissionError):
            middleware.process(
                {"multi_agent_message": True, "sender_verified": False},
                self._next,
            )

    def test_process_permitted_calls_next_handler(self):
        middleware = mod.OWASPMAFPolicyMiddleware(filter_instance=mod.OWASPAgenticGovernanceFilter())
        doc = {}
        result = middleware.process(doc, self._next)
        assert result["forwarded"] is True
        assert result["message"] == doc

    def test_process_permission_error_contains_asi10(self):
        middleware = mod.OWASPMAFPolicyMiddleware(filter_instance=mod.OWASPAgenticGovernanceFilter())
        with pytest.raises(PermissionError) as exc:
            middleware.process(
                {"multi_agent_message": True, "sender_verified": False},
                self._next,
            )
        assert "ASI10" in str(exc.value)


# ===========================================================================
# TestCrossFilterEdgeCases — boundary conditions and None values
# ===========================================================================


class TestCrossFilterEdgeCases:
    """Edge cases across all four filters."""

    def test_injection_filter_none_anomaly_score_permitted(self):
        r = mod.OWASPAgenticInjectionFilter().filter({"anomaly_score": None})
        # None should not trigger anomaly check (not > 0.7)
        assert r.decision == "PERMITTED"

    def test_data_leakage_none_confidence_score_permitted(self):
        r = mod.OWASPAgenticDataLeakageFilter().filter({"confidence_score": None})
        # None should not trigger confidence check (not < 0.6)
        assert r.decision == "PERMITTED"

    def test_injection_filter_empty_dict_permitted(self):
        r = mod.OWASPAgenticInjectionFilter().filter({})
        assert r.decision == "PERMITTED"

    def test_tool_safety_filter_empty_dict_permitted(self):
        r = mod.OWASPAgenticToolSafetyFilter().filter({})
        assert r.decision == "PERMITTED"

    def test_data_leakage_filter_empty_dict_permitted(self):
        r = mod.OWASPAgenticDataLeakageFilter().filter({})
        assert r.decision == "PERMITTED"

    def test_governance_filter_empty_dict_permitted(self):
        r = mod.OWASPAgenticGovernanceFilter().filter({})
        assert r.decision == "PERMITTED"

    def test_injection_filter_result_is_not_denied_for_rhr(self):
        r = mod.OWASPAgenticInjectionFilter().filter({"anomaly_score": 0.9})
        assert r.decision == "REQUIRES_HUMAN_REVIEW"
        assert not r.is_denied

    def test_governance_filter_result_is_not_denied_for_rhr(self):
        r = mod.OWASPAgenticGovernanceFilter().filter({"action_impact": "high", "human_in_loop": False})
        assert r.decision == "REQUIRES_HUMAN_REVIEW"
        assert not r.is_denied

    def test_all_filters_are_frozen_dataclasses(self):
        """Filters must be frozen=True (immutable)."""
        f1 = mod.OWASPAgenticInjectionFilter()
        f2 = mod.OWASPAgenticToolSafetyFilter()
        f3 = mod.OWASPAgenticDataLeakageFilter()
        f4 = mod.OWASPAgenticGovernanceFilter()
        import dataclasses

        for f in (f1, f2, f3, f4):
            assert dataclasses.is_dataclass(f)

    def test_filter_name_constants_present(self):
        assert mod.OWASPAgenticInjectionFilter.FILTER_NAME == "OWASP_AGENTIC_INJECTION_FILTER"
        assert mod.OWASPAgenticToolSafetyFilter.FILTER_NAME == "OWASP_AGENTIC_TOOL_SAFETY_FILTER"
        assert mod.OWASPAgenticDataLeakageFilter.FILTER_NAME == "OWASP_AGENTIC_DATA_LEAKAGE_FILTER"
        assert mod.OWASPAgenticGovernanceFilter.FILTER_NAME == "OWASP_AGENTIC_GOVERNANCE_FILTER"
