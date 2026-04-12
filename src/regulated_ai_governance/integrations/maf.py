"""
integrations/maf.py — Microsoft Agent Framework (MAF) integration.

Provides ``PolicyMiddleware``, a MAF ``MiddlewareBase`` that intercepts every
agent message, evaluates the configured ``ActionPolicy``, and emits a
``GovernanceAuditRecord`` for each intercepted call.

Microsoft Agent Framework (MAF) is the enterprise successor to AutoGen and
Semantic Kernel (released 2026). Both legacy frameworks are in maintenance
mode; new agentic AI workloads on Microsoft Azure should use MAF.

Installation::

    pip install 'regulated-ai-governance[maf]'

Usage::

    from regulated_ai_governance import ActionPolicy, EscalationRule
    from regulated_ai_governance.integrations.maf import PolicyMiddleware

    policy = ActionPolicy(
        allowed_actions={"read_transcript", "query_enrollment"},
        escalation_rules=[
            EscalationRule("export_attempt", "export", "compliance_officer")
        ],
    )
    middleware = PolicyMiddleware(
        policy=policy,
        regulation="FERPA",
        actor_id="stu-alice",
        block_on_escalation=True,
        audit_sink=lambda rec: write_to_log(rec.to_log_entry()),
    )

    runtime = AgentRuntime(middlewares=[middleware])
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any

from regulated_ai_governance.agent_guard import GovernedActionGuard
from regulated_ai_governance.audit import GovernanceAuditRecord
from regulated_ai_governance.policy import ActionPolicy

logger = logging.getLogger(__name__)


def _check_maf_available() -> None:
    """Verify microsoft-agent-framework is installed."""
    try:
        import microsoft_agent_framework  # noqa: F401
    except ImportError as exc:
        raise ImportError(
            "microsoft-agent-framework is required for the MAF integration. "
            "Install it with: pip install 'regulated-ai-governance[maf]'"
        ) from exc


class PolicyMiddleware:
    """
    MAF middleware enforcing ``ActionPolicy`` on every agent message.

    Implements MAF ``MiddlewareBase`` via duck typing. The MAF SDK is
    checked lazily at instantiation time — not at module import — so
    the module is importable in environments without the MAF SDK.

    Enforcement flow per message:
      1. Extract ``action_name`` from the message (``message.action`` or
         ``message.payload["action"]``).
      2. Evaluate ``ActionPolicy.is_allowed(action_name)``.
      3. Evaluate escalation rules; block if ``block_on_escalation=True``.
      4. Emit ``GovernanceAuditRecord`` via ``audit_sink``.
      5. If blocked: return an error message to the agent runtime.
      6. If allowed: call ``next_handler`` to continue the pipeline.

    Args:
        policy: ``ActionPolicy`` defining allowed actions and escalation rules.
        regulation: Label written to audit records (``"FERPA"``, ``"HIPAA"``…).
        actor_id: Authenticated principal identifier — must come from the
                  verified session token, not from agent-supplied input.
        audit_sink: Callable receiving each ``GovernanceAuditRecord``.
        block_on_escalation: If True (default), escalated actions are blocked.
        context: Optional static context dict added to every audit record.
    """

    def __init__(
        self,
        policy: ActionPolicy,
        regulation: str = "FERPA",
        actor_id: str = "",
        audit_sink: Callable[[GovernanceAuditRecord], None] | None = None,
        block_on_escalation: bool = True,
        context: dict[str, Any] | None = None,
    ) -> None:
        _check_maf_available()
        self._guard = GovernedActionGuard(
            policy=policy,
            regulation=regulation,
            actor_id=actor_id,
            audit_sink=audit_sink,
            block_on_escalation=block_on_escalation,
        )
        self._context = context or {}

    async def on_message(self, message: Any, next_handler: Any) -> Any:
        """
        Intercept an agent message, evaluate policy, and continue or block.

        Extracts the action name from the message and evaluates policy.
        If blocked, returns an error dict; otherwise continues the pipeline.

        Args:
            message: MAF message object (duck-typed; must expose ``.action``
                     or ``payload["action"]``).
            next_handler: Async callable for the next middleware / handler.
        """
        action_name = self._extract_action(message)
        if action_name is None:
            # Non-action message (e.g., status, heartbeat) — pass through
            return await next_handler(message)

        ctx = {**self._context, "message_type": type(message).__name__}

        result = self._guard.guard(
            action_name=action_name,
            execute_fn=lambda: _DEFERRED_SENTINEL,
            context=ctx,
        )

        if result is _DEFERRED_SENTINEL:
            # Policy passed — execute the actual next handler
            return await next_handler(message)

        # Policy blocked — result is an error string from GovernedActionGuard
        logger.warning(
            "[GOVERNANCE] MAF message blocked: action=%s actor=%s reason=%s",
            action_name,
            self._guard.actor_id,
            result,
        )
        return {"blocked": True, "reason": result, "action": action_name}

    @staticmethod
    def _extract_action(message: Any) -> str | None:
        """Extract action name from a MAF message object."""
        action = getattr(message, "action", None)
        if action:
            return str(action)
        payload = getattr(message, "payload", None)
        if isinstance(payload, dict):
            return payload.get("action")
        return None


# Internal sentinel to distinguish "policy passed, run the handler" from
# an error string returned by GovernedActionGuard when blocking.
_DEFERRED_SENTINEL = object()
