"""
Tests for framework adapters — CrewAI, AutoGen, Semantic Kernel.

All tests use duck-typed stubs; no real crewai/autogen/semantic-kernel
imports are required to run the suite.
"""
from __future__ import annotations

import logging
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from regulated_ai_governance.adapters.autogen import PolicyEnforcingAgent
from regulated_ai_governance.adapters.crewai import EnterpriseActionGuard, PolicyViolationError
from regulated_ai_governance.adapters.semantic_kernel import PolicyKernelPlugin
from regulated_ai_governance.policy import ActionPolicy


# ---------------------------------------------------------------------------
# Shared stubs
# ---------------------------------------------------------------------------


class _StubCrewAITool:
    """Duck-typed stand-in for a CrewAI BaseTool."""

    def __init__(self, name: str, return_value: Any = "tool_result") -> None:
        self.name = name
        self.description = f"Stub tool: {name}"
        self._return_value = return_value
        self.call_count = 0

    def _run(self, *args: Any, **kwargs: Any) -> Any:
        self.call_count += 1
        return self._return_value


class _StubAutoGenAgent:
    """Duck-typed stand-in for an AutoGen ConversableAgent."""

    def __init__(self, name: str, reply: str = "agent_reply") -> None:
        self.name = name
        self._reply = reply
        self.generate_reply_count = 0

    def generate_reply(self, messages: Any = None, sender: Any = None, **kwargs: Any) -> str:
        self.generate_reply_count += 1
        return self._reply

    def initiate_chat(self, *args: Any, **kwargs: Any) -> str:
        return "chat_started"

    def receive(self, *args: Any, **kwargs: Any) -> str:
        return "received"


def _allow_policy(*actions: str) -> ActionPolicy:
    """Return an ActionPolicy that permits exactly the listed actions."""
    return ActionPolicy(allowed_actions=set(actions), require_all_allowed=True)


def _deny_all_policy() -> ActionPolicy:
    """Return an ActionPolicy that permits nothing (empty allowed set + require_all)."""
    return ActionPolicy(allowed_actions=set(), require_all_allowed=True)


# ---------------------------------------------------------------------------
# Fixture: patch framework imports so tests run without SDKs installed
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _patch_framework_imports():
    """Prevent ImportError when crewai / autogen / semantic-kernel are absent."""
    with (
        patch("regulated_ai_governance.adapters.crewai._import_crewai", return_value=MagicMock()),
        patch("regulated_ai_governance.adapters.autogen._import_autogen", return_value=MagicMock()),
        patch(
            "regulated_ai_governance.adapters.semantic_kernel._import_semantic_kernel",
            return_value=MagicMock(),
        ),
    ):
        yield


# ===========================================================================
# EnterpriseActionGuard (CrewAI adapter)
# ===========================================================================


