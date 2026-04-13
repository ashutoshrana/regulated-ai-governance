"""
Framework-agnostic governed action guard.

``GovernedActionGuard`` wraps any callable with a policy check, escalation
routing, and compliance audit. It is deliberately framework-agnostic — the
framework-specific integrations in ``regulated_ai_governance.integrations``
use it as a backend.

Design
------
The guard enforces a two-decision model:

1. **Allow/deny**: Is this action permitted by the policy?
2. **Escalate**: Even if permitted, should a human or compliance system be notified?

Both decisions are recorded in a ``GovernanceAuditRecord`` and routed to the
``audit_sink`` for every evaluation, whether the action is permitted or not.

Usage
-----

.. code-block:: python

    from regulated_ai_governance.agent_guard import GovernedActionGuard
    from regulated_ai_governance.policy import ActionPolicy, EscalationRule
    from regulated_ai_governance.audit import GovernanceAuditRecord

    audit_log: list[GovernanceAuditRecord] = []

    policy = ActionPolicy(
        allowed_actions={"read_transcript", "read_enrollment_status"},
        escalation_rules=[
            EscalationRule(
                condition="transcript_export",
                action_pattern="export",
                escalate_to="compliance_officer",
            )
        ],
    )

    guard = GovernedActionGuard(
        policy=policy,
        regulation="FERPA",
        actor_id="stu-alice",
        audit_sink=audit_log.append,
        block_on_escalation=True,
    )

    result = guard.guard(
        action_name="read_transcript",
        execute_fn=lambda: {"credits": 45},
    )
    # → {"credits": 45}  (permitted, no escalation)

    result = guard.guard(
        action_name="export_transcript_pdf",
        execute_fn=lambda: b"PDF_DATA",
    )
    # → raises PermissionError (escalation blocked by policy)
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any

from regulated_ai_governance.audit import GovernanceAuditRecord
from regulated_ai_governance.policy import ActionPolicy, PolicyDecision

logger = logging.getLogger(__name__)


class GovernedActionGuard:
    """
    Wraps a callable with governance enforcement.

    :param policy: ``ActionPolicy`` defining what actions are permitted.
    :param regulation: Regulation name written to each audit record
        (``"FERPA"``, ``"HIPAA"``, ``"GLBA"``, etc.).
    :param actor_id: Authenticated principal identifier. Must come from the
        verified session — never from user-supplied input.
    :param audit_sink: Optional callable that receives a ``GovernanceAuditRecord``
        for every evaluation event. Wire to a durable compliance log store.
    :param block_on_escalation: If True (default), escalated actions are blocked
        even if the allow/deny check passes. If False, escalations are logged
        but execution continues.
    :param policy_version: Version label written to audit records.
    :param raise_on_deny: If True, raise ``PermissionError`` on denial.
        If False (default), return an error string describing the denial.
    """

    def __init__(
        self,
        policy: ActionPolicy,
        regulation: str = "FERPA",
        actor_id: str = "",
        audit_sink: Callable[[GovernanceAuditRecord], None] | None = None,
        block_on_escalation: bool = True,
        policy_version: str = "1.0",
        raise_on_deny: bool = False,
    ) -> None:
        self._policy = policy
        self._regulation = regulation
        self._actor_id = actor_id
        self._audit_sink = audit_sink
        self._block_on_escalation = block_on_escalation
        self._policy_version = policy_version
        self._raise_on_deny = raise_on_deny

    def evaluate(
        self,
        action_name: str,
        context: dict[str, Any] | None = None,
    ) -> PolicyDecision:
        """
        Evaluate the policy for *action_name* without executing anything.

        Use this to pre-check an action before calling ``guard``, or when you
        want the decision but will handle execution yourself.

        :param action_name: The action to evaluate.
        :param context: Optional context dict passed to escalation rules.
        :returns: A ``PolicyDecision`` with permit/deny result and any escalation.
        """
        permitted, reason = self._policy.permits(action_name)
        escalation = self._policy.escalation_for(action_name, context or {})

        # If escalation blocks, treat as a denial
        if permitted and escalation is not None and self._block_on_escalation:
            return PolicyDecision(
                permitted=False,
                denial_reason=(
                    f"Action '{action_name}' is routed to '{escalation.escalate_to}' "
                    f"for review (escalation rule: '{escalation.condition}'). "
                    "Execution blocked pending approval."
                ),
                escalation=escalation,
            )

        return PolicyDecision(
            permitted=permitted,
            denial_reason=reason if not permitted else None,
            escalation=escalation,
        )

    def _emit_audit(
        self,
        action_name: str,
        decision: PolicyDecision,
        context: dict[str, Any] | None,
    ) -> None:
        if self._audit_sink is None:
            return
        record = GovernanceAuditRecord(
            regulation=self._regulation,
            actor_id=self._actor_id,
            action_name=action_name,
            permitted=decision.permitted,
            denial_reason=decision.denial_reason,
            escalation_target=(decision.escalation.escalate_to if decision.escalation else None),
            context=context or {},
            policy_version=self._policy_version,
        )
        self._audit_sink(record)

    def guard(
        self,
        action_name: str,
        execute_fn: Callable[..., Any],
        context: dict[str, Any] | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Evaluate the policy for *action_name* and, if permitted, execute *execute_fn*.

        Always emits an audit record regardless of the outcome.

        :param action_name: Name of the action being guarded.
        :param execute_fn: Callable to invoke if the action is permitted.
        :param context: Optional context dict (session ID, agent ID, etc.).
        :param args: Positional arguments forwarded to *execute_fn*.
        :param kwargs: Keyword arguments forwarded to *execute_fn*.
        :returns: The return value of *execute_fn* if permitted; raises
            ``PermissionError`` if ``raise_on_deny=True``, or returns an
            error string if ``raise_on_deny=False``.
        :raises PermissionError: If the action is denied and ``raise_on_deny=True``.
        """
        decision = self.evaluate(action_name, context)
        self._emit_audit(action_name, decision, context)

        if not decision.permitted:
            message = f"[regulated-ai-governance] Action BLOCKED — {decision.denial_reason}"
            if decision.escalation:
                message += f" | Escalation target: {decision.escalation.escalate_to}"
            if self._raise_on_deny:
                raise PermissionError(message)
            return message

        # Escalation logged but not blocking — emit structured warning
        if decision.escalation is not None:
            logger.warning(
                "[regulated-ai-governance] ESCALATION NOTICE: action=%r routed to %r (rule: %r). Proceeding.",
                action_name,
                decision.escalation.escalate_to,
                decision.escalation.condition,
            )

        return execute_fn(*args, **kwargs)
