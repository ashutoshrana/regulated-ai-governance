"""
05_healthcare_ai_governance.py — Multi-framework AI governance for clinical decision support.

Demonstrates how ``GovernanceOrchestrator`` enforces three compliance frameworks
simultaneously for an ICU clinical decision support (CDS) agent:

    Framework 1 — HIPAA 45 CFR § 164.502(b): Minimum-necessary ePHI access.
                  Only treating-provider actions are permitted; external disclosure
                  is explicitly denied.

    Framework 2 — NIST AI RMF AI 600-1: High-risk AI in clinical settings requires
                  human oversight for any action that produces a clinical recommendation.
                  Escalation target: clinical_reviewer.

    Framework 3 — EU AI Act Art. 6 / Annex III: Clinical decision support is a
                  high-risk AI system; autonomous treatment decisions without
                  a qualified person in the loop are prohibited.

Deny-all aggregation: if ANY framework denies, the overall decision is DENY.

Scenarios
---------

  A. ``read_vitals``         — allowed by all three frameworks → ALLOW
  B. ``recommend_medication_dosage``
                             — HIPAA allows; NIST + EU trigger mandatory escalation
                               with block_on_escalation=True → DENY (human review required)
  C. ``share_phi_externally``
                             — explicitly denied by HIPAA → DENY immediately
                               (other frameworks not needed to reach the deny outcome)
  D. ``create_clinical_note``
                             — allowed by all three frameworks → ALLOW
  E. Audit-only mode         — all four actions evaluated without blocking;
                               full ``ComprehensiveAuditReport`` emitted per evaluation

No external dependencies required.

Run:
    python examples/05_healthcare_ai_governance.py
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
# Clinical action catalogue
# ---------------------------------------------------------------------------

#: Actions permitted for an AI agent operating under the treating-provider
#: exception (45 CFR § 164.506) — minimum necessary for ICU care coordination.
HIPAA_ICU_ALLOWED_ACTIONS: frozenset[str] = frozenset(
    {
        "read_vitals",
        "read_diagnosis",
        "read_treatment_notes",
        "read_lab_results",
        "read_imaging_report",
        "read_medication_list",
        "read_allergy_record",
        "query_drug_interactions",
        "create_clinical_note",
        "read_policy_document",
        "recommend_medication_dosage",
    }
)

#: Actions that access or transmit ePHI outside the covered-entity boundary.
HIPAA_ICU_DENIED_ACTIONS: frozenset[str] = frozenset(
    {
        "share_phi_externally",
        "export_phi",
        "disclose_phi_to_non_covered_entity",
        "send_phi_to_insurance_without_consent",
    }
)

#: Actions that generate a clinical recommendation — require human oversight
#: per NIST AI 600-1 (Human-AI Configuration risk) and EU AI Act Art. 14.
CLINICAL_RECOMMENDATION_ACTIONS: frozenset[str] = frozenset(
    {
        "recommend_medication_dosage",
        "recommend_diagnostic_test",
        "recommend_treatment_plan",
        "recommend_surgical_intervention",
    }
)

#: EU AI Act Art. 5 prohibited practices — unconditional denial regardless of
#: other policy settings.
EU_AI_ACT_PROHIBITED: frozenset[str] = frozenset(
    {
        "autonomous_treatment_decision_without_oversight",
        "emotion_recognition_clinical_staff",
        "patient_trustworthiness_scoring",
        "subliminal_clinical_manipulation",
    }
)

# ---------------------------------------------------------------------------
# Compliance audit log
# ---------------------------------------------------------------------------

compliance_log: list[dict[str, Any]] = []


def record_audit(report: Any) -> None:
    """Store the ComprehensiveAuditReport in the in-memory compliance log."""
    compliance_log.append(
        {
            "report_id": report.report_id,
            "action": report.action_name,
            "overall_permitted": report.overall_permitted,
            "framework_count": len(report.framework_results),
        }
    )


# ---------------------------------------------------------------------------
# Policy factories — one per compliance framework
# ---------------------------------------------------------------------------


def build_hipaa_icu_policy() -> ActionPolicy:
    """
    HIPAA minimum-necessary policy for an ICU CDS agent.

    Treating providers may access all clinical record types under 45 CFR
    § 164.506. External disclosure is explicitly denied; any share attempt
    escalates to the HIPAA Privacy Officer.
    """
    return ActionPolicy(
        allowed_actions=set(HIPAA_ICU_ALLOWED_ACTIONS),
        denied_actions=set(HIPAA_ICU_DENIED_ACTIONS),
        escalation_rules=[
            EscalationRule(
                condition="external_phi_disclosure",
                action_pattern="share",
                escalate_to="hipaa_privacy_officer",
            ),
            EscalationRule(
                condition="phi_export_attempt",
                action_pattern="export",
                escalate_to="hipaa_privacy_officer",
            ),
        ],
    )


def build_nist_ai_rmf_policy() -> ActionPolicy:
    """
    NIST AI RMF AI 600-1 policy for a high-risk clinical AI system.

    Any action that produces a clinical recommendation triggers the MANAGE
    function — human oversight is required before the recommendation is acted
    upon (Human-AI Configuration risk, AI 600-1 §2.6).
    """
    return ActionPolicy(
        allowed_actions=set(HIPAA_ICU_ALLOWED_ACTIONS),  # same action universe
        denied_actions=set(EU_AI_ACT_PROHIBITED),  # also block EU prohibited practices
        escalation_rules=[
            EscalationRule(
                condition="clinical_recommendation_requires_human_review",
                action_pattern="recommend",
                escalate_to="clinical_reviewer",
            ),
        ],
    )


def build_eu_ai_act_policy() -> ActionPolicy:
    """
    EU AI Act high-risk policy for a clinical decision support system.

    Under Annex III point 5(a), AI systems used in clinical decision support
    are classified as HIGH_RISK. Article 14 requires that humans have effective
    oversight and can intervene before any high-risk output is applied.

    Any recommendation action triggers mandatory routing to the human oversight
    controller. Prohibited practices (Art. 5) are explicitly denied.
    """
    return ActionPolicy(
        allowed_actions=set(HIPAA_ICU_ALLOWED_ACTIONS),
        denied_actions=set(EU_AI_ACT_PROHIBITED),
        escalation_rules=[
            EscalationRule(
                condition="high_risk_ai_output_requires_oversight",
                action_pattern="recommend",
                escalate_to="human_oversight_controller",
            ),
        ],
    )


# ---------------------------------------------------------------------------
# Build the multi-framework orchestrator
# ---------------------------------------------------------------------------


def build_cds_orchestrator(*, audit_only: bool = False) -> GovernanceOrchestrator:
    """
    Assemble a GovernanceOrchestrator for the ICU CDS agent.

    Three FrameworkGuards are active simultaneously:
    - HIPAA 45 CFR § 164 (block_on_escalation=True for external disclosure)
    - NIST AI RMF AI 600-1 (block_on_escalation=True for recommendation actions)
    - EU AI Act HIGH_RISK (block_on_escalation=True for recommendation actions)
    """
    hipaa_guard = GovernedActionGuard(
        policy=build_hipaa_icu_policy(),
        regulation="HIPAA_45CFR164",
        actor_id="cds_icu_agent_v2",
        audit_sink=None,  # orchestrator handles unified audit
        block_on_escalation=True,
        raise_on_deny=False,
    )
    nist_guard = GovernedActionGuard(
        policy=build_nist_ai_rmf_policy(),
        regulation="NIST_AI_RMF_600-1",
        actor_id="cds_icu_agent_v2",
        audit_sink=None,
        block_on_escalation=True,  # escalated recommendations require human sign-off
        raise_on_deny=False,
    )
    eu_guard = GovernedActionGuard(
        policy=build_eu_ai_act_policy(),
        regulation="EU_AI_ACT_HIGH_RISK",
        actor_id="cds_icu_agent_v2",
        audit_sink=None,
        block_on_escalation=True,  # Art. 14 human oversight — block until confirmed
        raise_on_deny=False,
    )
    return GovernanceOrchestrator(
        framework_guards=[
            FrameworkGuard(regulation="HIPAA_45CFR164", guard=hipaa_guard),
            FrameworkGuard(regulation="NIST_AI_RMF_600-1", guard=nist_guard),
            FrameworkGuard(regulation="EU_AI_ACT_HIGH_RISK", guard=eu_guard),
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
            actor_id="icu_nurse_station_12",
        )
        report = orchestrator.last_report
        decision = "ALLOW" if (report and report.overall_permitted) else "DENY"
        print(f"  Decision:    {decision}")
        if result is not None:
            print(f"  Result:      {result}")
        if report:
            for fr in report.framework_results:
                fw_decision = "ALLOW" if fr["permitted"] else "DENY"
                esc = f" → escalate:{fr['escalation_target']}" if fr.get("escalation_target") else ""
                print(f"  [{fr['regulation']:24s}] {fw_decision}{esc}")
    except PermissionError as exc:
        report = orchestrator.last_report
        print("  Decision:    DENY (PermissionError raised)")
        print(f"  Reason:      {exc}")
        if report:
            for fr in report.framework_results:
                fw_decision = "ALLOW" if fr["permitted"] else "DENY"
                note = fr.get("denial_reason") or (
                    f"escalated → {fr.get('escalation_target')}" if fr.get("escalation_target") else "allowed"
                )
                print(f"  [{fr['regulation']:24s}] {fw_decision} — {str(note)[:70]}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    print("=" * 70)
    print("Healthcare AI Governance — ICU Clinical Decision Support Agent")
    print("Frameworks: HIPAA 45 CFR § 164 + NIST AI RMF AI 600-1 + EU AI Act")
    print("=" * 70)

    # ------------------------------------------------------------------
    # Standard (blocking) orchestrator
    # ------------------------------------------------------------------
    orchestrator = build_cds_orchestrator(audit_only=False)

    print("\n── Scenario A: Read patient vitals ──────────────────────────────────")
    run_scenario(
        orchestrator,
        action_name="read_vitals",
        execute_fn=lambda: {"heart_rate": 88, "bp": "120/80", "spo2": 98},
        description="Nurse queries real-time vitals — permitted under all three frameworks",
    )

    print("\n── Scenario B: Recommend medication dosage ──────────────────────────")
    run_scenario(
        orchestrator,
        action_name="recommend_medication_dosage",
        execute_fn=lambda: {"drug": "norepinephrine", "dose_mcg_kg_min": 0.1},
        description=(
            "CDS agent generates a vasopressor recommendation — "
            "NIST AI RMF + EU AI Act require human review before action is applied"
        ),
    )

    print("\n── Scenario C: Attempt to share PHI externally ──────────────────────")
    run_scenario(
        orchestrator,
        action_name="share_phi_externally",
        execute_fn=lambda: {"target": "insurance_broker", "payload": "patient_record_019"},
        description="Agent attempts to transmit ePHI outside covered-entity boundary — HIPAA denies immediately",
    )

    print("\n── Scenario D: Create clinical note ─────────────────────────────────")
    run_scenario(
        orchestrator,
        action_name="create_clinical_note",
        execute_fn=lambda: {"note_id": "note_2026_001", "status": "draft_created"},
        description="Nurse creates a care note — permitted under all three frameworks, no escalation",
    )

    # ------------------------------------------------------------------
    # Audit-only mode — same actions, no blocking
    # ------------------------------------------------------------------
    print("\n\n── Scenario E: Audit-only mode ──────────────────────────────────────")
    print("  All actions evaluated against all three frameworks, none blocked.")
    print("  Useful for shadow-mode compliance evaluation during CDS rollout.")
    audit_orchestrator = build_cds_orchestrator(audit_only=True)

    for action in ["read_vitals", "recommend_medication_dosage", "share_phi_externally"]:
        audit_orchestrator.guard(
            action_name=action,
            execute_fn=lambda: "audit_only",
            actor_id="cds_audit_shadow",
        )

    if audit_orchestrator.last_report:
        last = audit_orchestrator.last_report
        print(f"\n  Last audit report: {last.report_id}")
        print(f"  Framework coverage: {[fr['regulation'] for fr in last.framework_results]}")
        print("  (All actions completed — audit-only mode does not block.)")

    # ------------------------------------------------------------------
    # Compliance log summary
    # ------------------------------------------------------------------
    print("\n\n── Compliance Audit Log ─────────────────────────────────────────────")
    print(f"  {'Action':<40} {'Decision':<10} {'Frameworks'}")
    print(f"  {'-' * 38} {'-' * 8} {'-' * 12}")
    for entry in compliance_log:
        decision = "ALLOW" if entry["overall_permitted"] else "DENY"
        print(f"  {entry['action']:<40} {decision:<10} {entry['framework_count']} frameworks evaluated")

    print("\n\n── Governance Design Notes ──────────────────────────────────────────")
    notes = [
        "1. Deny-all aggregation: one DENY from any framework stops the action.",
        "2. HIPAA minimum-necessary: allowed_actions mirrors treating-provider scope only.",
        "3. NIST AI RMF: 'recommend_*' actions trigger MANAGE function (human oversight).",
        "4. EU AI Act Art. 14: CDS system is HIGH_RISK; block_on_escalation=True.",
        "5. Audit-only mode enables shadow compliance evaluation before enforcement go-live.",
    ]
    for note in notes:
        print(f"  {note}")

    print()


if __name__ == "__main__":
    main()
