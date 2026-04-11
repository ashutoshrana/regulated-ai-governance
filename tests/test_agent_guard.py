"""Tests for GovernedActionGuard."""

from __future__ import annotations

from typing import Any

import pytest

from regulated_ai_governance.agent_guard import GovernedActionGuard
from regulated_ai_governance.audit import GovernanceAuditRecord
from regulated_ai_governance.policy import ActionPolicy, EscalationRule


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_policy(**kwargs: Any) -> ActionPolicy:
    return ActionPolicy(**kwargs)


def _echo(value: str = "hello") -> str:
    return f"echo:{value}"


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestGovernedActionGuardEvaluate:
    def test_permits_allowed_action(self):
        guard = GovernedActionGuard(
            policy=ActionPolicy(allowed_actions={"read_record"}),
        )
        decision = guard.evaluate("read_record")
        assert decision.permitted is True
        assert decision.denial_reason is None

    def test_denies_unlisted_action(self):
        guard = GovernedActionGuard(
            policy=ActionPolicy(allowed_actions={"read_record"}),
        )
        decision = guard.evaluate("export_record")
        assert decision.permitted is False
        assert "export_record" in decision.denial_reason

    def test_denies_explicitly_denied_action(self):
        guard = GovernedActionGuard(
            policy=ActionPolicy(
                allowed_actions={"read_record", "export_record"},
                denied_actions={"export_record"},
            ),
        )
        decision = guard.evaluate("export_record")
        assert decision.permitted is False

    def test_escalation_blocks_when_block_on_escalation_true(self):
        rule = EscalationRule("export_attempt", "export", "compliance")
        guard = GovernedActionGuard(
            policy=ActionPolicy(
                allowed_actions={"export_records"},
                escalation_rules=[rule],
            ),
            block_on_escalation=True,
        )
        decision = guard.evaluate("export_records")
        assert decision.permitted is False
        assert "compliance" in decision.denial_reason
        assert decision.escalation is not None

    def test_escalation_does_not_block_when_block_on_escalation_false(self):
        rule = EscalationRule("export_attempt", "export", "compliance")
        guard = GovernedActionGuard(
            policy=ActionPolicy(
                allowed_actions={"export_records"},
                escalation_rules=[rule],
            ),
            block_on_escalation=False,
        )
        decision = guard.evaluate("export_records")
        assert decision.permitted is True
        assert decision.escalation is not None


class TestGovernedActionGuardExecution:
    def test_executes_permitted_action(self):
        guard = GovernedActionGuard(
            policy=ActionPolicy(allowed_actions={"echo"}),
        )
        result = guard.guard("echo", _echo, value="world")
        assert result == "echo:world"

    def test_blocked_action_returns_error_string_by_default(self):
        guard = GovernedActionGuard(
            policy=ActionPolicy(allowed_actions={"read_record"}),
        )
        result = guard.guard("export_record", _echo)
        assert "BLOCKED" in result
        assert "export_record" in result

    def test_blocked_action_raises_on_raise_on_deny_true(self):
        guard = GovernedActionGuard(
            policy=ActionPolicy(allowed_actions={"read_record"}),
            raise_on_deny=True,
        )
        with pytest.raises(PermissionError) as exc_info:
            guard.guard("export_record", _echo)
        assert "export_record" in str(exc_info.value)

    def test_open_policy_permits_any_action(self):
        guard = GovernedActionGuard(
            policy=ActionPolicy(allowed_actions=set()),
        )
        result = guard.guard("anything", _echo, value="open")
        assert result == "echo:open"


class TestGovernedActionGuardAudit:
    def test_audit_sink_called_on_permitted_action(self):
        audit_log: list[GovernanceAuditRecord] = []
        guard = GovernedActionGuard(
            policy=ActionPolicy(allowed_actions={"read_record"}),
            regulation="FERPA",
            actor_id="stu-alice",
            audit_sink=audit_log.append,
        )
        guard.guard("read_record", _echo)
        assert len(audit_log) == 1
        record = audit_log[0]
        assert record.permitted is True
        assert record.regulation == "FERPA"
        assert record.actor_id == "stu-alice"
        assert record.action_name == "read_record"

    def test_audit_sink_called_on_denied_action(self):
        audit_log: list[GovernanceAuditRecord] = []
        guard = GovernedActionGuard(
            policy=ActionPolicy(allowed_actions={"read_record"}),
            audit_sink=audit_log.append,
        )
        guard.guard("export_records", _echo)
        assert len(audit_log) == 1
        assert audit_log[0].permitted is False
        assert audit_log[0].denial_reason is not None

    def test_audit_record_captures_escalation_target(self):
        audit_log: list[GovernanceAuditRecord] = []
        rule = EscalationRule("export_attempt", "export", "compliance_officer")
        guard = GovernedActionGuard(
            policy=ActionPolicy(
                allowed_actions={"export_records"},
                escalation_rules=[rule],
            ),
            block_on_escalation=True,
            audit_sink=audit_log.append,
        )
        guard.guard("export_records", _echo)
        assert audit_log[0].escalation_target == "compliance_officer"

    def test_audit_regulation_label_in_record(self):
        audit_log: list[GovernanceAuditRecord] = []
        guard = GovernedActionGuard(
            policy=ActionPolicy(allowed_actions=set()),
            regulation="HIPAA",
            audit_sink=audit_log.append,
        )
        guard.guard("read_phi", _echo)
        assert audit_log[0].regulation == "HIPAA"
