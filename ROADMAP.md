# Roadmap

This roadmap lists near-term development direction for `regulated-ai-governance`.
Items are listed in rough priority order. Dates are targets, not commitments.

---

## v0.4.0 — Expanded Framework Coverage

- LangGraph adapter — policy enforcement node for stateful multi-agent graphs
- Pydantic v2 migration across all internal data models
- Async policy evaluation (`evaluate_async`) for FastAPI and asyncio workloads
- Improve `ConsentStore` with pluggable database backend example (SQLAlchemy)

## v0.5.0 — Audit & Observability

- Structured JSONL audit log writer (rotation, async flush)
- OpenTelemetry span export for policy evaluation events
- Lineage graph export to DOT format for compliance review workflows
- HIPAA Minimum Necessary standard implementation (field-level filtering)

## v0.6.0 — Regulation Depth

- FERPA: parental consent override workflow
- GDPR: Right to erasure (Article 17) consent revocation propagation
- SOC 2 Type II: automated control evidence collection helpers
- ISO 27001 policy module

## Ongoing

- Example notebooks (Jupyter) for each regulation
- Published blog posts and implementation notes in `docs/`
- Framework adapter updates as CrewAI, AutoGen, Semantic Kernel APIs evolve

---

## Completed

- ✅ v0.1.0 — Core policy engine (ActionPolicy, PolicyViolationError, AuditRecord)
- ✅ v0.2.0 — GDPR, CCPA, SOC 2, FERPA, HIPAA, GLBA regulation modules; PII detector; consent store; lineage tracker; LangChain, LlamaIndex, Haystack, CrewAI, AutoGen, Semantic Kernel adapters
- ✅ v0.3.0 — CrewAI EnterpriseActionGuard, AutoGen PolicyEnforcingAgent, Semantic Kernel PolicyKernelPlugin; runnable examples; full CI; PyPI publish
