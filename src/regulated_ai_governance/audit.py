"""
Structured audit record for regulated AI governance.

``GovernanceAuditRecord`` captures every agent action evaluation event — whether
the action was permitted, denied, or escalated — in a format suitable for
compliance log stores.

The design satisfies the record-keeping requirements across the three core
regulations this library targets:

- **FERPA**: 34 CFR § 99.32 — institutions must maintain a record of each
  disclosure of education records, including who accessed them and when.
- **HIPAA**: 45 CFR § 164.312(b) — covered entities must implement hardware,
  software, and/or procedural mechanisms that record and examine activity in
  information systems that contain PHI.
- **GLBA**: 16 CFR § 314.4(e) — financial institutions must monitor and test
  safeguards, including access to customer information.

Every record is immutable after creation. Route each record to a durable,
regulation-appropriate store using the ``audit_sink`` callable.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class GovernanceAuditRecord:
    """
    A single compliance audit event produced when ``GovernedActionGuard``
    evaluates a policy check.

    :param regulation: The regulation governing this record
        (``"FERPA"``, ``"HIPAA"``, ``"GLBA"``, ``"GDPR"``, etc.).
    :param actor_id: Identifier of the authenticated principal taking the action
        (e.g. student ID, employee ID, agent ID). Must originate from the
        authenticated session — not from user-supplied input.
    :param action_name: The name of the action that was evaluated.
    :param permitted: Whether the action was allowed to execute.
    :param denial_reason: Reason for denial if ``permitted`` is False.
    :param escalation_target: Routing destination if an escalation rule fired.
    :param context: Additional context about the request
        (session ID, agent ID, channel, etc.).
    :param policy_version: Version string of the policy that was evaluated.
    :param record_id: Auto-generated UUID for this specific record.
    :param timestamp: UTC timestamp of the evaluation event.
    """

    regulation: str
    actor_id: str
    action_name: str
    permitted: bool
    denial_reason: str | None = None
    escalation_target: str | None = None
    context: dict[str, Any] = field(default_factory=dict)
    policy_version: str = "1.0"
    record_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_log_entry(self) -> dict[str, Any]:
        """
        Serialize to a flat dictionary suitable for writing to a log store,
        database table, or structured logging sink.

        The ``record_id`` field uniquely identifies this record in the audit log.
        The ``timestamp`` is always UTC ISO-8601 formatted.

        :returns: Dict with all audit fields; safe to pass to
            ``json.dumps`` or a SQL INSERT.
        """
        return {
            "record_id": self.record_id,
            "regulation": self.regulation,
            "actor_id": self.actor_id,
            "action_name": self.action_name,
            "permitted": self.permitted,
            "denial_reason": self.denial_reason,
            "escalation_target": self.escalation_target,
            "policy_version": self.policy_version,
            "timestamp": self.timestamp.isoformat(),
            **{f"ctx_{k}": v for k, v in self.context.items()},
        }
