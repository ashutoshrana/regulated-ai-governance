# Adoption

## PyPI Downloads

Historical download figures recorded from [pypistats.org](https://pypistats.org/packages/regulated-ai-governance) — independent third-party statistics.

| Week of | Downloads |
|---------|-----------|
| 2026-04-13 | ~2,165 |
| 2026-04-20 | ~1,862 |

These are download events, not verified unique users, independent adopters, or production installations. [PyPI Stats](https://pypistats.org/faqs) includes automated CI/CD downloads; these counts alone do not establish who installed the package or why. Independent adoption claims require attributable deployment or usage evidence.

## Framework Integrations

Framework wrappers are present in the source, but implementation is not evidence of production adoption or native SDK qualification. See the [README integration table](README.md#ai-framework-integrations), supported extras in `pyproject.toml`, and [security policy](SECURITY.md) for current support boundaries.

DSPy wrappers `GovernedDSPyModule` and `GovernedDSPyPipeline` are implemented in [`integrations/dspy.py`](src/regulated_ai_governance/integrations/dspy.py), with [stub-based tests](tests/test_dspy_integration.py). Native DSPy SDK compatibility is not qualified and no `dspy` installation extra is currently provided. This is neither a planned-only feature nor a verified production integration.

## Regulatory Coverage

The repository includes policy modules and examples addressing the laws, standards, and frameworks below. Coverage and applicability vary by module; this list is not a certification of legal compliance or a verified comparison with all other libraries:

**United States:** FERPA, HIPAA, GLBA, CCPA, NIST AI RMF, OWASP Agentic AI Top 10 2026, FedRAMP, FISMA, ITAR/EAR, SOC 2, NAIC, FINRA/SEC, FDA 21 CFR Part 11  
**European Union:** GDPR, EU AI Act, ePrivacy  
**Asia-Pacific:** Singapore PDPA + MAS FEAT + IMDA, Japan APPI + METI, South Korea PIPA, Australia Privacy Act, India DPDPA  
**Global:** ISO 42001, LGPD (Brazil), PIPEDA (Canada), UAE PDPL

## Reported Deployment Contexts

The following project contexts are maintainer-reported. This page does not yet link independent deployment records, version-specific usage evidence, or measured outcomes. Institutional population is not a measure of actual users served.

- Enterprise RAG platform in a higher education system (FERPA-related controls)
- Multi-agent admissions AI covering DocuSign, Jumio, Twilio, and Salesforce workflows (FERPA/HIPAA-related controls)
- Voice AI lead qualification pipeline (TCPA and state privacy-related controls)

## Related Packages

- [enterprise-rag-patterns](https://pypi.org/project/enterprise-rag-patterns/) — Pre-retrieval compliance filters for RAG pipelines
- [integration-automation-patterns](https://pypi.org/project/integration-automation-patterns/) — Enterprise integration and workflow orchestration patterns
- [ferpa-haystack](https://pypi.org/project/ferpa-haystack/) — Haystack-native FERPA document filter component
