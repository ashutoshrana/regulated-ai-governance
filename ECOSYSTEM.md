# Ecosystem Coverage

`regulated-ai-governance` is the **AI policy enforcement** layer of the
[Open Regulated AI Trilogy](https://github.com/ashutoshrana):

| Repo | Domain |
|------|--------|
| [enterprise-rag-patterns](https://github.com/ashutoshrana/enterprise-rag-patterns) | RAG retrieval and access-control patterns |
| [integration-automation-patterns](https://github.com/ashutoshrana/integration-automation-patterns) | Enterprise integration, messaging, and workflow |
| **regulated-ai-governance** ← you are here | Cross-regulation AI policy enforcement |

---

## Regulations Covered

| Regulation | Jurisdiction | Policy Factory | Request Handling | Status |
|------------|-------------|---------------|-----------------|--------|
| FERPA (20 U.S.C. § 1232g) | US Education | `make_ferpa_student_policy()` | Disclosure log (34 CFR § 99.32) | ✅ Implemented |
| HIPAA (45 CFR Parts 160/164) | US Healthcare | `make_hipaa_treating_provider_policy()` | PHI access log (§ 164.312(b)) | ✅ Implemented |
| GLBA (15 U.S.C. §§ 6801–6809) | US Financial | `make_glba_customer_service_policy()` | NPI access log (16 CFR § 314) | ✅ Implemented |
| GDPR (EU 2016/679) | EU/EEA | `make_gdpr_processing_policy()` | Art. 15/17 subject requests | ✅ Implemented |
| CCPA/CPRA (Cal. Civil Code § 1798) | California | `make_ccpa_processing_policy()` | Know/delete/opt-out requests | ✅ Implemented |
| SOC 2 TSC | AICPA standard | `make_soc2_agent_policy()` | Control test evidence | ✅ Implemented |
| PDPA (Thailand) | Thailand | — | — | 🔲 Planned |
| PIPEDA (Canada) | Canada | — | — | 🔲 Planned |
| AI Act (EU 2024/1689) | EU | `EUAIActGovernancePolicy` | Selected metadata checks; not conformity assessment | Implemented subset; applicability requires review |

---

## AI Framework Integrations

| Framework | Adapter | Current support boundary |
|-----------|---------|--------------------------|
| CrewAI | `EnterpriseActionGuard` | Security quarantined; native support suspended |
| AutoGen / AG2 | `GovernedAutoGenAgent` | Legacy object wrapper retained; native extra quarantined |
| LangChain | `GovernanceCallbackHandler`, `FERPAComplianceCallbackHandler` | Core >=1.3.3; see qualification matrix |
| LlamaIndex | `GovernedQueryEngine` | Core >=0.13.0; see qualification matrix |
| Semantic Kernel | `GovernedKernelPlugin` | >=1.41.0 plus security dependency floors |
| Haystack | `GovernedHaystackComponent` | >=2.20.0; see qualification matrix |
| Microsoft Agent Framework | `PolicyMiddleware` | `as_native()` bridge; core >=1.23.0,<2 |
| DSPy | `GovernedDSPyModule`, `GovernedDSPyPipeline` | Source/stub-tested only; no qualified SDK extra |

Version floors are package constraints, not proof that all later versions work.
Consult [package metadata](pyproject.toml), [migration guidance](MIGRATION.md),
[security policy](SECURITY.md), and [CI](.github/workflows/ci.yml) for Python and
native SDK boundaries. Implementation and tests are not production adoption.

---

DSPy has no supported install extra in the current package metadata. See [ADOPTION.md](ADOPTION.md#framework-integrations) for the distinction between source implementation, native SDK qualification, and production adoption. Other integration support may be restricted by the current [README](README.md#ai-framework-integrations) and [security policy](SECURITY.md).

## Cross-Cutting Compliance Primitives

| Primitive | Class | Purpose | Status |
|-----------|-------|---------|--------|
| PII Pre-flight | `PIIDetector` | Regex-based PII detection before LLM context | ✅ Implemented |
| Consent Management | `ConsentStore` | GDPR Art. 6/7, HIPAA, CCPA consent tracking | ✅ Implemented |
| Data Lineage | `LineageTracker` | GDPR Art. 30, HIPAA § 164.528, FERPA § 99.32 | ✅ Implemented |
| Audit Log | `GovernanceAuditRecord` | Cross-regulation audit emission | ✅ Implemented |
| Policy Evaluation | `GovernedActionGuard` | Framework-agnostic action guard | ✅ Implemented |
| DPIA Workflow | — | Art. 35 Data Protection Impact Assessment | 🔲 Planned |
| Model Cards | — | AI Act conformity documentation | 🔲 Planned |

---

## Vector Store Integration

For FERPA/GDPR-compliant vector store filtering, see
[enterprise-rag-patterns](https://github.com/ashutoshrana/enterprise-rag-patterns)
which implements adapters for:

| Store | Status |
|-------|--------|
| Pinecone | ✅ |
| Weaviate | ✅ |
| Qdrant | ✅ |
| ChromaDB | ✅ |

---

## Contributing

To add coverage for a new regulation or AI framework:

1. Open an issue using the appropriate issue template
2. Study an existing module (e.g. `regulations/gdpr.py`) for patterns
3. Implement the module following the existing style
4. Add tests following the test patterns in `tests/test_new_modules.py`
5. Update this file and `CHANGELOG.md`

See [CONTRIBUTING.md](./CONTRIBUTING.md) for the full contribution guide.
