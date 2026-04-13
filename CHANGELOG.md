# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.11.0] — 2026-04-13

### Added — Financial Services AI Governance (SEC Reg BI + FINRA Rule 3110 + SR 11-7)

**`examples/09_finra_sec_governance.py`** — multi-framework AI governance for a
registered broker-dealer's AI investment advisory assistant:

New classes (self-contained in the example):
- `CustomerType` — RETAIL (full Reg BI protections) vs. INSTITUTIONAL (Reg BI exempted)
- `RecommendationAction` — BUY, SELL, HOLD, REBALANCE, GENERATE_REPORT,
  GENERATE_SUITABILITY_ANALYSIS, SCREEN_SECURITIES
- `GovernanceOutcome` — ALLOW, DENY, ESCALATE_HUMAN, ADVISORY_ONLY, SHADOW_ALLOW;
  `ADVISORY_ONLY` is distinct from `DENY` — recommendation is generated but must
  include explicit model limitation disclosure (SEC Model Risk stale validation)
- `BrokerDealerRequestContext` — request boundary: customer type, action, securities,
  portfolio concentration %, firm inventory positions, suitability data age, model ID,
  model validation age, conflicts disclosed flag
- `RegBIGuard` — enforces SEC Reg BI §240.15l-1: (1) firm inventory conflict without
  disclosure → DENY; (2) BUY recommendation for conflicted security requires care
  obligation review even when disclosed; applies only to retail customers
- `FINRA3110Guard` — enforces FINRA Rule 3110: (1) concentration > 25% requires
  registered principal review → ESCALATE_HUMAN; (2) suitability data > 365 days
  requires KYC refresh; (3) large transaction (> 10% portfolio) requires supervisory
  review; principal review = ESCALATE_HUMAN (not DENY)
- `SECModelRiskGuard` — enforces SR 11-7 principles: (1) model must be in firm model
  inventory; (2) model validated > 365 days ago → ADVISORY_ONLY (not DENY — model is
  useful but must be presented as non-binding with limitation disclosure); unregistered
  model → DENY
- `BrokerDealerAuditRecord` — FINRA Rule 4511 / SEC Reg S-P compliant audit record:
  per-framework results, governance outcome, conflicts_detected, principal_review_required,
  advisory_only_mode
- `BrokerDealerGovernanceOrchestrator` — outcome priority: DENY > ESCALATE_HUMAN >
  ADVISORY_ONLY > ALLOW; shadow mode for FINRA exam / SEC model risk quarterly review

Scenarios:
- A: Standard diversified BUY (5% concentration, no conflicts, model validated 180d) → ALLOW
- B: High-concentration BUY (35% in single security) → ESCALATE_HUMAN (FINRA 3110)
- C: BUY in firm inventory security, conflicts not disclosed → DENY (Reg BI)
- D: Model last validated 420 days ago → ADVISORY_ONLY (SR 11-7; not DENY)
- E: Shadow audit mode — 4 scenarios logged without blocking for FINRA exam prep

Framework coverage now spans 9 regulated sectors:
healthcare · OT/manufacturing · government/defense · insurance · **broker-dealer/investment**

Closes #28.

---

## [0.10.0] — 2026-04-13

### Added — Insurance Sector AI Governance (NAIC Model Bulletin + State Anti-Discrimination + FCRA/GLBA)

**`examples/08_insurance_ai_governance.py`** — multi-framework AI governance for an
insurance underwriting and claims triage assistant, combining three compliance frameworks:

New classes (self-contained in the example):
- `InsuranceLine` — line of business (PERSONAL_AUTO, HOMEOWNERS, COMMERCIAL_PROPERTY,
  WORKERS_COMP, LIFE, HEALTH)
- `InsuranceAction` — agent actions (GENERATE_AUTO_QUOTE, UNDERWRITE_STANDARD_RISK,
  UNDERWRITE_ADVERSE_DECISION, TRIAGE_CLAIM, APPROVE_CLAIM, DENY_CLAIM,
  ISSUE_ADVERSE_ACTION_NOTICE, GENERATE_EXPLANATION)
- `InsuranceRequestContext` — request boundary: line of business, action, applicant state,
  model features, preliminary outcome, premium change %, credit report usage, MRM inventory ID
