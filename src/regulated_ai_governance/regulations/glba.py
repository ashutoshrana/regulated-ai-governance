"""
GLBA (Gramm-Leach-Bliley Act) Safeguards Rule policy helpers.

15 U.S.C. § 6801–6809; FTC Safeguards Rule at 16 CFR Part 314.

The GLBA Safeguards Rule requires financial institutions to develop, implement,
and maintain a comprehensive information security program to protect customer
financial information (NNPI — non-public personal information). For AI agent
systems that access customer financial records, the safeguards rule's access
control requirements (16 CFR § 314.4(c)) constrain what agents may access and
what actions they may take on customer data.

This module provides pre-built ``ActionPolicy`` instances for common
GLBA-regulated agent scenarios.
"""

from __future__ import annotations

from regulated_ai_governance.policy import ActionPolicy, EscalationRule

# Non-public personal information (NNPI) categories that require GLBA protection.
GLBA_NNPI_ACTION_PATTERNS: frozenset[str] = frozenset(
    {
        "read_account_number",
        "read_social_security_number",
        "read_credit_score",
        "read_loan_details",
        "read_transaction_history",
        "export_customer_financial_data",
        "share_nnpi_externally",
    }
)


def make_glba_customer_service_policy(
    escalate_nnpi_export_to: str = "glba_compliance_officer",
) -> ActionPolicy:
    """
    Return an ``ActionPolicy`` for a customer-service AI agent at a financial institution.

    Customer service agents need access to account status and product information
    to serve customers, but must not export or externally share NNPI.

    :param escalate_nnpi_export_to: Escalation target for any export or external
        share attempt involving customer financial data.
    """
    return ActionPolicy(
        allowed_actions={
            "read_account_balance",
            "read_account_status",
            "read_recent_transactions",
            "read_product_information",
            "read_branch_locator",
            "send_notification_to_customer",
            "read_policy_document",
        },
        denied_actions={
            "read_social_security_number",
            "export_customer_financial_data",
            "share_nnpi_externally",
        },
        escalation_rules=[
            EscalationRule(
                condition="nnpi_export_attempt",
                action_pattern="export",
                escalate_to=escalate_nnpi_export_to,
            ),
            EscalationRule(
                condition="nnpi_external_share_attempt",
                action_pattern="share_nnpi",
                escalate_to=escalate_nnpi_export_to,
            ),
        ],
    )


def make_glba_loan_officer_policy(
    escalate_to: str = "glba_compliance_officer",
) -> ActionPolicy:
    """
    Return an ``ActionPolicy`` for a loan-officer AI agent at a financial institution.

    Loan officers have broader access to NNPI for underwriting purposes,
    but cross-customer queries and bulk exports remain escalated.

    :param escalate_to: Escalation target for bulk exports or cross-customer queries.
    """
    return ActionPolicy(
        allowed_actions={
            "read_credit_score",
            "read_income_verification",
            "read_loan_application",
            "read_employment_history",
            "read_account_balance",
            "read_loan_details",
            "create_loan_decision_note",
            "read_policy_document",
        },
        denied_actions={
            "bulk_export_customer_data",
            "cross_customer_query",
            "share_nnpi_externally",
        },
        escalation_rules=[
            EscalationRule(
                condition="loan_officer_bulk_export",
                action_pattern="bulk_export",
                escalate_to=escalate_to,
            ),
        ],
    )
