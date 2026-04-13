"""
regulations — Cross-industry AI governance policy helpers.

Each sub-module provides pre-built policy factories and governance primitives
for a specific regulation or compliance framework.

Available modules
-----------------
Regulatory / statutory:
- ``ferpa``    — FERPA 34 CFR § 99 (educational records)
- ``gdpr``     — GDPR Articles 5, 6, 17 (EU data subject rights)
- ``hipaa``    — HIPAA 45 CFR §§ 164.312, 164.502 (ePHI access)
- ``glba``     — GLBA 16 CFR § 314 (financial customer safeguards)
- ``ccpa``     — CCPA / CPRA (California consumer privacy)

AI / technology governance:
- ``iso42001`` — ISO/IEC 42001:2023 AI Management System: operating scope
  enforcement (A.6.2.10), deployment approval gates (A.6.2.5), data
  provenance tracking (A.7.2/A.7.5/A.7.6), human oversight routing (A.9.5).
"""

from .iso42001 import (
    ISO42001AuditRecord,
    ISO42001DataProvenanceRecord,
    ISO42001DeploymentRecord,
    ISO42001GovernancePolicy,
    ISO42001OperatingScope,
    ISO42001PolicyDecision,
)

__all__ = [
    # ISO/IEC 42001:2023 AI Management System
    "ISO42001OperatingScope",
    "ISO42001DataProvenanceRecord",
    "ISO42001DeploymentRecord",
    "ISO42001AuditRecord",
    "ISO42001GovernancePolicy",
    "ISO42001PolicyDecision",
]
