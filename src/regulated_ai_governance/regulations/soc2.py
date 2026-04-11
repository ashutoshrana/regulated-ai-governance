"""
soc2.py — SOC 2 Trust Services Criteria (TSC) policy helpers.

AICPA Trust Services Criteria (TSC) for Security, Availability, Processing
Integrity, Confidentiality, and Privacy.

SOC 2 is a voluntary standard for service organisations demonstrating controls
over customer data. For AI agent systems, SOC 2 compliance requires:

- CC6.1 (Logical and physical access): restrict AI agent actions to authorised scope.
- CC6.6 (Logical access restrictions): prevent unauthorised data disclosure.
- CC7.2 (Monitoring): log all agent actions for anomaly detection.
- CC8.1 (Change management): document system and model changes.
- PI1.1 (Processing integrity): inputs/outputs are complete, accurate, timely.
- C1.1 (Confidentiality): protect confidential data from unauthorised disclosure.

This module provides ``ActionPolicy`` factories and audit control helpers.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from regulated_ai_governance.policy import ActionPolicy, EscalationRule

# Actions that would violate SOC 2 CC6 logical access restrictions.
SOC2_HIGH_RISK_ACTIONS: frozenset[str] = frozenset(
    {
        "export_customer_data_unencrypted",
        "disable_audit_logging",
        "modify_access_controls",
        "bypass_change_management",
        "access_production_data_without_approval",
        "disable_monitoring",
    }
)

# Actions permitted for a SOC 2-compliant AI processing agent.
SOC2_STANDARD_ALLOWED_ACTIONS: frozenset[str] = frozenset(
    {
        "read_authorised_data",
        "generate_compliance_report",
        "log_processing_activity",
        "send_alert_to_siem",
        "validate_data_integrity",
        "anonymise_output",
        "encrypt_sensitive_field",
    }
)


class SOC2TrustCategory(Enum):
    """SOC 2 Trust Services Categories."""

    SECURITY = "Security"
    AVAILABILITY = "Availability"
    PROCESSING_INTEGRITY = "ProcessingIntegrity"
    CONFIDENTIALITY = "Confidentiality"
    PRIVACY = "Privacy"


def make_soc2_agent_policy(
    allowed_actions: set[str] | None = None,
    escalate_violations_to: str = "security_operations_center",
    require_all_allowed: bool = True,
) -> ActionPolicy:
    """
    Return an ``ActionPolicy`` for an AI agent subject to SOC 2 controls.

    The policy:
    - Allows a standard set of authorised processing actions.
    - Denies actions that would violate CC6 logical access restrictions.
    - Escalates suspicious or out-of-scope actions to the SOC.

    Args:
        allowed_actions: Override the default allowed action set.
        escalate_violations_to: Identifier for the SOC escalation target.
        require_all_allowed: If True, only listed actions are permitted.

    Returns:
        A configured ``ActionPolicy`` instance.
    """
    effective_allowed = allowed_actions if allowed_actions is not None else set(SOC2_STANDARD_ALLOWED_ACTIONS)
    return ActionPolicy(
        allowed_actions=effective_allowed,
        denied_actions=set(SOC2_HIGH_RISK_ACTIONS),
        escalation_rules=[
            EscalationRule(
                condition="audit_log_tampering_attempt",
                action_pattern="disable_audit",
                escalate_to=escalate_violations_to,
            ),
            EscalationRule(
                condition="access_control_modification_attempt",
                action_pattern="modify_access",
                escalate_to=escalate_violations_to,
            ),
            EscalationRule(
                condition="production_data_access_without_approval",
                action_pattern="production_data",
                escalate_to=escalate_violations_to,
            ),
        ],
        require_all_allowed=require_all_allowed,
    )


@dataclass
class SOC2ControlTestResult:
    """
    The result of testing a SOC 2 control against an AI agent action.

    Used to populate evidence for SOC 2 audits demonstrating that controls
    are operating effectively.

    Attributes:
        result_id: UUID for this test result.
        control_id: SOC 2 control identifier (e.g. ``"CC6.1"``).
        trust_category: The TSC category this control belongs to.
        action_tested: The AI agent action that was tested.
        passed: Whether the control operated as designed.
        finding: Description of the finding (pass or exception).
        tested_at: UTC timestamp.
        tested_by: Identifier of the system or person that ran the test.
    """

    control_id: str
    trust_category: SOC2TrustCategory
    action_tested: str
    passed: bool
    finding: str
    tested_by: str
    result_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    tested_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_audit_evidence_dict(self) -> dict[str, Any]:
        """Return a JSON-serialisable dict suitable for SOC 2 audit evidence packages."""
        return {
            "result_id": self.result_id,
            "control_id": self.control_id,
            "trust_category": self.trust_category.value,
            "action_tested": self.action_tested,
            "passed": self.passed,
            "finding": self.finding,
            "tested_by": self.tested_by,
            "tested_at": self.tested_at.isoformat(),
            "standard": "SOC2",
        }
