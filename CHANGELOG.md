# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] — 2026-04-12

### Added
- Enhanced CI: coverage reporting (Codecov), ruff format check, build-check job, pip cache, concurrency cancellation
- Automation: PR auto-labeler, stale bot, Conventional Commits PR title check, first-contributor welcome bot
- Dependabot; CODEOWNERS; SECURITY.md; pre-commit config
- `adapters/crewai.py`: `EnterpriseActionGuard` — CrewAI tool wrapper with `ActionPolicy` enforcement + `PolicyViolationError`
- `adapters/autogen.py`: `PolicyEnforcingAgent` — AutoGen `ConversableAgent` duck-typing with policy-gated `generate_reply`
- `adapters/semantic_kernel.py`: `PolicyKernelPlugin` — SK-callable `check_action_permitted()` and `get_permitted_actions()`
- `integrations/langchain.py`: `GovernanceCallbackHandler` — `on_tool_start` enforcement with escalation support
- ADRs: `docs/adr/003-adapter-over-inheritance.md`, `004-framework-agnostic-core.md`
- README: badges, governance flow diagram, 30-second CrewAI example, framework/regulations tables, BibTeX citation
- GitHub Discussions; 22 standardized labels; milestones v0.3.0 + v1.0.0

---

## [0.2.0] - 2026-04-11

### Added

**Regulation modules:**
- `regulations.gdpr` — GDPR (EU 2016/679) policy helpers:
  - `make_gdpr_processing_policy()` — policy factory with DPO escalation rules
  - `GDPRSubjectRequest` — Art. 15/17 subject access/erasure requests with 30-day deadline
  - `GDPRProcessingRecord` — Art. 30 Record of Processing Activities (RoPA)
- `regulations.ccpa` — CCPA/CPRA (Cal. Civil Code §§ 1798.100–1798.199) policy helpers:
  - `make_ccpa_processing_policy()` — policy factory for California consumer data
  - `CCPAConsumerRequest` — know/delete/opt-out/correct requests with 45-day deadline
  - `CCPADataInventoryRecord` — data category inventory for § 1798.110 disclosures
- `regulations.soc2` — SOC 2 Trust Services Criteria policy helpers:
  - `make_soc2_agent_policy()` — policy factory enforcing CC6 logical access controls
  - `SOC2ControlTestResult` — structured evidence record for SOC 2 audit packages
  - `SOC2TrustCategory` — Security, Availability, Processing Integrity, Confidentiality, Privacy

**Framework integrations:**
- `integrations.autogen.GovernedAutoGenAgent` — wraps any AutoGen ConversableAgent;
  `.guarded_tool()` and `.guard_action()` enforce policy on every tool call
- `integrations.llama_index.GovernedQueryEngine` — wraps any LlamaIndex QueryEngine;
  `.query()` and `.aquery()` evaluated against policy before execution
- `integrations.semantic_kernel.GovernedKernelPlugin` — wraps Semantic Kernel functions;
  `.from_object()` auto-registers all public methods with policy enforcement;
  `.add_function()` for manual registration with fluent chaining
- `integrations.haystack.GovernedHaystackComponent` — Haystack-compatible component
  wrapping document processing steps; `.run()` and `.guard_callable()` interfaces

**Cross-cutting compliance primitives:**
- `pii_detector.PIIDetector` — zero-dependency regex PII pre-flight scanner:
  - Detects SSN, EMAIL, PHONE, CREDIT_CARD, IP_ADDRESS, DATE_OF_BIRTH, MRN, BANK_ACCOUNT
  - `.scan()` returns `PIIScanResult` with `PIIFinding` list and category set
  - `.redact()` replaces matches with `[REDACTED-<CATEGORY>]`
  - Category filtering for targeted detection
- `consent.ConsentStore` — in-memory consent registry with pluggable database backend:
  - `ConsentRecord.grant()` / `.revoke()` factories
  - `.is_consented()`, `.latest()`, `.history()` lookups
  - Expiry support (GDPR Art. 7(3) revocation)
- `lineage.LineageTracker` — data lineage trail for regulated pipeline runs:
  - `LineageEventType` — RETRIEVAL, COMPLIANCE_FILTER, CONTEXT_ASSEMBLY, LLM_INPUT, LLM_OUTPUT, TOOL_CALL, DISCLOSURE
  - `.record_retrieval()` and `.record_compliance_filter()` typed helpers
  - `.to_audit_trail()` — JSON-serialisable audit trail per pipeline execution

**OSS infrastructure:**
- `CODE_OF_CONDUCT.md` — Contributor Covenant 2.1
- `ECOSYSTEM.md` — regulation and framework coverage matrix
- Issue templates: new-regulation, new-framework-integration

### Changed
- `pyproject.toml` → version `0.2.0`; added `autogen`, `llama-index`, `semantic-kernel`,
  `haystack` optional dependency groups; expanded keywords

---

## [0.1.0] - 2026-04-11

### Added

- `ActionPolicy` — defines allowed/denied actions and escalation rules for a regulated agent context
- `EscalationRule` — triggers human-in-the-loop or compliance routing when a matching action is attempted
- `PolicyDecision` — result type returned by `ActionPolicy.permits()`
- `GovernedActionGuard` — framework-agnostic guard that checks policy, emits audit records, and optionally blocks on escalation before executing any callable
- `GovernanceAuditRecord` — structured compliance audit record covering FERPA (34 CFR § 99.32), HIPAA (45 CFR § 164.312(b)), and GLBA (16 CFR § 314.4(e)) logging requirements
- `regulations.ferpa` — `make_ferpa_student_policy()` and `make_ferpa_advisor_policy()` pre-built policy factories for FERPA-regulated agents
- `regulations.hipaa` — `make_hipaa_treating_provider_policy()`, `make_hipaa_billing_staff_policy()`, `make_hipaa_researcher_policy()` for HIPAA-regulated agents
- `regulations.glba` — `make_glba_customer_service_policy()` and `make_glba_loan_officer_policy()` for GLBA-regulated agents
- `integrations.crewai.EnterpriseActionGuard` — CrewAI `BaseTool` wrapper backed by `GovernedActionGuard`
- `integrations.langchain.FERPAComplianceCallbackHandler` — LangChain `BaseCallbackHandler` that applies two-layer FERPA identity filtering to retrieval results and emits `GovernanceAuditRecord` per 34 CFR § 99.32
- GitHub Actions CI matrix (Python 3.10, 3.11, 3.12) with pytest, ruff, mypy
- PyPI OIDC trusted publishing workflow (triggers on GitHub release)
- 50+ unit tests covering policy evaluation, audit record structure, regulation helpers, and guard execution paths

[0.1.0]: https://github.com/ashutoshrana/regulated-ai-governance/releases/tag/v0.1.0
