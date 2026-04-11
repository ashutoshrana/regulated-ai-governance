"""
FERPA (Family Educational Rights and Privacy Act) policy helpers.

20 U.S.C. § 1232g; implementing regulations at 34 CFR Part 99.

FERPA governs access to education records at institutions that receive
federal funding. For AI agent systems operating in higher-education
environments, the primary obligations are:

- Minimum disclosure: only the minimum necessary information is accessed.
- Access boundaries: one student's records may never be surfaced during
  a request made in the context of a different student's session.
- Disclosure log: 34 CFR § 99.32 requires a record of every disclosure.

This module provides pre-built ``ActionPolicy`` instances for the most
common FERPA-regulated agent scenarios.
"""

from __future__ import annotations

from regulated_ai_governance.policy import ActionPolicy, EscalationRule

# Actions that are restricted under FERPA's minimum-disclosure principle.
# AI agents should not execute these without explicit authorization context.
FERPA_HIGH_RISK_ACTIONS: frozenset[str] = frozenset(
    {
        "export_student_records",
        "share_records_externally",
        "read_counseling_notes",
        "read_disciplinary_records",
        "bulk_export",
        "cross_student_query",
    }
)

# Standard set of actions permitted for a student-facing enrollment assistant.
ENROLLMENT_ADVISOR_ALLOWED_ACTIONS: frozenset[str] = frozenset(
    {
        "read_enrollment_status",
        "read_academic_record",
        "read_course_schedule",
        "read_financial_record",
        "read_graduation_progress",
        "read_policy_document",
        "send_notification_to_self",
    }
)


def make_ferpa_student_policy(
    allowed_record_categories: set[str] | None = None,
    escalate_exports_to: str = "ferpa_compliance_officer",
    require_all_allowed: bool = True,
) -> ActionPolicy:
    """
    Return an ``ActionPolicy`` for a student-facing AI agent subject to FERPA.

    The policy:
    - Allows a standard set of read actions for a student's own records.
    - Denies actions that would access another student's records or perform
      bulk exports without an explicit disclosure basis.
    - Escalates any export action to the compliance officer.

    :param allowed_record_categories: Optional override for the set of
        record categories the agent may access. Defaults to
        ``ENROLLMENT_ADVISOR_ALLOWED_ACTIONS``.
    :param escalate_exports_to: Escalation target for export actions.
        Defaults to ``"ferpa_compliance_officer"``.
    :param require_all_allowed: If True (default), only listed actions
        are permitted. Set to False for advisory mode.
    :returns: A configured ``ActionPolicy`` instance.
    """
    allowed = set(allowed_record_categories or ENROLLMENT_ADVISOR_ALLOWED_ACTIONS)
    return ActionPolicy(
        allowed_actions=allowed,
        denied_actions=set(FERPA_HIGH_RISK_ACTIONS),
        escalation_rules=[
            EscalationRule(
                condition="ferpa_export_attempt",
                action_pattern="export",
                escalate_to=escalate_exports_to,
            ),
            EscalationRule(
                condition="ferpa_external_share_attempt",
                action_pattern="share",
                escalate_to=escalate_exports_to,
            ),
        ],
        require_all_allowed=require_all_allowed,
    )


def make_ferpa_advisor_policy(
    escalate_bulk_to: str = "ferpa_compliance_officer",
) -> ActionPolicy:
    """
    Return an ``ActionPolicy`` for an academic advisor agent subject to FERPA.

    Advisors have broader read access than students (they can read any
    student's records within their advising scope) but still cannot
    export or share records externally without a FERPA exception basis.

    :param escalate_bulk_to: Escalation target for bulk or export actions.
    """
    return ActionPolicy(
        allowed_actions={
            "read_student_academic_record",
            "read_student_enrollment_status",
            "read_student_graduation_progress",
            "read_student_course_schedule",
            "send_notification_to_student",
            "read_policy_document",
            "create_advising_note",
        },
        denied_actions={"cross_student_query", "bulk_export"},
        escalation_rules=[
            EscalationRule(
                condition="advisor_export_attempt",
                action_pattern="export",
                escalate_to=escalate_bulk_to,
            ),
        ],
    )
