"""
dora.py — EU Digital Operational Resilience Act (DORA) policy helpers.

EU Regulation 2022/2554, in force January 17, 2025.

DORA establishes a comprehensive framework for digital operational resilience
in the financial sector. It requires financial entities to manage ICT risks,
report major ICT incidents, test digital operational resilience, and oversee
ICT third-party service providers.

Key Articles addressed by this module:

- **Article 9**: ICT risk management — identification, protection, detection,
  response, and recovery (the NIST-inspired five-function framework).
- **Article 11**: Business continuity and disaster recovery — ensuring ICT
  systems can be restored and that continuity measures are tested.
- **Article 17–18**: ICT incident reporting — classification and mandatory
  reporting of major incidents to competent authorities.
- **Article 28**: Third-party ICT service provider risk management — maintaining
  a register of all ICT third-party arrangements with assessed risk levels.

This module provides ``ActionPolicy`` factories, enumerations, and record
dataclasses for AI agent systems operating under DORA obligations.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import Enum

# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------


class DORAICTRiskLevel(str, Enum):
    """ICT risk level classifications for DORA third-party assessments (Art. 28)."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class DORAICTCapabilityArea(str, Enum):
    """
    ICT capability areas from DORA Article 9 risk management framework.

    Mirrors the NIST Cybersecurity Framework functions adopted by DORA:
    Identify → Protect → Detect → Respond → Recover.
    """

    IDENTIFY = "identify"
    PROTECT = "protect"
    DETECT = "detect"
    RESPOND = "respond"
    RECOVER = "recover"


# ---------------------------------------------------------------------------
# High-risk action catalogue
# ---------------------------------------------------------------------------

DORA_HIGH_RISK_ICT_ACTIONS: frozenset[str] = frozenset(
    {
        "bypass_ict_controls",
        "skip_backup_procedure",
        "disable_monitoring",
        "unvalidated_third_party_access",
        "access_via_unassessed_provider",
        "unauthorized_provider_integration",
        "disable_incident_detection",
        "modify_audit_trail",
        "disable_disaster_recovery_test",
        "override_resilience_policy",
        "suppress_incident_report",
        "deactivate_continuity_plan",
    }
)


# ---------------------------------------------------------------------------
# Third-party register record (Art. 28)
# ---------------------------------------------------------------------------


@dataclass
class DORAThirdPartyRecord:
    """
    A record in the DORA Art. 28 third-party ICT service provider register.

    Financial entities must maintain an up-to-date register of all ICT
    third-party arrangements, including a risk assessment for each provider.

    Attributes:
        provider_id: Unique identifier for the ICT third-party provider.
        provider_name: Human-readable name of the provider.
        risk_level: Assessed ICT risk level for this provider.
        assessed: Whether a formal risk assessment has been completed.
        contract_id: Optional reference to the contractual arrangement.
        assessment_date: Optional ISO-8601 date of the last assessment.
    """

    provider_id: str
    provider_name: str
    risk_level: DORAICTRiskLevel
    assessed: bool
    contract_id: str = ""
    assessment_date: str = ""


# ---------------------------------------------------------------------------
# ICT incident record (Art. 17–18)
# ---------------------------------------------------------------------------


