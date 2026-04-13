"""
07_government_ai_governance.py — CMMC Level 2 + FedRAMP Moderate + NIST 800-53
governance for a DoD federal procurement AI assistant.

Demonstrates how ``GovernanceOrchestrator`` enforces three compliance frameworks
simultaneously for an AI agent deployed on a Department of Defense supplier portal:

    Framework 1 — CMMC Level 2 (32 CFR Part 170, effective 2025).
                  Defense contractors handling CUI must achieve CMMC Level 2
                  certification (110 NIST SP 800-171 practices). The AI agent
                  may only access CUI on behalf of CMMC-certified entities.
                  Any attempt to access CUI by an uncertified entity is denied.

    Framework 2 — FedRAMP Moderate (NIST SP 800-37 / FedRAMP Authorization).
                  AI agent compute and data must remain within a FedRAMP-authorized
                  boundary. Actions that invoke external, non-FedRAMP cloud services
                  are denied regardless of user authorization level.

    Framework 3 — NIST 800-53 Rev 5 AC-2 / AC-3 (Account Management /
                  Access Enforcement). Agency-defined access rules enforced at
                  the policy layer. Privileged functions (admin operations,
                  system configuration) require separately authorized accounts
                  beyond normal user access.

Deny-all aggregation: if ANY framework denies, the overall decision is DENY.

Scenarios
---------

  A. ``query_contract_vehicle_data``
     — CMMC-certified contractor queries CUI-tagged contract vehicle data.
       All three frameworks permit → ALLOW.

  B. ``query_cui_technical_specs``
     — Uncertified vendor attempts to access CUI technical specifications.
       CMMC Level 2 framework denies (entity not certified) → DENY.

  C. ``invoke_external_cloud_api``
     — Agent invokes an external analytics service without FedRAMP ATO.
       FedRAMP framework denies → DENY.

  D. ``modify_system_configuration``
     — Standard user attempts a privileged administrative function.
       NIST 800-53 AC-3 framework denies (privileged access required) → DENY.

  E. ``query_public_procurement_notice``
     — Any user queries publicly available procurement notices.
       No CUI restrictions; FedRAMP source is authorized; standard role suffices.
       All three frameworks permit → ALLOW.

No external dependencies required.

Run:
    python examples/07_government_ai_governance.py
"""

from __future__ import annotations

import os
import sys
from typing import Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from regulated_ai_governance.agent_guard import GovernedActionGuard
from regulated_ai_governance.orchestrator import FrameworkGuard, GovernanceOrchestrator
from regulated_ai_governance.policy import ActionPolicy, EscalationRule

# ---------------------------------------------------------------------------
# Action catalogue — DoD procurement AI assistant
# ---------------------------------------------------------------------------

#: Actions permitted for a CMMC Level 2 certified entity accessing CUI.
#: Maps to 32 CFR Part 170 — Controlled Unclassified Information access
#: requiring 110 NIST SP 800-171 security practices.
CMMC_L2_ALLOWED_ACTIONS: frozenset[str] = frozenset(
    {
        "query_contract_vehicle_data",
        "query_solicitation_documents",
        "query_technical_requirements",
        "query_cui_technical_specs",
        "submit_proposal_response",
        "query_past_performance_data",
        "read_award_notification",
        "query_public_procurement_notice",
        "query_market_research",
    }
)

#: Actions permitted within a FedRAMP-authorized boundary.
#: External cloud service invocations without FedRAMP ATO are explicitly denied.
FEDRAMP_ALLOWED_ACTIONS: frozenset[str] = frozenset(
    {
        "query_contract_vehicle_data",
        "query_solicitation_documents",
        "query_technical_requirements",
        "query_cui_technical_specs",
        "submit_proposal_response",
        "query_past_performance_data",
        "read_award_notification",
        "query_public_procurement_notice",
        "query_market_research",
        "modify_system_configuration",  # FedRAMP permits privileged functions inside boundary
    }
)

#: Actions explicitly denied by FedRAMP — invoke non-authorized cloud services
FEDRAMP_DENIED_ACTIONS: frozenset[str] = frozenset(
    {
        "invoke_external_cloud_api",
        "send_data_to_commercial_saas",
        "call_non_fedramp_llm_api",
        "sync_to_non_authorized_cloud_storage",
    }
)