class TestEnterpriseActionGuard:
    # -----------------------------------------------------------------------
    # Core permit / deny behaviour
    # -----------------------------------------------------------------------

    def test_permitted_action_executes_underlying_tool(self) -> None:
        tool = _StubCrewAITool("read_transcript")
        guard = EnterpriseActionGuard(tool=tool, policy=_allow_policy("read_transcript"))
        result = guard._run()
        assert result == "tool_result"
        assert tool.call_count == 1

    def test_blocked_action_raises_policy_violation_error(self) -> None:
        tool = _StubCrewAITool("export_records")
        guard = EnterpriseActionGuard(tool=tool, policy=_allow_policy("read_transcript"))
        with pytest.raises(PolicyViolationError):
            guard._run()

    def test_blocked_action_does_not_call_underlying_tool(self) -> None:
        tool = _StubCrewAITool("export_records")
        guard = EnterpriseActionGuard(tool=tool, policy=_allow_policy("read_transcript"))
        with pytest.raises(PolicyViolationError):
            guard._run()
        assert tool.call_count == 0

    def test_public_run_delegates_to_private_run(self) -> None:
        tool = _StubCrewAITool("read_transcript")
        guard = EnterpriseActionGuard(tool=tool, policy=_allow_policy("read_transcript"))
        assert guard.run() == guard._run.__func__(guard)  # type: ignore[attr-defined]

    def test_run_method_same_result_as__run(self) -> None:
        tool = _StubCrewAITool("read_transcript", return_value={"data": 42})
        guard = EnterpriseActionGuard(tool=tool, policy=_allow_policy("read_transcript"))
        assert guard.run() == {"data": 42}

    # -----------------------------------------------------------------------
    # PolicyViolationError fields
    # -----------------------------------------------------------------------

    def test_policy_violation_error_has_correct_action_field(self) -> None:
        tool = _StubCrewAITool("export_records")
        guard = EnterpriseActionGuard(
            tool=tool,
            policy=_allow_policy("other"),
            policy_name="test-policy",
        )
        with pytest.raises(PolicyViolationError) as exc_info:
            guard._run()
        assert exc_info.value.action == "export_records"

    def test_policy_violation_error_has_correct_policy_name(self) -> None:
        tool = _StubCrewAITool("export_records")
        guard = EnterpriseActionGuard(
            tool=tool,
            policy=_allow_policy("other"),
            policy_name="my-custom-policy",
        )
        with pytest.raises(PolicyViolationError) as exc_info:
            guard._run()
        assert exc_info.value.policy_name == "my-custom-policy"

    def test_policy_violation_error_has_regulation_citation(self) -> None:
        tool = _StubCrewAITool("export_records")
        guard = EnterpriseActionGuard(
            tool=tool,
            policy=_allow_policy("other"),
            regulation_citation="HIPAA 45 CFR § 164.308(a)(4)",
        )
        with pytest.raises(PolicyViolationError) as exc_info:
            guard._run()
        assert "HIPAA" in exc_info.value.regulation_citation

    def test_policy_violation_error_str_contains_action_and_policy(self) -> None:
        err = PolicyViolationError(
            action="forbidden_action",
            policy_name="strict-policy",
            regulation_citation="FERPA 34 CFR § 99.31(a)(1)",
        )
        text = str(err)
        assert "forbidden_action" in text
        assert "strict-policy" in text
        assert "FERPA" in text

    # -----------------------------------------------------------------------
    # Name / description mirroring
    # -----------------------------------------------------------------------

    def test_guard_mirrors_tool_name(self) -> None:
        tool = _StubCrewAITool("my_special_tool")
        guard = EnterpriseActionGuard(tool=tool, policy=_allow_policy("my_special_tool"))
        assert guard.name == "my_special_tool"

    def test_guard_mirrors_tool_description(self) -> None:
        tool = _StubCrewAITool("read_transcript")
        guard = EnterpriseActionGuard(tool=tool, policy=_allow_policy("read_transcript"))
        assert guard.description == tool.description

    # -----------------------------------------------------------------------
    # Audit logging
    # -----------------------------------------------------------------------

    def test_permitted_action_emits_info_log(self, caplog: pytest.LogCaptureFixture) -> None:
        tool = _StubCrewAITool("read_transcript")
        guard = EnterpriseActionGuard(tool=tool, policy=_allow_policy("read_transcript"))
        with caplog.at_level(logging.INFO, logger="regulated_ai_governance.adapters.crewai"):
            guard._run()
        assert any("permitted=True" in r.message for r in caplog.records)

    def test_blocked_action_emits_warning_log(self, caplog: pytest.LogCaptureFixture) -> None:
        tool = _StubCrewAITool("export_records")
        guard = EnterpriseActionGuard(tool=tool, policy=_allow_policy("read_transcript"))
        with caplog.at_level(logging.WARNING, logger="regulated_ai_governance.adapters.crewai"):
            with pytest.raises(PolicyViolationError):
                guard._run()
        assert any("permitted=False" in r.message for r in caplog.records)

    # -----------------------------------------------------------------------
    # Deny-list policy blocks specific actions
    # -----------------------------------------------------------------------

    def test_explicitly_denied_action_is_blocked(self) -> None:
        """ActionPolicy with action in denied_actions blocks execution."""
        policy = ActionPolicy(
            allowed_actions={"read_transcript"},
            denied_actions={"read_transcript"},
            require_all_allowed=True,
        )
        tool = _StubCrewAITool("read_transcript")
        guard = EnterpriseActionGuard(tool=tool, policy=policy)
        with pytest.raises(PolicyViolationError):
            guard._run()

    # -----------------------------------------------------------------------
    # Multiple allowed actions
    # -----------------------------------------------------------------------

    def test_multiple_allowed_actions_first_permitted(self) -> None:
        tool = _StubCrewAITool("read_transcript")
        guard = EnterpriseActionGuard(
            tool=tool,
            policy=_allow_policy("read_transcript", "read_enrollment", "read_grades"),
        )
        result = guard._run()
        assert result == "tool_result"

    def test_multiple_allowed_actions_unlisted_blocked(self) -> None:
        tool = _StubCrewAITool("export_full_db")
        guard = EnterpriseActionGuard(
            tool=tool,
            policy=_allow_policy("read_transcript", "read_enrollment"),
        )
        with pytest.raises(PolicyViolationError):
            guard._run()

    # -----------------------------------------------------------------------
    # Duck-typed policy (can_run interface)
    # -----------------------------------------------------------------------

    def test_duck_typed_policy_with_can_run_permitted(self) -> None:
        class _CanRunPolicy:
            def can_run(self, action_name: str) -> bool:
                return action_name == "safe_action"

        tool = _StubCrewAITool("safe_action")
        guard = EnterpriseActionGuard(tool=tool, policy=_CanRunPolicy())
        result = guard._run()
        assert result == "tool_result"

    def test_duck_typed_policy_with_can_run_blocked(self) -> None:
        class _CanRunPolicy:
            def can_run(self, action_name: str) -> bool:
                return False

        tool = _StubCrewAITool("any_action")
        guard = EnterpriseActionGuard(tool=tool, policy=_CanRunPolicy())
        with pytest.raises(PolicyViolationError):
            guard._run()


