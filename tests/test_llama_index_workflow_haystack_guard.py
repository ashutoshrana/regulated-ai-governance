"""
Tests for v0.4.1 additions:
  - PolicyWorkflowGuard  (integrations/llama_index.py)
  - PolicyWorkflowEvent  (integrations/llama_index.py)
  - make_haystack_policy_guard  (integrations/haystack.py)

All framework SDKs stubbed via sys.modules. Async tests use asyncio.run().
"""

from __future__ import annotations

import asyncio
import sys
from typing import Any
from unittest.mock import MagicMock

import pytest

from regulated_ai_governance.policy import ActionPolicy

# ---------------------------------------------------------------------------
# Stub framework modules before importing integration classes
# ---------------------------------------------------------------------------

for _mod in (
    "llama_index",
    "llama_index.core",
    "llama_index.core.workflow",
    "haystack",
    "haystack.core",
    "haystack.core.component",
):
    sys.modules.setdefault(_mod, MagicMock())

# Haystack @component stub: identity decorator that returns class unchanged
_hs = sys.modules["haystack"]


def _component_decorator(cls: type) -> type:
    """Identity @component decorator stub."""
    cls.output_types = lambda **kw: lambda fn: fn
    return cls


_component_decorator.output_types = lambda **kw: lambda fn: fn  # type: ignore[attr-defined]
_hs.component = _component_decorator  # type: ignore[assignment]

