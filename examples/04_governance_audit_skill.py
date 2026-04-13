"""
04_governance_audit_skill.py
=============================
Comprehensive governance audit skill — all channels, all scenarios.

Demonstrates ``GovernanceAuditSkill``:
  1. Direct Python API: audit_action() + audit_retrieval()
  2. Factory constructors: for_education(), for_healthcare(), for_enterprise()
  3. Per-framework scoping: evaluate only a subset of configured frameworks
  4. Audit-only shadow mode: evaluate without blocking

Run:
    python examples/04_governance_audit_skill.py
"""

from __future__ import annotations

from regulated_ai_governance import (
    ActionPolicy,
    ComprehensiveAuditReport,
    FrameworkConfig,
    GovernanceAuditSkill,
    GovernanceConfig,
    GovernedActionGuard,
)

# ---------------------------------------------------------------------------
# Shared audit log
# ---------------------------------------------------------------------------

audit_log: list[ComprehensiveAuditReport] = []


def _log(report: ComprehensiveAuditReport) -> None:
    audit_log.append(report)


# ---------------------------------------------------------------------------
# Demo 1: Education — FERPA enforcement via factory
# ---------------------------------------------------------------------------


def demo_education() -> None:
    print("=" * 60)
    print("Demo 1: Education — FERPA via GovernanceAuditSkill.for_education()")
    print("=" * 60)

    skill = GovernanceAuditSkill.for_education(
        actor_id="advisor_007",
        allowed_actions={
            "read_transcript",
            "read_enrollment_status",
            "answer_academic_question",
        },
        audit_sink=_log,
    )

    print(f"Active frameworks: {skill.active_frameworks}")
    print()

    # Permitted
    result = skill.audit_action(
        action_name="read_transcript",
        execute_fn=lambda: {"student_id": "stu_alice", "gpa": 3.9},
        actor_id="advisor_007",
        context={"session_id": "sess_edu_001"},
    )
    print(f"read_transcript → {result}")
    print(skill.last_report.to_compliance_summary())
    print()

    # Denied
    result = skill.audit_action(
        action_name="delete_student_record",
        execute_fn=lambda: "DELETED",
        actor_id="advisor_007",
        context={"session_id": "sess_edu_002"},
    )
    print(f"delete_student_record → {type(result).__name__} (denied)")
    print()


# ---------------------------------------------------------------------------
# Demo 2: Healthcare — HIPAA enforcement via factory
# ---------------------------------------------------------------------------


def demo_healthcare() -> None:
    print("=" * 60)
    print("Demo 2: Healthcare — HIPAA via GovernanceAuditSkill.for_healthcare()")
    print("=" * 60)

    skill = GovernanceAuditSkill.for_healthcare(
        actor_id="nurse_abc",
        audit_sink=_log,
    )

    retrieved_docs = [
        {"patient_id": "P001", "category": "vitals", "content": "BP 120/80"},
        {"patient_id": "P002", "category": "labs", "content": "CBC normal"},
        {"patient_id": "P003", "category": "medication", "content": "Aspirin"},
    ]

    # audit_retrieval — HIPAA doesn't block document retrieval in the
    # governance layer (document-level controls are in enterprise-rag-patterns);
    # here we demonstrate the skill's retrieval audit path
    safe_docs, report = skill.audit_retrieval(
        documents=retrieved_docs,
        actor_id="nurse_abc",
        context={"query": "patient vitals", "session_id": "sess_health_001"},
    )
    print(f"Documents retrieved: {len(retrieved_docs)} → permitted: {len(safe_docs)}")
    print(report.to_compliance_summary())
    print()


# ---------------------------------------------------------------------------
# Demo 3: Enterprise — multi-framework via factory
# ---------------------------------------------------------------------------