#: Actions permitted for standard agency user roles under NIST 800-53 AC-3.
#: Privileged functions require separately authorized (elevated) accounts.
NIST_80053_STANDARD_ROLE_ALLOWED: frozenset[str] = frozenset(
    {
        "query_contract_vehicle_data",
        "query_solicitation_documents",
        "query_technical_requirements",
        "query_cui_technical_specs",
        "submit_proposal_response",
        "query_past_performance_data",
        "read_award_notification",
        "query_public_procurement_notice",
        "query_market_research",
        "invoke_external_cloud_api",  # Role allows; FedRAMP blocks separately
    }
)

#: Privileged functions requiring elevated AC-3 authorization (admin accounts).
NIST_80053_PRIVILEGED_ONLY: frozenset[str] = frozenset(
    {
        "modify_system_configuration",
        "add_user_account",
        "remove_user_account",
        "reset_authentication_credentials",
        "export_full_audit_log",
        "modify_access_control_policy",
    }
)

# ---------------------------------------------------------------------------
# Compliance audit log
# ---------------------------------------------------------------------------

compliance_log: list[dict[str, Any]] = []


def record_audit(report: Any) -> None:
    compliance_log.append(
        {
            "report_id": report.report_id,
            "action": report.action_name,
            "overall_permitted": report.overall_permitted,
            "framework_count": len(report.framework_results),
        }
    )


# ---------------------------------------------------------------------------
# Policy factories
# ---------------------------------------------------------------------------


def build_cmmc_l2_policy() -> ActionPolicy:
    """
    CMMC Level 2 (32 CFR Part 170) policy for a DoD AI assistant.

    Only CMMC Level 2 certified entities may access CUI through the agent.
    Actions that access non-CUI (public procurement notices, market research)
    are permitted for all entity types.

    CMMC denial escalates to the contracting officer for remediation guidance
    (the entity must obtain CMMC certification before accessing CUI).
    """
    return ActionPolicy(
        allowed_actions=set(CMMC_L2_ALLOWED_ACTIONS),
        denied_actions=set(),  # No explicit denials — denial comes from "not in allowed" for CUI
        escalation_rules=[
            EscalationRule(
                condition="cmmc_cui_access_requires_certification",
                action_pattern="cui",
                escalate_to="contracting_officer",
            ),
            EscalationRule(
                condition="cmmc_technical_spec_requires_level2",
                action_pattern="technical",
                escalate_to="contracting_officer",
            ),
        ],
    )


def build_fedramp_policy() -> ActionPolicy:
    """
    FedRAMP Moderate authorization boundary policy.

    All permitted actions must operate within the FedRAMP-authorized boundary.
    Actions that explicitly invoke external, non-FedRAMP cloud services are
    denied regardless of user authorization level.

    Denial escalates to the ISO (Information System Owner) for ATO remediation.
    """
    return ActionPolicy(
        allowed_actions=set(FEDRAMP_ALLOWED_ACTIONS),
        denied_actions=set(FEDRAMP_DENIED_ACTIONS),
        escalation_rules=[
            EscalationRule(
                condition="non_fedramp_service_invocation",
                action_pattern="external",
                escalate_to="information_system_owner",
            ),
            EscalationRule(
                condition="non_fedramp_service_invocation",
                action_pattern="non_fedramp",
                escalate_to="information_system_owner",
            ),
            EscalationRule(
                condition="non_fedramp_data_exfiltration",
                action_pattern="commercial",
                escalate_to="information_system_owner",
            ),
        ],
    )


def build_nist_80053_policy() -> ActionPolicy:
    """
    NIST 800-53 Rev 5 AC-3 (Access Enforcement) policy for standard user roles.

    Standard agency users and contractors may perform query and submission
    actions. Privileged functions (account management, audit log export,
    system configuration) require separately authorized accounts.

    Privileged access denial escalates to the System Security Officer.
    """
    return ActionPolicy(
        allowed_actions=set(NIST_80053_STANDARD_ROLE_ALLOWED),
        denied_actions=set(NIST_80053_PRIVILEGED_ONLY),
        escalation_rules=[
            EscalationRule(
                condition="privileged_function_requires_elevated_account",
                action_pattern="modify",
                escalate_to="system_security_officer",
            ),
            EscalationRule(
                condition="privileged_function_requires_elevated_account",
                action_pattern="export",
                escalate_to="system_security_officer",
            ),
            EscalationRule(
                condition="privileged_function_requires_elevated_account",
                action_pattern="add_user",
                escalate_to="system_security_officer",
            ),
        ],
    )


# ---------------------------------------------------------------------------
# Build the multi-framework orchestrator
# ---------------------------------------------------------------------------


