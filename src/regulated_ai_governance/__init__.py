"""
regulated-ai-governance
=======================

Comprehensive governance framework for AI agents and RAG systems operating in
regulated environments. Covers cross-industry compliance across 10+ frameworks.

Supported frameworks
--------------------
Regulatory / statutory:
- FERPA (34 CFR § 99) — educational records
- HIPAA (45 CFR §§ 164.312, 164.502) — ePHI access
- GDPR (Articles 5, 6, 17) — EU data subject rights
- GLBA (16 CFR § 314) — financial customer safeguards
- CCPA / CPRA — California consumer privacy

IT audit / security:
- ISO/IEC 27001:2022 — ISMS CBAC (Annex A.5.12/A.5.15/A.8.2)
- PCI DSS v4.0 — CHD access + PAN masking (Req 3.4/7.2/7.2.1)
- SOC 2 Type II — tenant + confidentiality CBAC (CC6.1/CC6.6/C1.1)

AI / technology governance:
- NIST AI RMF 1.0 + AI 600-1 GenAI Profile — risk assessment
- OWASP LLM Top 10 (2025) — prompt injection, PII disclosure
- ISO/IEC 42001:2023 — AI Management System lifecycle governance
- EU AI Act Article 9/10/12 — high-risk AI documentation + logging
- DORA Article 9/28 — EU financial operational resilience

Core components
---------------
- ``ActionPolicy``, ``EscalationRule``, ``PolicyDecision``: policy primitives
- ``GovernedActionGuard``: framework-agnostic pre-execution policy guard
- ``GovernanceAuditRecord``: structured compliance audit record
- ``GovernanceOrchestrator``: multi-framework simultaneous evaluation
  with deny-all aggregation and ``ComprehensiveAuditReport``
- ``GovernanceAuditSkill``: high-level skill with channel adapters
  (LangChain, CrewAI, LlamaIndex, Haystack, MAF)

Quick start — single framework
--------------------------------

.. code-block:: python

    from regulated_ai_governance import ActionPolicy, GovernedActionGuard
    from regulated_ai_governance.regulations.ferpa import make_ferpa_student_policy

    policy = make_ferpa_student_policy(
        allowed_record_categories={"academic_record", "financial_record"}
    )
    guard = GovernedActionGuard(
        policy=policy, regulation="FERPA", actor_id="stu-alice",
        audit_sink=lambda rec: print(rec.to_log_entry()),
    )
    result = guard.guard(action_name="read_academic_record", execute_fn=lambda: {"gpa": 3.7})

Quick start — multi-framework orchestration
--------------------------------------------

.. code-block:: python

    from regulated_ai_governance import (
        ActionPolicy, GovernedActionGuard,
        GovernanceOrchestrator, FrameworkGuard,
    )

    orchestrator = GovernanceOrchestrator(
        framework_guards=[
            FrameworkGuard("FERPA", GovernedActionGuard(
                policy=ActionPolicy(allowed_actions={"read_transcript"}),
                regulation="FERPA", actor_id="advisor_007",
            )),
            FrameworkGuard("HIPAA", GovernedActionGuard(
                policy=ActionPolicy(allowed_actions={"read_vitals"}),
                regulation="HIPAA", actor_id="advisor_007",
            )),
        ],
        audit_sink=my_siem.append,
    )
    result = orchestrator.guard("read_transcript", lambda: {"gpa": 3.9}, actor_id="advisor_007")
    print(orchestrator.last_report.to_compliance_summary())

Quick start — governance skill with factory
--------------------------------------------

.. code-block:: python

    from regulated_ai_governance import GovernanceAuditSkill

    skill = GovernanceAuditSkill.for_education(
        actor_id="advisor_007",
        audit_sink=my_compliance_log.append,
    )
    result = skill.audit_action("read_transcript", lambda: {"gpa": 3.9})
    safe_docs, report = skill.audit_retrieval(retrieved_docs, actor_id="advisor_007")
"""

from regulated_ai_governance.agent_guard import GovernedActionGuard
from regulated_ai_governance.audit import GovernanceAuditRecord
from regulated_ai_governance.base import FilterResult, GovernanceFilter, GovernancePipeline
from regulated_ai_governance.orchestrator import (
    ComprehensiveAuditReport,
    FrameworkGuard,
    FrameworkResult,
    GovernanceOrchestrator,
    MultiFrameworkDecision,
)
from regulated_ai_governance.policy import ActionPolicy, EscalationRule, PolicyDecision
from regulated_ai_governance.skill import (
    FrameworkConfig,
    GovernanceAuditSkill,
    GovernanceConfig,
)

__all__ = [
    # Base filter primitives
    "FilterResult",
    "GovernanceFilter",
    "GovernancePipeline",
    # Core policy primitives
    "ActionPolicy",
    "EscalationRule",
    "PolicyDecision",
    # Audit
    "GovernanceAuditRecord",
    # Guard
    "GovernedActionGuard",
    # Orchestrator (multi-framework)
    "FrameworkGuard",
    "FrameworkResult",
    "MultiFrameworkDecision",
    "ComprehensiveAuditReport",
    "GovernanceOrchestrator",
    # Skill (high-level API)
    "FrameworkConfig",
    "GovernanceConfig",
    "GovernanceAuditSkill",
]

__version__ = "0.41.0"
