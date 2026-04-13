# Implementation Note 02 — Audit Trail Design for Regulated AI: What to Log and Why

**Repo:** `regulated-ai-governance`
**Relates to:** [`examples/04_governance_audit_skill.py`](../examples/04_governance_audit_skill.py), [`examples/05_healthcare_ai_governance.py`](../examples/05_healthcare_ai_governance.py)
**ADR cross-reference:** [ADR-001 (policy-before-execution)](adr/001-policy-before-execution.md)

---

## Why AI audit trails differ from application audit trails

A conventional application audit trail answers: *who did what, when, to which resource?* The fields are: `user_id`, `action`, `resource_id`, `timestamp`, `outcome`.

An AI system audit trail must answer several additional questions that have no equivalent in conventional applications:

- **Which model version made the decision?** A recommendation produced by model v1.2 is legally and technically distinct from one produced by v2.0. If a post-deployment investigation reveals a systematic bias, the audit trail must be able to identify which requests were processed by which model.
- **What was the prompt or query?** LLM outputs are non-deterministic. The same user action can produce different outputs depending on the context window. The audit record must capture a hash of the input context that produced the output — not just the action name.
- **What was the confidence or uncertainty?** For high-stakes AI actions (clinical recommendations, credit decisions), the audit trail should record the model's stated confidence. A correct decision made with low confidence is meaningfully different from a correct decision made with high confidence for post-hoc analysis.
- **What did the governance layer see?** The audit trail must capture the governance layer's view of the action — which policy evaluated it, which frameworks applied, what the deny/permit result was — independently of the application's own logging.

The `GovernanceAuditRecord` and `ComprehensiveAuditReport` classes in this library are designed around these requirements.

---

## The `GovernanceAuditRecord` structure

Every call to `GovernedActionGuard.guard()` or `.evaluate()` emits a `GovernanceAuditRecord` to the configured `audit_sink`. The record captures:

| Field | Purpose |
|-------|---------|
| `record_id` | UUID for deduplication and cross-system correlation |
| `actor_id` | The identity under which the action was evaluated |
| `action_name` | The action that was evaluated |
| `regulation` | The regulation/standard that produced this record |
| `permitted` | Boolean outcome — the governance layer's decision |
| `denial_reason` | Present when `permitted=False`; the specific policy clause that caused denial |
| `escalation_target` | Present when an escalation rule matched; the team/role to notify |
| `policy_version` | The version of the policy that was applied |
| `timestamp` | UTC timestamp of the evaluation |
| `context_hash` | Optional SHA-256 of the evaluation context (for prompt/query integrity) |

The `audit_sink` is a `Callable[[GovernanceAuditRecord], None]` — a plain Python callable. The governance library is responsible for emitting records; the sink is responsible for durability. Common sink patterns:

- **Append to a list** (testing and examples): `audit_sink=compliance_log.append`
- **Write to a database**: `audit_sink=lambda r: db.insert("ai_audit", r.to_dict())`
- **Publish to a SIEM**: `audit_sink=lambda r: siem_client.send(r.to_dict())`
- **Emit to a message queue**: `audit_sink=lambda r: outbox.append(OutboxRecord(...))`

---

## The `ComprehensiveAuditReport` structure

When `GovernanceOrchestrator.guard()` is called, it evaluates all registered framework guards and assembles a single `ComprehensiveAuditReport`. This is the authoritative record for multi-framework evaluation:

| Field | Purpose |
|-------|---------|
| `report_id` | UUID for this specific multi-framework evaluation |
| `actor_id` | The actor evaluated across all frameworks |
| `action_name` | The action evaluated |
| `overall_permitted` | `True` only if ALL frameworks permitted; `False` if any denied or any escalation blocked |
| `framework_results` | List of per-framework dicts: `regulation`, `permitted`, `denial_reason`, `escalation_target`, `skipped` |
| `timestamp` | UTC timestamp of the orchestrator evaluation |

The `framework_results` list is the forensic record. When investigating an incident, this list answers: *which framework denied the action and for what reason?* For systems subject to multiple concurrent regulations, this is the minimum record required to demonstrate compliance to multiple regulators simultaneously.

---

## Retention requirements by regulation

Retention requirements vary significantly across regulations. Mismatched retention — keeping records too short or deleting records that should be kept — creates regulatory exposure.

| Regulation | Minimum Retention | Notes |
|------------|------------------|-------|
| HIPAA (45 CFR § 164.530(j)) | 6 years from creation or last effective date | Applies to policies and procedures; audit logs should match |
| EU AI Act (Art. 12) | 10 years for high-risk AI systems | Logs must be accessible to competent authorities |
| GDPR (Art. 5(1)(e)) | Purpose-limited; delete when purpose ends | Audit logs of processing are themselves processing — apply data minimization |
| GLBA (16 CFR § 314.4) | No explicit retention period; "reasonable" per FTC guidance | Typically 3–7 years in practice |
| DORA (Regulation 2022/2554) | 5 years for ICT incident records (Art. 17) | Includes AI system incident logs |
| NIST AI RMF | No statutory retention; follows organizational risk management policy | Document in AI Risk Management Plan |
| ISO/IEC 42001 | Retention defined in AIMS documentation scope (Annex A.6.2.6) | Organization-defined |
| SOC 2 Type II | 1 year minimum (AICPA guidance); often 7 years in practice | Aligns with financial audit cycles |

**Design implication:** Do not co-mingle records with different retention requirements in a single log store without partition-by-regulation support. The simplest approach is to tag every `GovernanceAuditRecord` with the regulation label and store it in a partition or table that can be independently subject to a retention policy.

---

## Shadow (audit-only) mode and its compliance implications

`GovernanceOrchestrator(audit_only=True)` emits a full `ComprehensiveAuditReport` for every evaluation but does not block any action. This is the recommended rollout pattern for adding new regulations to production systems.

**Compliance note:** shadow mode records are real compliance records. They demonstrate that the organization evaluated the regulation's requirements against production traffic and made a conscious decision about the compliance gap before enforcing the new policy. This is stronger evidence of a compliance program than simply not logging at all.

Specifically for EU AI Act Article 9 (risk management system) and ISO/IEC 42001 A.5.2 (AI risk assessment), shadow-mode records during the rollout period constitute documented evidence of an ongoing AI risk management process.

**Shadow mode is not a compliance exemption.** If shadow-mode records show that an action would be denied under a regulation the organization is subject to, those records constitute evidence of a known compliance gap. Organizations should set a documented deadline for moving from shadow mode to enforcement.

---

## What the audit trail is NOT responsible for

The governance audit trail captures policy evaluation decisions — it is not a general application log, a model performance log, or a data lineage record.

- **Model outputs**: the governance layer does not see the text generated by an LLM. It sees the action name and context that the calling code provides. If the calling code does not pass a `context_hash` to the guard, the audit trail will not contain it.
- **RAG retrieval results**: for RAG pipelines, the governance layer evaluates whether retrieval is permitted for a given actor+scope. It does not log the actual documents retrieved. That is the responsibility of the RAG pipeline's own retrieval audit (see `enterprise-rag-patterns`).
- **Data provenance**: ISO/IEC 42001 A.7.6 (data provenance) requires a traceable chain of custody for knowledge base documents. This is tracked in `ISO42001DataProvenanceRecord`, not in the governance audit record.

The governance audit trail answers: *was this action permitted, by which policy, under which regulation?* Combining it with application logs, model logs, and data provenance records produces the complete audit record required for regulatory defensibility.
