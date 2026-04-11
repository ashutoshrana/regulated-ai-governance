"""
gdpr.py — GDPR (General Data Protection Regulation) policy helpers.

EU Regulation 2016/679.

Key GDPR obligations for AI systems handling personal data:

- Lawful basis: processing must have a valid legal basis (consent, contract,
  legitimate interest, vital interest, public task, legal obligation).
- Purpose limitation: data collected for one purpose must not be repurposed.
- Right to erasure (Art. 17): data subjects may request deletion of their data.
- Right to access (Art. 15): data subjects may request a copy of their data.
- Data minimisation: only the minimum necessary data should be processed.
- Transparency: processing activities must be documented and auditable.

This module provides ``ActionPolicy`` factories and erasure/access request
helpers for AI agent systems operating under GDPR.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from regulated_ai_governance.policy import ActionPolicy, EscalationRule

# Actions that require explicit DPA (Data Protection Authority) or DPO review.
GDPR_HIGH_RISK_ACTIONS: frozenset[str] = frozenset(
    {
        "bulk_export_personal_data",
        "cross_border_transfer",
        "profiling",
        "automated_decision_making",
        "special_category_processing",  # Art. 9 — health, biometric, etc.
        "large_scale_surveillance",
    }
)

# Actions permitted for a standard GDPR-compliant data processing agent.
GDPR_STANDARD_ALLOWED_ACTIONS: frozenset[str] = frozenset(
    {
        "read_consented_data",
        "update_consented_data",
        "anonymise_data",
        "pseudonymise_data",
        "generate_privacy_report",
        "log_processing_activity",
        "respond_to_subject_access_request",
        "process_erasure_request",
    }
)


def make_gdpr_processing_policy(
    allowed_actions: set[str] | None = None,
    escalate_high_risk_to: str = "data_protection_officer",
    require_all_allowed: bool = True,
) -> ActionPolicy:
    """
    Return an ``ActionPolicy`` for an AI agent processing data under GDPR.

    The policy:
    - Allows a standard set of lawful processing actions.
    - Denies actions that require explicit DPA review by default.
    - Escalates high-risk actions to the Data Protection Officer.

    Args:
        allowed_actions: Override the default allowed action set.
        escalate_high_risk_to: Identifier for the DPO escalation target.
        require_all_allowed: If True, only listed actions are permitted.

    Returns:
        A configured ``ActionPolicy`` instance.
    """
    effective_allowed = allowed_actions if allowed_actions is not None else set(GDPR_STANDARD_ALLOWED_ACTIONS)
    return ActionPolicy(
        allowed_actions=effective_allowed,
        denied_actions=set(GDPR_HIGH_RISK_ACTIONS),
        escalation_rules=[
            EscalationRule(
                condition="high_risk_processing_detected",
                action_pattern="profil",
                escalate_to=escalate_high_risk_to,
            ),
            EscalationRule(
                condition="cross_border_transfer_detected",
                action_pattern="cross_border",
                escalate_to=escalate_high_risk_to,
            ),
            EscalationRule(
                condition="special_category_detected",
                action_pattern="special_category",
                escalate_to=escalate_high_risk_to,
            ),
        ],
        require_all_allowed=require_all_allowed,
    )


@dataclass
class GDPRSubjectRequest:
    """
    A data subject request under GDPR Art. 15 (access) or Art. 17 (erasure).

    Attributes:
        request_id: UUID identifying this request.
        subject_id: Identifier for the data subject.
        request_type: ``"access"`` (Art. 15) or ``"erasure"`` (Art. 17).
        regulation: Always ``"GDPR"``.
        requested_at: UTC timestamp when the request was received.
        response_deadline: UTC timestamp for the 30-day response deadline.
    """

    subject_id: str
    request_type: str  # "access" | "erasure"
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    regulation: str = "GDPR"
    requested_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def response_deadline(self) -> datetime:
        """GDPR Art. 12(3): respond within 30 calendar days."""

        return datetime.fromtimestamp(
            self.requested_at.timestamp() + 30 * 86400,
            tz=timezone.utc,
        )


@dataclass
class GDPRProcessingRecord:
    """
    A record of a GDPR Art. 30 processing activity.

    Used to demonstrate compliance with the Record of Processing Activities (RoPA)
    requirement for organisations processing personal data at scale.

    Attributes:
        record_id: UUID for this processing record.
        controller: Name or ID of the data controller.
        purpose: Description of the processing purpose.
        legal_basis: GDPR legal basis (consent, contract, legitimate_interest, etc.).
        data_categories: Categories of personal data processed.
        recipients: Systems or organisations that receive the data.
        retention_days: Maximum retention period in days.
        created_at: UTC timestamp when this record was created.
    """

    controller: str
    purpose: str
    legal_basis: str
    data_categories: list[str]
    recipients: list[str]
    retention_days: int
    record_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_ropa_dict(self) -> dict[str, Any]:
        """Return a dict representation suitable for a Record of Processing Activities."""
        return {
            "record_id": self.record_id,
            "controller": self.controller,
            "purpose": self.purpose,
            "legal_basis": self.legal_basis,
            "data_categories": self.data_categories,
            "recipients": self.recipients,
            "retention_days": self.retention_days,
            "created_at": self.created_at.isoformat(),
            "regulation": "GDPR",
        }
