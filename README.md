# regulated-ai-governance

[![CI](https://github.com/ashutoshrana/regulated-ai-governance/actions/workflows/ci.yml/badge.svg)](https://github.com/ashutoshrana/regulated-ai-governance/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/regulated-ai-governance.svg)](https://pypi.org/project/regulated-ai-governance/)
[![Python](https://img.shields.io/pypi/pyversions/regulated-ai-governance.svg)](https://pypi.org/project/regulated-ai-governance/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Downloads](https://img.shields.io/pypi/dm/regulated-ai-governance.svg)](https://pypi.org/project/regulated-ai-governance/)

**Governance framework for AI agents and RAG systems in regulated environments — 35 examples, 21 jurisdictions, 9 AI frameworks, 2023 tests.**

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

## Example catalog — 35 governance examples

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
| 24 | `24_south_korea_ai_governance.py` | South Korea | Korea AI Framework Act 2024 (Art. 6/10 high-impact + prohibited AI), PIPA (Art. 15/23/28-2/28-3/39-3 automated decisions + profiling + cross-border), Credit Information Act Art. 20, MFDS SaMD approval |
| 25 | `25_middle_east_ai_governance.py` | Middle East (GCC) | UAE PDPL (Federal Decree-Law No. 45/2021 Art. 7/10/16) + UAE AI Ethics 2019, Saudi PDPL (Royal Decree M/19 Art. 4/NDMO) + SAMA/SFDA, Qatar PDPA (Law No. 13/2016 Art. 8/9) + Qatar AI Strategy 2030, GCCCrossBorderFilter (adequate: AE/SA/QA/BH/KW/OM) |
| 26 | `26_africa_ai_governance.py` | Africa (Kenya, Nigeria, South Africa) | Kenya DPA 2019 (§25/§30/§31 automated decisions + sensitive data + profiling), Nigeria NDPA 2023 (§25/§34) + NITDA AI Policy §3.2, South Africa POPIA 2013 (§26/§71) + FSCA AI Guidance 2023, AU cross-border adequacy framework (KE/NG/ZA/GH/MA/TN/EG) |
| 27 | `27_iso42001_compliance.py` | ISO 42001:2023 AI Management System | ISO 42001 Clause 5 (AI Policy — top management leadership), Clause 6 (Risk assessment + Annex B impact assessment), Clause 8 (Operations — human oversight + data governance + third-party AI), Clause 9 (Performance evaluation — audit trail + documented information + incident process); conformity_level: FULL/PARTIAL/NON_CONFORMING |
| 28 | `28_nordic_ai_governance.py` | Nordic/Scandinavia (Sweden, Denmark, Finland) | Sweden IMY AI Guidelines 2023 + SFS 2018:218, Denmark Datatilsynet AI Guidance 2023 + Act No. 502/2018, Finland TSV AI Guidelines 2023 + Data Protection Act 1050/2018, NordicCrossBorderFilter (intra-EEA adequate; non-EEA jurisdiction-specific GDPR Art. 46 denials) |
| 29 | `29_eastern_europe_ai_governance.py` | Eastern Europe (Poland, Czech Republic, Hungary) | Poland UODO AI Guidelines 2023 + GDPR Act Dz.U. 2018, Czech ÚOOÚ AI Guidance 2023 + Act 110/2019, Hungary NAIH AI Guidelines 2023 + Privacy Act CXII/2011, EasternEuropeCrossBorderFilter (30-jurisdiction EEA adequate set + SCC/BCR fallback) |
| 30 | `30_us_state_ai_laws.py` | US State AI Laws (Colorado, Illinois, Virginia) | Colorado AI Act 2024 SB 24-205 §6-1-1702 (high-risk AI impact assessment + human oversight + bias testing), Illinois BIPA 740 ILCS 14/15 (biometric written consent + video interview AI + third-party sharing), Virginia CDPA AI provisions Va. Code §59.1-577/578/579/581 (sensitive data + automated profiling + high-risk AI), USStateAICrossBorderFilter (IL biometric / CO high-risk / CA CPRA / VA-TX-CT opt-out matrix) |
| 31 | `31_eu_ai_act_high_risk.py` | EU AI Act 2024 High-Risk Systems | EUAIActHighRiskCategoryFilter (Art. 5 prohibited + Annex III §1-8 conformity assessment + Art. 27 FRIA + Art. 49/71 database registration), EUAIActTechnicalRequirementsFilter (Arts. 9-15 risk mgmt/data governance/technical docs/human oversight/accuracy), EUAIActTransparencyFilter (Arts. 50/13 AI disclosure/deepfake labeling/emotion recognition/instructions), EUAIActCrossBorderFilter (Art. 2 export + Arts. 51-55 GPAI technical docs/systemic risk/copyright), 8 ecosystem wrappers |
| 32 | `32_gdpr_ai_accountability.py` | GDPR AI Accountability (EU/EEA) | GDPRAutomatedDecisionFilter (Art. 22(1) legal basis + Art. 22(3) explanation right + Art. 22(4) special category data + Art. 21(2) direct marketing objection), GDPRTransparencyFilter (Art. 13(1) privacy notice + Art. 13(2)(f) logic disclosure + Art. 13(1)(f) transfer safeguards + Art. 13(2)(a) retention period), GDPRDPIAFilter (Art. 35(1) high-risk DPIA + Art. 35(3)(c) systematic monitoring + Art. 35(3)(b) special category scale + Art. 36(1) SA prior consultation), GDPRDataMinimisationFilter (Art. 5(1)(c) minimisation + Art. 5(1)(b)/89 purpose limitation + Art. 25(1) privacy by design + Art. 5(1)(e) storage limitation), 8 ecosystem wrappers |
| 33 | `33_singapore_ai_governance.py` | Singapore (PDPA + MAS FEAT + AI Verify) | SingaporePDPAFilter (§13 consent + §15A sensitive data NRIC/FIN/health/biometric + §26 cross-border adequacy AU/CA/DE/JP/NZ/UK/EU + AI Advisory §4.2 automated decision), MASFEATFilter (Fairness §2.1 + Accountability §4.1 + Transparency §5.2 + Ethics §3.3), AIVerifySingaporeFilter (§3.1 self-assessment 11 principles + §4.2 explainability LIME/SHAP + IMDA GenAI §5.1 + §4.1 fairness testing), SingaporeCrossBorderFilter (MAS TRM §4.1 financial safeguards + PDPC TIA for CN/RU/KP + MAS Cloud AWS/GCP/Azure SG whitelist + FAA-N18 FATF), 8 ecosystem wrappers |
| 34 | `34_japan_ai_governance.py` | Japan (APPI 2022 + FSA + METI AI Governance) | JapanAPPIFilter (Arts. 15/17 consent + Art. 20 specially considered PI race/creed/medical/criminal/disability + Art. 28 cross-border adequacy EU/UK + PPC AI Guidelines §3.2 automated profiling), JapanFSAAIFilter (FIEA Art. 40 suitability + FSA Principle 3 credit explainability + Insurance Business Act Art. 113 actuarial opinion + FSA stress testing), JapanAIGovernanceFilter (METI Guideline v1.1 §4 self-assessment + AI Strategy §2.1 human oversight + METI GenAI §3 eight principles + Cabinet Office §3.3 public services), JapanCrossBorderFilter (APPI Art. 28 CN/RU/KP restricted + AML FATF non-compliant jurisdictions + FSA Cloud aws_tokyo/gcp_tokyo/azure_japan_east whitelist + US adequacy pending), 8 ecosystem wrappers |
| 35 | `35_south_korea_ai_governance.py` | South Korea (PIPA 2023 + FSC + AI Basic Act 2024) | KoreaPIPAFilter (Art. 15 consent + Art. 23 sensitive ideology/beliefs/union/political/health/sexual/biometric/criminal/genetic + Art. 28-8 cross-border adequacy EU/UK/CA + Art. 37-2 automated decision explanation 2023 amendment), KoreaFSCAIFilter (FSCMA Art. 7 robo-advisor registration + CB Act Art. 26 credit scoring FSC validation + IBA Art. 176 actuarial cert + FSCMA Art. 63 algorithmic trading), KoreaAIBasicActFilter (Art. 47 high-impact impact assessment + Art. 35 transparency + Art. 36 GenAI watermark + Art. 46 critical infrastructure human oversight), KoreaCrossBorderFilter (PIPA Art. 28-8 CN/RU/KP + FSC EFTA Art. 21-2 financial safeguards + FSC Cloud AWS/GCP/Azure Seoul whitelist + PIPC biometric notification), 8 ecosystem wrappers |

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
| **South Korea** | Korea AI Framework Act 2024, PIPA 2020/2023 amendments, Credit Information Use and Protection Act, Korean Medical Devices Act (MFDS SaMD) | 24 |
| **Middle East (GCC)** | UAE PDPL Federal Decree-Law No. 45/2021 + UAE AI Ethics 2019, Saudi PDPL Royal Decree M/19 + NDMO + SAMA + SFDA, Qatar PDPA Law No. 13/2016 + Qatar AI Strategy 2030, GCC cross-border adequacy | 25 |
| **Africa** | Kenya DPA 2019 (§25/§30/§31), Nigeria NDPA 2023 (§25/§34) + NITDA AI Policy §3.2, South Africa POPIA 2013 (§26/§71) + FSCA AI Guidance 2023, AU Data Policy Framework 2022 cross-border adequacy | 26 |
| **Nordic / Scandinavia** | Sweden IMY AI Guidelines 2023 + SFS 2018:218, Denmark Datatilsynet AI Guidance 2023 + Act No. 502/2018, Finland TSV AI Guidelines 2023 + Data Protection Act 1050/2018, EEA intra-transfer adequacy | 28 |
| **Eastern Europe (Poland, Czech Republic, Hungary)** | Poland UODO AI Guidelines 2023 + GDPR Act Dz.U. 2018 poz. 1000, Czech ÚOOÚ AI Guidance 2023 + Act 110/2019 Coll., Hungary NAIH AI Guidelines 2023 + Privacy Act CXII/2011, 30-jurisdiction EEA adequate set + SCC/BCR fallback | 29 |
| **US State AI Laws (Colorado, Illinois, Virginia)** | Colorado AI Act 2024 SB 24-205 (impact assessment, human oversight, bias testing), Illinois BIPA 740 ILCS 14 (biometric consent, video interview AI), Virginia CDPA AI provisions §59.1-577/578/579 (sensitive data, automated profiling, high-risk AI), multi-state cross-border applicability matrix | 30 |
| **EU AI Act — High-Risk Systems** | EU AI Act 2024/1689 Art. 5 prohibited practices, Annex III §1-8 high-risk categories, Arts. 9-15 technical requirements, Arts. 50/13 transparency, Arts. 51-55 GPAI/systemic risk; 8 ecosystem wrappers (LangChain/CrewAI/AutoGen/SK/LlamaIndex/Haystack/DSPy/MAF) | 31 |

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
examples/                     # 29 runnable governance examples (see catalog above)
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

- `29_latam_ai_governance.py` — Argentina AAIP + Chile SII + Colombia SIC AI enforcement
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
  version = {0.34.0},
  url     = {https://github.com/ashutoshrana/regulated-ai-governance},
  license = {MIT}
}
```

---

## Part of the enterprise AI patterns trilogy

| Library | Focus | Coverage |
|---------|-------|---------|
| [enterprise-rag-patterns](https://github.com/ashutoshrana/enterprise-rag-patterns) | What to retrieve | 44 sectors · 58 regulations · 1548 tests |
| **regulated-ai-governance** | What agents may do | 35 governance examples · 21 jurisdictions · 2023 tests |
| [integration-automation-patterns](https://github.com/ashutoshrana/integration-automation-patterns) | How data flows | 37 patterns · schema registry · GraphQL · 1503 tests |

---

## License

MIT — see [LICENSE](LICENSE).
