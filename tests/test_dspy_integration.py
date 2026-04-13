"""Tests for GovernedDSPyModule and GovernedDSPyPipeline."""

from __future__ import annotations

from typing import Any

import pytest

from regulated_ai_governance.audit import GovernanceAuditRecord
from regulated_ai_governance.integrations.dspy import GovernedDSPyModule, GovernedDSPyPipeline
from regulated_ai_governance.policy import ActionPolicy, EscalationRule

# ---------------------------------------------------------------------------
# Fake DSPy-like module stubs (no dspy dependency required)
# ---------------------------------------------------------------------------


class FakePredict:
    """Minimal stub that mimics dspy.Module's __call__ / forward contract."""

    def __init__(self, return_value: Any = "predicted") -> None:
        self._return = return_value

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self._return

    def predictors(self) -> list[Any]:
        return [self]

    def parameters(self) -> list[Any]:
        return []


class FakeRetrieve:
    def __init__(self, passages: list[str] | None = None) -> None:
        self._passages = passages or ["doc-1", "doc-2"]

    def __call__(self, query: str = "") -> dict[str, Any]:
        return {"passages": self._passages, "query": query}

    def predictors(self) -> list[Any]:
        return []


class FakeRaiseModule:
    """Always raises RuntimeError — used to confirm guard blocks before calling."""

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        raise RuntimeError("should not be called")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _policy(allowed: set[str] | None = None) -> ActionPolicy:
    return ActionPolicy(
        allowed_actions=allowed or {"FakePredict", "FakeRetrieve"},
    )


def _governed(
    module: Any,
    *,
    allowed: set[str] | None = None,
    escalation_rules: list[EscalationRule] | None = None,
    actor_id: str = "stu-alice",
    audit_sink: Any = None,
    block_on_escalation: bool = True,
    action_name: str | None = None,
) -> GovernedDSPyModule:
    policy = ActionPolicy(
        allowed_actions=allowed or {type(module).__name__},
        escalation_rules=escalation_rules or [],
    )
    return GovernedDSPyModule(
        wrapped_module=module,
        policy=policy,
        regulation="FERPA",
        actor_id=actor_id,
        audit_sink=audit_sink,
        block_on_escalation=block_on_escalation,
        action_name=action_name,
    )


# ===========================================================================
# GovernedDSPyModule — basic invocation
# ===========================================================================


class TestGovernedDSPyModuleBasic:
    def test_call_returns_wrapped_result(self) -> None:
        module = FakePredict("hello world")
        guard = _governed(module)
        assert guard(question="test") == "hello world"

    def test_forward_returns_wrapped_result(self) -> None:
        module = FakePredict("direct-forward")
        guard = _governed(module)
        assert guard.forward(question="test") == "direct-forward"

    def test_call_delegates_to_forward(self) -> None:
        calls: list[str] = []

        class TrackingModule:
            def __call__(self, **kwargs: Any) -> str:
                calls.append("called")
                return "ok"

        guard = _governed(TrackingModule())
        guard(question="q")
        assert calls == ["called"]

    def test_action_name_defaults_to_class_name(self) -> None:
        guard = _governed(FakePredict())
        assert guard._action_name == "FakePredict"

    def test_action_name_override(self) -> None:
        guard = _governed(FakePredict(), action_name="custom_action", allowed={"custom_action"})
        assert guard._action_name == "custom_action"
        result = guard(question="test")
        assert result == "predicted"

    def test_repr_contains_action_name(self) -> None:
        guard = _governed(FakePredict())
        assert "FakePredict" in repr(guard)

    def test_attribute_delegation_to_wrapped(self) -> None:
        module = FakePredict()
        guard = _governed(module)
        # predictors() exists on FakePredict but not on GovernedDSPyModule
        assert guard.predictors() == module.predictors()

    def test_attribute_delegation_parameters(self) -> None:
        module = FakePredict()
        guard = _governed(module)
        assert guard.parameters() == []