# ===========================================================================
# PolicyEnforcingAgent (AutoGen adapter)
# ===========================================================================


class TestPolicyEnforcingAgent:
    def test_permitted_agent_generates_reply(self) -> None:
        agent = _StubAutoGenAgent("advisor")
        wrapped = PolicyEnforcingAgent(
            agent=agent,
            policy=_allow_policy("advisor"),
        )
        result = wrapped.generate_reply(messages=[{"content": "hello"}])
        assert result == "agent_reply"
        assert agent.generate_reply_count == 1

    def test_blocked_agent_returns_blocked_reply(self) -> None:
        agent = _StubAutoGenAgent("advisor")
        wrapped = PolicyEnforcingAgent(
            agent=agent,
            policy=_allow_policy("other_agent"),
        )
        result = wrapped.generate_reply(messages=[])
        assert result == "[Response blocked by compliance policy]"
        assert agent.generate_reply_count == 0

    def test_custom_blocked_reply_message(self) -> None:
        agent = _StubAutoGenAgent("advisor")
        wrapped = PolicyEnforcingAgent(
            agent=agent,
            policy=_allow_policy("other_agent"),
            blocked_reply="COMPLIANCE VIOLATION — reply suppressed",
        )
        result = wrapped.generate_reply()
        assert "COMPLIANCE VIOLATION" in result

    def test_name_mirrors_underlying_agent(self) -> None:
        agent = _StubAutoGenAgent("my-advisor-agent")
        wrapped = PolicyEnforcingAgent(agent=agent, policy=_allow_policy("my-advisor-agent"))
        assert wrapped.name == "my-advisor-agent"

    def test_initiate_chat_delegates_to_agent(self) -> None:
        agent = _StubAutoGenAgent("advisor")
        wrapped = PolicyEnforcingAgent(agent=agent, policy=_allow_policy("advisor"))
        result = wrapped.initiate_chat()
        assert result == "chat_started"

    def test_receive_delegates_to_agent(self) -> None:
        agent = _StubAutoGenAgent("advisor")
        wrapped = PolicyEnforcingAgent(agent=agent, policy=_allow_policy("advisor"))
        result = wrapped.receive()
        assert result == "received"

    def test_permitted_emits_info_log(self, caplog: pytest.LogCaptureFixture) -> None:
        agent = _StubAutoGenAgent("advisor")
        wrapped = PolicyEnforcingAgent(agent=agent, policy=_allow_policy("advisor"))
        with caplog.at_level(logging.INFO, logger="regulated_ai_governance.adapters.autogen"):
            wrapped.generate_reply()
        assert any("permitted=True" in r.message for r in caplog.records)

    def test_blocked_emits_warning_log(self, caplog: pytest.LogCaptureFixture) -> None:
        agent = _StubAutoGenAgent("advisor")
        wrapped = PolicyEnforcingAgent(agent=agent, policy=_allow_policy("other_agent"))
        with caplog.at_level(logging.WARNING, logger="regulated_ai_governance.adapters.autogen"):
            wrapped.generate_reply()
        assert any("autogen_policy_blocked" in r.message for r in caplog.records)

    def test_duck_typed_can_run_policy_permits(self) -> None:
        class _CanRunPolicy:
            def can_run(self, action_name: str) -> bool:
                return True

        agent = _StubAutoGenAgent("advisor")
        wrapped = PolicyEnforcingAgent(agent=agent, policy=_CanRunPolicy())
        result = wrapped.generate_reply()
        assert result == "agent_reply"

    def test_duck_typed_can_run_policy_blocks(self) -> None:
        class _CanRunPolicy:
            def can_run(self, action_name: str) -> bool:
                return False

        agent = _StubAutoGenAgent("advisor")
        wrapped = PolicyEnforcingAgent(agent=agent, policy=_CanRunPolicy())
        result = wrapped.generate_reply()
        assert "blocked" in result.lower()


