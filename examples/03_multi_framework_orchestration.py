"""
03_multi_framework_orchestration.py
====================================
Multi-framework governance orchestration with deny-all aggregation.

Demonstrates ``GovernanceOrchestrator`` evaluating an agent action against
FERPA + HIPAA + ISO 42001 simultaneously, with a ``ComprehensiveAuditReport``
capturing every framework's individual decision.

Run:
    python examples/03_multi_framework_orchestration.py
"""

from __future__ import annotations

from regulated_ai_governance import (
    ActionPolicy,
    ComprehensiveAuditReport,
    FrameworkGuard,
    GovernanceOrchestrator,
    GovernedActionGuard,
)
from regulated_ai_governance.policy import EscalationRule
from regulated_ai_governance.regulations.iso42001 import (
    ISO42001GovernancePolicy,
    ISO42001OperatingScope,
)


def main() -> None:
    # -------------------------------------------------------------------
    # 1. Build per-framework guards
    # -------------------------------------------------------------------

    # FERPA guard: advisor may read transcripts and enrollment status
    ferpa_guard = GovernedActionGuard(
        policy=ActionPolicy(
            allowed_actions={"read_transcript", "read_enrollment_status"},
            escalation_rules=[
                EscalationRule(
                    condition="transcript_export",
                    action_pattern="export",
                    escalate_to="registrar_compliance_queue",
                )
            ],
        ),
        regulation="FERPA",
        actor_id="advisor_007",
    )

    # HIPAA guard: advisor does NOT have access to health records
    hipaa_guard = GovernedActionGuard(
        policy=ActionPolicy(
            allowed_actions={"read_enrollment_status"},  # read_transcript not in PHI scope
            denied_actions={"read_health_record", "read_medication"},
        ),
        regulation="HIPAA",
        actor_id="advisor_007",
    )

    # ISO 42001 guard: operating scope permits academic assistant actions
    iso42001_scope = ISO42001OperatingScope(
        system_id="student_advisor_ai_v2",
        permitted_use_cases={
            "read_transcript",
            "read_enrollment_status",
            "answer_academic_question",
        },
        prohibited_use_cases={
            "generate_legal_advice",
            "make_admissions_decision",
        },
        deployment_approved=True,
        deployment_approver="cto_alice",
        human_oversight_required_for={"generate_recommendation_letter"},
    )
    iso42001_policy = ISO42001GovernancePolicy(
        scope=iso42001_scope,
        session_id="sess_iso42001_demo",
    )

    # Wrap ISO 42001 as a GovernedActionGuard using evaluate hook
    # (ISO 42001 has its own evaluation path — we bridge it via a custom guard)
    class ISO42001Guard(GovernedActionGuard):
        def __init__(self, iso_policy: ISO42001GovernancePolicy) -> None:
            from regulated_ai_governance.policy import ActionPolicy

            super().__init__(
                policy=ActionPolicy(allowed_actions=set()),
                regulation="ISO_42001",
                actor_id="advisor_007",
            )
            self._iso = iso_policy

        def evaluate(self, action_name, context=None):  # type: ignore[override]
            from regulated_ai_governance.policy import PolicyDecision

            decision = self._iso.evaluate_action(action_name, context=context)
            return PolicyDecision(
                permitted=decision.permitted,
                denial_reason=decision.denial_reason,
                escalation=(
                    EscalationRule(
                        condition="human_oversight",
                        action_pattern=action_name,
                        escalate_to="human_reviewer",
                    )
                    if decision.human_oversight_required
                    else None
                ),
            )

    iso42001_guard = ISO42001Guard(iso_policy=iso42001_policy)

    # -------------------------------------------------------------------
    # 2. Build the orchestrator
    # -------------------------------------------------------------------
    audit_log: list[ComprehensiveAuditReport] = []

    orchestrator = GovernanceOrchestrator(
        framework_guards=[
            FrameworkGuard(regulation="FERPA", guard=ferpa_guard),
            FrameworkGuard(regulation="HIPAA", guard=hipaa_guard),
            FrameworkGuard(regulation="ISO_42001", guard=iso42001_guard),
        ],
        audit_sink=audit_log.append,
        audit_only=False,
    )

    print("=" * 60)
    print("Multi-Framework Governance Orchestration Demo")
    print("=" * 60)
    print(f"Active frameworks: {orchestrator.active_regulations}\n")

    # -------------------------------------------------------------------
    # 3. Permitted action: read_transcript
    # -------------------------------------------------------------------
    print("--- Action: read_transcript ---")
    result = orchestrator.guard(
        action_name="read_transcript",
        execute_fn=lambda: {"student_id": "stu_alice", "gpa": 3.9, "credits": 45},
        actor_id="advisor_007",
        context={"session_id": "sess_001", "channel": "web_advisor_portal"},
    )
    print(f"Result: {result}")
    print()
    print(orchestrator.last_report.to_compliance_summary())
    print()

    # -------------------------------------------------------------------
    # 4. Denied action: HIPAA blocks read_transcript (not in HIPAA scope)
    # -------------------------------------------------------------------
    print("--- Action: read_health_record (HIPAA deny) ---")
    result = orchestrator.guard(
        action_name="read_health_record",
        execute_fn=lambda: {"diagnosis": "n/a"},
        actor_id="advisor_007",
        context={"session_id": "sess_002"},
    )
    print(f"Result: {result}")
    print()
    print(orchestrator.last_report.to_compliance_summary())
    print()

    # -------------------------------------------------------------------
    # 5. ISO 42001 blocks: action outside permitted use
    # -------------------------------------------------------------------
    print("--- Action: generate_legal_advice (ISO 42001 prohibited) ---")
    result = orchestrator.guard(
        action_name="generate_legal_advice",
        execute_fn=lambda: "Legal advice text...",
        actor_id="advisor_007",
        context={"session_id": "sess_003"},
    )
    print(f"Result: {result}")
    print()
    print(orchestrator.last_report.to_compliance_summary())
    print()

    # -------------------------------------------------------------------
    # 6. Audit log summary
    # -------------------------------------------------------------------
    print("=" * 60)
    print(f"Total audit records: {len(audit_log)}")
    for i, report in enumerate(audit_log, 1):
        status = "PERMIT" if report.overall_permitted else "DENY"
        denied_by = ", ".join(sorted(report.frameworks_denied)) or "none"
        print(f"  [{i}] {report.action_name:<30} → {status}  (denied by: {denied_by})")
    print()
    print("SHA-256 tamper-evidence hashes:")
    for i, report in enumerate(audit_log, 1):
        print(f"  [{i}] {report.content_hash()[:16]}...")


if __name__ == "__main__":
    main()
