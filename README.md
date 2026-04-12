# regulated-ai-governance

[![CI](https://github.com/ashutoshrana/regulated-ai-governance/actions/workflows/ci.yml/badge.svg)](https://github.com/ashutoshrana/regulated-ai-governance/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/regulated-ai-governance.svg)](https://pypi.org/project/regulated-ai-governance/)
[![Python](https://img.shields.io/pypi/pyversions/regulated-ai-governance.svg)](https://pypi.org/project/regulated-ai-governance/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Downloads](https://img.shields.io/pypi/dm/regulated-ai-governance.svg)](https://pypi.org/project/regulated-ai-governance/)

---

## The problem this solves

AI agents in regulated environments (FERPA, HIPAA, GLBA) can access and process data they are not authorized to see. Standard agent frameworks — CrewAI, AutoGen, LangChain, Semantic Kernel — have no concept of regulated industry access control. When you deploy an agent in a higher-education, healthcare, or financial-services environment, the framework will not tell you whether the agent is allowed to access a record type, who must approve an export, or how to produce the audit record the regulation requires. This library provides those answers as composable Python primitives, with pre-built policy adapters for each major framework that enforce authorization before any action executes.

---

## Architecture

```
CrewAI / AutoGen / Semantic Kernel / LangChain Agent
     │
     ▼
EnterpriseActionGuard / PolicyEnforcingAgent / GovernanceCallback
(wraps your tool or callback — drop-in replacement)
     │
     ├─ ActionPolicy.can_run(action_name)? ─────────────────────┐
     │        ├─ Permitted ────────────────────► Execute         │
     │        ├─ Escalation required ──────────► Block + notify │
     │        └─ Denied ──────────────────────► PolicyViolation │
     │                                                           │
     └─ GovernanceAuditRecord ───────────────────────────────────┘
          regulation citation + action_name + actor_id
          permitted / denied / escalated + timestamp
          → audit_sink (durable compliance log)
```

---

## Installation

```bash
pip install regulated-ai-governance
```

With framework integrations:

```bash
pip install "regulated-ai-governance[crewai]"
pip install "regulated-ai-governance[langchain]"
pip install "regulated-ai-governance[autogen]"
pip install "regulated-ai-governance[llama-index]"
pip install "regulated-ai-governance[semantic-kernel]"
pip install "regulated-ai-governance[haystack]"
```

---

## 30-second example: CrewAI + FERPA

```python
from regulated_ai_governance.integrations.crewai import EnterpriseActionGuard
from regulated_ai_governance.regulations.ferpa import make_ferpa_student_policy

guard = EnterpriseActionGuard(
    wrapped_tool=MyTranscriptTool(),           # your existing CrewAI tool
    policy=make_ferpa_student_policy(
        allowed_record_categories={"academic_record"}
    ),
    regulation="FERPA",
    actor_id="stu-alice",                      # from verified session token
    audit_sink=lambda rec: write_to_db(rec),   # wire to durable compliance store
    block_on_escalation=True,
)

agent = Agent(tools=[guard], ...)  # drop-in replacement — no other changes needed
```

Every call to `guard` emits a `GovernanceAuditRecord` whether permitted or denied, suitable for direct insert into a 34 CFR § 99.32 disclosure log.

---

## Framework support

| Framework | Adapter Class | Install Extra |
|-----------|--------------|---------------|
| CrewAI | `EnterpriseActionGuard` | `[crewai]` |
| AutoGen | `PolicyEnforcingAgent` | `[autogen]` |
| Semantic Kernel | `PolicyKernelPlugin` | `[semantic-kernel]` |
| LangChain | `GovernanceCallbackHandler` | `[langchain]` |
| Haystack | via enterprise-rag-patterns | — |

---

## Regulations supported

| Regulation | Status | Audit Citation |
|------------|--------|---------------|
| FERPA (34 CFR § 99) | Implemented | 34 CFR § 99.32 disclosure log |
| HIPAA (45 CFR § 164) | Implemented | 45 CFR § 164.312(b) access controls |
| GLBA (16 CFR § 314) | Implemented | 16 CFR § 314.4(e) safeguards |
| GDPR | Implemented | Art. 17, Art. 22 automated decision |
| CCPA | Planned | Cal. Civ. Code § 1798.100 |
| SOC 2 | Planned | CC6.1 logical access controls |

---

## Quick start: HIPAA and GLBA

```python
from regulated_ai_governance.regulations.hipaa import make_hipaa_treating_provider_policy
from regulated_ai_governance import GovernedActionGuard

# HIPAA — clinical decision support agent
policy = make_hipaa_treating_provider_policy(
    escalate_external_share_to="hipaa_privacy_officer"
)
guard = GovernedActionGuard(policy=policy, regulation="HIPAA", actor_id="nurse-001")
result = guard.guard("read_lab_results", lambda: {"hba1c": 6.2})
# → {"hba1c": 6.2}
```

```python
from regulated_ai_governance.regulations.glba import make_glba_customer_service_policy

# GLBA — customer-service chatbot
policy = make_glba_customer_service_policy()
guard = GovernedActionGuard(policy=policy, regulation="GLBA", actor_id="cust-7890")
guard.guard("read_account_balance", lambda: {"balance": "$1,240.00"})
# → {"balance": "$1,240.00"}
```

---

## Audit records

Every guard evaluation emits a `GovernanceAuditRecord`:

```python
print(audit_log[0].to_log_entry())
# {
#   "record_id": "a3f8...",
#   "regulation": "FERPA",
#   "actor_id": "stu-alice",
#   "action_name": "read_academic_record",
#   "permitted": true,
#   "denial_reason": null,
#   "escalation_target": null,
#   "policy_version": "1.0",
#   "timestamp": "2026-04-11T14:30:00+00:00"
# }
```

JSON-serializable, suitable for direct insert into a compliance database per 34 CFR § 99.32 (FERPA), 45 CFR § 164.312(b) (HIPAA), or 16 CFR § 314.4(e) (GLBA).

---

## Ecosystem

See [ECOSYSTEM.md](./ECOSYSTEM.md) for the full regulation and framework coverage matrix.

---

## Contributing

Contributions are welcome. Please read [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines. Run `pytest tests/ -v` to verify your changes before opening a pull request.

---

## Citation

If you use these patterns in research or production, please cite:

```bibtex
@software{rana2026rag,
  author    = {Rana, Ashutosh},
  title     = {regulated-ai-governance: Policy enforcement for AI agents in regulated environments},
  year      = {2026},
  url       = {https://github.com/ashutoshrana/regulated-ai-governance},
  license   = {MIT}
}
```

Or use GitHub's "Cite this repository" button above (reads `CITATION.cff`).

---

## Part of the enterprise AI patterns trilogy

| Library | Focus | Regulation |
|---------|-------|-----------|
| [enterprise-rag-patterns](https://github.com/ashutoshrana/enterprise-rag-patterns) | What to retrieve | FERPA identity-scoped RAG |
| **regulated-ai-governance** | What agents may do | FERPA, HIPAA, GLBA, GDPR, CCPA, SOC2 |
| [integration-automation-patterns](https://github.com/ashutoshrana/integration-automation-patterns) | How data flows | Event-driven enterprise integration |

---

## License

MIT — see [LICENSE](LICENSE).
