"""
06_manufacturing_ot_governance.py — Multi-framework AI governance for
manufacturing and operational technology (OT) environments.

Demonstrates how ``GovernanceOrchestrator`` enforces three compliance frameworks
simultaneously for a predictive maintenance AI agent deployed in a chemical plant:

    Framework 1 — ISO/IEC 42001:2023 AI Management System.
                  Operating scope enforcement (A.6.2.10), deployment approval gate
                  (A.6.2.5), and human oversight for autonomous actuation (A.9.5).
                  Risk level: HIGH (process control system).

    Framework 2 — IEC 62443 Industrial Cybersecurity (Security Levels).
                  Zone/conduit model: the agent is authorized at Security Level 2
                  (authenticated access). Actions requiring SL-3 (authenticated +
                  integrity verified) or SL-4 (physically secured) are denied.
                  Zone boundary enforcement: data must not cross Process Control
                  Zone → Business Zone without an approved conduit.

    Framework 3 — DORA (EU Regulation 2022/2554) ICT Risk Management.
                  AI agents in financial entities (plant operator is listed on EU
                  exchanges) must have documented third-party ICT service providers
                  (Art. 28). Actions that invoke undocumented third-party ML models
                  are denied.

Deny-all aggregation: if ANY framework denies, the overall decision is DENY.

Scenarios
---------

  A. ``sensor_anomaly_detection``
     — Advisory-mode anomaly detection on sensor telemetry.
       All three frameworks permit → ALLOW.

  B. ``autonomous_valve_control``
     — Fully autonomous actuation of a process control valve without human review.
       ISO 42001 A.9.5: autonomous control requires human-in-loop (HIGH risk system).
       IEC 62443: valve controller is in SL-3 zone; agent has SL-2 clearance.
       → DENY (both ISO 42001 and IEC 62443 deny independently).

  C. ``third_party_ml_inference``
     — Inference against an undocumented third-party ML service.
       DORA Art. 28: third-party ICT service is not in the ICT service register.
       → DENY.

  D. ``maintenance_scheduling_recommendation``
     — Advisory recommendation for maintenance window scheduling.
       All three frameworks permit (advisory, documented, SL-2 asset zone) → ALLOW.

  E. ``cross_plant_data_sharing``
     — Sending process control telemetry to a cross-plant analytics platform.
       IEC 62443: data crosses from Process Control Zone to Business Zone without
       an approved conduit → DENY.

No external dependencies required.

Run:
    python examples/06_manufacturing_ot_governance.py
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
# Action catalogue — predictive maintenance AI agent
# ---------------------------------------------------------------------------

#: Advisory/monitoring actions safe at Security Level 2 within the Process
#: Monitoring Zone. ISO 42001 A.6.2.10: within the documented operating scope.
MONITORING_ZONE_ALLOWED: frozenset[str] = frozenset(
    {
        "sensor_anomaly_detection",
        "vibration_trend_analysis",
        "temperature_deviation_alert",
        "pressure_threshold_check",
        "read_historian_data",
        "query_asset_registry",
        "maintenance_scheduling_recommendation",
        "parts_inventory_query",
        "maintenance_work_order_create",
        "safety_interlock_status_read",
    }
)

#: Actions requiring Security Level 3 — authenticated access + message integrity
#: verification + protection against deliberate disruption. Reserved for
#: direct process control actuation (IEC 62443 SL-3 Control Zone).
SL3_CONTROL_ZONE_ACTIONS: frozenset[str] = frozenset(
    {
        "autonomous_valve_control",
        "emergency_shutdown_initiate",
        "process_setpoint_override",
        "safety_interlock_bypass",
        "pump_speed_adjustment",
        "pressure_relief_valve_actuation",
    }
)

#: Actions that cross zone boundaries — Process Control Zone → Business Zone.
#: Require an approved conduit with documented data-flow authorization
#: (IEC 62443 zone/conduit model, §3.2.4).
CROSS_ZONE_ACTIONS: frozenset[str] = frozenset(
    {
        "cross_plant_data_sharing",
        "export_telemetry_to_cloud",
        "send_process_data_to_erp",
        "publish_metrics_to_business_intelligence",
    }
)

#: Third-party ML inference actions that are NOT in the DORA ICT service register.
#: DORA Art. 28: organizations must maintain a register of all ICT third-party
#: service providers and assess their risk level before relying on them.
UNDOCUMENTED_THIRD_PARTY_ACTIONS: frozenset[str] = frozenset(
    {
        "third_party_ml_inference",
        "external_llm_api_call",
        "undocumented_saas_analytics",
    }
)

# ---------------------------------------------------------------------------
# Compliance audit log
# ---------------------------------------------------------------------------

compliance_log: list[dict[str, Any]] = []


def record_audit(report: Any) -> None:
    """Append the ComprehensiveAuditReport summary to the in-memory log."""
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


def build_iso42001_ot_policy() -> ActionPolicy:
    """
    ISO/IEC 42001:2023 operating-scope policy for a high-risk OT AI system.

    Controls applied:
    - A.6.2.10: Only monitoring-zone actions are within the documented operating
      scope. SL-3 control-zone and cross-zone actions are outside scope.
    - A.9.5: Autonomous actuation actions require human oversight — escalate to
      the process safety engineer before execution.

    Risk classification: HIGH — the AI system directly influences a process
    control environment and must maintain documented deployment approval.
    """
    return ActionPolicy(
        allowed_actions=set(MONITORING_ZONE_ALLOWED),
        denied_actions=set(SL3_CONTROL_ZONE_ACTIONS) | set(CROSS_ZONE_ACTIONS),
        escalation_rules=[
            EscalationRule(
                condition="autonomous_actuation_requires_human_oversight",
                action_pattern="control",
                escalate_to="process_safety_engineer",
            ),
            EscalationRule(
                condition="emergency_action_requires_human_confirmation",
                action_pattern="emergency",
                escalate_to="plant_control_room_operator",
            ),
        ],
    )


def build_iec62443_policy() -> ActionPolicy:
    """
    IEC 62443 Security Level policy for an OT environment.

    The predictive maintenance agent is authorized at Security Level 2
    (authenticated access, protection against inadvertent/casual violation).

    Actions in the SL-3 Control Zone require:
    - Authentication + authorization (SL-2) ✓
    - Message integrity protection via cryptographic means (SL-3) ✗ — not
      established for this agent deployment

    Actions crossing zone boundaries (Process Control → Business Zone) are
    denied in the absence of an approved conduit with documented data-flow
    authorization (IEC 62443 §3.2.4 zone/conduit model).
    """
    return ActionPolicy(
        allowed_actions=set(MONITORING_ZONE_ALLOWED),
        denied_actions=set(SL3_CONTROL_ZONE_ACTIONS) | set(CROSS_ZONE_ACTIONS),
        escalation_rules=[
            EscalationRule(
                condition="sl3_zone_access_requires_security_upgrade",
                action_pattern="valve",
                escalate_to="ot_security_team",
            ),
            EscalationRule(
                condition="zone_boundary_crossing_requires_conduit_approval",
                action_pattern="cross",
                escalate_to="ot_security_team",
            ),
        ],
    )


def build_dora_ot_policy() -> ActionPolicy:
    """
    DORA ICT risk management policy for an OT AI agent.

    Under DORA Art. 28, organizations must maintain a register of all ICT
    third-party service providers and assess their concentration risk before
    relying on them in operational processes.

    This policy denies any action that invokes a third-party ICT service
    (ML API, SaaS analytics) that has not been assessed and documented in
    the ICT service register. All monitoring-zone actions against internal,
    documented systems are permitted.
    """
    return ActionPolicy(
        allowed_actions=set(MONITORING_ZONE_ALLOWED),
        denied_actions=set(UNDOCUMENTED_THIRD_PARTY_ACTIONS),
        escalation_rules=[
            EscalationRule(
                condition="undocumented_third_party_ict_dependency",
                action_pattern="third_party",
                escalate_to="ict_risk_manager",
            ),
            EscalationRule(
                condition="undocumented_third_party_ict_dependency",
                action_pattern="external",
                escalate_to="ict_risk_manager",
            ),
        ],
    )


# ---------------------------------------------------------------------------
# Build the multi-framework orchestrator
# ---------------------------------------------------------------------------


def build_ot_orchestrator(*, audit_only: bool = False) -> GovernanceOrchestrator:
    """
    Assemble a GovernanceOrchestrator for the predictive maintenance AI agent.

    Three FrameworkGuards active simultaneously:
    - ISO/IEC 42001:2023 (block autonomous actuation; deny out-of-scope)
    - IEC 62443 SL-2 (deny SL-3 zone actions and zone boundary crossings)
    - DORA Art. 28 (deny undocumented third-party ICT dependencies)
    """
    iso42001_guard = GovernedActionGuard(
        policy=build_iso42001_ot_policy(),
        regulation="ISO_42001_AIMS",
        actor_id="pred_maintenance_agent_v1",
        audit_sink=None,
        block_on_escalation=True,
        raise_on_deny=False,
    )
    iec62443_guard = GovernedActionGuard(
        policy=build_iec62443_policy(),
        regulation="IEC_62443_SL2",
        actor_id="pred_maintenance_agent_v1",
        audit_sink=None,
        block_on_escalation=True,
        raise_on_deny=False,
    )
    dora_guard = GovernedActionGuard(
        policy=build_dora_ot_policy(),
        regulation="DORA_ART28",
        actor_id="pred_maintenance_agent_v1",
        audit_sink=None,
        block_on_escalation=True,
        raise_on_deny=False,
    )
    return GovernanceOrchestrator(
        framework_guards=[
            FrameworkGuard(regulation="ISO_42001_AIMS", guard=iso42001_guard),
            FrameworkGuard(regulation="IEC_62443_SL2", guard=iec62443_guard),
            FrameworkGuard(regulation="DORA_ART28", guard=dora_guard),
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
            actor_id="pred_maintenance_agent_v1",
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
    print("Manufacturing / OT — Multi-Framework AI Governance")
    print("  AI System  : Predictive Maintenance Agent v1")
    print("  Plant      : Chemical Process Facility — Reactor Line 3")
    print("  Frameworks : ISO 42001 AIMS | IEC 62443 SL-2 | DORA Art.28")
    print("=" * 68)

    orchestrator = build_ot_orchestrator()

    # ------------------------------------------------------------------
    # Scenario A — sensor anomaly detection (monitoring zone, advisory)
    # ------------------------------------------------------------------
    print("\n--- Scenario A: Advisory anomaly detection ---")
    run_scenario(
        orchestrator,
        action_name="sensor_anomaly_detection",
        execute_fn=lambda: {
            "anomaly_score": 0.82,
            "sensor_id": "PT-3042",
            "recommendation": "schedule_inspection",
            "confidence": 0.91,
        },
        description=(
            "Advisory anomaly detection on pressure sensor PT-3042. "
            "Monitoring zone, SL-2, documented model — all frameworks permit."
        ),
    )

    # ------------------------------------------------------------------
    # Scenario B — autonomous valve control (SL-3 zone, no human oversight)
    # ------------------------------------------------------------------
    print("\n--- Scenario B: Autonomous valve control (denied) ---")
    run_scenario(
        orchestrator,
        action_name="autonomous_valve_control",
        execute_fn=lambda: {"valve_id": "CV-3001", "position_pct": 45},
        description=(
            "Autonomous actuation of control valve CV-3001 to 45%% open. "
            "Denied: ISO 42001 A.9.5 (human oversight required for HIGH-risk "
            "autonomous actuation) + IEC 62443 (SL-3 zone, agent has SL-2 clearance)."
        ),
    )

    # ------------------------------------------------------------------
    # Scenario C — undocumented third-party ML inference
    # ------------------------------------------------------------------
    print("\n--- Scenario C: Undocumented third-party ML inference (denied) ---")
    run_scenario(
        orchestrator,
        action_name="third_party_ml_inference",
        execute_fn=lambda: {"prediction": "bearing_failure_in_72h"},
        description=(
            "Inference against an external ML API not registered in the DORA "
            "ICT service register. Denied: DORA Art. 28 (undocumented third-party "
            "ICT dependency — concentration risk not assessed)."
        ),
    )

    # ------------------------------------------------------------------
    # Scenario D — maintenance scheduling recommendation (advisory, allowed)
    # ------------------------------------------------------------------
    print("\n--- Scenario D: Maintenance scheduling recommendation ---")
    run_scenario(
        orchestrator,
        action_name="maintenance_scheduling_recommendation",
        execute_fn=lambda: {
            "asset_id": "PUMP-3005",
            "recommended_window": "2026-04-20T02:00Z",
            "estimated_downtime_hours": 4,
            "risk_if_deferred": "HIGH",
        },
        description=(
            "Advisory maintenance scheduling for centrifugal pump PUMP-3005. "
            "Advisory-mode, SL-2 asset registry zone, documented model — "
            "all frameworks permit."
        ),
    )

    # ------------------------------------------------------------------
    # Scenario E — cross-plant data sharing (zone boundary violation)
    # ------------------------------------------------------------------
    print("\n--- Scenario E: Cross-plant data sharing (zone boundary violation) ---")
    run_scenario(
        orchestrator,
        action_name="cross_plant_data_sharing",
        execute_fn=lambda: {
            "destination": "enterprise_analytics_platform",
            "records": 14400,
        },
        description=(
            "Sending 14,400 process control telemetry records to the "
            "enterprise analytics platform (Business Zone). "
            "Denied: IEC 62443 zone boundary — Process Control Zone → Business Zone "
            "without an approved conduit."
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
    print(f"\n  Per-action breakdown:")
    for entry in compliance_log:
        status = "ALLOW" if entry["overall_permitted"] else "DENY "
        print(f"    [{status}] {entry['action']}")

    print("\n  IEC 62443 zone coverage:")
    print("    Monitoring Zone (SL-2): sensor_anomaly_detection, "
          "maintenance_scheduling_recommendation")
    print("    Control Zone (SL-3): autonomous_valve_control — access denied")
    print("    Zone boundary (P.Control→Business): cross_plant_data_sharing — denied")

    print("\n  DORA Art. 28 ICT register:")
    print("    Documented    : internal historian, asset registry, work order system")
    print("    Undocumented  : third_party_ml_inference — denied")
    print("=" * 68)


if __name__ == "__main__":
    main()
