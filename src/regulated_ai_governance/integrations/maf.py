"""
integrations/maf.py — Microsoft Agent Framework (MAF) integration.

``PolicyMiddleware.on_message`` retains the legacy message/next-handler
contract. Use ``as_native()`` to obtain Microsoft Agent Framework's native
``FunctionMiddleware`` and check function policy before execution.

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

    agent = Agent(client=client, middleware=[middleware.as_native()])
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
    """Verify the native agent_framework namespace is installed."""
    try:
        import agent_framework  # noqa: F401
    except ImportError as exc:
        raise ImportError(
            "agent-framework-core is required for the MAF integration. "
            "Install it with: pip install 'regulated-ai-governance[maf]'"
        ) from exc


class PolicyMiddleware:
    """
    Policy checks for legacy messages and native function middleware.

    ``on_message`` is an application-level compatibility interface, not an SDK
    middleware base class. Register ``as_native()`` with the native Agent.
    The SDK is checked lazily at instantiation time.

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
        require_audit: bool = False,
    ) -> None:
        _check_maf_available()
        self._guard = GovernedActionGuard(
            policy=policy,
            regulation=regulation,
            actor_id=actor_id,
            audit_sink=audit_sink,
            require_audit=require_audit,
            block_on_escalation=block_on_escalation,
        )
        self._context = context or {}

    def as_native(self) -> Any:
        """Return SDK FunctionMiddleware; decision and audit precede the tool call."""
        from agent_framework import FunctionMiddleware

        guard = self._guard
        context_metadata = self._context

        class NativePolicyMiddleware(FunctionMiddleware):
            async def process(self, context: Any, call_next: Any) -> None:
                permitted = object()
                result = guard.guard(context.function.name, lambda: permitted, context=context_metadata)
                if result is not permitted:
                    raise PermissionError(str(result))
                await call_next()

        return NativePolicyMiddleware()

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
            self._guard._actor_id,
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
