# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
