# regulated-ai-governance

![CI](https://github.com/ashutoshrana/regulated-ai-governance/actions/workflows/ci.yml/badge.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)
![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![PyPI](https://img.shields.io/pypi/v/regulated-ai-governance.svg)

Governance patterns for AI agents operating in regulated environments — FERPA, HIPAA, and GLBA.

Policy enforcement, escalation routing, and compliance audit for enterprise AI systems.

---

## The problem this solves

Standard AI agent frameworks have no concept of regulated industry access control. When you deploy an AI agent in a higher-education, healthcare, or financial-services environment, you need answers to questions that no general-purpose agent framework addresses:

- Is this agent allowed to access this type of record at all?
- If it tries to export or share data, who needs to approve that?
- How do I produce the audit record the regulation requires?

This library provides those answers as composable Python primitives.

---

## Three regulations, one pattern

```
ActionPolicy
    │
    ▼
GovernedActionGuard
    │
    ├─── Permitted? ───► Execute
    │
    ├─── Escalation? ──► Block (or log-and-continue)
    │
    └─── Always ───────► GovernanceAuditRecord → audit_sink
```

The same three-step pattern — allow/deny, escalate, audit — applies to FERPA-regulated student record access, HIPAA-regulated clinical record access, and GLBA-regulated customer financial data access. The regulation-specific details are in pre-built policy factories; the enforcement engine is the same.

---

## Installation

```bash
pip install regulated-ai-governance
```

With CrewAI integration:
```bash
pip install "regulated-ai-governance[crewai]"
```

With LangChain integration:
```bash
pip install "regulated-ai-governance[langchain]"
```

---

## Quick start

### FERPA: student-facing enrollment assistant

```python
from regulated_ai_governance import GovernedActionGuard
from regulated_ai_governance.regulations.ferpa import make_ferpa_student_policy
from regulated_ai_governance.audit import GovernanceAuditRecord

audit_log: list[GovernanceAuditRecord] = []

policy = make_ferpa_student_policy(
    allowed_record_categories={"academic_record", "financial_record"}
)

guard = GovernedActionGuard(
    policy=policy,
    regulation="FERPA",
    actor_id="stu-alice",           # from verified session token — not from user input
    audit_sink=audit_log.append,    # wire to durable compliance log store
    block_on_escalation=True,
)

# Permitted — executes, emits audit record
result = guard.guard(
    action_name="read_academic_record",
    execute_fn=lambda: {"gpa": 3.7, "credits": 90},
)
# → {"gpa": 3.7, "credits": 90}

# Blocked — denied by policy, emits audit record
result = guard.guard(
    action_name="export_student_records",
    execute_fn=lambda: b"PDF_DATA",
)
# → "[regulated-ai-governance] Action BLOCKED — ..."
```

### HIPAA: clinical decision support agent

```python
from regulated_ai_governance.regulations.hipaa import make_hipaa_treating_provider_policy

policy = make_hipaa_treating_provider_policy(
    escalate_external_share_to="hipaa_privacy_officer"
)
guard = GovernedActionGuard(policy=policy, regulation="HIPAA", actor_id="nurse-001")

result = guard.guard("read_lab_results", lambda: {"hba1c": 6.2})
# → {"hba1c": 6.2}
```

### GLBA: customer-service chatbot

```python
from regulated_ai_governance.regulations.glba import make_glba_customer_service_policy

policy = make_glba_customer_service_policy()
guard = GovernedActionGuard(policy=policy, regulation="GLBA", actor_id="cust-7890")

guard.guard("read_account_balance", lambda: {"balance": "$1,240.00"})
# → {"balance": "$1,240.00"}
```

---

## CrewAI integration

```python
from regulated_ai_governance.integrations.crewai import EnterpriseActionGuard
from regulated_ai_governance.regulations.ferpa import make_ferpa_student_policy

guard = EnterpriseActionGuard(
    wrapped_tool=MyTranscriptTool(),
    policy=make_ferpa_student_policy(),
    regulation="FERPA",
    actor_id="stu-alice",
    audit_sink=lambda rec: write_to_compliance_db(rec),
    block_on_escalation=True,
)

agent = Agent(tools=[guard], ...)  # drop-in replacement for the raw tool
```

---

## LangChain integration (FERPA retrieval)

```python
from regulated_ai_governance.integrations.langchain import FERPAComplianceCallbackHandler

handler = FERPAComplianceCallbackHandler(
    student_id="stu-alice",         # from verified session token
    institution_id="univ-east",
    allowed_categories={"academic_record", "financial_record"},
    audit_sink=lambda rec: write_to_compliance_db(rec),
)

retriever = vector_store.as_retriever(callbacks=[handler])
docs = retriever.invoke("What is my enrollment status?")
```

---

## Audit records

Every guard evaluation emits a `GovernanceAuditRecord` — permitted, denied, or escalated:

```python
print(audit_log[0].to_log_entry())
# {
#   "record_id": "a3f8...",
#   "regulation": "FERPA",
#   "actor_id": "stu-alice",
#   "action_name": "read_academic_record",
#   "permitted": True,
#   "denial_reason": None,
#   "escalation_target": None,
#   "policy_version": "1.0",
#   "timestamp": "2026-04-11T14:30:00+00:00"
# }
```

JSON-serializable, suitable for direct insert into a compliance database or disclosure log per 34 CFR § 99.32 (FERPA), 45 CFR § 164.312(b) (HIPAA), 16 CFR § 314.4(e) (GLBA).

---

## Part of the enterprise AI patterns trilogy

| Library | Focus | Regulation |
|---------|-------|-----------|
| [enterprise-rag-patterns](https://github.com/ashutoshrana/enterprise-rag-patterns) | What to retrieve | FERPA identity-scoped RAG |
| **regulated-ai-governance** | What agents may do | FERPA, HIPAA, GLBA policy enforcement |
| [integration-automation-patterns](https://github.com/ashutoshrana/integration-automation-patterns) | How data flows | Event-driven enterprise integration |

---

## License

MIT — see [LICENSE](LICENSE).