from regulated_ai_governance.integrations.haystack import (  # noqa: E402
    make_haystack_policy_guard,
)
from regulated_ai_governance.integrations.llama_index import (  # noqa: E402
    PolicyWorkflowEvent,
    PolicyWorkflowGuard,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _allow_policy(*actions: str) -> ActionPolicy:
    """Policy permitting exactly the listed actions."""
    return ActionPolicy(allowed_actions=set(actions), require_all_allowed=True)


def _deny_policy(*actions: str) -> ActionPolicy:
    """Policy that explicitly denies the listed actions (or all if using denied_actions)."""
    return ActionPolicy(denied_actions=set(actions) or {"__all__"})


class _FakeDoc:
    """Generic stub document."""

    def __init__(self, content: str = "text") -> None:
        self.content = content
        self.metadata: dict[str, Any] = {}


# ---------------------------------------------------------------------------
# PolicyWorkflowEvent
# ---------------------------------------------------------------------------


class TestPolicyWorkflowEvent:
    def test_minimal_construction(self) -> None:
        docs = [_FakeDoc()]
        event = PolicyWorkflowEvent(documents=docs)
        assert event.documents is docs
        assert event.query == ""
        assert event.action_name == "workflow_step"

    def test_full_construction(self) -> None:
        docs = [_FakeDoc()]
        event = PolicyWorkflowEvent(documents=docs, query="What is my GPA?", action_name="read_grades")
        assert event.query == "What is my GPA?"
        assert event.action_name == "read_grades"


# ---------------------------------------------------------------------------
# PolicyWorkflowGuard
# ---------------------------------------------------------------------------


class TestPolicyWorkflowGuard:
    def test_construction(self) -> None:
        guard = PolicyWorkflowGuard(
            policy=_allow_policy("workflow_step"),
            regulation="FERPA",
            actor_id="stu-alice",
        )
        assert guard._guard is not None

    def test_permits_allowed_action(self) -> None:
        guard = PolicyWorkflowGuard(
            policy=_allow_policy("retrieve_docs"),
            regulation="FERPA",
            actor_id="stu-alice",
        )
        docs = [_FakeDoc(), _FakeDoc()]
        event = PolicyWorkflowEvent(documents=docs, action_name="retrieve_docs")
        result = asyncio.run(guard(event))
        assert result is event
        assert result.documents == docs

    def test_blocks_denied_action(self) -> None:
        guard = PolicyWorkflowGuard(
            policy=_deny_policy("export_grades"),
            regulation="FERPA",
            actor_id="stu-alice",
        )
        event = PolicyWorkflowEvent(documents=[_FakeDoc()], action_name="export_grades")
        with pytest.raises(PermissionError):
            asyncio.run(guard(event))

    def test_empty_documents_permitted(self) -> None:
        guard = PolicyWorkflowGuard(
            policy=_allow_policy("workflow_step"),
            regulation="FERPA",
            actor_id="stu-alice",
        )
        event = PolicyWorkflowEvent(documents=[])
        result = asyncio.run(guard(event))
        assert result.documents == []

    def test_audit_sink_receives_record(self) -> None:
        audit_log: list[Any] = []
        guard = PolicyWorkflowGuard(
            policy=_allow_policy("read_docs"),
            regulation="FERPA",
            actor_id="stu-alice",
            audit_sink=audit_log.append,
        )
        event = PolicyWorkflowEvent(documents=[_FakeDoc()], action_name="read_docs")
        asyncio.run(guard(event))
        assert len(audit_log) == 1

    def test_documents_unchanged_after_permit(self) -> None:
        guard = PolicyWorkflowGuard(
            policy=_allow_policy("summarize"),
            regulation="HIPAA",
            actor_id="clinician-bob",
        )
        docs = [_FakeDoc("patient note")]
        event = PolicyWorkflowEvent(documents=docs, query="summarize", action_name="summarize")
        result = asyncio.run(guard(event))
        assert result.documents[0].content == "patient note"

    def test_custom_regulation_label(self) -> None:
        audit_log: list[Any] = []
        guard = PolicyWorkflowGuard(
            policy=_allow_policy("step"),
            regulation="HIPAA",
            actor_id="nurse-carol",
            audit_sink=audit_log.append,
        )
        event = PolicyWorkflowEvent(documents=[], action_name="step")
        asyncio.run(guard(event))
        record = audit_log[0]
        assert record.regulation == "HIPAA"


# ---------------------------------------------------------------------------
# make_haystack_policy_guard
# ---------------------------------------------------------------------------


class TestMakeHaystackPolicyGuard:
    def test_returns_class(self) -> None:
        GuardClass = make_haystack_policy_guard(
            policy=_allow_policy("haystack_pipeline_step"),
            regulation="FERPA",
            actor_id="stu-alice",
        )
        assert isinstance(GuardClass, type)

    def test_instance_run_permitted(self) -> None:
        GuardClass = make_haystack_policy_guard(
            policy=_allow_policy("haystack_pipeline_step"),
            regulation="FERPA",
            actor_id="stu-alice",
        )
        guard = GuardClass()
        docs = [_FakeDoc(), _FakeDoc()]
        result = guard.run(documents=docs, query="GPA?")
        assert "documents" in result
        assert result["documents"] == docs

    def test_instance_run_denied(self) -> None:
        GuardClass = make_haystack_policy_guard(
            policy=_deny_policy("export_transcript"),
            regulation="FERPA",
            actor_id="stu-alice",
            action_name="export_transcript",
        )
        guard = GuardClass()
        with pytest.raises(PermissionError):
            guard.run(documents=[_FakeDoc()], query="export grades")

    def test_empty_documents_permitted(self) -> None:
        GuardClass = make_haystack_policy_guard(
            policy=_allow_policy("haystack_pipeline_step"),
            regulation="GLBA",
            actor_id="advisor-dan",
        )
        guard = GuardClass()
        result = guard.run(documents=[], query="")
        assert result["documents"] == []

    def test_audit_sink_called(self) -> None:
        audit_log: list[Any] = []
        GuardClass = make_haystack_policy_guard(
            policy=_allow_policy("retrieve"),
            regulation="FERPA",
            actor_id="stu-alice",
            action_name="retrieve",
            audit_sink=audit_log.append,
        )
        guard = GuardClass()
        guard.run(documents=[_FakeDoc()], query="courses")
        assert len(audit_log) == 1

    def test_custom_action_name(self) -> None:
        GuardClass = make_haystack_policy_guard(
            policy=_allow_policy("custom_step"),
            regulation="HIPAA",
            actor_id="doctor-eve",
            action_name="custom_step",
        )
        guard = GuardClass()
        result = guard.run(documents=[_FakeDoc()])
        assert "documents" in result

    def test_documents_returned_unchanged(self) -> None:
        GuardClass = make_haystack_policy_guard(
            policy=_allow_policy("haystack_pipeline_step"),
            regulation="FERPA",
            actor_id="stu-alice",
        )
        guard = GuardClass()
        docs = [_FakeDoc("note A"), _FakeDoc("note B")]
        result = guard.run(documents=docs)
        contents = [d.content for d in result["documents"]]
        assert contents == ["note A", "note B"]
