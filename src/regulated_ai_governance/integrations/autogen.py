"""
autogen.py — AutoGen / AG2 integration for regulated AI governance.

Wraps an AutoGen ``ConversableAgent`` so that every tool call is evaluated
against an ``ActionPolicy`` before execution. Denied actions raise
``PermissionError``; escalated actions route to the configured escalation
sink while still permitting or blocking according to ``block_on_escalation``.

Compatible with AutoGen 0.4+ (ag2 / pyautogen ≥ 0.4.0).

Installation:
    pip install regulated-ai-governance[autogen]

Usage::

    from autogen import ConversableAgent
    from regulated_ai_governance.integrations.autogen import GovernedAutoGenAgent
    from regulated_ai_governance.regulations.ferpa import make_ferpa_student_policy

    policy = make_ferpa_student_policy()
    agent = GovernedAutoGenAgent.wrap(
        agent=ConversableAgent("advisor", ...),
        policy=policy,
        regulation="FERPA",
        actor_id="stu-alice",
        audit_sink=audit_log.append,
    )
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from regulated_ai_governance.agent_guard import GovernedActionGuard
from regulated_ai_governance.audit import GovernanceAuditRecord
from regulated_ai_governance.policy import ActionPolicy


class GovernedAutoGenAgent:
    """
    Wraps an AutoGen ``ConversableAgent`` with regulated action enforcement.

    Each registered tool function is wrapped so that the governance policy is
    checked before the underlying function executes. The agent itself is stored
    as ``.agent`` for direct access when needed.

    Args:
        agent: The underlying AutoGen ``ConversableAgent`` (or any agent-like
            object with a ``register_for_llm`` / ``register_for_execution`` API).
        guard: Configured ``GovernedActionGuard`` for this agent.
    """

    def __init__(self, agent: Any, guard: GovernedActionGuard) -> None:
        self.agent = agent
        self._guard = guard

    @classmethod
    def wrap(
        cls,
        agent: Any,
        policy: ActionPolicy,
        regulation: str,
        actor_id: str,
        audit_sink: Callable[[GovernanceAuditRecord], None] | None = None,
        block_on_escalation: bool = True,
    ) -> GovernedAutoGenAgent:
        """
        Factory: create a ``GovernedAutoGenAgent`` from an existing ConversableAgent.

        Args:
            agent: AutoGen ``ConversableAgent`` to wrap.
            policy: ``ActionPolicy`` defining permitted actions.
            regulation: Regulation label for audit records (``"FERPA"``, ``"HIPAA"``).
            actor_id: Identifier of the user or entity on whose behalf the agent acts.
            audit_sink: Callable that receives each ``GovernanceAuditRecord``.
            block_on_escalation: If True, escalated actions are blocked in addition
                to being routed to the escalation target.

        Returns:
            A ``GovernedAutoGenAgent`` wrapping the provided agent.
        """
        guard = GovernedActionGuard(
            policy=policy,
            regulation=regulation,
            actor_id=actor_id,
            audit_sink=audit_sink or (lambda _: None),
            block_on_escalation=block_on_escalation,
            raise_on_deny=True,
        )
        return cls(agent=agent, guard=guard)

    def guarded_tool(self, action_name: str, fn: Callable[..., Any]) -> Callable[..., Any]:
        """
        Return a wrapper around *fn* that enforces the governance policy.

        Use this to register tools with AutoGen:

        .. code-block:: python

            @agent.register_for_execution()
            def read_transcript(student_id: str) -> dict:
                ...

            guarded = governed_agent.guarded_tool("read_transcript", read_transcript)

        Args:
            action_name: The policy action name to check (must match policy allow-list).
            fn: The underlying tool function.

        Returns:
            A wrapped callable that checks policy before calling *fn*.
        """

        def _governed(*args: Any, **kwargs: Any) -> Any:
            return self._guard.guard(
                action_name=action_name,
                execute_fn=lambda: fn(*args, **kwargs),
            )

        _governed.__name__ = fn.__name__
        _governed.__doc__ = fn.__doc__
        return _governed

    def guard_action(self, action_name: str, execute_fn: Callable[[], Any]) -> Any:
        """
        Directly guard a named action without wrapping a function.

        Args:
            action_name: Policy action name to evaluate.
            execute_fn: Zero-argument callable to run if permitted.

        Returns:
            The result of ``execute_fn()`` if the action is permitted.

        Raises:
            PermissionError: If the action is denied by policy.
        """
        return self._guard.guard(action_name=action_name, execute_fn=execute_fn)