# ===========================================================================
# GovernedDSPyModule — policy enforcement
# ===========================================================================


class TestGovernedDSPyModulePolicyEnforcement:
    def test_denied_action_raises_permission_error(self) -> None:
        module = FakeRaiseModule()
        guard = GovernedDSPyModule(
            wrapped_module=module,
            policy=ActionPolicy(allowed_actions={"other_module"}),  # FakeRaiseModule not listed
            regulation="FERPA",
            actor_id="stu-alice",
        )
        with pytest.raises(PermissionError):
            guard(question="test")

    def test_denied_action_does_not_call_wrapped_module(self) -> None:
        module = FakeRaiseModule()
        guard = GovernedDSPyModule(
            wrapped_module=module,
            policy=ActionPolicy(allowed_actions={"other_module"}),
            regulation="FERPA",
            actor_id="stu-alice",
        )
        with pytest.raises(PermissionError):
            guard()
        # If wrapped module had been called, RuntimeError would bubble up instead of PermissionError

    def test_allowed_action_executes_successfully(self) -> None:
        module = FakePredict("ok")
        guard = _governed(module)
        assert guard() == "ok"

    def test_escalation_blocks_when_block_on_escalation_true(self) -> None:
        escalation_rules = [EscalationRule("grade_access", "FakePredict", "registrar")]
        guard = _governed(
            FakePredict(),
            escalation_rules=escalation_rules,
            allowed={"FakePredict"},
            block_on_escalation=True,
        )
        with pytest.raises(PermissionError):
            guard(question="test")

    def test_escalation_allows_when_block_on_escalation_false(self) -> None:
        escalation_rules = [EscalationRule("grade_access", "FakePredict", "registrar")]
        guard = _governed(
            FakePredict("escalated-result"),
            escalation_rules=escalation_rules,
            allowed={"FakePredict"},
            block_on_escalation=False,
        )
        result = guard(question="test")
        assert result == "escalated-result"


# ===========================================================================
# GovernedDSPyModule — audit logging
# ===========================================================================


class TestGovernedDSPyModuleAuditLogging:
    def test_audit_sink_called_on_permitted_action(self) -> None:
        records: list[GovernanceAuditRecord] = []
        guard = _governed(FakePredict(), audit_sink=records.append)
        guard(question="test")
        assert len(records) == 1
        assert isinstance(records[0], GovernanceAuditRecord)

    def test_audit_record_action_name(self) -> None:
        records: list[GovernanceAuditRecord] = []
        guard = _governed(FakePredict(), audit_sink=records.append)
        guard(question="test")
        assert records[0].action_name == "FakePredict"

    def test_audit_record_actor_id(self) -> None:
        records: list[GovernanceAuditRecord] = []
        guard = _governed(FakePredict(), actor_id="stu-bob", audit_sink=records.append)
        guard()
        assert records[0].actor_id == "stu-bob"

    def test_audit_sink_called_on_denial(self) -> None:
        records: list[GovernanceAuditRecord] = []
        guard = GovernedDSPyModule(
            wrapped_module=FakePredict(),
            policy=ActionPolicy(allowed_actions={"other_module"}),  # FakePredict not listed
            regulation="FERPA",
            actor_id="stu-alice",
            audit_sink=records.append,
        )
        with pytest.raises(PermissionError):
            guard()
        assert len(records) == 1
        assert records[0].permitted is False

    def test_audit_record_regulation(self) -> None:
        records: list[GovernanceAuditRecord] = []
        guard = GovernedDSPyModule(
            wrapped_module=FakePredict(),
            policy=ActionPolicy(allowed_actions={"FakePredict"}),
            regulation="HIPAA",
            actor_id="nurse-1",
            audit_sink=records.append,
        )
        guard()
        assert records[0].regulation == "HIPAA"

    def test_no_sink_does_not_raise(self) -> None:
        guard = _governed(FakePredict(), audit_sink=None)
        guard(question="test")  # must not raise

    def test_context_included_in_audit(self) -> None:
        records: list[GovernanceAuditRecord] = []
        guard = GovernedDSPyModule(
            wrapped_module=FakePredict(),
            policy=ActionPolicy(allowed_actions={"FakePredict"}),
            regulation="FERPA",
            actor_id="stu-alice",
            audit_sink=records.append,
            context={"session_id": "sess-xyz"},
        )
        guard()
        ctx = records[0].context or {}
        assert ctx.get("session_id") == "sess-xyz"


