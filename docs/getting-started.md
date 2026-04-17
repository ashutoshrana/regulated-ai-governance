# Getting Started — regulated-ai-governance

This guide walks from installation to running a governed AI agent with a structured compliance audit record in under 10 minutes.

---

## 1. Install

```bash
pip install regulated-ai-governance
```

With AI framework extras:

```bash
pip install "regulated-ai-governance[crewai]"
pip install "regulated-ai-governance[langchain]"
pip install "regulated-ai-governance[autogen]"
pip install "regulated-ai-governance[llama-index]"
pip install "regulated-ai-governance[semantic-kernel]"
pip install "regulated-ai-governance[haystack]"
```

---

## 2. Core concepts

### The policy guard pattern

AI agents in regulated environments can access and process data they are not authorized to see. The `GovernedActionGuard` wraps any callable — tool execution, LLM call, data fetch — and applies a policy before execution:

```
Agent wants to call: read_student_record("stu_001")
           │
           ▼
GovernedActionGuard.guard(action_name, execute_fn)
           │
           ├── Policy.is_allowed(action_name)?
           │      YES → execute_fn() → return result + audit record
           │      NO  → raise PolicyViolation + audit record (action not executed)
           │
           └── audit_sink(GovernanceAuditRecord)  ← always called
```

Every evaluation produces a `GovernanceAuditRecord` regardless of outcome — whether permitted, denied, or escalated. The record contains a regulation citation suitable for a compliance database or SIEM.

### Frozen context objects

All compliance context is passed as `@dataclass(frozen=True)` objects — no mutable state passes through the governance pipeline. This makes each evaluation deterministic and independently testable.

---

## 3. Quickstart: single framework (FERPA)

```python
from regulated_ai_governance import ActionPolicy, GovernedActionGuard
from regulated_ai_governance.regulations.ferpa import make_ferpa_student_policy

policy = make_ferpa_student_policy(
    allowed_record_categories={"academic_record", "financial_record"}
)

guard = GovernedActionGuard(
    policy=policy,
    regulation="FERPA",
    actor_id="advisor_007",
    audit_sink=lambda rec: print(rec.to_log_entry()),
)

result = guard.guard(
    action_name="read_academic_record",
    execute_fn=lambda: {"gpa": 3.7, "major": "Computer Science"},
)
# Prints:
# [FERPA][PERMITTED] actor=advisor_007 action=read_academic_record
# regulation_citation=34 CFR §99.31(a)(1)
```

---

## 4. Multi-framework orchestration

When an agent operates under multiple regulatory regimes simultaneously, use `GovernanceOrchestrator`. It applies **deny-all aggregation**: if any single framework denies, the overall decision is DENIED.

```python
from regulated_ai_governance import (
    ActionPolicy,
    GovernedActionGuard,
    GovernanceOrchestrator,
    FrameworkGuard,
)
from regulated_ai_governance.regulations.ferpa import make_ferpa_student_policy
from regulated_ai_governance.regulations.hipaa import make_hipaa_covered_entity_policy

orchestrator = GovernanceOrchestrator(
    framework_guards=[
        FrameworkGuard("FERPA", GovernedActionGuard(
            policy=make_ferpa_student_policy(allowed_record_categories={"academic_record"}),
            regulation="FERPA",
            actor_id="advisor_007",
        )),
        FrameworkGuard("HIPAA", GovernedActionGuard(
            policy=make_hipaa_covered_entity_policy(allowed_phi_categories={"clinical_note"}),
            regulation="HIPAA",
            actor_id="advisor_007",
        )),
    ],
    audit_sink=my_compliance_log.append,
)

result = orchestrator.guard(
    action_name="read_student_health_record",
    execute_fn=lambda: fetch_health_record("stu_001"),
    actor_id="advisor_007",
)

print(orchestrator.last_report.to_compliance_summary())
# APPROVED under FERPA: legitimate educational interest
# APPROVED under HIPAA: treatment relationship confirmed
# OVERALL: APPROVED
```

---

## 5. CrewAI integration

```python
from crewai import Agent
from regulated_ai_governance.integrations.crewai import EnterpriseActionGuard
from regulated_ai_governance.regulations.ferpa import make_ferpa_student_policy

guard = EnterpriseActionGuard(
    wrapped_tool=TranscriptReaderTool(),
    policy=make_ferpa_student_policy(allowed_record_categories={"academic_record"}),
    regulation="FERPA",
    actor_id="agent-student-advisor",
    audit_sink=lambda rec: write_to_db(rec),
    block_on_escalation=True,
)

agent = Agent(
    role="Student Advisor",
    tools=[guard],
    llm=llm,
)
```

