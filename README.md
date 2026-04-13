# regulated-ai-governance

[![CI](https://github.com/ashutoshrana/regulated-ai-governance/actions/workflows/ci.yml/badge.svg)](https://github.com/ashutoshrana/regulated-ai-governance/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/regulated-ai-governance.svg)](https://pypi.org/project/regulated-ai-governance/)
[![Python](https://img.shields.io/pypi/pyversions/regulated-ai-governance.svg)](https://pypi.org/project/regulated-ai-governance/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Downloads](https://img.shields.io/pypi/dm/regulated-ai-governance.svg)](https://pypi.org/project/regulated-ai-governance/)

**Governance framework for AI agents and RAG systems in regulated environments — 23 examples, 11 jurisdictions, 9 AI frameworks, 1027 tests.**

Policy enforcement, audit logging, and compliance orchestration for AI systems that must satisfy FERPA, HIPAA, GDPR, EU AI Act, APPI, MAS FEAT, and 15+ additional regulatory frameworks.

---

## The problem this solves

AI agents in regulated environments can access and process data they are not authorized to see. Standard agent frameworks — CrewAI, AutoGen, LangChain, Semantic Kernel, Haystack — have no concept of regulated industry access control. When you deploy an agent in healthcare, financial services, or a government agency, the framework will not tell you whether the agent is allowed to access a record type, which decisions require human review, or how to produce the audit record the regulator requires.

This library provides those answers as composable Python filters: each filter enforces one regulatory framework, each context object is a frozen dataclass of verifiable compliance state, and every decision produces a structured audit record with a regulation citation.

---

## Architecture

```
User / AI Agent Request
     │
     ▼
GovernanceOrchestrator.evaluate(context, document)
     │
     ├── Filter 1: Identity / Data Protection Gate ──────────────► FilterResult
     │      (FERPA, HIPAA, GDPR, APPI, PDPA...)
     │
     ├── Filter 2: Responsible AI Principles Gate ───────────────► FilterResult
     │      (METI, PDPC Model AI Framework, EU AI Act...)
     │
     ├── Filter 3: Sector-Specific Gate ─────────────────────────► FilterResult
     │      (MAS FEAT, MHLW, DORA, NIST AI RMF...)
     │
     └── Filter 4: Jurisdiction-Specific Gate ───────────────────► FilterResult
            (Cabinet Office, AHRC, DTA ADM, DSIT...)
                     │
                     ▼
              GovernanceReport
              overall_decision: APPROVED / DENIED / REQUIRES_HUMAN_REVIEW / REDACTED
              is_compliant: bool
              compliance_summary: str (human-readable for audit file)
```

**Every filter is independently testable.** Adding a new regulation means adding a new filter class — no existing filter is modified. Each context object is a `@dataclass(frozen=True)` — no mutable state passes through the governance pipeline.

---

## Installation

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

## Quick start: CrewAI + FERPA

```python
from regulated_ai_governance.integrations.crewai import EnterpriseActionGuard
from regulated_ai_governance.regulations.ferpa import make_ferpa_student_policy

guard = EnterpriseActionGuard(
    wrapped_tool=MyTranscriptTool(),
    policy=make_ferpa_student_policy(
        allowed_record_categories={"academic_record"}
    ),
    regulation="FERPA",
    actor_id="stu-alice",
    audit_sink=lambda rec: write_to_db(rec),
    block_on_escalation=True,
)
agent = Agent(tools=[guard], ...)  # drop-in replacement
```

Every evaluation emits a `GovernanceAuditRecord` — whether permitted or denied — with a regulation citation, suitable for a 34 CFR §99.32 disclosure log.

---

## Quick start: Singapore Financial AI (MAS FEAT)

```python
from regulated_ai_governance.examples import singapore_ai_governance as sg

context = sg.SingaporeAIContext(
    user_id="credit-model-v3",
    sector=sg.SingaporeSector.FINANCIAL_SERVICES,
    ai_risk_level=sg.SingaporeAIRiskLevel.HIGH,
    is_automated_decision=True,
    involves_personal_data=True,
    has_pdpa_consent=True,
    is_financial_institution=True,
    has_mas_approval=True,         # MAS FEAT Accountability A.2
    explainability_available=True, # MAS FEAT Transparency T.1
    bias_testing_done=True,        # MAS FEAT Fairness F.1
    human_review_available=True,   # PDPC Framework §2.3
    # ... other fields
)
orch = sg.SingaporeAIGovernanceOrchestrator()
results = orch.evaluate(context, document)
report = sg.SingaporeAIGovernanceReport(context=context, document=document, filter_results=results)
print(report.overall_decision)    # SingaporeAIDecision.APPROVED
print(report.compliance_summary)  # human-readable for audit file
```

---

## Example catalog — 23 governance examples

| # | File | Jurisdiction / Domain | Frameworks Enforced |
|---|------|----------------------|---------------------|
| 01 | `01_basic_policy_enforcement.py` | Cross-industry | FERPA, HIPAA, GDPR, GLBA |
| 02 | `02_crewai_guard.py` | Multi-agent | CrewAI EnterpriseActionGuard |
| 03 | `03_multi_framework_orchestration.py` | Multi-framework | LangChain, CrewAI, AutoGen orchestration |
| 04 | `04_governance_audit_skill.py` | Audit | Audit record assembly + compliance reporting |
| 05 | `05_healthcare_ai_governance.py` | Healthcare | HIPAA, FDA AI/ML Action Plan, ONC |
| 06 | `06_manufacturing_ot_governance.py` | Manufacturing | IEC 62443 OT, ISA-95, safety integrity levels |
| 07 | `07_government_ai_governance.py` | U.S. Government | NIST AI RMF, Executive Order 14110, FedRAMP |
| 08 | `08_insurance_ai_governance.py` | Insurance | NAIC Model Law, FCRA §615, state insurance |
| 09 | `09_finra_sec_governance.py` | U.S. Financial | FINRA, SEC, Reg BI, CCAR |
| 10 | `10_eu_ai_act_governance.py` | European Union | EU AI Act Articles 9/10/12, Annex III |
| 11 | `11_automotive_ai_governance.py` | Automotive | ISO 26262, SOTIF, UN-R155, GDPR |
| 12 | `12_medtech_ai_governance.py` | MedTech | EU MDR, FDA 510(k), IEC 62304, HIPAA |
| 13 | `13_financial_ai_governance.py` | EU Financial | MiFID II, PSD2, DORA Article 9/28 |
| 14 | `14_insurance_ai_governance.py` | Insurance (extended) | Solvency II, ORSA, GDPR |
| 15 | `15_public_sector_ai_governance.py` | Public Sector | NIST AI RMF, ISO 42001:2023, EO 14110 |
| 16 | `16_eu_ai_act_governance.py` | EU AI Act (extended) | Full risk classification + conformity assessment |
| 17 | `17_uk_ai_governance.py` | United Kingdom | UK GDPR Art.22, ICO AI Auditing, Equality Act, DSIT |
| 18 | `18_canada_ai_governance.py` | Canada | AIDA Bill C-27, CPPA, OPC Guidelines, Québec Law 25 |
| 19 | `19_australia_ai_governance.py` | Australia | DIIS 8 AI Ethics, Privacy Act APPs, DTA ADM, AHRC |
| 20 | `20_singapore_ai_governance.py` | Singapore | PDPC Model AI Framework v2, PDPA, MAS FEAT, IMDA |
| 21 | `21_japan_ai_governance.py` | Japan | APPI 2022, METI AI Principles v1.1, MHLW, Cabinet Office |
| 22 | `22_brazil_ai_governance.py` | Brazil | LGPD Law 13.709/2018 (Art. 7/11/33/37), Brazilian AI Bill PL 2338/2023 (Art. 3/14/16/22), ANPD Guidelines 2023, CFM 2299/2021, BCB Circular 3.978/2020, CLT + MPT |
| 23 | `23_india_ai_governance.py` | India | DPDP Act 2023 (§4/6/9/12/16), MEITY AI Advisory 2024 (synthetic media + election safeguards + bias testing), IT Act §43A + IT Rules 2011, RBI/IRDAI/CDSCO sectoral AI guidance |

---

## Jurisdiction and regulation coverage matrix

| Jurisdiction | Regulations Covered | Example |
|-------------|---------------------|---------|
| **United States** | FERPA, HIPAA, GLBA, NIST AI RMF, EO 14110, FINRA, SEC, NAIC | 01, 05, 07–09, 15 |
| **European Union** | EU AI Act (Art. 9/10/12/14), GDPR Art. 22 ADM, MiFID II, PSD2, DORA, Solvency II | 10, 13, 14, 16 |
| **United Kingdom** | UK GDPR Art. 22, ICO AI Auditing Framework 2022, Equality Act 2010 (s.19/s.149 PSED), DSIT AI Safety White Paper | 17 |
| **Canada** | AIDA Bill C-27, CPPA (replacing PIPEDA), OPC Guidelines 2023, Québec Law 25 (Act 25) | 18 |
| **Australia** | DIIS 8 AI Ethics Principles, Privacy Act 1988 (APPs 1/3/6/11, NDB), DTA ADM Framework, AHRC AI & Human Rights | 19 |
| **Singapore** | PDPC Model AI Governance Framework v2 (2020), PDPA 2012 (§§13/26/27/28), MAS FEAT (F.1/T.1/A.2), IMDA AI Testing | 20 |
| **Japan** | APPI 2022 (Art. 20-2/27/28), METI AI Governance Guidelines v1.1, MHLW Medical AI Guidelines, Cabinet Office Social Principles | 21 |
| **Manufacturing / OT** | IEC 62443, ISA-95, IEC 61508 SIL, ISO 26262 (automotive), UN-R155 | 06, 11 |
| **MedTech / Healthcare** | EU MDR, FDA 510(k), IEC 62304, HIPAA, FDA AI/ML Action Plan | 05, 12 |
| **Brazil** | LGPD Law 13.709/2018, Brazilian AI Bill PL 2338/2023, ANPD Guidelines 2023, CFM Resolution 2299/2021, BCB Circular 3.978/2020 | 22 |
| **India** | DPDP Act 2023, MEITY AI Advisory 2024, IT Act 2000 §43A + IT Rules 2011, RBI AI Guidance, IRDAI Guidelines, CDSCO SaMD Guidance | 23 |

---

## AI framework integrations

| Framework | Adapter | Notes |
|-----------|---------|-------|
| CrewAI | `EnterpriseActionGuard` | Tool wrapper — drop-in replacement |
| LangChain | `GovernanceCallbackHandler` | `callbacks.on_retriever_end` |
| LlamaIndex | `ComplianceNodePostprocessor` | Post-processor for retrieved nodes |
| AutoGen | `PolicyEnforcingAgent` (maintenance mode — prefer MAF) | Message interceptor |
| Semantic Kernel | `PolicyKernelPlugin` (maintenance mode — prefer MAF) | SK Plugin interface |
| Haystack | `FERPAMetadataFilter` | PR #11080 — OPEN in deepset-ai/haystack |
| DSPy | `ComplianceModule` | DSPy module wrapper |
| Microsoft Agent Framework (MAF) | `GovernanceMAFMiddleware` | Successor to AutoGen + Semantic Kernel |

---

## Repository structure

```
src/regulated_ai_governance/
├── __init__.py               # Core exports
├── policy.py                 # ActionPolicy, GovernanceAuditRecord
├── regulations/
│   ├── ferpa.py              # FERPA 34 CFR §99
│   ├── hipaa.py              # HIPAA 45 CFR §164
│   ├── gdpr.py               # GDPR Art. 17/22
│   ├── glba.py               # GLBA 16 CFR §314
│   └── ...
└── integrations/
    ├── crewai.py             # EnterpriseActionGuard
    ├── langchain.py          # GovernanceCallbackHandler
    ├── autogen.py            # PolicyEnforcingAgent
    ├── llama_index.py        # ComplianceNodePostprocessor
    ├── semantic_kernel.py    # PolicyKernelPlugin
    ├── haystack.py           # FERPAMetadataFilter
    ├── dspy.py               # ComplianceModule
    └── maf.py                # GovernanceMAFMiddleware
examples/                     # 23 runnable governance examples (see catalog above)
tests/                        # 983 passing tests
docs/
└── ECOSYSTEM.md              # Full regulation and framework coverage matrix
```

---

## Audit record format

Every filter evaluation produces a structured audit record:

```python
{
    "filter_name":          "APPI_DATA_PROTECTION",
    "decision":             "DENIED",
    "reason":               "APPI Article 20-2: Opt-in consent required for sensitive personal information",
    "regulation_citation":  "Act on Protection of Personal Information (APPI) 2022 Article 20-2",
    "requires_logging":     True
}
```

JSON-serializable; suitable for compliance databases, SIEM ingestion, and regulator production requests.

---

## External PR — highest adoption signal

**deepset-ai/haystack#11080** — `FERPAMetadataFilter` component for Haystack pipelines (25 tests, full serialization, async support, zero new dependencies). PR open since April 2026. When merged, any Haystack pipeline can apply FERPA identity scoping with one `pipeline.add_component()` call.

---

## Near-term roadmap

- `24_south_korea_ai_governance.py` — AI Basic Act + PIPA
- `25_middle_east_ai_governance.py` — UAE AI Strategy 2031 + Saudi NDS + Qatar NDCS
- ISO 42001:2023 AI Management System compliance layer (standalone)
- Async filter support for FastAPI/asyncio environments

---

## Contributing

Read [CONTRIBUTING.md](./CONTRIBUTING.md) and [GOVERNANCE.md](./GOVERNANCE.md). Run `pytest tests/ -v` before opening a pull request.

---

## Citation

```bibtex
@software{rana2026rag,
  author  = {Rana, Ashutosh},
  title   = {regulated-ai-governance: Policy enforcement for AI agents in regulated environments},
  year    = {2026},
  version = {0.24.0},
  url     = {https://github.com/ashutoshrana/regulated-ai-governance},
  license = {MIT}
}
```

---

## Part of the enterprise AI patterns trilogy

| Library | Focus | Coverage |
|---------|-------|---------|
| [enterprise-rag-patterns](https://github.com/ashutoshrana/enterprise-rag-patterns) | What to retrieve | 30 sectors · 29 regulations · 924 tests |
| **regulated-ai-governance** | What agents may do | 23 governance examples · 11 jurisdictions · 1027 tests |
| [integration-automation-patterns](https://github.com/ashutoshrana/integration-automation-patterns) | How data flows | 24 patterns · distributed tracing · event sourcing · 657 tests |

---

## License

MIT — see [LICENSE](LICENSE).