def demo_enterprise() -> None:
    print("=" * 60)
    print("Demo 3: Enterprise — multi-framework via for_enterprise()")
    print("=" * 60)

    skill = GovernanceAuditSkill.for_enterprise(
        actor_id="agent_corp_001",
        allowed_actions={"search_knowledge_base", "summarize_document"},
        regulations=["FERPA", "HIPAA", "GDPR"],
        audit_sink=_log,
    )

    print(f"Configured frameworks: {skill.configured_frameworks}")
    print(f"Active frameworks:     {skill.active_frameworks}")
    print()

    # Permitted by all 3 frameworks
    result = skill.audit_action(
        action_name="search_knowledge_base",
        execute_fn=lambda: [{"doc": "policy.pdf"}, {"doc": "handbook.pdf"}],
        actor_id="agent_corp_001",
        context={"query": "leave policy"},
    )
    print(f"search_knowledge_base → {result}")
    print(skill.last_report.to_compliance_summary())
    print()


# ---------------------------------------------------------------------------
# Demo 4: Scoped evaluation — only run FERPA + GDPR out of FERPA/HIPAA/GDPR
# ---------------------------------------------------------------------------


def demo_framework_scoping() -> None:
    print("=" * 60)
    print("Demo 4: Framework scoping — restrict evaluation to subset")
    print("=" * 60)

    skill = GovernanceAuditSkill.for_enterprise(
        actor_id="agent_gdpr_001",
        allowed_actions={"read_document", "answer_question"},
        regulations=["FERPA", "GDPR"],
        audit_sink=_log,
    )

    # Only evaluate GDPR — skip FERPA for this action
    result = skill.audit_action(
        action_name="read_document",
        execute_fn=lambda: {"content": "GDPR-scoped content"},
        actor_id="agent_gdpr_001",
        frameworks=["GDPR"],  # restrict to GDPR only
        context={"purpose": "data_subject_request"},
    )
    print(f"read_document (GDPR only) → {result}")
    report = skill.last_report
    if report:
        skipped = report.frameworks_skipped
        print(f"Frameworks skipped in this call: {skipped}")
        print(f"Frameworks active for this call: {report.frameworks_permitted}")
    print()


# ---------------------------------------------------------------------------
# Demo 5: Audit-only shadow mode
# ---------------------------------------------------------------------------


def demo_audit_only() -> None:
    print("=" * 60)
    print("Demo 5: Audit-only shadow mode — evaluate without blocking")
    print("=" * 60)

    skill = GovernanceAuditSkill(
        config=GovernanceConfig(
            frameworks=[
                FrameworkConfig(
                    regulation="FERPA",
                    guard=GovernedActionGuard(
                        policy=ActionPolicy(allowed_actions={"read_transcript"}),
                        regulation="FERPA",
                        actor_id="shadow_agent",
                    ),
                ),
            ],
            audit_only=True,  # ← shadow mode: never block
        ),
        audit_sink=_log,
    )

    print(f"Audit-only mode: {skill.audit_only}")

    # Would be denied in enforcing mode (action not allowed), but proceeds in shadow mode
    result = skill.audit_action(
        action_name="delete_all_records",  # not in allowed_actions
        execute_fn=lambda: "WOULD_BE_BLOCKED",
        actor_id="shadow_agent",
    )
    print(f"delete_all_records (shadow mode) → {result}")
    report = skill.last_report
    if report:
        print(f"Audit-only mode in report: {report.audit_only_mode}")
        print(f"What would have been denied by: {report.frameworks_denied}")
    print()


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------


def print_summary() -> None:
    print("=" * 60)
    print(f"Total audit reports generated: {len(audit_log)}")
    permit_count = sum(1 for r in audit_log if r.overall_permitted)
    deny_count = sum(1 for r in audit_log if not r.overall_permitted)
    print(f"  Permitted: {permit_count}")
    print(f"  Denied:    {deny_count}")
    print()
    print("Framework breakdown:")
    framework_eval_count: dict[str, int] = {}
    for report in audit_log:
        for fw in report.frameworks_evaluated:
            framework_eval_count[fw] = framework_eval_count.get(fw, 0) + 1
    for fw, count in sorted(framework_eval_count.items()):
        print(f"  {fw:<20} {count} evaluations")
    print()
    print("SHA-256 tamper hashes for all reports:")
    for i, report in enumerate(audit_log, 1):
        print(f"  [{i:02d}] {report.action_name:<35} {report.content_hash()[:24]}...")


if __name__ == "__main__":
    demo_education()
    demo_healthcare()
    demo_enterprise()
    demo_framework_scoping()
    demo_audit_only()
    print_summary()