- `NAICModelBulletinGuard` — enforces NAIC Model Bulletin on AI (2023): (1) AI system must
  be in MRM inventory, (2) adverse decisions ≥ 15% premium impact require human attestation,
  (3) claims denials require human review under §IV.B
- `StateAntiDiscriminationGuard` — enforces state prohibited proxy variable registries;
  state-specific: CA bans credit_score + zip_code for auto (CA Ins. Code §1861.02), NY
  bans credit_score (N.Y. Ins. Law §2611), MI bans credit_score; federal baseline bans
  race/religion/national_origin/sex; blocks decisions using prohibited proxy features
- `FCRAGLBAGuard` — enforces FCRA §615 (credit-based adverse action requires written
  consumer disclosure) and GLBA Safeguards Rule (NPI features — SSN, account_number,
  income, credit_history — must not appear unprotected in AI payload)
- `InsuranceGovernanceAuditRecord` — NAIC MRM-required audit record: request context,
  per-framework results, governance outcome, prohibited proxies detected, human oversight
  required flag, adverse action disclosure required flag
- `InsuranceGovernanceOrchestrator` — deny-all aggregation; `ESCALATE_HUMAN` when NAIC
  requires human oversight; `DENY` for state anti-discrimination violations; shadow mode
  for quarterly MRM reporting

Scenarios:
- A: Standard CA auto quote (no prohibited proxies, no adverse outcome) — ALLOW
- B: Adverse underwriting decision (premium +28%, CA) — NAIC threshold exceeded →
  ESCALATE_HUMAN (human attestation required)
- C: Underwriting with `credit_score` feature in CA — state anti-discrimination guard
  detects prohibited proxy → DENY (escalate to compliance review)
- D: Claims denial with credit report (NY) — NAIC (§IV.B human attestation) + FCRA §615
  (written disclosure) both fire → ESCALATE_HUMAN with adverse_action_disclosure=True
- E: Shadow mode — all 4 actions evaluated without blocking; violation counts logged
  for NAIC quarterly MRM review (§IV.C)

Framework coverage now spans 8 regulated sectors:
HIPAA + NIST AI RMF + EU AI Act (healthcare) · ISO 42001 + IEC 62443 + DORA (OT) ·
CMMC L2 + FedRAMP + NIST 800-53 (defense) · **NAIC + state anti-discrimination + FCRA/GLBA (insurance)**

Closes #27.

---

## [0.9.0] — 2026-04-13

### Added — Government/Defense AI Governance Example (CMMC L2 + FedRAMP + NIST 800-53)

**`examples/07_government_ai_governance.py`** — multi-framework AI governance for a
DoD procurement AI assistant, combining CMMC Level 2 (32 CFR Part 170), FedRAMP
Moderate authorization boundary, and NIST 800-53 AC-3 access control:

Three `FrameworkGuard`s orchestrated by a single `GovernanceOrchestrator` (deny-all
aggregation — any one framework blocking an action stops execution):

- **CMMC Level 2 Guard (32 CFR Part 170):** Defense contractors handling CUI must be
  CMMC Level 2 certified. Allowed actions restricted to the 11 domains of CMMC L2
  (`CMMC_L2_ALLOWED_ACTIONS`). Non-certified entities have a minimal allowed set.
- **FedRAMP Moderate Guard:** Actions touching federal systems must operate within
  the FedRAMP authorization boundary. `FEDRAMP_DENIED_ACTIONS` (use_commercial_api,
  store_data_commercial_cloud, export_controlled_data_transfer) are blocked regardless
  of CMMC status; `FEDRAMP_ALLOWED_ACTIONS` defines the approved surface.
- **NIST 800-53 AC-3 Guard:** Privileged functions (`run_privileged_query`,
  `modify_system_configuration`, `export_controlled_data_transfer`) are restricted to
  the `nist_privileged` role; standard government users are denied.

Scenarios:
- A: CMMC L2 certified contractor + FedRAMP boundary + standard role → `query_procurement_database`
  allowed by all three frameworks (ALLOW)
- B: Non-certified vendor attempts CUI access → CMMC L2 guard denies immediately (DENY);
  uses a separate `GovernanceOrchestrator` with an uncertified policy to accurately model
  a non-certified entity
- C: Certified contractor calls `use_commercial_api` → FedRAMP guard denies (DENY);
  action is in `FEDRAMP_DENIED_ACTIONS` regardless of CMMC certification
