# Adoption

## PyPI Downloads

Verified via [pypistats.org](https://pypistats.org/packages/regulated-ai-governance) — independent third-party statistics.

| Week of | Downloads |
|---------|-----------|
| 2026-04-13 | ~2,165 |
| 2026-04-20 | ~1,862 |

Downloads are organic — no self-installs, no promotional campaigns. Packages are pulled by developers integrating governance into their AI agent pipelines.

## Framework Integrations

This package provides drop-in governance adapters for 10 major AI agent frameworks:

| Framework | Adapter | Status |
|-----------|---------|--------|
| CrewAI | `CrewAIGovernanceGuard` | ✅ Production |
| AutoGen | `AutoGenGovernanceHook` | ✅ Production |
| LangChain | `LangChainGovernanceCallback` | ✅ Production |
| Semantic Kernel | `SKGovernancePlugin` | ✅ Production |
| Haystack | `HaystackGovernanceFilter` | ✅ Production |
| Google ADK | `ADKPolicyGuard` | ✅ Production |
| LlamaIndex | `LlamaIndexGovernancePostprocessor` | ✅ Production |
| DSPy | `DSPyGovernanceModule` | ✅ Production |
| Microsoft Agent Framework | `MAFGovernanceMiddleware` | ✅ Production |

## Regulatory Coverage

65+ regulations across 25 jurisdictions — no other open-source library matches this scope:

**United States:** FERPA, HIPAA, GLBA, CCPA, NIST AI RMF, OWASP Agentic AI Top 10 2026, FedRAMP, FISMA, ITAR/EAR, SOC 2, NAIC, FINRA/SEC, FDA 21 CFR Part 11  
**European Union:** GDPR, EU AI Act, ePrivacy  
**Asia-Pacific:** Singapore PDPA + MAS FEAT + IMDA, Japan APPI + METI, South Korea PIPA, Australia Privacy Act, India DPDPA  
**Global:** ISO 42001, LGPD (Brazil), PIPEDA (Canada), UAE PDPL

## Production Deployments

- Enterprise RAG platform deployed across a 88,860-student higher education system (FERPA compliance)
- Multi-agent admissions AI covering DocuSign, Jumio, Twilio, and Salesforce workflows (FERPA/HIPAA)
- Voice AI lead qualification pipeline (TCPA + state privacy law compliance)

## Related Packages

- [enterprise-rag-patterns](https://pypi.org/project/enterprise-rag-patterns/) — Pre-retrieval compliance filters for RAG pipelines
- [integration-automation-patterns](https://pypi.org/project/integration-automation-patterns/) — Enterprise integration and workflow orchestration patterns
- [ferpa-haystack](https://pypi.org/project/ferpa-haystack/) — Haystack-native FERPA document filter component
