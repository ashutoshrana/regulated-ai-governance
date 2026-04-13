"""Tests for GovernanceOrchestrator, FrameworkGuard, ComprehensiveAuditReport."""

from __future__ import annotations

import json

from regulated_ai_governance import (
    ActionPolicy,
    ComprehensiveAuditReport,
    FrameworkGuard,
    FrameworkResult,
    GovernanceOrchestrator,
    GovernedActionGuard,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_guard(allowed: set[str], regulation: str, actor: str = "actor") -> FrameworkGuard:
    guard = GovernedActionGuard(
        policy=ActionPolicy(allowed_actions=allowed),
        regulation=regulation,
        actor_id=actor,
    )
    return FrameworkGuard(regulation=regulation, guard=guard)


def _make_orchestrator(guards: list[FrameworkGuard], audit_only: bool = False) -> GovernanceOrchestrator:
    return GovernanceOrchestrator(framework_guards=guards, audit_only=audit_only)


# ---------------------------------------------------------------------------
# FrameworkGuard and FrameworkResult
# ---------------------------------------------------------------------------


class TestFrameworkGuard:
    def test_enabled_by_default(self):
        fg = _make_guard({"read"}, "FERPA")
        assert fg.enabled is True

    def test_can_disable(self):
        fg = _make_guard({"read"}, "FERPA")
        fg.enabled = False
        assert fg.enabled is False


class TestFrameworkResult:
    def test_to_dict_keys(self):
        result = FrameworkResult(regulation="FERPA", permitted=True)
        d = result.to_dict()
        assert d["regulation"] == "FERPA"
        assert d["permitted"] is True
        assert d["denial_reason"] is None
        assert d["escalation_target"] is None
        assert d["skipped"] is False

    def test_to_dict_denied_with_reason(self):
        result = FrameworkResult(
            regulation="HIPAA",
            permitted=False,
            denial_reason="PHI access denied",
            skipped=False,
        )
        d = result.to_dict()
        assert d["permitted"] is False
        assert d["denial_reason"] == "PHI access denied"


# ---------------------------------------------------------------------------
# GovernanceOrchestrator — evaluate()
# ---------------------------------------------------------------------------


class TestOrchestratorEvaluate:
    def test_single_framework_permit(self):
        orch = _make_orchestrator([_make_guard({"read_transcript"}, "FERPA")])
        decision = orch.evaluate("read_transcript")
        assert decision.overall_permitted is True
        assert decision.denial_frameworks == []

    def test_single_framework_deny(self):
        # non-empty whitelist: only "read_transcript" allowed → "delete_record" denied
        orch = _make_orchestrator([_make_guard({"read_transcript"}, "FERPA")])
        decision = orch.evaluate("delete_record")
        assert decision.overall_permitted is False
        assert "FERPA" in decision.denial_frameworks

    def test_multi_framework_all_permit(self):
        orch = _make_orchestrator([
            _make_guard({"read_transcript"}, "FERPA"),
            _make_guard({"read_transcript"}, "HIPAA"),
        ])
        decision = orch.evaluate("read_transcript")
        assert decision.overall_permitted is True

    def test_multi_framework_one_denies(self):
        """Deny-all: one deny means overall deny."""
        orch = _make_orchestrator([
            _make_guard({"read_transcript"}, "FERPA"),
            _make_guard({"other_action"}, "HIPAA"),  # HIPAA whitelist excludes read_transcript
        ])
        decision = orch.evaluate("read_transcript")
        assert decision.overall_permitted is False
        assert "HIPAA" in decision.denial_frameworks
        assert "FERPA" not in decision.denial_frameworks

    def test_skipped_framework_not_in_deny(self):
        fg = _make_guard({"other_action"}, "HIPAA")  # HIPAA would deny "read"
        fg.enabled = False
        orch = _make_orchestrator([_make_guard({"read"}, "FERPA"), fg])
        decision = orch.evaluate("read")
        assert decision.overall_permitted is True
        assert "HIPAA" not in decision.denial_frameworks

    def test_denial_reasons_populated(self):
        # non-empty whitelist: "allowed_only" → anything else is denied
        orch = _make_orchestrator([_make_guard({"allowed_only"}, "FERPA")])
        decision = orch.evaluate("forbidden_action")
        assert len(decision.denial_reasons) > 0
        assert "FERPA" in decision.denial_reasons[0]

    def test_framework_results_keys(self):
        orch = _make_orchestrator([
            _make_guard({"x"}, "FERPA"),
            _make_guard({"x"}, "HIPAA"),
        ])
        decision = orch.evaluate("x")
        assert "FERPA" in decision.framework_results
        assert "HIPAA" in decision.framework_results


# ---------------------------------------------------------------------------
# GovernanceOrchestrator — guard()
# ---------------------------------------------------------------------------


class TestOrchestratorGuard:
    def test_guard_executes_fn_when_permitted(self):
        orch = _make_orchestrator([_make_guard({"read"}, "FERPA")])
        result = orch.guard("read", execute_fn=lambda: "DATA")
        assert result == "DATA"

    def test_guard_blocks_when_denied(self):
        # Whitelist only "other_action" — "read" is denied
        orch = _make_orchestrator([_make_guard({"other_action"}, "FERPA")])
        result = orch.guard("read", execute_fn=lambda: "DATA")
        assert isinstance(result, str)
        assert "BLOCKED" in result
        assert "FERPA" in result

    def test_guard_audit_only_always_executes(self):
        orch = _make_orchestrator([_make_guard(set(), "FERPA")], audit_only=True)
        result = orch.guard("forbidden", execute_fn=lambda: "EXECUTED")
        assert result == "EXECUTED"

    def test_guard_emits_report_to_sink(self):
        log: list[ComprehensiveAuditReport] = []
        fg = _make_guard({"read"}, "FERPA")
        orch = GovernanceOrchestrator(framework_guards=[fg], audit_sink=log.append)
        orch.guard("read", execute_fn=lambda: None)
        assert len(log) == 1
        assert log[0].action_name == "read"

    def test_last_report_updated_after_guard(self):
        orch = _make_orchestrator([_make_guard({"x"}, "FERPA")])
        assert orch.last_report is None
        orch.guard("x", execute_fn=lambda: None)
        assert orch.last_report is not None
        assert orch.last_report.action_name == "x"

    def test_guard_forwards_kwargs_to_execute_fn(self):
        orch = _make_orchestrator([_make_guard({"compute"}, "TEST")])
        result = orch.guard("compute", execute_fn=lambda **kw: kw, key="value")
        assert result == {"key": "value"}


# ---------------------------------------------------------------------------
# ComprehensiveAuditReport
# ---------------------------------------------------------------------------


class TestComprehensiveAuditReport:
    def _make_report(self, permitted: bool = True) -> ComprehensiveAuditReport:
        log: list[ComprehensiveAuditReport] = []
        orch = GovernanceOrchestrator(
            framework_guards=[_make_guard({"ok"}, "FERPA"), _make_guard({"ok"}, "HIPAA")],
            audit_sink=log.append,
        )
        action = "ok" if permitted else "bad"
        orch.guard(action, execute_fn=lambda: None)
        return log[0]

    def test_to_log_entry_is_valid_json(self):
        report = self._make_report()
        entry = report.to_log_entry()
        parsed = json.loads(entry)
        assert parsed["event"] == "multi_framework_governance_evaluation"

    def test_to_log_entry_contains_required_fields(self):
        report = self._make_report()
        parsed = json.loads(report.to_log_entry())
        for key in ("report_id", "action_name", "actor_id", "overall_permitted",
                    "frameworks_evaluated", "frameworks_permitted", "frameworks_denied",
                    "timestamp_utc"):
            assert key in parsed, f"Missing field: {key}"

    def test_content_hash_is_stable(self):
        orch = GovernanceOrchestrator(framework_guards=[_make_guard({"x"}, "FERPA")])
        orch.guard("x", execute_fn=lambda: None)
        report = orch.last_report
        assert report is not None
        h1 = report.content_hash()
        h2 = report.content_hash()
        assert h1 == h2

    def test_content_hash_is_hex_string(self):
        orch = GovernanceOrchestrator(framework_guards=[_make_guard({"x"}, "FERPA")])
        orch.guard("x", execute_fn=lambda: None)
        h = orch.last_report.content_hash()
        assert len(h) == 64
        int(h, 16)  # raises if not hex

    def test_to_compliance_summary_contains_action(self):
        report = self._make_report(permitted=True)
        summary = report.to_compliance_summary()
        assert "ok" in summary
        assert "PERMITTED" in summary

    def test_to_compliance_summary_denied_shows_deny(self):
        report = self._make_report(permitted=False)
        summary = report.to_compliance_summary()
        assert "DENIED" in summary

    def test_audit_only_mode_field(self):
        orch = GovernanceOrchestrator(
            framework_guards=[_make_guard(set(), "FERPA")],
            audit_only=True,
        )
        log: list[ComprehensiveAuditReport] = []
        orch._audit_sink = log.append
        orch.guard("forbidden", execute_fn=lambda: None)
        assert log[0].audit_only_mode is True

    def test_frameworks_evaluated_lists_all(self):
        log: list[ComprehensiveAuditReport] = []
        orch = GovernanceOrchestrator(
            framework_guards=[_make_guard({"x"}, "FERPA"), _make_guard({"x"}, "ISO_27001")],
            audit_sink=log.append,
        )
        orch.guard("x", execute_fn=lambda: None)
        assert set(log[0].frameworks_evaluated) == {"FERPA", "ISO_27001"}


# ---------------------------------------------------------------------------
# GovernanceOrchestrator — add/remove/enable/disable
# ---------------------------------------------------------------------------


class TestOrchestratorMutability:
    def test_add_framework(self):
        orch = _make_orchestrator([_make_guard({"x"}, "FERPA")])
        orch.add_framework(_make_guard({"x"}, "HIPAA"))
        assert "HIPAA" in orch.configured_regulations

    def test_remove_framework_returns_true(self):
        orch = _make_orchestrator([_make_guard({"x"}, "FERPA"), _make_guard({"x"}, "HIPAA")])
        removed = orch.remove_framework("HIPAA")
        assert removed is True
        assert "HIPAA" not in orch.configured_regulations

    def test_remove_nonexistent_returns_false(self):
        orch = _make_orchestrator([_make_guard({"x"}, "FERPA")])
        assert orch.remove_framework("GDPR") is False

    def test_disable_enable_framework(self):
        orch = _make_orchestrator([_make_guard({"only_this"}, "FERPA")])
        # deny before disable — "other_action" not in whitelist
        assert orch.evaluate("other_action").overall_permitted is False
        orch.disable_framework("FERPA")
        assert orch.evaluate("other_action").overall_permitted is True
        orch.enable_framework("FERPA")
        assert orch.evaluate("other_action").overall_permitted is False

    def test_active_regulations_excludes_disabled(self):
        orch = _make_orchestrator([
            _make_guard({"x"}, "FERPA"),
            _make_guard({"x"}, "HIPAA"),
        ])
        orch.disable_framework("HIPAA")
        assert "FERPA" in orch.active_regulations
        assert "HIPAA" not in orch.active_regulations

    def test_configured_regulations_includes_disabled(self):
        orch = _make_orchestrator([
            _make_guard({"x"}, "FERPA"),
            _make_guard({"x"}, "HIPAA"),
        ])
        orch.disable_framework("HIPAA")
        assert "HIPAA" in orch.configured_regulations