- D: Standard user attempts `run_privileged_query` → NIST AC-3 guard denies (DENY);
  action restricted to `nist_privileged` role
- E: Public notice action (`publish_solicitation_notice`) → all three frameworks allow
  (ALLOW); action is in all approved sets and requires no privileged role

Closes #26.

---

## [0.8.0] — 2026-04-13

### Added — Manufacturing/OT Governance Example + Implementation Notes

**`examples/06_manufacturing_ot_governance.py`** — multi-framework AI governance for a
predictive maintenance agent in a chemical plant, combining ISO/IEC 42001:2023 AI Management
System, IEC 62443 OT Security Levels, and DORA ICT Risk Management (Art. 28):
- ISO 42001 A.6.2.10: operating-scope enforcement (advisory monitoring zone only)
- ISO 42001 A.9.5: human oversight required for autonomous actuation (HIGH-risk classification)
- IEC 62443 SL-2: agent authorized at Security Level 2; SL-3 Control Zone actions denied
- IEC 62443 zone/conduit model: Process Control Zone → Business Zone crossing denied
- DORA Art. 28: third-party ML services not in the ICT service register are denied
- Scenario A: `sensor_anomaly_detection` — advisory monitoring, all frameworks permit (ALLOW)
- Scenario B: `autonomous_valve_control` — ISO 42001 + IEC 62443 both deny (DENY)
- Scenario C: `third_party_ml_inference` — DORA Art. 28 undocumented dependency (DENY)
- Scenario D: `maintenance_scheduling_recommendation` — advisory, all frameworks permit (ALLOW)
- Scenario E: `cross_plant_data_sharing` — IEC 62443 zone boundary violation (DENY)
- Closes #21.

**`docs/implementation-note-01.md`** — "Multi-Framework AI Governance: Why Single-Layer Compliance Fails":
- Deny-all aggregation rationale and the conjunctive nature of compliance obligations
- Escalation routing: why different violations go to different targets
- Skip vs. deny distinction for jurisdictional applicability
- Concrete failure scenario: HIPAA-only system lacking NIST AI RMF guard
- Three-step pattern for adding a new framework to an existing orchestrator
- Closes #20 (partially).

**`docs/implementation-note-02.md`** — "Audit Trail Design for Regulated AI: What to Log and Why":
- `GovernanceAuditRecord` and `ComprehensiveAuditReport` field-by-field rationale
- Retention requirements by regulation: HIPAA (6yr), EU AI Act (10yr), GDPR, DORA, SOC 2
- Shadow (audit-only) mode and its compliance implications
- What the governance audit trail is NOT responsible for
- Closes #20 (partially).

**`docs/implementation-note-03.md`** — "Adapter Pattern for Multi-Framework Integrations":
- Why adapter-over-inheritance (ADR-003) keeps the compliance core framework-agnostic
- Complete integration table: 8 framework adapters (CrewAI, LangChain, AutoGen, SK, Haystack, LlamaIndex, DSPy, MAF)
- Step-by-step guide to adding a new framework adapter
- Testing strategy: unit testing guards vs. integration testing adapters
- Framework version migration pattern (e.g. AutoGen 0.2 → MAF)
- Closes #20.

---

## [0.7.1] — 2026-04-13

### Added — Healthcare AI Governance Example

**`examples/05_healthcare_ai_governance.py`** — multi-framework AI governance for an
ICU clinical decision support (CDS) agent combining HIPAA, NIST AI RMF AI 600-1,
and EU AI Act HIGH_RISK classification:
- Deny-all aggregation: `GovernanceOrchestrator` with three `FrameworkGuard`s active
  simultaneously — one DENY from any framework stops the action.
- Scenario A: `read_vitals` — allowed by all three frameworks (ALLOW)
- Scenario B: `recommend_medication_dosage` — HIPAA allows; NIST AI RMF + EU AI Act
  trigger mandatory escalation with `block_on_escalation=True` (DENY, human review required)
- Scenario C: `share_phi_externally` — explicitly denied by HIPAA (DENY immediately)
- Scenario D: `create_clinical_note` — allowed by all frameworks (ALLOW)
- Scenario E: Audit-only mode — all four actions evaluated without blocking; full
  `ComprehensiveAuditReport` emitted per evaluation for shadow compliance assessment
