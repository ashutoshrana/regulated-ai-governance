"""Regression checks for audit snapshots and action/sink failure boundaries."""

import json
from dataclasses import FrozenInstanceError

import pytest

from regulated_ai_governance.agent_guard import AuditDeliveryError, GovernedActionGuard
from regulated_ai_governance.audit import GovernanceAuditRecord
from regulated_ai_governance.policy import ActionPolicy


def test_record_is_a_deep_snapshot_and_exports_are_independent():
    context = {"nested": {"ids": ["original"]}}
    record = GovernanceAuditRecord("example", "actor", "read", True, context=context)
    context["nested"]["ids"].append("changed")
    with pytest.raises(FrozenInstanceError):
        record.permitted = False
    with pytest.raises(TypeError):
        record.context["nested"]["new"] = True
    entry = record.to_log_entry()
    entry["ctx_nested"]["ids"].append("export-mutated")
    assert record.to_log_entry()["ctx_nested"] == {"ids": ["original"]}
    json.dumps(record.to_log_entry(), allow_nan=False)


@pytest.mark.parametrize("value", [float("nan"), float("inf"), object(), {1: "bad key"}])
def test_invalid_context_is_rejected(value):
    with pytest.raises(TypeError):
        GovernanceAuditRecord("example", "actor", "read", True, context={"value": value})


def test_required_audit_needs_a_sink():
    with pytest.raises(ValueError):
        GovernedActionGuard(ActionPolicy(), require_audit=True)


def test_preexecution_sink_failure_never_invokes_action():
    calls = []

    def unavailable(record):
        raise OSError("store unavailable")

    guard = GovernedActionGuard(ActionPolicy(allowed_actions={"write"}), audit_sink=unavailable, require_audit=True)
    with pytest.raises(AuditDeliveryError) as error:
        guard.guard("write", lambda: calls.append("executed"))
    assert error.value.action_executed is False
    assert calls == []


def test_outcome_events_are_correlated_and_preserve_action_errors():
    events = []
    guard = GovernedActionGuard(
        ActionPolicy(allowed_actions={"write"}),
        audit_sink=events.append,
        require_audit=True,
        audit_execution=True,
        raise_on_deny=True,
    )
    assert guard.guard("write", lambda: 42) == 42
    assert [event.event_type for event in events] == ["decision", "execution"]
    assert events[0].correlation_id == events[1].correlation_id
    assert events[1].outcome == "succeeded"
    with pytest.raises(PermissionError):
        guard.guard("delete", lambda: pytest.fail("denied action ran"))
    assert events[-1].event_type == "decision"
    assert not events[-1].permitted

    def broken_action():
        raise ValueError("action failed")

    with pytest.raises(ValueError, match="action failed"):
        guard.guard("write", broken_action)
    assert events[-1].outcome == "failed"


def test_postexecution_sink_failure_reports_side_effect_may_have_happened():
    calls = []

    def sink(record):
        if record.event_type == "execution":
            raise OSError("lost connection")

    guard = GovernedActionGuard(ActionPolicy(allowed_actions={"write"}), audit_sink=sink, audit_execution=True)
    with pytest.raises(AuditDeliveryError) as error:
        guard.guard("write", lambda: calls.append("executed"))
    assert error.value.action_executed is True
    assert calls == ["executed"]


def test_execution_audit_does_not_claim_async_completion():
    events = []
    guard = GovernedActionGuard(ActionPolicy(allowed_actions={"write"}), audit_sink=events.append, audit_execution=True)

    async def async_action():
        return 1

    with pytest.raises(TypeError, match="synchronous callable"):
        guard.guard("write", async_action)
    assert events == []
    with pytest.raises(TypeError, match="synchronous result"):
        guard.guard("write", lambda: async_action())
    assert events[-1].outcome == "failed"


def test_async_sinks_cannot_bypass_required_auditing():
    async def sink(record):
        pytest.fail("Unawaited sink should be rejected")

    with pytest.raises(TypeError, match="synchronously"):
        GovernedActionGuard(ActionPolicy(), audit_sink=sink, require_audit=True)
    calls = []
    guard = GovernedActionGuard(
        ActionPolicy(allowed_actions={"write"}), audit_sink=lambda record: sink(record), require_audit=True
    )
    with pytest.raises(AuditDeliveryError) as error:
        guard.guard("write", lambda: calls.append(True))
    assert not error.value.action_executed
    assert not calls


def test_action_context_mutation_cannot_corrupt_execution_record():
    events = []
    context = {"request": ["original"]}
    guard = GovernedActionGuard(ActionPolicy(allowed_actions={"write"}), audit_sink=events.append, audit_execution=True)
    guard.guard("write", lambda: context.update(request=object()), context)
    assert len(events) == 2
    assert events[-1].outcome == "succeeded"
    assert events[0].context == events[1].context
    assert events[-1].to_log_entry()["ctx_request"] == ["original"]