def build_procurement_orchestrator(*, audit_only: bool = False) -> GovernanceOrchestrator:
    """
    Assemble a GovernanceOrchestrator for the DoD procurement AI assistant.

    Three FrameworkGuards active simultaneously:
    - CMMC Level 2 (block CUI access for uncertified entities)
    - FedRAMP Moderate (deny non-FedRAMP cloud invocations)
    - NIST 800-53 AC-3 (deny privileged functions for standard roles)
    """
    cmmc_guard = GovernedActionGuard(
        policy=build_cmmc_l2_policy(),
        regulation="CMMC_LEVEL_2",
        actor_id="procurement_ai_agent_v1",
        audit_sink=None,
        block_on_escalation=True,
        raise_on_deny=False,
    )
    fedramp_guard = GovernedActionGuard(
        policy=build_fedramp_policy(),
        regulation="FEDRAMP_MODERATE",
        actor_id="procurement_ai_agent_v1",
        audit_sink=None,
        block_on_escalation=True,
        raise_on_deny=False,
    )
    nist_guard = GovernedActionGuard(
        policy=build_nist_80053_policy(),
        regulation="NIST_800-53_AC3",
        actor_id="procurement_ai_agent_v1",
        audit_sink=None,
        block_on_escalation=True,
        raise_on_deny=False,
    )
    return GovernanceOrchestrator(
        framework_guards=[
            FrameworkGuard(regulation="CMMC_LEVEL_2", guard=cmmc_guard),
            FrameworkGuard(regulation="FEDRAMP_MODERATE", guard=fedramp_guard),
            FrameworkGuard(regulation="NIST_800-53_AC3", guard=nist_guard),
        ],
        audit_sink=record_audit,
        audit_only=audit_only,
    )


# ---------------------------------------------------------------------------
# Scenario runner
# ---------------------------------------------------------------------------