@dataclass
class DORAICTIncidentRecord:
    """
    A DORA ICT incident record for classification and authority reporting.

    Under DORA Articles 17–18, financial entities must classify ICT incidents
    as major, significant, or standard and report major incidents to the
    relevant competent authority within prescribed timeframes.

    Attributes:
        incident_id: Unique identifier for this incident.
        classification: ``"major"``, ``"significant"``, or ``"standard"``.
        affected_services: List of ICT services impacted by the incident.
        reported_to_authority: Whether the incident has been reported to the
            competent supervisory authority.
        timestamp_utc: ISO-8601 UTC timestamp when the incident was detected.
    """

    incident_id: str
    classification: str  # "major" | "significant" | "standard"
    affected_services: list[str]
    reported_to_authority: bool
    timestamp_utc: str

    def to_log_entry(self) -> str:
        """Serialize to a structured JSON log entry for DORA audit purposes."""
        return json.dumps(
            {
                "framework": "DORA_EU_2022_2554",
                "record_type": "ict_incident",
                "incident_id": self.incident_id,
                "classification": self.classification,
                "affected_services": sorted(self.affected_services),
                "reported_to_authority": self.reported_to_authority,
                "timestamp_utc": self.timestamp_utc,
            },
            separators=(",", ":"),
        )

    def content_hash(self) -> str:
        """SHA-256 hash for tamper-evidence in the incident audit trail."""
        return hashlib.sha256(self.to_log_entry().encode()).hexdigest()


# ---------------------------------------------------------------------------
# Policy factories
# ---------------------------------------------------------------------------

# Import here to avoid circular imports at module level
from regulated_ai_governance.policy import ActionPolicy, EscalationRule  # noqa: E402


def make_dora_ict_management_policy(
    allowed_actions: set[str] | None = None,
    escalate_incidents_to: str = "ict_risk_management_team",
) -> ActionPolicy:
    """
    Return an ``ActionPolicy`` for AI agents operating under DORA ICT risk management.

    Implements the five-function resilience framework from DORA Article 9:
    Identify, Protect, Detect, Respond, Recover. The policy denies actions
    that undermine ICT controls and escalates incident-related actions to the
    ICT risk management team.

    Args:
        allowed_actions: Override the default permitted action set. If None,
            a standard set of safe ICT management actions is used.
        escalate_incidents_to: Escalation target for incident-related actions.

    Returns:
        A configured ``ActionPolicy`` instance.
    """
    effective_allowed: set[str] = (
        allowed_actions
        if allowed_actions is not None
        else {
            "read_ict_risk_register",
            "log_ict_event",
            "trigger_incident_response",
            "run_backup_procedure",
            "enable_monitoring",
            "generate_resilience_report",
            "test_disaster_recovery",
            "validate_continuity_plan",
        }
    )
    return ActionPolicy(
        allowed_actions=effective_allowed,
        denied_actions={
            "bypass_ict_controls",
            "skip_backup_procedure",
            "disable_monitoring",
            "unvalidated_third_party_access",
        },
        escalation_rules=[
            EscalationRule(
                condition="ict_incident_action_detected",
                action_pattern="incident",
                escalate_to=escalate_incidents_to,
            ),
            EscalationRule(
                condition="disaster_recovery_action_detected",
                action_pattern="disaster_recovery",
                escalate_to=escalate_incidents_to,
            ),
        ],
        require_all_allowed=True,
    )


def make_dora_third_party_policy(
    authorized_providers: set[str] | None = None,
    escalate_to: str = "third_party_risk_manager",
) -> ActionPolicy:
    """
    Return an ``ActionPolicy`` for AI agents managing DORA Art. 28 third-party risk.

    Financial entities must ensure all ICT third-party integrations are covered
    by a formal risk assessment before access is granted. This policy denies
    access through unassessed or unauthorised providers.

    Args:
        authorized_providers: Set of assessed and authorized provider identifiers.
            Used to construct human-readable context; enforcement is via
            the denied_actions list.
        escalate_to: Escalation target for third-party integration attempts.

    Returns:
        A configured ``ActionPolicy`` instance.
    """
    _ = authorized_providers  # reserved for future provider-specific enforcement
    return ActionPolicy(
        allowed_actions={
            "read_provider_register",
            "update_provider_assessment",
            "log_provider_access",
            "generate_third_party_report",
        },
        denied_actions={
            "access_via_unassessed_provider",
            "unauthorized_provider_integration",
        },
        escalation_rules=[
            EscalationRule(
                condition="third_party_integration_attempt",
                action_pattern="provider",
                escalate_to=escalate_to,
            ),
        ],
        require_all_allowed=True,
    )