# ===========================================================================
# PolicyKernelPlugin (Semantic Kernel adapter)
# ===========================================================================


class TestPolicyKernelPlugin:
    def test_permitted_action_returns_true(self) -> None:
        plugin = PolicyKernelPlugin(policy=_allow_policy("read_patient_data"))
        assert plugin.check_action_permitted("read_patient_data") is True

    def test_blocked_action_returns_false(self) -> None:
        plugin = PolicyKernelPlugin(policy=_allow_policy("read_patient_data"))
        assert plugin.check_action_permitted("delete_all_records") is False

    def test_get_permitted_actions_returns_sorted_list(self) -> None:
        policy = _allow_policy("write_note", "read_patient_data", "search_records")
        plugin = PolicyKernelPlugin(policy=policy)
        actions = plugin.get_permitted_actions()
        assert actions == sorted(["write_note", "read_patient_data", "search_records"])

    def test_get_permitted_actions_empty_policy_returns_empty_list(self) -> None:
        policy = ActionPolicy(allowed_actions=set(), require_all_allowed=True)
        plugin = PolicyKernelPlugin(policy=policy)
        assert plugin.get_permitted_actions() == []

    def test_check_action_emits_info_log(self, caplog: pytest.LogCaptureFixture) -> None:
        plugin = PolicyKernelPlugin(policy=_allow_policy("read_patient_data"))
        with caplog.at_level(logging.INFO, logger="regulated_ai_governance.adapters.semantic_kernel"):
            plugin.check_action_permitted("read_patient_data")
        assert any("sk_policy_check" in r.message for r in caplog.records)

    def test_duck_typed_can_run_policy_true(self) -> None:
        class _CanRunPolicy:
            def can_run(self, action_name: str) -> bool:
                return action_name.startswith("read_")

        plugin = PolicyKernelPlugin(policy=_CanRunPolicy())
        assert plugin.check_action_permitted("read_data") is True
        assert plugin.check_action_permitted("write_data") is False

    def test_duck_typed_policy_without_allowed_actions_attr(self) -> None:
        """get_permitted_actions returns [] if policy has no allowed_actions attribute."""

        class _MinimalPolicy:
            def permits(self, action_name: str) -> tuple[bool, str]:
                return True, ""

        plugin = PolicyKernelPlugin(policy=_MinimalPolicy())
        assert plugin.get_permitted_actions() == []

    def test_custom_regulation_citation_stored(self) -> None:
        plugin = PolicyKernelPlugin(
            policy=_allow_policy("read_data"),
            regulation_citation="HIPAA 45 CFR § 164.308",
        )
        assert plugin._regulation_citation == "HIPAA 45 CFR § 164.308"

    def test_multiple_allowed_actions_all_permitted(self) -> None:
        policy = _allow_policy("action_a", "action_b", "action_c")
        plugin = PolicyKernelPlugin(policy=policy)
        for action in ("action_a", "action_b", "action_c"):
            assert plugin.check_action_permitted(action) is True

    def test_unlisted_action_denied_when_require_all(self) -> None:
        policy = _allow_policy("action_a", "action_b")
        plugin = PolicyKernelPlugin(policy=policy)
        assert plugin.check_action_permitted("action_c") is False


# ===========================================================================
# __init__.py exports
# ===========================================================================


class TestAdaptersPackageExports:
    def test_all_symbols_importable_from_adapters(self) -> None:
        from regulated_ai_governance.adapters import (  # noqa: F401
            EnterpriseActionGuard,
            PolicyEnforcingAgent,
            PolicyKernelPlugin,
            PolicyViolationError,
        )

    def test_policy_violation_error_is_exception_subclass(self) -> None:
        assert issubclass(PolicyViolationError, Exception)