def run_scenario(
    orchestrator: GovernanceOrchestrator,
    action_name: str,
    execute_fn: Any,
    description: str,
) -> None:
    print(f"\n  Action:      {action_name}")
    print(f"  Scenario:    {description}")

    try:
        result = orchestrator.guard(
            action_name=action_name,
            execute_fn=execute_fn,
            actor_id="procurement_ai_agent_v1",
        )
        report = orchestrator.last_report
        decision = "ALLOW" if (report and report.overall_permitted) else "DENY"
        print(f"  Decision:    {decision}")
        if result is not None:
            print(f"  Result:      {result}")
        if report:
            for fr in report.framework_results:
                fw_decision = "ALLOW" if fr["permitted"] else "DENY"
                esc = (
                    f" → escalate:{fr['escalation_target']}"
                    if fr.get("escalation_target")
                    else ""
                )
                print(f"  [{fr['regulation']:20s}] {fw_decision}{esc}")
    except PermissionError as exc:
        report = orchestrator.last_report
        print("  Decision:    DENY (PermissionError raised)")
        print(f"  Reason:      {str(exc)[:90]}")
        if report:
            for fr in report.framework_results:
                fw_decision = "ALLOW" if fr["permitted"] else "DENY"
                note = fr.get("denial_reason") or (
                    f"escalated → {fr.get('escalation_target')}"
                    if fr.get("escalation_target")
                    else "allowed"
                )
                print(
                    f"  [{fr['regulation']:20s}] {fw_decision} — {str(note)[:70]}"
                )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    print("=" * 68)
    print("Government AI Governance — CMMC L2 + FedRAMP Moderate + NIST 800-53")
    print("  System     : DoD Procurement AI Assistant")
    print("  Portal     : SBIR/STTR Supplier Portal — Army Medical R&D")
    print("  Frameworks : CMMC Level 2 | FedRAMP Moderate | NIST 800-53 AC-3")
    print("=" * 68)

    orchestrator = build_procurement_orchestrator()

    # ------------------------------------------------------------------
    # Scenario A — CMMC-certified contractor queries contract vehicle data
    # ------------------------------------------------------------------
    print("\n--- Scenario A: Certified contractor queries CUI contract data ---")
    run_scenario(
        orchestrator,
        action_name="query_contract_vehicle_data",
        execute_fn=lambda: {
            "vehicles": ["W81XWH-26-R-0012", "W81XWH-26-R-0015"],
            "total_value": "$24.6M",
            "cui_category": "CUI//PROC",
        },
        description=(
            "CMMC Level 2 certified contractor queries contract vehicle registry. "
            "CUI//PROC data; within FedRAMP boundary; standard role. All permit."
        ),
    )

    # ------------------------------------------------------------------
    # Scenario B — Uncertified vendor attempts CUI technical specs
    # ------------------------------------------------------------------
    print("\n--- Scenario B: Uncertified vendor attempts CUI access ---")

    # Override the CMMC policy to simulate uncertified entity
    # (denied because CMMC requires certification for CUI technical specs)
    from regulated_ai_governance.policy import ActionPolicy, EscalationRule

    uncertified_cmmc_policy = ActionPolicy(
        allowed_actions={"query_public_procurement_notice", "query_market_research"},
        # CUI actions removed — entity is not CMMC certified
        denied_actions=set(),
        escalation_rules=[
            EscalationRule(
                condition="cmmc_certification_required",
                action_pattern="cui",
                escalate_to="contracting_officer",
            ),
        ],
    )
    uncertified_guard = GovernedActionGuard(
        policy=uncertified_cmmc_policy,
        regulation="CMMC_LEVEL_2",
        actor_id="uncertified_vendor_agent",
        block_on_escalation=True,
        raise_on_deny=False,
    )
    uncertified_orch = GovernanceOrchestrator(
        framework_guards=[
            FrameworkGuard(regulation="CMMC_LEVEL_2", guard=uncertified_guard),
            FrameworkGuard(
                regulation="FEDRAMP_MODERATE",
                guard=GovernedActionGuard(
                    policy=build_fedramp_policy(),
                    regulation="FEDRAMP_MODERATE",
                    actor_id="uncertified_vendor_agent",
                    block_on_escalation=True,
                ),
            ),
            FrameworkGuard(
                regulation="NIST_800-53_AC3",
                guard=GovernedActionGuard(
                    policy=build_nist_80053_policy(),
                    regulation="NIST_800-53_AC3",
                    actor_id="uncertified_vendor_agent",
                    block_on_escalation=True,
                ),
            ),
        ],
        audit_sink=record_audit,
    )
    run_scenario(
        uncertified_orch,
        action_name="query_cui_technical_specs",
        execute_fn=lambda: {"specs": "...CUI//CTI technical data..."},
        description=(
            "Vendor without CMMC Level 2 certification attempts to access "
            "CUI//CTI technical specifications. Denied: CMMC requires certification."
        ),
    )

    # ------------------------------------------------------------------
    # Scenario C — Non-FedRAMP cloud service invocation
    # ------------------------------------------------------------------
    print("\n--- Scenario C: Non-FedRAMP external cloud API invocation ---")
    run_scenario(
        orchestrator,
        action_name="invoke_external_cloud_api",
        execute_fn=lambda: {"response": "...external analytics result..."},
        description=(
            "AI agent invokes an external commercial analytics API without FedRAMP ATO. "
            "Denied: FedRAMP Moderate boundary — non-authorized cloud service invocation."
        ),
    )

    # ------------------------------------------------------------------
    # Scenario D — Privileged function without elevated account
    # ------------------------------------------------------------------
    print("\n--- Scenario D: Privileged system configuration without elevated account ---")
    run_scenario(
        orchestrator,
        action_name="modify_system_configuration",
        execute_fn=lambda: {"config": "rate_limit=500", "applied": True},
        description=(
            "Standard user role attempts to modify system configuration. "
            "Denied: NIST 800-53 AC-3 — privileged function requires separate "
            "elevated account authorization."
        ),
    )

    # ------------------------------------------------------------------
    # Scenario E — Public procurement notice (no CUI, always allowed)
    # ------------------------------------------------------------------
    print("\n--- Scenario E: Public procurement notice (no CUI restrictions) ---")
    run_scenario(
        orchestrator,
        action_name="query_public_procurement_notice",
        execute_fn=lambda: {
            "notices": ["W81XWH-26-R-0012 Sources Sought"],
            "source": "sam.gov public posting",
            "cui_category": "PUBLIC",
        },
        description=(
            "Any user queries publicly available SAM.gov procurement notices. "
            "No CUI restrictions; no FedRAMP source restriction for public data; "
            "standard role suffices. All frameworks permit."
        ),
    )

    # ------------------------------------------------------------------
    # Audit summary
    # ------------------------------------------------------------------
    print("\n" + "=" * 68)
    print("Compliance Audit Summary")
    print("=" * 68)
    allowed = sum(1 for e in compliance_log if e["overall_permitted"])
    denied = sum(1 for e in compliance_log if not e["overall_permitted"])
    print(f"  Total evaluations : {len(compliance_log)}")
    print(f"  Allowed           : {allowed}")
    print(f"  Denied            : {denied}")
    for entry in compliance_log:
        status = "ALLOW" if entry["overall_permitted"] else "DENY "
        print(f"    [{status}] {entry['action']}")
    print("=" * 68)


if __name__ == "__main__":
    main()
