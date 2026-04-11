"""
CrewAI integration — ``EnterpriseActionGuard`` tool wrapper.

Wraps any CrewAI ``BaseTool`` and enforces an ``ActionPolicy`` (from this library)
before the underlying tool executes. Produces a ``GovernanceAuditRecord`` for
every tool invocation.

Installation:
    pip install regulated-ai-governance[crewai]

Usage:
    from crewai.tools import BaseTool
    from regulated_ai_governance import ActionPolicy, EscalationRule
    from regulated_ai_governance.integrations.crewai import EnterpriseActionGuard

    policy = ActionPolicy(
        allowed_actions={"read_transcript", "read_enrollment_status"},
        escalation_rules=[
            EscalationRule("export_attempt", "export", "compliance_officer")
        ],
    )

    guard = EnterpriseActionGuard(
        wrapped_tool=MyTool(),
        policy=policy,
        regulation="FERPA",
        actor_id="stu-alice",
        audit_sink=lambda rec: write_to_log(rec.to_log_entry()),
        block_on_escalation=True,
    )

    # Use guard in a CrewAI agent's tool list instead of the raw tool.
    agent = Agent(tools=[guard], ...)
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

try:
    from crewai.tools import BaseTool
    from pydantic import PrivateAttr
except ImportError as exc:
    raise ImportError(
        "crewai is required for this integration. "
        "Install it with: pip install regulated-ai-governance[crewai]"
    ) from exc

from regulated_ai_governance.agent_guard import GovernedActionGuard
from regulated_ai_governance.audit import GovernanceAuditRecord
from regulated_ai_governance.policy import ActionPolicy


class EnterpriseActionGuard(BaseTool):
    """
    CrewAI ``BaseTool`` wrapper that enforces ``ActionPolicy`` before execution.

    This guard sits between a CrewAI agent and any tool. When the agent invokes
    the tool, the guard:

    1. Checks the action name against the ``ActionPolicy`` (allow/deny).
    2. Evaluates escalation rules — if triggered and ``block_on_escalation=True``,
       execution is blocked and the agent receives an error response.
    3. Emits a ``GovernanceAuditRecord`` to the ``audit_sink`` for every call,
       regardless of the outcome.

    The tool name and description are inherited from the wrapped tool so that
    the agent's task planning is unaffected.

    :param wrapped_tool: The ``BaseTool`` to wrap.
    :param policy: ``ActionPolicy`` defining what this tool is allowed to do.
    :param regulation: Regulation label written to audit records
        (``"FERPA"``, ``"HIPAA"``, ``"GLBA"``, etc.).
    :param actor_id: Authenticated principal identifier — must originate from
        the verified session, not from user input.
    :param audit_sink: Callable that receives a ``GovernanceAuditRecord`` for
        each invocation. Wire to a durable compliance log store.
    :param block_on_escalation: If True (default), escalated tool calls are
        blocked. If False, escalations are logged and execution continues.
    :param context: Optional static context dict included in every audit record
        (e.g. session ID, agent ID).
    """

    _wrapped_tool: BaseTool = PrivateAttr()
    _guard: GovernedActionGuard = PrivateAttr()
    _context: dict[str, Any] = PrivateAttr(default_factory=dict)

    def __init__(
        self,
        wrapped_tool: BaseTool,
        policy: ActionPolicy,
        regulation: str = "FERPA",
        actor_id: str = "",
        audit_sink: Callable[[GovernanceAuditRecord], None] | None = None,
        block_on_escalation: bool = True,
        context: dict[str, Any] | None = None,
        **data: Any,
    ) -> None:
        super().__init__(
            name=wrapped_tool.name,
            description=wrapped_tool.description,
            **data,
        )
        self._wrapped_tool = wrapped_tool
        self._context = context or {}
        self._guard = GovernedActionGuard(
            policy=policy,
            regulation=regulation,
            actor_id=actor_id,
            audit_sink=audit_sink,
            block_on_escalation=block_on_escalation,
        )

    def _run(self, *args: Any, **kwargs: Any) -> Any:
        """
        Evaluate policy and execute the wrapped tool if permitted.

        :returns: The wrapped tool's result if permitted; an error string if blocked.
        """
        ctx = {**self._context, "args": str(args)[:200], "kwargs_keys": list(kwargs.keys())}
        return self._guard.guard(
            action_name=self.name,
            execute_fn=lambda: self._wrapped_tool._run(*args, **kwargs),
            context=ctx,
        )