# ===========================================================================
# GovernedDSPyPipeline
# ===========================================================================


class TestGovernedDSPyPipeline:
    def test_pipeline_executes_single_step(self) -> None:
        pipeline = GovernedDSPyPipeline(
            modules=[FakePredict("step1")],
            policy=ActionPolicy(allowed_actions={"FakePredict"}),
            regulation="FERPA",
            actor_id="stu-alice",
        )
        assert pipeline(question="test") == "step1"

    def test_pipeline_passes_dict_result_as_kwargs(self) -> None:
        received: list[Any] = []

        class CaptureModule:
            def __call__(self, **kwargs: Any) -> str:
                received.append(kwargs)
                return "final"

        pipeline = GovernedDSPyPipeline(
            modules=[FakeRetrieve(["doc-a"]), CaptureModule()],
            policy=ActionPolicy(allowed_actions={"FakeRetrieve", "CaptureModule"}),
            regulation="FERPA",
            actor_id="stu-alice",
        )
        result = pipeline(query="test-query")
        assert result == "final"
        # CaptureModule received the dict output from FakeRetrieve as kwargs
        assert "passages" in received[0]

    def test_pipeline_passes_non_dict_result_as_positional(self) -> None:
        received: list[Any] = []

        class PositionalCapture:
            def __call__(self, arg: Any = None) -> str:
                received.append(arg)
                return "ok"

        pipeline = GovernedDSPyPipeline(
            modules=[FakePredict("scalar-output"), PositionalCapture()],
            policy=ActionPolicy(allowed_actions={"FakePredict", "PositionalCapture"}),
            regulation="FERPA",
            actor_id="stu-alice",
        )
        pipeline(question="test")
        assert received[0] == "scalar-output"

    def test_pipeline_denied_first_step_raises(self) -> None:
        pipeline = GovernedDSPyPipeline(
            modules=[FakePredict(), FakePredict()],
            policy=ActionPolicy(allowed_actions={"other_module"}),  # FakePredict not listed
            regulation="FERPA",
            actor_id="stu-alice",
        )
        with pytest.raises(PermissionError):
            pipeline(question="test")

    def test_pipeline_repr_shows_steps(self) -> None:
        pipeline = GovernedDSPyPipeline(
            modules=[FakeRetrieve(), FakePredict()],
            policy=ActionPolicy(allowed_actions={"FakeRetrieve", "FakePredict"}),
            regulation="FERPA",
            actor_id="stu-alice",
        )
        assert "FakeRetrieve" in repr(pipeline)
        assert "FakePredict" in repr(pipeline)

    def test_pipeline_audit_sink_called_per_step(self) -> None:
        records: list[GovernanceAuditRecord] = []
        pipeline = GovernedDSPyPipeline(
            modules=[FakePredict("step1"), FakePredict("step2")],
            policy=ActionPolicy(allowed_actions={"FakePredict"}),
            regulation="FERPA",
            actor_id="stu-alice",
            audit_sink=records.append,
        )
        pipeline(question="test")
        assert len(records) == 2

    def test_empty_pipeline_returns_none(self) -> None:
        pipeline = GovernedDSPyPipeline(
            modules=[],
            policy=ActionPolicy(allowed_actions=set()),
            regulation="FERPA",
            actor_id="stu-alice",
        )
        result = pipeline(question="test")
        assert result is None