---

## 6. Google ADK integration

```python
from google.adk.agents import LlmAgent
from regulated_ai_governance.adapters.google_adk_adapter import (
    ADKPolicyGuard, Regulation, BigQueryAuditSink
)

guard = ADKPolicyGuard(
    regulations=[Regulation.FERPA, Regulation.HIPAA],
    audit_sink=BigQueryAuditSink(project="my-gcp-project", dataset="ai_audit"),
    agent_id="student-advisor-agent",
)

agent = LlmAgent(
    name="StudentAdvisor",
    model="gemini-2.0-flash",
    instruction="Help students with academic questions.",
    before_model_callback=guard.before_model_callback,
    before_agent_callback=guard.before_agent_callback,
    before_tool_callback=guard.before_tool_callback,
)
```

Every ADK callback fires before LLM or tool execution. Non-compliant requests are blocked before any data is processed.

---

## 7. LangChain integration

```python
from regulated_ai_governance.integrations.langchain import GovernanceCallbackHandler

handler = GovernanceCallbackHandler(
    regulations=["FERPA", "HIPAA"],
    actor_id="advisor_007",
    audit_sink=lambda rec: my_siem.ingest(rec),
)

llm = ChatOpenAI(callbacks=[handler])
chain = retriever | llm
result = chain.invoke("What are Alice's recent grades?")
```

---

## 8. High-level skill API

For simpler use cases, `GovernanceAuditSkill` provides factory methods per sector:

```python
from regulated_ai_governance import GovernanceAuditSkill

# Education: FERPA + OWASP LLM
skill = GovernanceAuditSkill.for_education(
    actor_id="advisor_007",
    audit_sink=my_compliance_log.append,
)

# Guard an action
result = skill.audit_action(
    "read_transcript",
    lambda: fetch_transcript("stu_001"),
)

# Guard a retrieval batch
safe_docs, report = skill.audit_retrieval(retrieved_docs, actor_id="advisor_007")
```

Available factory methods:
- `GovernanceAuditSkill.for_education()` — FERPA + OWASP LLM
- `GovernanceAuditSkill.for_healthcare()` — HIPAA + FDA SaMD
- `GovernanceAuditSkill.for_financial()` — GLBA + FINRA + SEC Reg S-P
- `GovernanceAuditSkill.for_government()` — FedRAMP + FISMA + CUI

---

## 9. Audit record format

Every evaluation — permitted or denied — produces:

```python
GovernanceAuditRecord(
    filter_name="FERPA_STUDENT_POLICY",
    decision="PERMITTED",
    reason="Legitimate educational interest confirmed (34 CFR §99.31(a)(1))",
    regulation_citation="34 CFR §99.31(a)(1) — FERPA 1974",
    requires_logging=True,
    actor_id="advisor_007",
    action_name="read_academic_record",
    timestamp="2026-04-17T09:23:41Z",
)
```

JSON-serializable; sink to PostgreSQL, BigQuery, Splunk, or any SIEM.

---

## 10. Example files

| File | What it shows |
|------|---------------|
| `01_basic_policy_enforcement.py` | Minimal single-framework guard |
| `02_crewai_guard.py` | CrewAI tool wrapper |
| `03_multi_framework_orchestration.py` | Multi-framework deny-all |
| `10_eu_ai_act_governance.py` | EU AI Act high-risk system |
| `39_owasp_agentic_top10_governance.py` | OWASP Agentic AI Top 10 2026 |
| `41_trilogy_security_audit.py` | Full enterprise security audit |

---

## 11. Running tests

```bash
pip install pytest
pytest tests/ -v
```

2,631 tests, all passing.

---

## See also

- [API Reference](./api-reference.md)
- [Jurisdiction Coverage](./jurisdictions.md)
- [Architecture Decision Records](./adr/)
- [enterprise-rag-patterns](https://github.com/ashutoshrana/enterprise-rag-patterns) — retrieval-layer pre-filters
- [ferpa-haystack](https://github.com/ashutoshrana/ferpa-haystack) — standalone Haystack FERPA component