- Governance design notes: minimum-necessary scoping, MANAGE function escalation,
  Art. 14 human oversight, audit-only rollout pattern
- Closes #19.

---

## [0.7.0] — 2026-04-13

### Added — DSPy Framework Integration

- `integrations/dspy.py`: `GovernedDSPyModule` and `GovernedDSPyPipeline` —
  policy-enforcing wrappers for DSPy `Module` objects (DSPy ≥ 2.5.0, Pydantic v2).

  **`GovernedDSPyModule`** wraps any DSPy module:
  - `forward(*args, **kwargs)` and `__call__` evaluate the `ActionPolicy` before
    delegating to the wrapped module.  Denied actions raise `PermissionError`.
  - `action_name` defaults to `type(wrapped_module).__name__` — configure
    `ActionPolicy.allowed_actions` with class names of permitted modules.
  - Emits a `GovernanceAuditRecord` for every call (permitted, denied, escalated).
  - `__getattr__` delegation — DSPy introspection (`predictors()`, `parameters()`,
    etc.) works transparently through the guard wrapper.
  - Optional `context` dict included in every audit record (session ID, pipeline
    stage, etc.).

  **`GovernedDSPyPipeline`** wraps a sequential pipeline:
  - Each module is individually guarded; denied intermediate steps fail fast.
  - Dict outputs are unpacked as `**kwargs` for the next step; non-dict outputs
    are passed as a single positional argument.

  Closes #2. 27 new tests.

- `integrations/__init__.py`: exports `GovernedDSPyModule`, `GovernedDSPyPipeline`.

---

## [0.6.0] — 2026-04-13

### Added — Cross-Industry AI Governance Regulation Modules

**EU AI Act 2024/1689** (`regulations/eu_ai_act.py`):
- `EUAIActRiskCategory`: UNACCEPTABLE / HIGH_RISK / LIMITED_RISK / MINIMAL_RISK.
- `EUAIActSystemProfile`: declares system risk category, prohibited practices, high-risk domains, conformity assessment status, FRIA completion, transparency obligations.
- `EUAIActGovernancePolicy.evaluate_action()`: six-step evaluation — Art. 5 prohibited practices → Art. 6–9 risk category check → Art. 43 conformity assessment gate (high-risk) → Art. 27 FRIA check → Art. 14 human oversight routing → Art. 12 logging requirement.
- `EUAIActAuditRecord`: structured audit record with SHA-256 tamper evidence.
- `make_eu_ai_act_minimal_risk_policy()` / `make_eu_ai_act_high_risk_policy()`: factory constructors.
- `EU_AI_ACT_PROHIBITED_PRACTICES`, `EU_AI_ACT_HIGH_RISK_DOMAINS`: curated constant sets for Art. 5 and Annex III.
- 58 tests in `tests/test_eu_ai_act.py`.

**DORA EU 2022/2554** (`regulations/dora.py`):
- `DORAICTRiskLevel`: CRITICAL / HIGH / MEDIUM / LOW.
- `DORAICTCapabilityArea`: IDENTIFY / PROTECT / DETECT / RESPOND / RECOVER (Art. 9 five-function model).
- `DORAThirdPartyRecord`: third-party ICT provider risk assessment (Art. 28).
- `DORAICTIncidentRecord`: ICT incident report with impact, RTO, response timeline (Art. 17–18).
- `make_dora_ict_management_policy()` / `make_dora_third_party_policy()`: factory constructors.
- `DORA_HIGH_RISK_ICT_ACTIONS`: curated set of actions triggering DORA Art. 9 controls.
- Tests in `tests/test_dora.py`.

**NIST AI RMF 1.0 + AI 600-1 GenAI Profile** (`regulations/nist_ai_rmf.py`):
- `NISTAIRMFFunction`: GOVERN / MAP / MEASURE / MANAGE.
- `NISTAIRMFRiskCategory`: CONFABULATION / DATA_BIAS / HUMAN_AI_CONFIGURATION / HARMFUL_CONTENT / PRIVACY / SECURITY / ACCOUNTABILITY / TRANSPARENCY.
- `NISTAIRMFRiskAssessment`: structured risk assessment across RMF functions with severity and likelihood.
- `make_nist_ai_rmf_policy()`: factory constructor mapping GenAI profile controls.
- `NIST_GENAI_HIGH_RISK_ACTIONS`: actions requiring MANAGE-function controls per AI 600-1.
- Tests in `tests/test_nist_ai_rmf.py`.

