"""
regulations — Cross-industry AI governance policy helpers.

Each sub-module provides pre-built policy factories and governance primitives
for a specific regulation or compliance framework.

Available modules
-----------------
Regulatory / statutory:
- ``ferpa``      — FERPA 34 CFR § 99 (educational records)
- ``gdpr``       — GDPR Articles 5, 6, 17 (EU data subject rights)
- ``hipaa``      — HIPAA 45 CFR §§ 164.312, 164.502 (ePHI access)
- ``glba``       — GLBA 16 CFR § 314 (financial customer safeguards)
- ``ccpa``       — CCPA / CPRA (California consumer privacy)

AI / technology governance:
- ``iso42001``   — ISO/IEC 42001:2023 AI Management System: operating scope
  enforcement (A.6.2.10), deployment approval gates (A.6.2.5), data
  provenance tracking (A.7.2/A.7.5/A.7.6), human oversight routing (A.9.5).
- ``eu_ai_act``  — EU AI Act 2024/1689: risk categories (Art. 6-9), prohibited
  practices (Art. 5), high-risk deployment gates (Art. 43), FRIA (Art. 27),
  human oversight (Art. 14), logging (Art. 12).
- ``dora``       — DORA EU 2022/2554: ICT risk management (Art. 9), third-party
  provider risk (Art. 28), incident reporting (Art. 17-18).
- ``nist_ai_rmf`` — NIST AI RMF 1.0 + AI 600-1 GenAI Profile: GOVERN/MAP/
  MEASURE/MANAGE functions, confabulation, data bias, human-AI configuration.
- ``owasp_llm``  — OWASP LLM Top 10 (2025): prompt injection (LLM01), sensitive
  info disclosure (LLM02), excessive agency (LLM06), system prompt leakage (LLM07).
"""

from .dora import (
    DORA_HIGH_RISK_ICT_ACTIONS,
    DORAICTCapabilityArea,
    DORAICTIncidentRecord,
    DORAICTRiskLevel,
    DORAThirdPartyRecord,
    make_dora_ict_management_policy,
    make_dora_third_party_policy,
)
from .eu_ai_act import (
    EU_AI_ACT_HIGH_RISK_DOMAINS,
    EU_AI_ACT_PROHIBITED_PRACTICES,
    EUAIActAuditRecord,
    EUAIActGovernancePolicy,
    EUAIActPolicyDecision,
    EUAIActRiskCategory,
    EUAIActSystemProfile,
    make_eu_ai_act_high_risk_policy,
    make_eu_ai_act_minimal_risk_policy,
)
from .iso42001 import (
    ISO42001AuditRecord,
    ISO42001DataProvenanceRecord,
    ISO42001DeploymentRecord,
    ISO42001GovernancePolicy,
    ISO42001OperatingScope,
    ISO42001PolicyDecision,
)
from .nist_ai_rmf import (
    NIST_GENAI_HIGH_RISK_ACTIONS,
    NISTAIRMFFunction,
    NISTAIRMFRiskAssessment,
    NISTAIRMFRiskCategory,
    make_nist_ai_rmf_policy,
)
from .owasp_llm import (
    OWASP_LLM_2025_ALL_RISKS,
    OWASP_LLM_DENIED_ACTIONS,
    OWASPLLMRisk,
    make_owasp_llm_policy,
)

__all__ = [
    # ISO/IEC 42001:2023 AI Management System
    "ISO42001OperatingScope",
    "ISO42001DataProvenanceRecord",
    "ISO42001DeploymentRecord",
    "ISO42001AuditRecord",
    "ISO42001GovernancePolicy",
    "ISO42001PolicyDecision",
    # EU AI Act 2024/1689
    "EUAIActRiskCategory",
    "EUAIActSystemProfile",
    "EUAIActGovernancePolicy",
    "EUAIActPolicyDecision",
    "EUAIActAuditRecord",
    "EU_AI_ACT_PROHIBITED_PRACTICES",
    "EU_AI_ACT_HIGH_RISK_DOMAINS",
    "make_eu_ai_act_minimal_risk_policy",
    "make_eu_ai_act_high_risk_policy",
    # DORA EU 2022/2554
    "DORAICTRiskLevel",
    "DORAICTCapabilityArea",
    "DORAThirdPartyRecord",
    "DORAICTIncidentRecord",
    "make_dora_ict_management_policy",
    "make_dora_third_party_policy",
    "DORA_HIGH_RISK_ICT_ACTIONS",
    # NIST AI RMF 1.0 + AI 600-1
    "NISTAIRMFFunction",
    "NISTAIRMFRiskCategory",
    "NISTAIRMFRiskAssessment",
    "make_nist_ai_rmf_policy",
    "NIST_GENAI_HIGH_RISK_ACTIONS",
    # OWASP LLM Top 10 (2025)
    "OWASPLLMRisk",
    "OWASP_LLM_DENIED_ACTIONS",
    "OWASP_LLM_2025_ALL_RISKS",
    "make_owasp_llm_policy",
]
