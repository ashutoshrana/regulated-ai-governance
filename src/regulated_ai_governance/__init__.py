"""
regulated-ai-governance
=======================

Governance patterns for AI agents operating in regulated environments.

Covers FERPA (educational records), HIPAA (health information),
GLBA (financial data), and general multi-agent policy enforcement.

Core components
---------------
- ``ActionPolicy``: defines allowed actions, denied actions, and escalation rules
- ``GovernedActionGuard``: framework-agnostic guard that checks policy before execution
- ``GovernanceAuditRecord``: structured compliance audit record per action event
- ``regulations``: pre-built policy helpers for FERPA, HIPAA, and GLBA
- ``integrations``: bindings for LangChain and CrewAI

Quick start
-----------

.. code-block:: python

    from regulated_ai_governance import ActionPolicy, GovernedActionGuard
    from regulated_ai_governance.regulations.ferpa import make_ferpa_student_policy
    from regulated_ai_governance.audit import GovernanceAuditRecord

    policy = make_ferpa_student_policy(
        allowed_record_categories={"academic_record", "financial_record"}
    )

    guard = GovernedActionGuard(
        policy=policy,
        regulation="FERPA",
        actor_id="stu-alice",
        audit_sink=lambda rec: print(rec.to_log_entry()),
    )

    result = guard.guard(
        action_name="read_academic_record",
        execute_fn=lambda: {"gpa": 3.7},
    )
"""

from regulated_ai_governance.agent_guard import GovernedActionGuard
from regulated_ai_governance.audit import GovernanceAuditRecord
from regulated_ai_governance.policy import ActionPolicy, EscalationRule, PolicyDecision

__all__ = [
    "ActionPolicy",
    "EscalationRule",
    "PolicyDecision",
    "GovernanceAuditRecord",
    "GovernedActionGuard",
]

__version__ = "0.4.1"
