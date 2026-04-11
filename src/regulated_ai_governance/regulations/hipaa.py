"""
HIPAA (Health Insurance Portability and Accountability Act) policy helpers.

45 CFR Part 164 — Security and Privacy Rules.

The HIPAA Security Rule requires covered entities and business associates to
implement administrative, physical, and technical safeguards to protect
electronic protected health information (ePHI). For AI agent systems that
access ePHI, the minimum-necessary standard (45 CFR § 164.502(b)) is the
primary constraint: agents must access only the ePHI that is the minimum
necessary to accomplish the intended purpose.

This module provides pre-built ``ActionPolicy`` instances for the most
common HIPAA-regulated agent scenarios.
"""

from __future__ import annotations

from regulated_ai_governance.policy import ActionPolicy, EscalationRule

# Actions that access ePHI — require minimum-necessary justification.
HIPAA_PHI_ACTIONS: frozenset[str] = frozenset(
    {
        "read_diagnosis",
        "read_treatment_notes",
        "read_prescription",
        "read_lab_results",
        "read_imaging_report",
        "read_mental_health_notes",
        "read_substance_use_records",
        "export_phi",
        "share_phi_externally",
    }
)


def make_hipaa_treating_provider_policy(
    escalate_external_share_to: str = "hipaa_privacy_officer",
) -> ActionPolicy:
    """
    Return an ``ActionPolicy`` for an AI agent assisting a treating provider.

    Treating providers have the broadest permitted access to ePHI under
    HIPAA's treatment operations exception (45 CFR § 164.506). This policy
    allows clinical record access but escalates any external disclosure attempt.

    :param escalate_external_share_to: Escalation target for external share actions.
    """
    return ActionPolicy(
        allowed_actions={
            "read_diagnosis",
            "read_treatment_notes",
            "read_prescription",
            "read_lab_results",
            "read_imaging_report",
            "read_medication_list",
            "create_clinical_note",
            "read_policy_document",
        },
        denied_actions={"export_phi", "share_phi_externally"},
        escalation_rules=[
            EscalationRule(
                condition="phi_external_disclosure",
                action_pattern="share",
                escalate_to=escalate_external_share_to,
            ),
        ],
    )


def make_hipaa_billing_staff_policy(
    escalate_clinical_access_to: str = "hipaa_privacy_officer",
) -> ActionPolicy:
    """
    Return an ``ActionPolicy`` for an AI agent assisting billing staff.

    Billing staff access is limited to the minimum ePHI necessary for payment
    operations under 45 CFR § 164.506(c). Clinical notes and mental health
    records are outside the scope of billing operations.

    :param escalate_clinical_access_to: Escalation target if the agent attempts
        to access clinical records outside the billing scope.
    """
    return ActionPolicy(
        allowed_actions={
            "read_diagnosis_codes",
            "read_procedure_codes",
            "read_insurance_information",
            "read_payment_record",
            "read_policy_document",
            "submit_claim",
        },
        denied_actions={
            "read_treatment_notes",
            "read_mental_health_notes",
            "read_substance_use_records",
            "read_imaging_report",
            "export_phi",
        },
        escalation_rules=[
            EscalationRule(
                condition="billing_clinical_access_attempt",
                action_pattern="read_diagnosis",
                escalate_to=escalate_clinical_access_to,
            ),
        ],
    )


def make_hipaa_researcher_policy(
    irb_approved_categories: set[str],
    escalate_to: str = "irb_compliance_officer",
) -> ActionPolicy:
    """
    Return an ``ActionPolicy`` for a research agent operating under an IRB protocol.

    Research access to ePHI is permitted under 45 CFR § 164.512(i) with an
    appropriate IRB authorization or waiver. This policy constrains the agent
    to only the ePHI categories covered by the IRB protocol.

    :param irb_approved_categories: Set of ePHI category action names approved
        under the IRB protocol (e.g. ``{"read_diagnosis_codes", "read_lab_results"}``).
    :param escalate_to: Escalation target for any access outside the approved set.
    """
    return ActionPolicy(
        allowed_actions=set(irb_approved_categories) | {"read_policy_document"},
        denied_actions={"export_phi", "share_phi_externally", "create_clinical_note"},
        escalation_rules=[
            EscalationRule(
                condition="research_scope_exceeded",
                action_pattern="",  # matches all — escalate anything outside allowed set
                escalate_to=escalate_to,
            ),
        ],
        require_all_allowed=True,
    )
