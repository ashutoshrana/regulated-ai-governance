"""
ccpa.py — CCPA/CPRA (California Consumer Privacy Act) policy helpers.

California Civil Code §§ 1798.100–1798.199 (CCPA, as amended by CPRA).

Key CCPA obligations for AI systems handling California resident data:

- Right to know: consumers may request disclosure of personal information collected,
  sources, purposes, and recipients (§ 1798.110).
- Right to delete: consumers may request deletion of their personal information
  (§ 1798.105).
- Right to opt-out: consumers may opt out of the sale/sharing of personal
  information (§ 1798.120).
- Right to correct: consumers may correct inaccurate personal information (§ 1798.106).
- Automated decision-making (CPRA): consumers have rights regarding profiling
  and automated decision-making that produces legal or significant effects.
- Response timeline: 45 calendar days to respond to consumer requests (§ 1798.130).

This module provides ``ActionPolicy`` factories and consumer request helpers.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from regulated_ai_governance.policy import ActionPolicy, EscalationRule

# Actions requiring explicit consumer authorisation or opt-in under CCPA/CPRA.
CCPA_HIGH_RISK_ACTIONS: frozenset[str] = frozenset(
    {
        "sell_personal_information",
        "share_personal_information_for_cross_context_advertising",
        "automated_profiling_with_legal_effect",
        "process_sensitive_personal_information",  # CPRA § 1798.121
        "retain_beyond_disclosed_purpose",
    }
)

# Standard processing actions compatible with CCPA disclosed purposes.
CCPA_STANDARD_ALLOWED_ACTIONS: frozenset[str] = frozenset(
    {
        "read_consented_data",
        "update_consumer_preference",
        "process_deletion_request",
        "process_access_request",
        "process_correction_request",
        "log_data_collection",
        "generate_privacy_notice",
        "anonymise_data",
    }
)


def make_ccpa_processing_policy(
    allowed_actions: set[str] | None = None,
    escalate_sensitive_to: str = "privacy_compliance_team",
    require_all_allowed: bool = True,
) -> ActionPolicy:
    """
    Return an ``ActionPolicy`` for an AI agent processing California resident data.

    The policy:
    - Allows standard disclosed-purpose processing actions.
    - Denies actions that would violate CCPA opt-out or sensitive PI rules.
    - Escalates sensitive personal information handling to the privacy team.

    Args:
        allowed_actions: Override the default allowed action set.
        escalate_sensitive_to: Identifier for the privacy team escalation target.
        require_all_allowed: If True, only listed actions are permitted.

    Returns:
        A configured ``ActionPolicy`` instance.
    """
    effective_allowed = allowed_actions if allowed_actions is not None else set(CCPA_STANDARD_ALLOWED_ACTIONS)
    return ActionPolicy(
        allowed_actions=effective_allowed,
        denied_actions=set(CCPA_HIGH_RISK_ACTIONS),
        escalation_rules=[
            EscalationRule(
                condition="sensitive_personal_information_detected",
                action_pattern="sensitive",
                escalate_to=escalate_sensitive_to,
            ),
            EscalationRule(
                condition="cross_context_advertising_attempt",
                action_pattern="advertising",
                escalate_to=escalate_sensitive_to,
            ),
        ],
        require_all_allowed=require_all_allowed,
    )


@dataclass
class CCPAConsumerRequest:
    """
    A consumer rights request under CCPA §§ 1798.105–1798.110.

    Attributes:
        request_id: UUID identifying this request.
        consumer_id: Identifier for the California resident.
        request_type: ``"know"``, ``"delete"``, ``"opt_out"``, or ``"correct"``.
        regulation: Always ``"CCPA"``.
        requested_at: UTC timestamp when the request was received.
        response_deadline: UTC timestamp for the 45-day response deadline.
        categories_requested: For ``"know"`` requests — specific categories, or empty for all.
    """

    consumer_id: str
    request_type: str  # "know" | "delete" | "opt_out" | "correct"
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    regulation: str = "CCPA"
    requested_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    categories_requested: list[str] = field(default_factory=list)

    @property
    def response_deadline(self) -> datetime:
        """CCPA § 1798.130(a)(2): respond within 45 calendar days."""
        return datetime.fromtimestamp(
            self.requested_at.timestamp() + 45 * 86400,
            tz=timezone.utc,
        )

    def to_request_dict(self) -> dict[str, Any]:
        """Return a JSON-serialisable representation for audit logging."""
        return {
            "request_id": self.request_id,
            "consumer_id": self.consumer_id,
            "request_type": self.request_type,
            "regulation": self.regulation,
            "requested_at": self.requested_at.isoformat(),
            "response_deadline": self.response_deadline.isoformat(),
            "categories_requested": self.categories_requested,
        }


@dataclass
class CCPADataInventoryRecord:
    """
    A record of personal information collected, required for CCPA § 1798.110 disclosures.

    Attributes:
        record_id: UUID for this inventory record.
        data_category: CCPA category of personal information (e.g. ``"identifiers"``,
            ``"commercial_information"``, ``"internet_activity"``).
        sources: List of sources from which data was collected.
        business_purpose: Purpose for which data is collected or used.
        third_party_recipients: Third parties data is disclosed to.
        sold_or_shared: Whether data is sold or shared for cross-context advertising.
        created_at: UTC timestamp.
    """

    data_category: str
    sources: list[str]
    business_purpose: str
    third_party_recipients: list[str]
    sold_or_shared: bool
    record_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_disclosure_dict(self) -> dict[str, Any]:
        """Return a JSON-serialisable representation for consumer disclosure."""
        return {
            "record_id": self.record_id,
            "data_category": self.data_category,
            "sources": self.sources,
            "business_purpose": self.business_purpose,
            "third_party_recipients": self.third_party_recipients,
            "sold_or_shared": self.sold_or_shared,
            "created_at": self.created_at.isoformat(),
            "regulation": "CCPA",
        }