**OWASP LLM Top 10 (2025)** (`regulations/owasp_llm.py`):
- `OWASPLLMRisk`: LLM01 Prompt Injection / LLM02 Sensitive Info Disclosure / LLM05 Output Handling / LLM06 Excessive Agency / LLM07 System Prompt Leakage / LLM09 Misinformation / LLM10 Unbounded Consumption.
- `make_owasp_llm_policy()`: factory constructor blocking the 7 highest-severity OWASP LLM risks.
- `OWASP_LLM_DENIED_ACTIONS`, `OWASP_LLM_2025_ALL_RISKS`: curated constants.
- Tests in `tests/test_owasp_llm.py`.

**`regulations/__init__.py`**: updated to export all symbols from the four new modules alongside existing `iso42001` exports.

### Tests
- +198 new tests (58 EU AI Act, 51 DORA, 49 NIST AI RMF, 40 OWASP LLM).
- Total test count: **480 passing**.

---

## [0.5.0] — 2026-04-13

### Added — Comprehensive Governance Architecture

**Multi-Framework Orchestrator** (`orchestrator.py`):
- `GovernanceOrchestrator`: evaluates agent actions against multiple compliance frameworks simultaneously with deny-all aggregation — if any framework denies, the overall decision is DENY. Suitable for regulated environments requiring simultaneous FERPA + HIPAA + GDPR + ISO 42001 enforcement.
- `FrameworkGuard`: associates a `GovernedActionGuard` with a regulation label and enabled/disabled state.
- `FrameworkResult`: per-framework evaluation result (regulation, permitted, denial_reason, escalation_target, skipped).
- `MultiFrameworkDecision`: aggregated decision across all frameworks with framework-level attribution.
- `ComprehensiveAuditReport`: unified compliance audit record capturing every framework's decision, denial reasons, escalation targets, tamper-evident SHA-256 hash, `to_log_entry()` (SIEM-ready JSON), `to_compliance_summary()` (human-readable GRC report).
- `GovernanceOrchestrator.audit_only`: shadow mode — evaluate all frameworks and log outcomes without blocking any action. For progressive rollout and compliance posture assessment.

**ISO/IEC 42001:2023 AI Management System** (`regulations/iso42001.py`):
- `ISO42001OperatingScope`: defines permitted/prohibited use cases, deployment approval status, and human oversight requirements per the ISO 42001 operating scope (A.6.2.10).
- `ISO42001GovernancePolicy.evaluate_action()`: three-step evaluation — A.6.2.5 deployment gate → A.6.2.10 prohibited/permitted use → A.9.5 human oversight routing.
- `ISO42001DataProvenanceRecord`: documents chain of custody for AI training/knowledge data (A.7.2/A.7.5/A.7.6).
- `ISO42001DeploymentRecord`: formal deployment approval record with risk assessment and impact assessment outcomes (A.5.2/A.5.3/A.6.2.5).
- `ISO42001AuditRecord`: structured audit record per governance evaluation with SHA-256 tamper evidence.
- `ISO42001PolicyDecision`: decision with `human_oversight_required` flag for A.9.5 routing.

**Governance Audit Skill** (`skill.py`):
- `GovernanceAuditSkill`: high-level skill wrapping `GovernanceOrchestrator` with framework-aware factory constructors and multi-channel adapters.
- `GovernanceAuditSkill.for_education()`: FERPA-compliant skill factory for educational AI systems.
- `GovernanceAuditSkill.for_healthcare()`: HIPAA-compliant skill factory for healthcare AI systems.
- `GovernanceAuditSkill.for_enterprise()`: multi-regulation skill factory (FERPA + HIPAA + GDPR + GLBA + SOC2 simultaneously) for enterprise AI agents.
- `GovernanceAuditSkill.audit_action()`: evaluate and execute with per-call framework scoping — restrict evaluation to a subset of configured frameworks for individual actions.
- `GovernanceAuditSkill.audit_retrieval()`: action-level authorization gate for document retrieval. Returns all documents if actor is authorized; empty list if denied. Content-level filtering remains in `enterprise-rag-patterns`.
- `GovernanceAuditSkill._framework_scope`: context manager for per-call framework restriction; automatically restores disabled frameworks on exit.
- Channel adapters: `as_langchain_handler()`, `as_crewai_tool()`, `as_llama_index_postprocessor()`, `as_haystack_component()`, `as_maf_middleware()` — all lazy imports.
- `GovernanceConfig`, `FrameworkConfig`: declarative configuration dataclasses.

