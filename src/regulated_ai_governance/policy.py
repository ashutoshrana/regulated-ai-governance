"""
Core policy primitives for regulated AI governance.

``ActionPolicy`` defines what actions an AI agent is permitted to execute.
``EscalationRule`` triggers a routing event when a matching action is attempted.
``PolicyDecision`` is the result of a policy check — permitted or not, with reason.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class EscalationRule:
    """
    Triggers an escalation routing event when an action matches ``action_pattern``.

    :param condition: Human-readable label for this rule (e.g. ``"external_email_detected"``).
    :param action_pattern: Substring matched against the action name. An empty string
        matches all actions unconditionally.
    :param escalate_to: Identifier for the escalation target
        (e.g. ``"human_operator"``, ``"compliance_queue"``).
    """

    condition: str
    action_pattern: str
    escalate_to: str

    def matches(self, action_name: str) -> bool:
        """Return True if this rule applies to *action_name*."""
        if not self.action_pattern:
            return True
        return self.action_pattern in action_name


@dataclass
class PolicyDecision:
    """
    The result of evaluating an ``ActionPolicy`` against an action.

    :param permitted: Whether the action is allowed to proceed.
    :param denial_reason: Human-readable reason if ``permitted`` is False.
    :param escalation: The ``EscalationRule`` that was triggered, if any.
    """

    permitted: bool
    denial_reason: str | None = None
    escalation: EscalationRule | None = None


@dataclass
class ActionPolicy:
    """
    Defines what actions an AI agent or workflow step is permitted to execute.

    Enforcement model
    -----------------
    1. If ``allowed_actions`` is non-empty and ``require_all_allowed`` is True,
       only listed actions are permitted. Unlisted actions are denied.
    2. If ``allowed_actions`` is empty, all actions are permitted by default
       (open policy — use sparingly in regulated environments).
    3. Escalation rules are evaluated *after* the allow/deny check. An escalation
       does not automatically deny; use ``GovernedActionGuard.block_on_escalation``
       to control whether escalated actions are blocked or logged-and-continued.

    :param allowed_actions: Set of action names permitted under this policy.
        An empty set means "allow all" when ``require_all_allowed`` is False.
    :param denied_actions: Set of action names explicitly denied. Takes
        precedence over ``allowed_actions``.
    :param escalation_rules: List of rules that trigger routing events.
    :param require_all_allowed: If True (default), any action not in
        ``allowed_actions`` is denied. If False, ``allowed_actions`` is advisory.
    """

    allowed_actions: set[str] = field(default_factory=set)
    denied_actions: set[str] = field(default_factory=set)
    escalation_rules: list[EscalationRule] = field(default_factory=list)
    require_all_allowed: bool = True

    def permits(self, action_name: str) -> tuple[bool, str]:
        """
        Evaluate whether *action_name* is permitted.

        :returns: ``(True, "")`` if allowed; ``(False, reason)`` if denied.
        """
        if action_name in self.denied_actions:
            return False, f"Action '{action_name}' is explicitly denied by policy."

        if self.allowed_actions and self.require_all_allowed:
            if action_name not in self.allowed_actions:
                return False, (
                    f"Action '{action_name}' is not in the allowed actions set. "
                    f"Allowed: {sorted(self.allowed_actions)}"
                )

        return True, ""

    def escalation_for(
        self, action_name: str, context: dict | None = None
    ) -> EscalationRule | None:
        """
        Return the first ``EscalationRule`` that matches *action_name*, or None.

        :param action_name: The name of the action being evaluated.
        :param context: Optional execution context (reserved for future rule enrichment).
        """
        _ = context  # reserved
        for rule in self.escalation_rules:
            if rule.matches(action_name):
                return rule
        return None