**Examples**:
- `examples/03_multi_framework_orchestration.py`: FERPA + HIPAA + ISO 42001 simultaneous orchestration with `ComprehensiveAuditReport`.
- `examples/04_governance_audit_skill.py`: all five scenarios — education/healthcare/enterprise factories, per-call framework scoping, audit-only shadow mode.

**Tests** (+80 new, 282 total):
- `tests/test_orchestrator.py` (42 tests): `FrameworkGuard`, `FrameworkResult`, orchestrator evaluate/guard, `ComprehensiveAuditReport` JSON/hash/summary, add/remove/enable/disable framework.
- `tests/test_iso42001.py` (27 tests): `ISO42001OperatingScope`, `ISO42001GovernancePolicy` evaluate_action (deployment gate, prohibited, permitted, human oversight), all three record types, orchestrator integration test.
- `tests/test_skill.py` (29 tests): factory constructors, `audit_action`, `audit_retrieval`, channel adapter ImportError, `_framework_scope` context manager.

**Top-level exports** (added to `__init__.py`):
`FrameworkGuard`, `FrameworkResult`, `MultiFrameworkDecision`, `ComprehensiveAuditReport`, `GovernanceOrchestrator`, `FrameworkConfig`, `GovernanceConfig`, `GovernanceAuditSkill`.

---

## [0.4.1] — 2026-04-13

### Added
- `integrations/llama_index.py`: `PolicyWorkflowGuard` — LlamaIndex 0.12+ event-driven Workflow guard step. Receives a `PolicyWorkflowEvent`, evaluates `ActionPolicy`, emits `GovernanceAuditRecord`, and either passes the event downstream (permitted) or raises `PermissionError` (denied/escalation-blocked). Closes #17.
- `integrations/llama_index.py`: `PolicyWorkflowEvent` — Workflow event type carrying `documents`, `query`, and `action_name` between Workflow steps.
- `integrations/haystack.py`: `make_haystack_policy_guard()` — factory that returns a Haystack 2.27 `@component`-decorated class enforcing `ActionPolicy` inside a Haystack pipeline. Applies `@component` and `@component.output_types(documents=list)` at call time (lazy Haystack import). Closes #18.
- `integrations/__init__.py`: exports `PolicyWorkflowGuard`, `PolicyWorkflowEvent`, `make_haystack_policy_guard`

---

## [0.4.0] — 2026-04-12

### Added
- `integrations/maf.py`: `PolicyMiddleware` — Microsoft Agent Framework (MAF) middleware intercepting agent messages, evaluating `ActionPolicy`, emitting `GovernanceAuditRecord` per call, and blocking escalated actions. MAF is the enterprise successor to AutoGen and Semantic Kernel (2026).
- `[maf]` optional dependency: `microsoft-agent-framework>=1.0.0`
- `[all]` extra combining all framework integrations (crewai, langchain, llama-index, semantic-kernel, haystack, maf)

### Changed
- Bumped ecosystem compatibility pins:
  - `crewai`: `>=1.0.0` → `>=1.14.0` (CrewAI 1.14.1 current; tool-search support, Anthropic contextvars propagation)
  - `semantic-kernel`: `>=1.0.0` → `>=1.41.0` (Semantic Kernel 1.41.1 current)
  - `haystack-ai`: `>=2.0.0` → `>=2.20.0` (Haystack 2.27.0 current)
- `integrations/__init__.py`: added MAF deprecation notice for AutoGen and Semantic Kernel; exports updated
- `pyproject.toml`: version bumped to 0.4.0

### Deprecation Notice
AutoGen (`pyautogen`) is in maintenance mode as of 2026 — Microsoft has moved to Microsoft Agent Framework (MAF). The `autogen.py` integration remains functional for backward compatibility. **New projects should use `integrations/maf.py`** (`PolicyMiddleware`). The `autogen` optional dependency will be removed in v1.0.0.

Similarly, Semantic Kernel (`semantic-kernel`) projects are recommended to migrate to MAF per Microsoft guidance.

---

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
