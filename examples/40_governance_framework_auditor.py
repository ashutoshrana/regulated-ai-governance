"""
40_governance_framework_auditor.py — Holistic AI Governance Framework Auditor

Implements a unified AI governance audit engine that evaluates a deployed AI
system against five authoritative regulatory and security frameworks
simultaneously:

    Framework 1  — OWASP LLM Top 10 2025 (GOV-OLLM):

               GOV-OLLM-001 Prompt Injection (LLM01) CRITICAL
               GOV-OLLM-002 Insecure Output Handling (LLM02) HIGH
               GOV-OLLM-003 Supply Chain Security (LLM03) HIGH
               GOV-OLLM-004 Data Poisoning (LLM04) CRITICAL
               GOV-OLLM-005 Sensitive Info Controls (LLM06) CRITICAL
               GOV-OLLM-006 Vector/Embedding Security (LLM08) HIGH
               GOV-OLLM-007 Misinformation Controls (LLM09) HIGH
               GOV-OLLM-008 Consumption Limits (LLM10) MEDIUM

    Framework 2  — OWASP Agentic AI Top 10 2026 (GOV-OASI):

               GOV-OASI-001 Goal Hijack Prevention (ASI01) CRITICAL
               GOV-OASI-002 Tool Misuse Prevention (ASI02) CRITICAL
               GOV-OASI-003 Memory Poisoning Controls (ASI03) HIGH
               GOV-OASI-004 Trust Boundary Controls (ASI08-10) CRITICAL

    Framework 3  — NIST AI RMF + AI 600-1 (GOV-NIST):

               GOV-NIST-001 MAP Function (Risk Identification) HIGH
               GOV-NIST-002 MEASURE Function (Risk Quantification) HIGH
               GOV-NIST-003 MANAGE Function (Risk Treatment) HIGH
               GOV-NIST-004 GOVERN Function (Oversight) CRITICAL
               GOV-NIST-005 GenAI-Specific Testing (AI 600-1) HIGH

    Framework 4  — ISO/IEC 42001:2023 (GOV-ISO):

               GOV-ISO-001 AI Policy (Cl.5.2) CRITICAL
               GOV-ISO-002 Risk Assessment (Cl.6.1) CRITICAL
               GOV-ISO-003 AI Objectives (Cl.6.2) HIGH
               GOV-ISO-004 Competence Management (Cl.7.2) MEDIUM
               GOV-ISO-005 Documented Information (Cl.7.5) HIGH
               GOV-ISO-006 Operational Controls (Cl.8.4) HIGH
               GOV-ISO-007 Monitoring & Evaluation (Cl.9.1) HIGH
               GOV-ISO-008 Internal Audit (Cl.9.2) MEDIUM
               GOV-ISO-009 Management Review (Cl.9.3) MEDIUM

    Framework 5  — MITRE ATLAS v5.1 (GOV-ATLAS):

               GOV-ATLAS-001 Reconnaissance Detection (TA0001) HIGH
               GOV-ATLAS-002 Training Data Poisoning Detection (T0020) CRITICAL
               GOV-ATLAS-003 Model Exfiltration Controls (T0024) HIGH
               GOV-ATLAS-004 Prompt Injection Detection (T0051) CRITICAL
               GOV-ATLAS-005 Agent Tool Invocation Controls (T0060) HIGH
               GOV-ATLAS-006 RAG Database Prompting Controls (T0057) HIGH

    Framework 6  — CSA Agentic Trust Framework (GOV-CSA):

               GOV-CSA-001 Sandbox Controls (Level 1) HIGH
               GOV-CSA-002 Controlled Deployment (Level 2) HIGH
               GOV-CSA-003 Trusted Operations (Level 3) HIGH
               GOV-CSA-004 Autonomous Operations (Level 4) MEDIUM
               GOV-CSA-005 Continuous Trust Assessment HIGH

Scoring model
-------------
Each CRITICAL control that fails deducts 15 points from a 100-point baseline.
Each HIGH control that fails deducts 7 points.
Each MEDIUM control that fails deducts 3 points.
Scores below zero are floored at 0.

Maturity thresholds
-------------------
  90–100  OPTIMIZING    — all critical controls pass; continuous improvement
  75–89   MANAGED       — critical and most high controls implemented
  50–74   DEFINED       — defined policies; significant gaps remain
  25–49   DEVELOPING    — foundational controls only
   0–24   INITIAL       — minimal governance; immediate action required

Commercial use cases
--------------------
+----------------------------------------------+-----------------------------+
| Use case                                     | Primary frameworks applied  |
+----------------------------------------------+-----------------------------+
| Enterprise GenAI platform (ISO certification)| ISO 42001, NIST AI RMF     |
| Autonomous agent deployment (security audit) | OWASP ASI, MITRE ATLAS     |
| RAG-augmented enterprise chatbot             | OWASP LLM, ATLAS T0057     |
| Regulated financial AI system                | NIST AI RMF, ISO 42001     |
| Multi-agent cloud AI pipeline                | CSA ATF, OWASP ASI         |
| Public-sector AI deployment                  | ISO 42001, NIST AI RMF     |
| Clinical AI decision-support system          | NIST AI 600-1, ISO 42001   |
| AI supply-chain security review              | OWASP LLM03, ATLAS T0024   |
+----------------------------------------------+-----------------------------+

37 controls across 6 framework domains are evaluated in total.

No external dependencies required.

Run:
    python examples/40_governance_framework_auditor.py
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# ---------------------------------------------------------------------------
# GovernanceFrameworkConfig
# ---------------------------------------------------------------------------


@dataclass
class GovernanceFrameworkConfig:
    """
    Configuration object representing the AI governance controls that are
    active for a given deployed AI system.

    Each boolean field maps to a specific control required by one or more of
    the five audited frameworks: OWASP LLM Top 10 2025, OWASP Agentic AI
    Top 10 2026, NIST AI RMF (AI 600-1), ISO/IEC 42001:2023, MITRE ATLAS
    v5.1, and CSA Agentic Trust Framework.

    A field value of ``True`` means the corresponding control is implemented
    and operational.  A value of ``False`` means the control is absent or not
    verified — the auditor will raise a finding.

    Attributes
    ----------
    system_id : str
        Human-readable identifier for the AI system under audit.

    OWASP LLM Top 10 2025 controls (GOV-OLLM)
    ------------------------------------------
    owasp_llm_prompt_injection_controls : bool
        LLM01 — prompt injection detection and prevention active for all
        user-supplied and retrieved inputs processed by the LLM.
    owasp_llm_insecure_output_handling : bool
        LLM02 — output validation and encoding enforced before LLM responses
        are rendered or acted upon by downstream consumers.
    owasp_llm_supply_chain_controls : bool
        LLM03 — model provenance, dependency verification, and SBOM in place
        for all AI model and plugin supply-chain components.
    owasp_llm_data_poisoning_controls : bool
        LLM04 — training data integrity, provenance tracking, and anomaly
        detection controls implemented to detect poisoned data.
    owasp_llm_sensitive_info_controls : bool
        LLM06 — DLP scanning, output filtering, and RAG access controls
        preventing sensitive information (PII, credentials, PHI) disclosure.
    owasp_llm_vector_weakness_controls : bool
        LLM08 — vector store integrity checks, embedding validation, and
        adversarial embedding detection controls implemented.
    owasp_llm_misinformation_controls : bool
        LLM09 — factual grounding, hallucination detection, and output
        confidence disclosure implemented to mitigate misinformation risk.
    owasp_llm_unlimited_consumption_controls : bool
        LLM10 — rate limiting, quota enforcement, and resource caps
        preventing unbounded LLM API consumption.

    OWASP Agentic AI Top 10 2026 controls (GOV-OASI)
    -------------------------------------------------
    owasp_asi_goal_hijack_controls : bool
        ASI01 — indirect prompt injection detection for all external inputs
        routed into agent context (retrieved docs, tool outputs, web pages).
    owasp_asi_tool_misuse_controls : bool
        ASI02 — tool allowlist enforcement, capability-scoped permissions,
        and tool invocation approval gates for agentic workflows.
    owasp_asi_memory_poisoning_controls : bool
        ASI03 — session-scoped memory isolation and memory integrity checks
        preventing cross-session memory contamination.
    owasp_asi_trust_boundary_controls : bool
        ASI08-ASI10 — rollback for irreversible actions, per-step audit
        trails, and cryptographic sender verification for multi-agent
        message passing.

    NIST AI RMF (AI 600-1) controls (GOV-NIST)
    -------------------------------------------
    nist_map_function_implemented : bool
        MAP — AI risk context established; risk sources identified and
        categorised across technical, organisational, and societal dimensions.
    nist_measure_function_implemented : bool
        MEASURE — risk metrics defined, measurement methodologies documented,
        and ongoing evaluation mechanisms operational.
    nist_manage_function_implemented : bool
        MANAGE — risk treatment plans, mitigation actions, residual risk
        acceptance, and incident response procedures in place.
    nist_govern_function_implemented : bool
        GOVERN — AI governance structure, roles, accountability, policies,
        and oversight mechanisms formally established.
    nist_genai_testing_implemented : bool
        AI 600-1 §4.1 — GenAI-specific testing (red teaming, adversarial
        evaluation, factuality testing) implemented beyond standard ML testing.

    ISO/IEC 42001:2023 controls (GOV-ISO)
    --------------------------------------
    iso_ai_policy_defined : bool
        Cl.5.2 — formal AI policy documented, approved by top management,
        and communicated to relevant stakeholders.
    iso_ai_risk_assessment : bool
        Cl.6.1 — AI-specific risk assessment process defined and executed,
        including identification, analysis, and evaluation of AI risks.
    iso_ai_objectives_set : bool
        Cl.6.2 — measurable AI objectives aligned to policy, with plans for
        achievement and progress tracking.
    iso_ai_competence_managed : bool
        Cl.7.2 — competence requirements for AI roles defined; training,
        awareness, and skills verification programmes implemented.
    iso_ai_documented_info : bool
        Cl.7.5 — required documented information (policies, procedures,
        records, evidence) created, maintained, and controlled.
    iso_ai_operational_controls : bool
        Cl.8.4 — operational controls for AI system development, deployment,
        and decommissioning designed and implemented.
    iso_ai_monitoring : bool
        Cl.9.1 — performance and conformance monitoring, measurement, and
        evaluation processes operational for deployed AI systems.
    iso_ai_internal_audit : bool
        Cl.9.2 — internal audit programme for the AI management system
        established and executed at planned intervals.
    iso_ai_management_review : bool
        Cl.9.3 — top management review of the AI management system conducted
        at planned intervals to ensure continuing suitability and effectiveness.

    MITRE ATLAS v5.1 controls (GOV-ATLAS)
    --------------------------------------
    mitre_recon_detection : bool
        TA0001 — reconnaissance detection controls identifying adversarial
        attempts to gather intelligence about AI models, APIs, and training data.
    mitre_poisoning_detection : bool
        T0020 — training data poisoning detection and model integrity
        verification controls implemented.
    mitre_extraction_controls : bool
        T0024 — model exfiltration controls preventing extraction of model
        weights, architectures, or training data through API abuse.
    mitre_prompt_injection_detection : bool
        T0051 — prompt injection detection aligned to ATLAS AML.T0051.000
        (indirect) and AML.T0051.001 (direct).
    mitre_tool_invocation_controls : bool
        T0060 — agent tool invocation controls preventing adversarial
        manipulation of tool calls in agentic pipelines.
    mitre_rag_db_controls : bool
        T0057 — RAG database prompting controls preventing adversarial
        content injection into vector store retrieval pipelines.

    CSA Agentic Trust Framework controls (GOV-CSA)
    -----------------------------------------------
    csa_atf_sandbox_controls : bool
        Level 1 — sandbox isolation controls preventing agentic AI systems
        from accessing production systems during evaluation.
    csa_atf_controlled_controls : bool
        Level 2 — controlled deployment controls: injection detection,
        session-scoped memory, DLP on outputs, tool allowlists.
    csa_atf_trusted_controls : bool
        Level 3 — trusted operations controls: full audit trail, formal
        capability attestation, HITL gates for high-impact actions.
    csa_atf_autonomous_controls : bool
        Level 4 — autonomous operations controls: continuous monitoring,
        quarterly red teaming, automated anomaly response.
    csa_atf_continuous_assessment : bool
        CSA ATF §4.1 — continuous trust assessment process evaluating agent
        trustworthiness at runtime, not only at initial deployment.
    """

    system_id: str = "ai-governance-system"

    # OWASP LLM Top 10 2025 Controls
    owasp_llm_prompt_injection_controls: bool = False    # LLM01
    owasp_llm_insecure_output_handling: bool = False     # LLM02
    owasp_llm_supply_chain_controls: bool = False        # LLM03
    owasp_llm_data_poisoning_controls: bool = False      # LLM04
    owasp_llm_sensitive_info_controls: bool = False      # LLM06
    owasp_llm_vector_weakness_controls: bool = False     # LLM08
    owasp_llm_misinformation_controls: bool = False      # LLM09
    owasp_llm_unlimited_consumption_controls: bool = False  # LLM10

    # OWASP Agentic AI Top 10 2026 Controls
    owasp_asi_goal_hijack_controls: bool = False         # ASI01
    owasp_asi_tool_misuse_controls: bool = False         # ASI02
    owasp_asi_memory_poisoning_controls: bool = False    # ASI03
    owasp_asi_trust_boundary_controls: bool = False      # ASI08-ASI10

    # NIST AI RMF (AI 600-1) Controls
    nist_map_function_implemented: bool = False          # MAP: identify AI risks
    nist_measure_function_implemented: bool = False      # MEASURE: quantify risks
    nist_manage_function_implemented: bool = False       # MANAGE: treat risks
    nist_govern_function_implemented: bool = False       # GOVERN: oversight structure
    nist_genai_testing_implemented: bool = False         # AI 600-1 GenAI-specific testing

    # ISO/IEC 42001:2023 Controls
    iso_ai_policy_defined: bool = False                  # Cl.5.2 AI Policy
    iso_ai_risk_assessment: bool = False                 # Cl.6.1 Risk Assessment
    iso_ai_objectives_set: bool = False                  # Cl.6.2 AI Objectives
    iso_ai_competence_managed: bool = False              # Cl.7.2 Competence
    iso_ai_documented_info: bool = False                 # Cl.7.5 Documented Information
    iso_ai_operational_controls: bool = False            # Cl.8.4 Operational Controls
    iso_ai_monitoring: bool = False                      # Cl.9.1 Monitoring
    iso_ai_internal_audit: bool = False                  # Cl.9.2 Internal Audit
    iso_ai_management_review: bool = False               # Cl.9.3 Management Review

    # MITRE ATLAS v5.1 Controls
    mitre_recon_detection: bool = False                  # TA0001 Reconnaissance detection
    mitre_poisoning_detection: bool = False              # T0020 Training Data Poisoning
    mitre_extraction_controls: bool = False              # T0024 Exfiltration controls
    mitre_prompt_injection_detection: bool = False       # T0051 Prompt Injection detection
    mitre_tool_invocation_controls: bool = False         # T0060 Agent Tool Invocation controls
    mitre_rag_db_controls: bool = False                  # T0057 RAG Database Prompting controls

    # CSA Agentic Trust Framework (ATF) Controls
    csa_atf_sandbox_controls: bool = False               # Level 1: Sandbox isolation
    csa_atf_controlled_controls: bool = False            # Level 2: Controlled deployment
    csa_atf_trusted_controls: bool = False               # Level 3: Trusted operations
    csa_atf_autonomous_controls: bool = False            # Level 4: Autonomous operations
    csa_atf_continuous_assessment: bool = False          # Continuous trust assessment


# ---------------------------------------------------------------------------
# AuditFinding
# ---------------------------------------------------------------------------


@dataclass
class AuditFinding:
    """
    A single audit finding produced by ``GovernanceFrameworkAuditor``.

    Each finding maps one control check to a status, severity, cross-framework
    references, evidence description, and a concrete remediation step.

    Attributes
    ----------
    control_id : str
        Unique identifier for the control (e.g. ``"GOV-OLLM-001"``).
    control_name : str
        Short human-readable name of the control
        (e.g. ``"Prompt Injection Controls (LLM01)"``).
    domain : str
        Framework domain the control belongs to
        (e.g. ``"OWASP LLM Top 10 2025"``).
    status : str
        Audit outcome: one of ``"PASS"``, ``"FAIL"``, ``"WARN"``,
        or ``"SKIP"``.
    severity : str
        Risk severity when the control fails: ``"CRITICAL"``, ``"HIGH"``,
        or ``"MEDIUM"``.
    framework_refs : list[str]
        Authoritative cross-references to standards, clauses, or technique
        identifiers that mandate this control.
    evidence : str
        Description of the evidence (or its absence) that drove the finding.
    remediation_step : str
        Concrete, actionable step to remediate a FAIL or WARN finding.
    """

    control_id: str
    control_name: str
    domain: str
    status: str           # PASS | FAIL | WARN | SKIP
    severity: str         # CRITICAL | HIGH | MEDIUM
    framework_refs: list[str]
    evidence: str
    remediation_step: str

    @property
    def score_deduction(self) -> int:
        """
        Points deducted from the 100-point governance score when this
        finding is a FAIL.

        Returns ``0`` for PASS, WARN, or SKIP findings.  Returns 15 for
        CRITICAL, 7 for HIGH, and 3 for MEDIUM FAIL findings.
        """
        if self.status != "FAIL":
            return 0
        return {"CRITICAL": 15, "HIGH": 7, "MEDIUM": 3}.get(self.severity, 0)


# ---------------------------------------------------------------------------
# GovernanceAuditReport
# ---------------------------------------------------------------------------


@dataclass
class GovernanceAuditReport:
    """
    Aggregated output of a ``GovernanceFrameworkAuditor`` run.

    Contains all findings, computed score, maturity level, and per-domain
    breakdown statistics.

    Attributes
    ----------
    system_id : str
        Identifier of the AI system that was audited.
    findings : list[AuditFinding]
        All findings produced by the audit in check order.
    score : int
        Governance score (0–100).  Starts at 100 and deducts per FAIL severity.
    maturity_level : str
        Human-readable maturity band derived from ``score``:
        OPTIMIZING / MANAGED / DEFINED / DEVELOPING / INITIAL.
    total_controls : int
        Total number of controls evaluated.
    passed : int
        Number of controls that produced a PASS finding.
    failed : int
        Number of controls that produced a FAIL finding.
    warned : int
        Number of controls that produced a WARN finding.
    domain_summary : dict[str, dict[str, int]]
        Per-domain breakdown mapping domain name to a dict with keys
        ``pass``, ``fail``, ``warn``, and ``total``.
    """

    system_id: str
    findings: list[AuditFinding]
    score: int
    maturity_level: str
    total_controls: int
    passed: int
    failed: int
    warned: int
    domain_summary: dict[str, dict[str, int]]

    def critical_failures(self) -> list[AuditFinding]:
        """Return all FAIL findings with severity CRITICAL."""
        return [f for f in self.findings if f.status == "FAIL" and f.severity == "CRITICAL"]

    def high_failures(self) -> list[AuditFinding]:
        """Return all FAIL findings with severity HIGH."""
        return [f for f in self.findings if f.status == "FAIL" and f.severity == "HIGH"]

    def findings_by_domain(self, domain: str) -> list[AuditFinding]:
        """Return all findings whose ``domain`` matches the given string."""
        return [f for f in self.findings if f.domain == domain]


# ---------------------------------------------------------------------------
# GovernanceFrameworkAuditor
# ---------------------------------------------------------------------------


class GovernanceFrameworkAuditor:
    """
    Holistic AI governance framework auditor covering OWASP LLM Top 10 2025,
    OWASP Agentic AI Top 10 2026, NIST AI RMF (AI 600-1), ISO/IEC 42001:2023,
    MITRE ATLAS v5.1, and the CSA Agentic Trust Framework.

    The auditor evaluates a ``GovernanceFrameworkConfig`` instance against 37
    controls across six domains, computes a weighted governance score, assigns
    a maturity level, and returns a ``GovernanceAuditReport`` with all
    findings, remediation steps, and per-domain statistics.

    Scoring
    -------
    Score starts at 100.  Each FAIL finding deducts:
      - CRITICAL: −15 points
      - HIGH:     −7 points
      - MEDIUM:   −3 points
    Score is floored at 0.

    Maturity levels
    ---------------
    90–100  OPTIMIZING  — comprehensive controls; continuous improvement
    75–89   MANAGED     — critical and most high controls implemented
    50–74   DEFINED     — defined policies; significant gaps remain
    25–49   DEVELOPING  — foundational controls only
     0–24   INITIAL     — minimal governance; immediate action required

    Usage
    -----
    ::

        config = GovernanceFrameworkConfig(
            system_id="my-rag-chatbot",
            owasp_llm_prompt_injection_controls=True,
            nist_govern_function_implemented=True,
            ...
        )
        auditor = GovernanceFrameworkAuditor()
        report = auditor.audit(config)
        print(report.score, report.maturity_level)
    """

    # Maturity thresholds (inclusive lower bounds, exclusive upper bounds)
    _MATURITY_BANDS: list[tuple[int, str]] = [
        (90, "OPTIMIZING"),
        (75, "MANAGED"),
        (50, "DEFINED"),
        (25, "DEVELOPING"),
        (0, "INITIAL"),
    ]

    def audit(self, config: GovernanceFrameworkConfig) -> GovernanceAuditReport:
        """
        Execute the full governance audit against the supplied configuration.

        Runs all six checker methods in sequence, collects ``AuditFinding``
        instances, computes the weighted score, derives the maturity level,
        and builds the domain summary.

        Parameters
        ----------
        config : GovernanceFrameworkConfig
            Governance control configuration for the AI system under audit.

        Returns
        -------
        GovernanceAuditReport
            Complete audit report with findings, score, and maturity level.
        """
        findings: list[AuditFinding] = []
        findings.extend(self._check_owasp_llm(config))
        findings.extend(self._check_owasp_agentic(config))
        findings.extend(self._check_nist_rmf(config))
        findings.extend(self._check_iso_42001(config))
        findings.extend(self._check_mitre_atlas(config))
        findings.extend(self._check_csa_atf(config))

        raw_score = 100 - sum(f.score_deduction for f in findings)
        score = max(0, raw_score)

        maturity_level = "INITIAL"
        for threshold, label in self._MATURITY_BANDS:
            if score >= threshold:
                maturity_level = label
                break

        passed = sum(1 for f in findings if f.status == "PASS")
        failed = sum(1 for f in findings if f.status == "FAIL")
        warned = sum(1 for f in findings if f.status == "WARN")

        domain_summary: dict[str, dict[str, int]] = {}
        for f in findings:
            if f.domain not in domain_summary:
                domain_summary[f.domain] = {"pass": 0, "fail": 0, "warn": 0, "total": 0}
            domain_summary[f.domain]["total"] += 1
            if f.status == "PASS":
                domain_summary[f.domain]["pass"] += 1
            elif f.status == "FAIL":
                domain_summary[f.domain]["fail"] += 1
            elif f.status == "WARN":
                domain_summary[f.domain]["warn"] += 1

        return GovernanceAuditReport(
            system_id=config.system_id,
            findings=findings,
            score=score,
            maturity_level=maturity_level,
            total_controls=len(findings),
            passed=passed,
            failed=failed,
            warned=warned,
            domain_summary=domain_summary,
        )

    # ------------------------------------------------------------------
    # Checker — OWASP LLM Top 10 2025
    # ------------------------------------------------------------------

    def _check_owasp_llm(self, config: GovernanceFrameworkConfig) -> list[AuditFinding]:
        """
        Evaluate the eight OWASP LLM Top 10 2025 controls.

        Covers LLM01 Prompt Injection, LLM02 Insecure Output Handling,
        LLM03 Supply Chain Security, LLM04 Data Poisoning, LLM06 Sensitive
        Information Disclosure, LLM08 Vector/Embedding Weaknesses, LLM09
        Misinformation, and LLM10 Unlimited Consumption.

        References
        ----------
        OWASP Top 10 for Large Language Model Applications 2025
            https://owasp.org/www-project-top-10-for-large-language-model-applications/
        MITRE ATLAS v5.1 (November 2025) — cross-referenced where noted.
        ISO/IEC 42001:2023 Cl.8.4 — cross-referenced where noted.
        GDPR Art. 32 — cross-referenced where noted.

        Parameters
        ----------
        config : GovernanceFrameworkConfig
            Configuration under audit.

        Returns
        -------
        list[AuditFinding]
            Eight findings, one per OWASP LLM control.
        """
        domain = "OWASP LLM Top 10 2025"
        findings: list[AuditFinding] = []

        # GOV-OLLM-001 — LLM01 Prompt Injection
        if config.owasp_llm_prompt_injection_controls:
            findings.append(AuditFinding(
                control_id="GOV-OLLM-001",
                control_name="Prompt Injection Controls (LLM01)",
                domain=domain,
                status="PASS",
                severity="CRITICAL",
                framework_refs=["OWASP LLM01", "MITRE ATLAS T0051"],
                evidence=(
                    "Prompt injection detection and prevention controls are active; "
                    "all user-supplied and retrieved inputs routed through injection "
                    "detection layer before LLM processing."
                ),
                remediation_step="No action required — control is implemented.",
            ))
        else:
            findings.append(AuditFinding(
                control_id="GOV-OLLM-001",
                control_name="Prompt Injection Controls (LLM01)",
                domain=domain,
                status="FAIL",
                severity="CRITICAL",
                framework_refs=["OWASP LLM01", "MITRE ATLAS T0051"],
                evidence=(
                    "owasp_llm_prompt_injection_controls is False — no prompt injection "
                    "detection or prevention layer is active; adversarial instructions "
                    "embedded in user input or retrieved context can override system "
                    "instructions and redirect LLM behaviour without detection."
                ),
                remediation_step=(
                    "Implement a prompt injection detection layer that inspects all "
                    "user-supplied inputs and retrieved context before LLM processing; "
                    "apply pattern matching, semantic outlier detection, and input "
                    "sandboxing; align to OWASP LLM01 mitigation guidance and MITRE "
                    "ATLAS T0051 countermeasures."
                ),
            ))

        # GOV-OLLM-002 — LLM02 Insecure Output Handling
        if config.owasp_llm_insecure_output_handling:
            findings.append(AuditFinding(
                control_id="GOV-OLLM-002",
                control_name="Insecure Output Handling (LLM02)",
                domain=domain,
                status="PASS",
                severity="HIGH",
                framework_refs=["OWASP LLM02"],
                evidence=(
                    "Output validation and encoding enforced; LLM responses are "
                    "validated and context-appropriately encoded before being rendered "
                    "or acted upon by downstream consumers."
                ),
                remediation_step="No action required — control is implemented.",
            ))
        else:
            findings.append(AuditFinding(
                control_id="GOV-OLLM-002",
                control_name="Insecure Output Handling (LLM02)",
                domain=domain,
                status="FAIL",
                severity="HIGH",
                framework_refs=["OWASP LLM02"],
                evidence=(
                    "owasp_llm_insecure_output_handling is False — LLM outputs are not "
                    "validated or encoded before downstream use; this exposes consumers "
                    "to XSS, code injection, SSRF, and privilege escalation when LLM "
                    "responses are rendered in web contexts or passed to interpreters."
                ),
                remediation_step=(
                    "Treat LLM outputs as untrusted data; apply context-appropriate "
                    "output encoding (HTML, SQL, shell) before rendering; validate "
                    "response structure against expected schemas; implement output "
                    "content policies to prevent malicious instruction propagation "
                    "per OWASP LLM02 mitigation guidance."
                ),
            ))

        # GOV-OLLM-003 — LLM03 Supply Chain Security
        if config.owasp_llm_supply_chain_controls:
            findings.append(AuditFinding(
                control_id="GOV-OLLM-003",
                control_name="Supply Chain Security (LLM03)",
                domain=domain,
                status="PASS",
                severity="HIGH",
                framework_refs=["OWASP LLM03", "ISO 42001 Cl.8.4"],
                evidence=(
                    "Model provenance, dependency verification, and SBOM controls are "
                    "in place; all AI model and plugin supply-chain components are "
                    "verified before deployment."
                ),
                remediation_step="No action required — control is implemented.",
            ))
        else:
            findings.append(AuditFinding(
                control_id="GOV-OLLM-003",
                control_name="Supply Chain Security (LLM03)",
                domain=domain,
                status="FAIL",
                severity="HIGH",
                framework_refs=["OWASP LLM03", "ISO 42001 Cl.8.4"],
                evidence=(
                    "owasp_llm_supply_chain_controls is False — no model provenance "
                    "verification, dependency scanning, or SBOM in place; compromised "
                    "model weights, poisoned fine-tuning datasets, or malicious "
                    "third-party plugins can be introduced into the deployment pipeline "
                    "without detection."
                ),
                remediation_step=(
                    "Establish an AI SBOM (Software Bill of Materials) covering all "
                    "model components, training datasets, and plugins; implement "
                    "cryptographic provenance verification for model weights; conduct "
                    "dependency scanning for all third-party AI libraries; align to "
                    "OWASP LLM03 and ISO 42001 Cl.8.4 operational controls."
                ),
            ))

        # GOV-OLLM-004 — LLM04 Data Poisoning
        if config.owasp_llm_data_poisoning_controls:
            findings.append(AuditFinding(
                control_id="GOV-OLLM-004",
                control_name="Data Poisoning Controls (LLM04)",
                domain=domain,
                status="PASS",
                severity="CRITICAL",
                framework_refs=["OWASP LLM04", "MITRE ATLAS T0020"],
                evidence=(
                    "Training data integrity, provenance tracking, and anomaly "
                    "detection controls are implemented to detect and prevent "
                    "data poisoning attacks."
                ),
                remediation_step="No action required — control is implemented.",
            ))
        else:
            findings.append(AuditFinding(
                control_id="GOV-OLLM-004",
                control_name="Data Poisoning Controls (LLM04)",
                domain=domain,
                status="FAIL",
                severity="CRITICAL",
                framework_refs=["OWASP LLM04", "MITRE ATLAS T0020"],
                evidence=(
                    "owasp_llm_data_poisoning_controls is False — no training data "
                    "integrity or provenance controls in place; an adversary who can "
                    "write to training datasets or fine-tuning corpora can embed "
                    "backdoors or steering behaviours that persist across model "
                    "updates and are extremely difficult to remove post-training."
                ),
                remediation_step=(
                    "Implement cryptographic integrity verification for all training "
                    "datasets; establish provenance tracking from data collection to "
                    "model training; deploy statistical anomaly detection on training "
                    "corpus; conduct regular model behavioural testing for poisoning "
                    "signatures per OWASP LLM04 and MITRE ATLAS T0020."
                ),
            ))

        # GOV-OLLM-005 — LLM06 Sensitive Information
        if config.owasp_llm_sensitive_info_controls:
            findings.append(AuditFinding(
                control_id="GOV-OLLM-005",
                control_name="Sensitive Info Controls (LLM06)",
                domain=domain,
                status="PASS",
                severity="CRITICAL",
                framework_refs=["OWASP LLM06", "GDPR Art.32"],
                evidence=(
                    "DLP scanning, output filtering, and RAG access controls are active; "
                    "sensitive information (PII, credentials, PHI) is prevented from "
                    "appearing in LLM outputs."
                ),
                remediation_step="No action required — control is implemented.",
            ))
        else:
            findings.append(AuditFinding(
                control_id="GOV-OLLM-005",
                control_name="Sensitive Info Controls (LLM06)",
                domain=domain,
                status="FAIL",
                severity="CRITICAL",
                framework_refs=["OWASP LLM06", "GDPR Art.32"],
                evidence=(
                    "owasp_llm_sensitive_info_controls is False — no DLP scanning or "
                    "output filtering in place; PII, authentication credentials, PHI, "
                    "and proprietary data in the model's training set or retrieval "
                    "corpus can surface in LLM responses, triggering GDPR Art.32 "
                    "breach obligations and regulatory penalties."
                ),
                remediation_step=(
                    "Implement DLP (Data Loss Prevention) scanning on all LLM outputs "
                    "before delivery; apply RAG access control to ensure retrieval is "
                    "scoped to the authenticated user's permissions; conduct training "
                    "data audits to identify sensitive information memorised during "
                    "pre-training; align to OWASP LLM06 and GDPR Art.32."
                ),
            ))

        # GOV-OLLM-006 — LLM08 Vector/Embedding Security
        if config.owasp_llm_vector_weakness_controls:
            findings.append(AuditFinding(
                control_id="GOV-OLLM-006",
                control_name="Vector/Embedding Security (LLM08)",
                domain=domain,
                status="PASS",
                severity="HIGH",
                framework_refs=["OWASP LLM08"],
                evidence=(
                    "Vector store integrity checks, embedding validation, and adversarial "
                    "embedding detection controls are implemented."
                ),
                remediation_step="No action required — control is implemented.",
            ))
        else:
            findings.append(AuditFinding(
                control_id="GOV-OLLM-006",
                control_name="Vector/Embedding Security (LLM08)",
                domain=domain,
                status="FAIL",
                severity="HIGH",
                framework_refs=["OWASP LLM08"],
                evidence=(
                    "owasp_llm_vector_weakness_controls is False — no vector store "
                    "integrity or adversarial embedding controls in place; an attacker "
                    "who can write to the vector database can inject adversarial "
                    "embeddings that cause the retrieval system to surface malicious "
                    "content into LLM context without triggering conventional content "
                    "filters."
                ),
                remediation_step=(
                    "Implement access control and write-access auditing for all vector "
                    "databases; deploy embedding anomaly detection (cosine similarity "
                    "deviation from corpus centroid); validate embeddings at ingestion "
                    "against known-good document signatures; align to OWASP LLM08 "
                    "vector/embedding weakness mitigation guidance."
                ),
            ))

        # GOV-OLLM-007 — LLM09 Misinformation
        if config.owasp_llm_misinformation_controls:
            findings.append(AuditFinding(
                control_id="GOV-OLLM-007",
                control_name="Misinformation Controls (LLM09)",
                domain=domain,
                status="PASS",
                severity="HIGH",
                framework_refs=["OWASP LLM09", "ISO 42001 Cl.9.1"],
                evidence=(
                    "Factual grounding, hallucination detection, and output confidence "
                    "disclosure are implemented to mitigate misinformation risk."
                ),
                remediation_step="No action required — control is implemented.",
            ))
        else:
            findings.append(AuditFinding(
                control_id="GOV-OLLM-007",
                control_name="Misinformation Controls (LLM09)",
                domain=domain,
                status="FAIL",
                severity="HIGH",
                framework_refs=["OWASP LLM09", "ISO 42001 Cl.9.1"],
                evidence=(
                    "owasp_llm_misinformation_controls is False — no hallucination "
                    "detection or confidence disclosure implemented; LLM outputs that "
                    "contain factual errors or hallucinated content are delivered to "
                    "users as authoritative, creating reputational, regulatory, and "
                    "safety risks, particularly in medical, legal, and financial "
                    "deployment contexts."
                ),
                remediation_step=(
                    "Implement RAG grounding to anchor LLM responses in verifiable "
                    "source documents; deploy hallucination detection metrics (faithfulness "
                    "scoring, citation verification); include confidence indicators in "
                    "LLM response metadata; establish human review escalation for "
                    "low-confidence outputs per OWASP LLM09 and ISO 42001 Cl.9.1."
                ),
            ))

        # GOV-OLLM-008 — LLM10 Unlimited Consumption
        if config.owasp_llm_unlimited_consumption_controls:
            findings.append(AuditFinding(
                control_id="GOV-OLLM-008",
                control_name="Consumption Limits (LLM10)",
                domain=domain,
                status="PASS",
                severity="MEDIUM",
                framework_refs=["OWASP LLM10"],
                evidence=(
                    "Rate limiting, quota enforcement, and resource caps are active; "
                    "unbounded LLM API consumption is prevented."
                ),
                remediation_step="No action required — control is implemented.",
            ))
        else:
            findings.append(AuditFinding(
                control_id="GOV-OLLM-008",
                control_name="Consumption Limits (LLM10)",
                domain=domain,
                status="FAIL",
                severity="MEDIUM",
                framework_refs=["OWASP LLM10"],
                evidence=(
                    "owasp_llm_unlimited_consumption_controls is False — no rate "
                    "limiting, quota enforcement, or resource caps implemented; an "
                    "adversary can abuse the LLM API to cause denial of service, "
                    "exhaust inference budgets, or trigger runaway cost accumulation "
                    "through automated high-volume requests."
                ),
                remediation_step=(
                    "Implement per-user and per-session rate limits on LLM API calls; "
                    "enforce per-request token limits (input and output); set monthly "
                    "quota caps with automated alerting; deploy circuit breakers that "
                    "suspend service under anomalous consumption patterns per OWASP LLM10."
                ),
            ))

        return findings

    # ------------------------------------------------------------------
    # Checker — OWASP Agentic AI Top 10 2026
    # ------------------------------------------------------------------

    def _check_owasp_agentic(self, config: GovernanceFrameworkConfig) -> list[AuditFinding]:
        """
        Evaluate the four OWASP Agentic AI Top 10 2026 control groups.

        Covers ASI01 Agent Goal Hijack, ASI02 Tool Misuse, ASI03 Memory
        Poisoning, and ASI08-ASI10 Trust Boundaries (cascading failures,
        monitoring, and unvalidated agent composition).

        References
        ----------
        OWASP Top 10 for Agentic Applications 2026 (December 2025)
        MITRE ATLAS v5.1 T0060 — cross-referenced for ASI02.

        Parameters
        ----------
        config : GovernanceFrameworkConfig
            Configuration under audit.

        Returns
        -------
        list[AuditFinding]
            Four findings, one per OWASP Agentic control group.
        """
        domain = "OWASP Agentic AI Top 10 2026"
        findings: list[AuditFinding] = []

        # GOV-OASI-001 — ASI01 Goal Hijack Prevention
        if config.owasp_asi_goal_hijack_controls:
            findings.append(AuditFinding(
                control_id="GOV-OASI-001",
                control_name="Goal Hijack Prevention (ASI01)",
                domain=domain,
                status="PASS",
                severity="CRITICAL",
                framework_refs=["OWASP ASI01"],
                evidence=(
                    "Indirect prompt injection detection is active for all external "
                    "inputs routed into agent context; goal hijack prevention controls "
                    "are implemented."
                ),
                remediation_step="No action required — control is implemented.",
            ))
        else:
            findings.append(AuditFinding(
                control_id="GOV-OASI-001",
                control_name="Goal Hijack Prevention (ASI01)",
                domain=domain,
                status="FAIL",
                severity="CRITICAL",
                framework_refs=["OWASP ASI01"],
                evidence=(
                    "owasp_asi_goal_hijack_controls is False — no indirect prompt "
                    "injection detection for agent external inputs; adversarial "
                    "instructions embedded in retrieved documents, tool outputs, or "
                    "web pages can redirect the agent's goal state without detection, "
                    "causing the agent to act contrary to its intended objectives."
                ),
                remediation_step=(
                    "Implement injection detection on all external inputs routed into "
                    "agent context including retrieved documents, tool return values, "
                    "and environmental observations; apply semantic outlier detection "
                    "and instruction pattern matching; sandbox tool outputs before "
                    "re-injection into the agent's context window per OWASP ASI01."
                ),
            ))

        # GOV-OASI-002 — ASI02 Tool Misuse Prevention
        if config.owasp_asi_tool_misuse_controls:
            findings.append(AuditFinding(
                control_id="GOV-OASI-002",
                control_name="Tool Misuse Prevention (ASI02)",
                domain=domain,
                status="PASS",
                severity="CRITICAL",
                framework_refs=["OWASP ASI02", "MITRE ATLAS T0060"],
                evidence=(
                    "Tool allowlist enforcement, capability-scoped permissions, and "
                    "approval gates for agentic tool invocations are active."
                ),
                remediation_step="No action required — control is implemented.",
            ))
        else:
            findings.append(AuditFinding(
                control_id="GOV-OASI-002",
                control_name="Tool Misuse Prevention (ASI02)",
                domain=domain,
                status="FAIL",
                severity="CRITICAL",
                framework_refs=["OWASP ASI02", "MITRE ATLAS T0060"],
                evidence=(
                    "owasp_asi_tool_misuse_controls is False — no tool allowlist "
                    "enforcement or capability-scoped permissions in place; a hijacked "
                    "or misbehaving agent can invoke arbitrary tools, escalate "
                    "privileges, execute shell commands, or exfiltrate data by calling "
                    "tools outside its intended operational scope."
                ),
                remediation_step=(
                    "Define and enforce a per-agent tool allowlist restricting available "
                    "tools to the minimum set required; implement capability-scoped "
                    "permissions using least-privilege principles; require explicit "
                    "human approval for high-risk tool invocations (shell execution, "
                    "file system writes, external API calls) per OWASP ASI02 and "
                    "MITRE ATLAS T0060."
                ),
            ))

        # GOV-OASI-003 — ASI03 Memory Poisoning Controls
        if config.owasp_asi_memory_poisoning_controls:
            findings.append(AuditFinding(
                control_id="GOV-OASI-003",
                control_name="Memory Poisoning Controls (ASI03)",
                domain=domain,
                status="PASS",
                severity="HIGH",
                framework_refs=["OWASP ASI03"],
                evidence=(
                    "Session-scoped memory isolation and memory integrity checks are "
                    "implemented; cross-session memory contamination is prevented."
                ),
                remediation_step="No action required — control is implemented.",
            ))
        else:
            findings.append(AuditFinding(
                control_id="GOV-OASI-003",
                control_name="Memory Poisoning Controls (ASI03)",
                domain=domain,
                status="FAIL",
                severity="HIGH",
                framework_refs=["OWASP ASI03"],
                evidence=(
                    "owasp_asi_memory_poisoning_controls is False — agent memory is "
                    "not session-scoped or integrity-checked; adversarial content "
                    "written to agent memory in one session can contaminate other "
                    "users' sessions, and memory persistence across sessions creates "
                    "cross-user data leakage vectors that bypass output DLP controls."
                ),
                remediation_step=(
                    "Scope all agent memory (episodic, semantic, and working memory) "
                    "to the authenticated session; encrypt memory with session-specific "
                    "keys; purge or isolate memory on session end; implement memory "
                    "integrity checksums to detect adversarial writes; audit memory "
                    "read and write operations per OWASP ASI03."
                ),
            ))

        # GOV-OASI-004 — ASI08-10 Trust Boundary Controls
        if config.owasp_asi_trust_boundary_controls:
            findings.append(AuditFinding(
                control_id="GOV-OASI-004",
                control_name="Trust Boundary Controls (ASI08-10)",
                domain=domain,
                status="PASS",
                severity="CRITICAL",
                framework_refs=["OWASP ASI08", "OWASP ASI09", "OWASP ASI10"],
                evidence=(
                    "Rollback for irreversible actions, per-step audit trails, and "
                    "cryptographic sender verification for multi-agent messages are "
                    "all active."
                ),
                remediation_step="No action required — control is implemented.",
            ))
        else:
            findings.append(AuditFinding(
                control_id="GOV-OASI-004",
                control_name="Trust Boundary Controls (ASI08-10)",
                domain=domain,
                status="FAIL",
                severity="CRITICAL",
                framework_refs=["OWASP ASI08", "OWASP ASI09", "OWASP ASI10"],
                evidence=(
                    "owasp_asi_trust_boundary_controls is False — rollback controls "
                    "for irreversible actions, per-step audit trails, and multi-agent "
                    "sender verification are absent; irreversible actions (emails, "
                    "deletions, API state changes) can execute without human oversight; "
                    "agent actions are unauditable; multi-agent message channels are "
                    "susceptible to agent impersonation attacks."
                ),
                remediation_step=(
                    "Implement rollback/compensation transactions for all irreversible "
                    "agent actions (ASI08); deploy append-only, tamper-evident audit "
                    "logs recording every tool invocation, memory access, and decision "
                    "step (ASI09); enforce cryptographic sender identity verification "
                    "using agent-specific credentials for all multi-agent messages "
                    "(ASI10) per OWASP Agentic Top 10 2026."
                ),
            ))

        return findings

    # ------------------------------------------------------------------
    # Checker — NIST AI RMF + AI 600-1
    # ------------------------------------------------------------------

    def _check_nist_rmf(self, config: GovernanceFrameworkConfig) -> list[AuditFinding]:
        """
        Evaluate the five NIST AI RMF and AI 600-1 controls.

        Covers the four RMF core functions (MAP, MEASURE, MANAGE, GOVERN) and
        the GenAI-specific testing requirements from NIST AI 600-1 §4.1.

        References
        ----------
        NIST AI Risk Management Framework 1.0 (January 2023)
        NIST AI 600-1 GenAI Profile (July 2024)

        Parameters
        ----------
        config : GovernanceFrameworkConfig
            Configuration under audit.

        Returns
        -------
        list[AuditFinding]
            Five findings, one per NIST AI RMF control.
        """
        domain = "NIST AI RMF"
        findings: list[AuditFinding] = []

        # GOV-NIST-001 — MAP Function
        if config.nist_map_function_implemented:
            findings.append(AuditFinding(
                control_id="GOV-NIST-001",
                control_name="MAP Function (Risk Identification)",
                domain=domain,
                status="PASS",
                severity="HIGH",
                framework_refs=["NIST AI RMF MAP", "NIST AI 600-1"],
                evidence=(
                    "AI risk context is established; risk sources are identified and "
                    "categorised across technical, organisational, and societal "
                    "dimensions per the NIST AI RMF MAP function."
                ),
                remediation_step="No action required — control is implemented.",
            ))
        else:
            findings.append(AuditFinding(
                control_id="GOV-NIST-001",
                control_name="MAP Function (Risk Identification)",
                domain=domain,
                status="FAIL",
                severity="HIGH",
                framework_refs=["NIST AI RMF MAP", "NIST AI 600-1"],
                evidence=(
                    "nist_map_function_implemented is False — no AI risk context or "
                    "systematic risk identification in place; without the MAP function, "
                    "the organisation lacks the foundational risk inventory that all "
                    "subsequent MEASURE and MANAGE activities depend on."
                ),
                remediation_step=(
                    "Execute the NIST AI RMF MAP function: establish AI risk context "
                    "(deployment context, intended use, affected communities); identify "
                    "and catalogue risk sources across technical (model behaviour, data "
                    "quality), organisational (process failures), and societal "
                    "(bias, fairness, safety) dimensions; document risk register "
                    "aligned to NIST AI RMF MAP 1.1–5.2 subcategories."
                ),
            ))

        # GOV-NIST-002 — MEASURE Function
        if config.nist_measure_function_implemented:
            findings.append(AuditFinding(
                control_id="GOV-NIST-002",
                control_name="MEASURE Function (Risk Quantification)",
                domain=domain,
                status="PASS",
                severity="HIGH",
                framework_refs=["NIST AI RMF MEASURE"],
                evidence=(
                    "Risk metrics are defined, measurement methodologies documented, "
                    "and ongoing evaluation mechanisms are operational."
                ),
                remediation_step="No action required — control is implemented.",
            ))
        else:
            findings.append(AuditFinding(
                control_id="GOV-NIST-002",
                control_name="MEASURE Function (Risk Quantification)",
                domain=domain,
                status="FAIL",
                severity="HIGH",
                framework_refs=["NIST AI RMF MEASURE"],
                evidence=(
                    "nist_measure_function_implemented is False — no risk metrics, "
                    "measurement methodologies, or ongoing evaluation mechanisms "
                    "defined; AI risks cannot be prioritised, tracked, or reported "
                    "to governance bodies without quantitative measurement."
                ),
                remediation_step=(
                    "Implement the NIST AI RMF MEASURE function: define quantitative "
                    "and qualitative metrics for identified AI risks; establish "
                    "measurement methodologies (evaluation datasets, red teaming, "
                    "monitoring dashboards); schedule regular measurement cycles and "
                    "integrate results into risk reporting per MEASURE 1.1–4.2."
                ),
            ))

        # GOV-NIST-003 — MANAGE Function
        if config.nist_manage_function_implemented:
            findings.append(AuditFinding(
                control_id="GOV-NIST-003",
                control_name="MANAGE Function (Risk Treatment)",
                domain=domain,
                status="PASS",
                severity="HIGH",
                framework_refs=["NIST AI RMF MANAGE"],
                evidence=(
                    "Risk treatment plans, mitigation actions, residual risk acceptance, "
                    "and incident response procedures are in place."
                ),
                remediation_step="No action required — control is implemented.",
            ))
        else:
            findings.append(AuditFinding(
                control_id="GOV-NIST-003",
                control_name="MANAGE Function (Risk Treatment)",
                domain=domain,
                status="FAIL",
                severity="HIGH",
                framework_refs=["NIST AI RMF MANAGE"],
                evidence=(
                    "nist_manage_function_implemented is False — no risk treatment "
                    "plans, mitigation actions, or incident response procedures "
                    "in place; identified and measured AI risks have no defined "
                    "treatment pathway, leaving the organisation unable to respond "
                    "to AI incidents in a structured, repeatable manner."
                ),
                remediation_step=(
                    "Implement the NIST AI RMF MANAGE function: develop risk treatment "
                    "plans for all prioritised risks; assign risk owners; document "
                    "mitigation controls, residual risk acceptance criteria, and "
                    "contingency plans; establish an AI incident response procedure "
                    "covering detection, containment, eradication, and post-incident "
                    "review per MANAGE 1.1–4.2."
                ),
            ))

        # GOV-NIST-004 — GOVERN Function
        if config.nist_govern_function_implemented:
            findings.append(AuditFinding(
                control_id="GOV-NIST-004",
                control_name="GOVERN Function (Oversight)",
                domain=domain,
                status="PASS",
                severity="CRITICAL",
                framework_refs=["NIST AI RMF GOVERN"],
                evidence=(
                    "AI governance structure, roles, accountability, policies, and "
                    "oversight mechanisms are formally established."
                ),
                remediation_step="No action required — control is implemented.",
            ))
        else:
            findings.append(AuditFinding(
                control_id="GOV-NIST-004",
                control_name="GOVERN Function (Oversight)",
                domain=domain,
                status="FAIL",
                severity="CRITICAL",
                framework_refs=["NIST AI RMF GOVERN"],
                evidence=(
                    "nist_govern_function_implemented is False — no AI governance "
                    "structure, accountability roles, or oversight mechanisms formally "
                    "established; without the GOVERN function, all other RMF activities "
                    "(MAP, MEASURE, MANAGE) lack institutional authority and cannot "
                    "be sustained across organisational change."
                ),
                remediation_step=(
                    "Establish the NIST AI RMF GOVERN function: appoint an AI "
                    "governance body (board or committee) with executive sponsorship; "
                    "define AI roles and accountability (AI Owner, AI Risk Officer, "
                    "Ethics Board); publish organisational AI policy; establish "
                    "escalation paths for AI risk decisions; implement governance "
                    "reporting per GOVERN 1.1–6.2."
                ),
            ))

        # GOV-NIST-005 — GenAI-Specific Testing (AI 600-1)
        if config.nist_genai_testing_implemented:
            findings.append(AuditFinding(
                control_id="GOV-NIST-005",
                control_name="GenAI-Specific Testing (AI 600-1)",
                domain=domain,
                status="PASS",
                severity="HIGH",
                framework_refs=["NIST AI 600-1 §4.1"],
                evidence=(
                    "GenAI-specific testing including red teaming, adversarial "
                    "evaluation, and factuality testing is implemented beyond "
                    "standard ML evaluation."
                ),
                remediation_step="No action required — control is implemented.",
            ))
        else:
            findings.append(AuditFinding(
                control_id="GOV-NIST-005",
                control_name="GenAI-Specific Testing (AI 600-1)",
                domain=domain,
                status="FAIL",
                severity="HIGH",
                framework_refs=["NIST AI 600-1 §4.1"],
                evidence=(
                    "nist_genai_testing_implemented is False — no GenAI-specific "
                    "testing programme beyond standard accuracy/performance metrics "
                    "in place; NIST AI 600-1 §4.1 requires testing for GenAI-specific "
                    "failure modes including prompt injection, hallucination, harmful "
                    "content generation, and adversarial robustness that conventional "
                    "ML test suites do not cover."
                ),
                remediation_step=(
                    "Implement a GenAI-specific testing programme per NIST AI 600-1 "
                    "§4.1: conduct structured red teaming for prompt injection, "
                    "jailbreaking, and adversarial inputs; measure hallucination rates "
                    "using factuality benchmarks; test for harmful content generation "
                    "across sensitive categories; establish automated regression testing "
                    "for safety properties on every model update."
                ),
            ))

        return findings

    # ------------------------------------------------------------------
    # Checker — ISO/IEC 42001:2023
    # ------------------------------------------------------------------

    def _check_iso_42001(self, config: GovernanceFrameworkConfig) -> list[AuditFinding]:
        """
        Evaluate the nine ISO/IEC 42001:2023 controls.

        Covers Clauses 5.2 (AI Policy), 6.1 (Risk Assessment), 6.2
        (AI Objectives), 7.2 (Competence), 7.5 (Documented Information),
        8.4 (Operational Controls), 9.1 (Monitoring), 9.2 (Internal Audit),
        and 9.3 (Management Review).

        References
        ----------
        ISO/IEC 42001:2023 — Artificial Intelligence Management System (AIMS)

        Parameters
        ----------
        config : GovernanceFrameworkConfig
            Configuration under audit.

        Returns
        -------
        list[AuditFinding]
            Nine findings, one per ISO 42001 clause control.
        """
        domain = "ISO/IEC 42001:2023"
        findings: list[AuditFinding] = []

        # GOV-ISO-001 — Cl.5.2 AI Policy
        if config.iso_ai_policy_defined:
            findings.append(AuditFinding(
                control_id="GOV-ISO-001",
                control_name="AI Policy (Cl.5.2)",
                domain=domain,
                status="PASS",
                severity="CRITICAL",
                framework_refs=["ISO 42001 Cl.5.2"],
                evidence=(
                    "Formal AI policy is documented, approved by top management, and "
                    "communicated to relevant stakeholders."
                ),
                remediation_step="No action required — control is implemented.",
            ))
        else:
            findings.append(AuditFinding(
                control_id="GOV-ISO-001",
                control_name="AI Policy (Cl.5.2)",
                domain=domain,
                status="FAIL",
                severity="CRITICAL",
                framework_refs=["ISO 42001 Cl.5.2"],
                evidence=(
                    "iso_ai_policy_defined is False — no formal AI policy documented "
                    "or approved by top management; ISO 42001 Cl.5.2 is a mandatory "
                    "requirement for AIMS certification; its absence means there is no "
                    "documented organisational commitment to responsible AI governance, "
                    "making all downstream controls ungoverned."
                ),
                remediation_step=(
                    "Draft and obtain top management approval for an AI policy "
                    "addressing: organisational commitment to responsible AI; alignment "
                    "with organisational objectives; provision of resources; commitment "
                    "to continual improvement; and communication to all relevant "
                    "internal and external stakeholders per ISO 42001 Cl.5.2."
                ),
            ))

        # GOV-ISO-002 — Cl.6.1 Risk Assessment
        if config.iso_ai_risk_assessment:
            findings.append(AuditFinding(
                control_id="GOV-ISO-002",
                control_name="Risk Assessment (Cl.6.1)",
                domain=domain,
                status="PASS",
                severity="CRITICAL",
                framework_refs=["ISO 42001 Cl.6.1"],
                evidence=(
                    "AI-specific risk assessment process is defined and executed, "
                    "covering identification, analysis, and evaluation of AI risks."
                ),
                remediation_step="No action required — control is implemented.",
            ))
        else:
            findings.append(AuditFinding(
                control_id="GOV-ISO-002",
                control_name="Risk Assessment (Cl.6.1)",
                domain=domain,
                status="FAIL",
                severity="CRITICAL",
                framework_refs=["ISO 42001 Cl.6.1"],
                evidence=(
                    "iso_ai_risk_assessment is False — no AI-specific risk assessment "
                    "process defined or executed; ISO 42001 Cl.6.1 mandates a documented "
                    "process for identifying, analysing, and evaluating AI risks as the "
                    "foundation for the planning and operational clauses; absence makes "
                    "AIMS certification non-conformant."
                ),
                remediation_step=(
                    "Define and execute an AI risk assessment process per ISO 42001 "
                    "Cl.6.1: identify AI-specific risk sources (data quality, model "
                    "bias, adversarial attacks, third-party dependencies); analyse "
                    "likelihood and impact; evaluate risks against acceptance criteria; "
                    "document results and maintain as controlled information; repeat "
                    "at planned intervals and after significant system changes."
                ),
            ))

        # GOV-ISO-003 — Cl.6.2 AI Objectives
        if config.iso_ai_objectives_set:
            findings.append(AuditFinding(
                control_id="GOV-ISO-003",
                control_name="AI Objectives (Cl.6.2)",
                domain=domain,
                status="PASS",
                severity="HIGH",
                framework_refs=["ISO 42001 Cl.6.2"],
                evidence=(
                    "Measurable AI objectives aligned to policy are defined, with plans "
                    "for achievement and progress tracking mechanisms in place."
                ),
                remediation_step="No action required — control is implemented.",
            ))
        else:
            findings.append(AuditFinding(
                control_id="GOV-ISO-003",
                control_name="AI Objectives (Cl.6.2)",
                domain=domain,
                status="FAIL",
                severity="HIGH",
                framework_refs=["ISO 42001 Cl.6.2"],
                evidence=(
                    "iso_ai_objectives_set is False — no measurable AI objectives "
                    "defined or aligned to policy; ISO 42001 Cl.6.2 requires that the "
                    "organisation establishes AI objectives at relevant functions and "
                    "levels with plans for their achievement; without objectives, "
                    "governance progress cannot be measured or reported."
                ),
                remediation_step=(
                    "Establish measurable AI objectives per ISO 42001 Cl.6.2: align "
                    "objectives to AI policy commitments; make them measurable (KPIs, "
                    "thresholds, timelines); assign accountability; define actions, "
                    "resources, and timelines for achievement; integrate into "
                    "management review reporting cycles."
                ),
            ))

        # GOV-ISO-004 — Cl.7.2 Competence
        if config.iso_ai_competence_managed:
            findings.append(AuditFinding(
                control_id="GOV-ISO-004",
                control_name="Competence Management (Cl.7.2)",
                domain=domain,
                status="PASS",
                severity="MEDIUM",
                framework_refs=["ISO 42001 Cl.7.2"],
                evidence=(
                    "Competence requirements for AI roles are defined; training, "
                    "awareness, and skills verification programmes are implemented."
                ),
                remediation_step="No action required — control is implemented.",
            ))
        else:
            findings.append(AuditFinding(
                control_id="GOV-ISO-004",
                control_name="Competence Management (Cl.7.2)",
                domain=domain,
                status="FAIL",
                severity="MEDIUM",
                framework_refs=["ISO 42001 Cl.7.2"],
                evidence=(
                    "iso_ai_competence_managed is False — no competence requirements "
                    "or training programmes defined for AI roles; ISO 42001 Cl.7.2 "
                    "requires the organisation to determine necessary competences for "
                    "persons working in AI roles and to ensure those competences are "
                    "acquired and maintained."
                ),
                remediation_step=(
                    "Define competence requirements for all AI roles (ML engineers, "
                    "data scientists, AI risk officers, AI ethicists) per ISO 42001 "
                    "Cl.7.2; implement training programmes covering AI safety, bias, "
                    "regulatory requirements, and operational responsibilities; "
                    "maintain records of training completion and competence assessments."
                ),
            ))

        # GOV-ISO-005 — Cl.7.5 Documented Information
        if config.iso_ai_documented_info:
            findings.append(AuditFinding(
                control_id="GOV-ISO-005",
                control_name="Documented Information (Cl.7.5)",
                domain=domain,
                status="PASS",
                severity="HIGH",
                framework_refs=["ISO 42001 Cl.7.5"],
                evidence=(
                    "Required documented information — policies, procedures, records, "
                    "and evidence — is created, maintained, and controlled."
                ),
                remediation_step="No action required — control is implemented.",
            ))
        else:
            findings.append(AuditFinding(
                control_id="GOV-ISO-005",
                control_name="Documented Information (Cl.7.5)",
                domain=domain,
                status="FAIL",
                severity="HIGH",
                framework_refs=["ISO 42001 Cl.7.5"],
                evidence=(
                    "iso_ai_documented_info is False — required documented information "
                    "for the AI management system is not created or controlled; ISO "
                    "42001 Cl.7.5 mandates documented information to support AIMS "
                    "operation and to provide evidence of conformity; its absence "
                    "makes audit evidence unavailable and certification non-conformant."
                ),
                remediation_step=(
                    "Establish document control for all AIMS documented information "
                    "per ISO 42001 Cl.7.5: create required documents (AI policy, risk "
                    "assessment records, objectives, audit records, management review "
                    "minutes); implement version control, review cycles, and access "
                    "controls; define retention periods; maintain evidence of AIMS "
                    "operation and conformity."
                ),
            ))

        # GOV-ISO-006 — Cl.8.4 Operational Controls
        if config.iso_ai_operational_controls:
            findings.append(AuditFinding(
                control_id="GOV-ISO-006",
                control_name="Operational Controls (Cl.8.4)",
                domain=domain,
                status="PASS",
                severity="HIGH",
                framework_refs=["ISO 42001 Cl.8.4"],
                evidence=(
                    "Operational controls for AI system development, deployment, and "
                    "decommissioning are designed and implemented."
                ),
                remediation_step="No action required — control is implemented.",
            ))
        else:
            findings.append(AuditFinding(
                control_id="GOV-ISO-006",
                control_name="Operational Controls (Cl.8.4)",
                domain=domain,
                status="FAIL",
                severity="HIGH",
                framework_refs=["ISO 42001 Cl.8.4"],
                evidence=(
                    "iso_ai_operational_controls is False — no operational controls "
                    "defined for AI system lifecycle (development, testing, deployment, "
                    "decommissioning); ISO 42001 Cl.8.4 requires controls over all "
                    "AI operational processes to ensure they are conducted in accordance "
                    "with the AIMS and produce AI systems that meet specified requirements."
                ),
                remediation_step=(
                    "Design and implement operational controls per ISO 42001 Cl.8.4: "
                    "establish AI development lifecycle controls (data governance, "
                    "model validation, testing gates); define deployment controls "
                    "(approval workflows, staged rollout, rollback procedures); "
                    "implement decommissioning procedures; integrate security controls "
                    "from OWASP LLM03 and supply chain requirements into operational "
                    "processes."
                ),
            ))

        # GOV-ISO-007 — Cl.9.1 Monitoring
        if config.iso_ai_monitoring:
            findings.append(AuditFinding(
                control_id="GOV-ISO-007",
                control_name="Monitoring & Evaluation (Cl.9.1)",
                domain=domain,
                status="PASS",
                severity="HIGH",
                framework_refs=["ISO 42001 Cl.9.1"],
                evidence=(
                    "Performance and conformance monitoring, measurement, and evaluation "
                    "processes are operational for deployed AI systems."
                ),
                remediation_step="No action required — control is implemented.",
            ))
        else:
            findings.append(AuditFinding(
                control_id="GOV-ISO-007",
                control_name="Monitoring & Evaluation (Cl.9.1)",
                domain=domain,
                status="FAIL",
                severity="HIGH",
                framework_refs=["ISO 42001 Cl.9.1"],
                evidence=(
                    "iso_ai_monitoring is False — no monitoring or evaluation processes "
                    "operational for deployed AI systems; ISO 42001 Cl.9.1 requires "
                    "ongoing monitoring of AI system performance, conformance with "
                    "requirements, and effectiveness of controls; without monitoring, "
                    "performance degradation, bias drift, and control failures go "
                    "undetected."
                ),
                remediation_step=(
                    "Implement AI system monitoring per ISO 42001 Cl.9.1: define "
                    "what to monitor (accuracy, fairness metrics, drift indicators, "
                    "safety violations); establish measurement frequency and methods; "
                    "set thresholds and alerting; integrate with NIST AI RMF MEASURE "
                    "metrics; feed results into management review and risk treatment "
                    "processes."
                ),
            ))

        # GOV-ISO-008 — Cl.9.2 Internal Audit
        if config.iso_ai_internal_audit:
            findings.append(AuditFinding(
                control_id="GOV-ISO-008",
                control_name="Internal Audit (Cl.9.2)",
                domain=domain,
                status="PASS",
                severity="MEDIUM",
                framework_refs=["ISO 42001 Cl.9.2"],
                evidence=(
                    "Internal audit programme for the AI management system is "
                    "established and executed at planned intervals."
                ),
                remediation_step="No action required — control is implemented.",
            ))
        else:
            findings.append(AuditFinding(
                control_id="GOV-ISO-008",
                control_name="Internal Audit (Cl.9.2)",
                domain=domain,
                status="FAIL",
                severity="MEDIUM",
                framework_refs=["ISO 42001 Cl.9.2"],
                evidence=(
                    "iso_ai_internal_audit is False — no internal audit programme "
                    "established for the AI management system; ISO 42001 Cl.9.2 "
                    "requires planned internal audits to determine whether the AIMS "
                    "conforms to requirements and is effectively implemented; without "
                    "internal audit, non-conformities accumulate undetected."
                ),
                remediation_step=(
                    "Establish an AI management system internal audit programme per "
                    "ISO 42001 Cl.9.2: define audit criteria, scope, frequency, and "
                    "methods; appoint competent, objective auditors; conduct audits at "
                    "planned intervals; report results to management; track and verify "
                    "closure of all non-conformities identified."
                ),
            ))

        # GOV-ISO-009 — Cl.9.3 Management Review
        if config.iso_ai_management_review:
            findings.append(AuditFinding(
                control_id="GOV-ISO-009",
                control_name="Management Review (Cl.9.3)",
                domain=domain,
                status="PASS",
                severity="MEDIUM",
                framework_refs=["ISO 42001 Cl.9.3"],
                evidence=(
                    "Top management review of the AI management system is conducted "
                    "at planned intervals to ensure continuing suitability and "
                    "effectiveness."
                ),
                remediation_step="No action required — control is implemented.",
            ))
        else:
            findings.append(AuditFinding(
                control_id="GOV-ISO-009",
                control_name="Management Review (Cl.9.3)",
                domain=domain,
                status="FAIL",
                severity="MEDIUM",
                framework_refs=["ISO 42001 Cl.9.3"],
                evidence=(
                    "iso_ai_management_review is False — no top management review of "
                    "the AIMS conducted; ISO 42001 Cl.9.3 requires management reviews "
                    "to consider monitoring results, audit findings, risk changes, and "
                    "opportunities for improvement; without management review, the "
                    "AIMS cannot achieve continual improvement and senior accountability "
                    "for AI governance is absent."
                ),
                remediation_step=(
                    "Establish a management review cycle per ISO 42001 Cl.9.3: "
                    "schedule reviews at defined intervals (minimum annually); include "
                    "agenda items for monitoring results, audit findings, risk register "
                    "changes, stakeholder concerns, and objectives performance; "
                    "document review outputs (decisions, actions, resource commitments); "
                    "maintain review records as controlled information."
                ),
            ))

        return findings

    # ------------------------------------------------------------------
    # Checker — MITRE ATLAS v5.1
    # ------------------------------------------------------------------

    def _check_mitre_atlas(self, config: GovernanceFrameworkConfig) -> list[AuditFinding]:
        """
        Evaluate the six MITRE ATLAS v5.1 adversarial controls.

        Covers TA0001 Reconnaissance detection, T0020 Training Data Poisoning,
        T0024 Model Exfiltration, T0051 Prompt Injection, T0060 Agent Tool
        Invocation, and T0057 RAG Database Prompting.

        References
        ----------
        MITRE ATLAS v5.1 (November 2025)
            https://atlas.mitre.org/

        Parameters
        ----------
        config : GovernanceFrameworkConfig
            Configuration under audit.

        Returns
        -------
        list[AuditFinding]
            Six findings, one per MITRE ATLAS control.
        """
        domain = "MITRE ATLAS v5.1"
        findings: list[AuditFinding] = []

        # GOV-ATLAS-001 — TA0001 Reconnaissance Detection
        if config.mitre_recon_detection:
            findings.append(AuditFinding(
                control_id="GOV-ATLAS-001",
                control_name="Reconnaissance Detection (TA0001)",
                domain=domain,
                status="PASS",
                severity="HIGH",
                framework_refs=["MITRE ATLAS TA0001"],
                evidence=(
                    "Reconnaissance detection controls are active; adversarial attempts "
                    "to gather intelligence about AI models, APIs, and training data are "
                    "identified and logged."
                ),
                remediation_step="No action required — control is implemented.",
            ))
        else:
            findings.append(AuditFinding(
                control_id="GOV-ATLAS-001",
                control_name="Reconnaissance Detection (TA0001)",
                domain=domain,
                status="FAIL",
                severity="HIGH",
                framework_refs=["MITRE ATLAS TA0001"],
                evidence=(
                    "mitre_recon_detection is False — no reconnaissance detection "
                    "controls active; adversaries conducting model architecture probing, "
                    "API scanning, training data extraction attempts, or capability "
                    "boundary testing go undetected, enabling informed subsequent attack "
                    "stages (T0020 poisoning, T0051 injection, T0024 exfiltration)."
                ),
                remediation_step=(
                    "Implement reconnaissance detection per MITRE ATLAS TA0001: "
                    "monitor API request patterns for systematic capability probing "
                    "(unusual query distributions, boundary testing sequences); "
                    "detect and alert on automated scanning tools targeting model "
                    "endpoints; log and analyse anomalous error enumeration patterns; "
                    "rate-limit and challenge suspicious reconnaissance-like traffic."
                ),
            ))

        # GOV-ATLAS-002 — T0020 Training Data Poisoning Detection
        if config.mitre_poisoning_detection:
            findings.append(AuditFinding(
                control_id="GOV-ATLAS-002",
                control_name="Training Data Poisoning Detection (T0020)",
                domain=domain,
                status="PASS",
                severity="CRITICAL",
                framework_refs=["MITRE ATLAS T0020"],
                evidence=(
                    "Training data poisoning detection and model integrity verification "
                    "controls are implemented."
                ),
                remediation_step="No action required — control is implemented.",
            ))
        else:
            findings.append(AuditFinding(
                control_id="GOV-ATLAS-002",
                control_name="Training Data Poisoning Detection (T0020)",
                domain=domain,
                status="FAIL",
                severity="CRITICAL",
                framework_refs=["MITRE ATLAS T0020"],
                evidence=(
                    "mitre_poisoning_detection is False — no training data poisoning "
                    "detection or model integrity verification in place; MITRE ATLAS "
                    "T0020 identifies training data poisoning as a primary technique "
                    "for embedding backdoors and steering model behaviour; poisoned "
                    "models can behave normally on most inputs while exhibiting "
                    "attacker-controlled behaviour on trigger inputs."
                ),
                remediation_step=(
                    "Implement MITRE ATLAS T0020 countermeasures: audit training "
                    "dataset provenance and integrity before every training run; "
                    "deploy statistical anomaly detection on training corpora to "
                    "identify atypical label distributions or semantic outliers; "
                    "conduct post-training model behavioural testing for known backdoor "
                    "trigger patterns; implement differential privacy where applicable "
                    "to limit memorisation of poisoned samples."
                ),
            ))

        # GOV-ATLAS-003 — T0024 Model Exfiltration Controls
        if config.mitre_extraction_controls:
            findings.append(AuditFinding(
                control_id="GOV-ATLAS-003",
                control_name="Model Exfiltration Controls (T0024)",
                domain=domain,
                status="PASS",
                severity="HIGH",
                framework_refs=["MITRE ATLAS T0024"],
                evidence=(
                    "Model exfiltration controls are implemented; extraction of model "
                    "weights, architectures, or training data through API abuse is "
                    "prevented."
                ),
                remediation_step="No action required — control is implemented.",
            ))
        else:
            findings.append(AuditFinding(
                control_id="GOV-ATLAS-003",
                control_name="Model Exfiltration Controls (T0024)",
                domain=domain,
                status="FAIL",
                severity="HIGH",
                framework_refs=["MITRE ATLAS T0024"],
                evidence=(
                    "mitre_extraction_controls is False — no model exfiltration "
                    "controls in place; MITRE ATLAS T0024 identifies model extraction "
                    "via systematic API queries as a viable technique to reconstruct "
                    "proprietary model weights, architectures, and training data; "
                    "extracted models can be used to prepare highly targeted adversarial "
                    "examples or to circumvent licensing controls."
                ),
                remediation_step=(
                    "Implement MITRE ATLAS T0024 countermeasures: apply rate limiting "
                    "and query throttling to model inference APIs; add output "
                    "perturbation or prediction rounding to reduce extraction signal "
                    "fidelity; monitor API query patterns for systematic extraction "
                    "sequences (grid sampling, decision boundary probing); watermark "
                    "model outputs for extraction attribution."
                ),
            ))

        # GOV-ATLAS-004 — T0051 Prompt Injection Detection
        if config.mitre_prompt_injection_detection:
            findings.append(AuditFinding(
                control_id="GOV-ATLAS-004",
                control_name="Prompt Injection Detection (T0051)",
                domain=domain,
                status="PASS",
                severity="CRITICAL",
                framework_refs=["MITRE ATLAS T0051", "OWASP LLM01"],
                evidence=(
                    "Prompt injection detection aligned to ATLAS AML.T0051.000 "
                    "(indirect) and AML.T0051.001 (direct) is implemented."
                ),
                remediation_step="No action required — control is implemented.",
            ))
        else:
            findings.append(AuditFinding(
                control_id="GOV-ATLAS-004",
                control_name="Prompt Injection Detection (T0051)",
                domain=domain,
                status="FAIL",
                severity="CRITICAL",
                framework_refs=["MITRE ATLAS T0051", "OWASP LLM01"],
                evidence=(
                    "mitre_prompt_injection_detection is False — no ATLAS-aligned "
                    "prompt injection detection covering both direct (AML.T0051.001) "
                    "and indirect (AML.T0051.000) injection vectors; MITRE ATLAS T0051 "
                    "documents prompt injection as an active adversarial technique with "
                    "real-world exploits against deployed LLM applications; absence of "
                    "this detection is a CRITICAL gap cross-referenced by OWASP LLM01."
                ),
                remediation_step=(
                    "Implement MITRE ATLAS T0051 countermeasures for both direct and "
                    "indirect prompt injection: deploy injection detection on all "
                    "inputs and retrieved context; implement input validation and "
                    "sanitisation per ATLAS AML.T0051 mitigation guidance; use "
                    "privilege-separated prompt architecture (system, user, retrieved "
                    "context at different trust levels); test against the ATLAS prompt "
                    "injection technique catalogue."
                ),
            ))

        # GOV-ATLAS-005 — T0060 Agent Tool Invocation Controls
        if config.mitre_tool_invocation_controls:
            findings.append(AuditFinding(
                control_id="GOV-ATLAS-005",
                control_name="Agent Tool Invocation Controls (T0060)",
                domain=domain,
                status="PASS",
                severity="HIGH",
                framework_refs=["MITRE ATLAS T0060"],
                evidence=(
                    "Agent tool invocation controls are implemented; adversarial "
                    "manipulation of tool calls in agentic pipelines is prevented."
                ),
                remediation_step="No action required — control is implemented.",
            ))
        else:
            findings.append(AuditFinding(
                control_id="GOV-ATLAS-005",
                control_name="Agent Tool Invocation Controls (T0060)",
                domain=domain,
                status="FAIL",
                severity="HIGH",
                framework_refs=["MITRE ATLAS T0060"],
                evidence=(
                    "mitre_tool_invocation_controls is False — no controls on agent "
                    "tool invocations aligned to MITRE ATLAS T0060; adversaries who "
                    "achieve prompt injection (T0051) in an agentic context can "
                    "subsequently invoke arbitrary tools, escalate privileges, exfiltrate "
                    "data, or execute shell commands by manipulating the agent's tool "
                    "selection and parameter construction."
                ),
                remediation_step=(
                    "Implement MITRE ATLAS T0060 countermeasures: enforce strict tool "
                    "allowlists per agent identity; validate tool call parameters "
                    "against expected schemas before execution; log all tool invocations "
                    "with full parameter values to append-only audit logs; require "
                    "human-in-the-loop approval for high-risk tool classes "
                    "(shell execution, file writes, external API calls)."
                ),
            ))

        # GOV-ATLAS-006 — T0057 RAG Database Prompting Controls
        if config.mitre_rag_db_controls:
            findings.append(AuditFinding(
                control_id="GOV-ATLAS-006",
                control_name="RAG Database Prompting Controls (T0057)",
                domain=domain,
                status="PASS",
                severity="HIGH",
                framework_refs=["MITRE ATLAS T0057", "OWASP LLM08"],
                evidence=(
                    "RAG database prompting controls are implemented; adversarial "
                    "content injection into vector store retrieval pipelines is "
                    "prevented."
                ),
                remediation_step="No action required — control is implemented.",
            ))
        else:
            findings.append(AuditFinding(
                control_id="GOV-ATLAS-006",
                control_name="RAG Database Prompting Controls (T0057)",
                domain=domain,
                status="FAIL",
                severity="HIGH",
                framework_refs=["MITRE ATLAS T0057", "OWASP LLM08"],
                evidence=(
                    "mitre_rag_db_controls is False — no controls on RAG database "
                    "prompting per MITRE ATLAS T0057; an adversary who can write to "
                    "the vector database or retrieval corpus can inject documents "
                    "containing adversarial instructions that will be retrieved and "
                    "routed into the LLM's context when semantically similar queries "
                    "are made, bypassing conventional input filtering."
                ),
                remediation_step=(
                    "Implement MITRE ATLAS T0057 countermeasures: enforce write-access "
                    "controls and integrity verification for all vector databases; "
                    "deploy semantic anomaly detection on documents at ingestion time; "
                    "validate retrieved chunks against expected content patterns before "
                    "routing to LLM context; implement retrieval audit logs; align to "
                    "OWASP LLM08 vector/embedding security controls."
                ),
            ))

        return findings

    # ------------------------------------------------------------------
    # Checker — CSA Agentic Trust Framework
    # ------------------------------------------------------------------

    def _check_csa_atf(self, config: GovernanceFrameworkConfig) -> list[AuditFinding]:
        """
        Evaluate the five CSA Agentic Trust Framework controls.

        Covers ATF Level 1 (Sandbox), Level 2 (Controlled), Level 3
        (Trusted), Level 4 (Autonomous), and the §4.1 Continuous Trust
        Assessment requirement.

        References
        ----------
        CSA Agentic AI Trust Framework v1.0 (February 2026)
            https://cloudsecurityalliance.org/

        Parameters
        ----------
        config : GovernanceFrameworkConfig
            Configuration under audit.

        Returns
        -------
        list[AuditFinding]
            Five findings, one per CSA ATF control.
        """
        domain = "CSA Agentic Trust Framework"
        findings: list[AuditFinding] = []

        # GOV-CSA-001 — Level 1 Sandbox Controls
        if config.csa_atf_sandbox_controls:
            findings.append(AuditFinding(
                control_id="GOV-CSA-001",
                control_name="Sandbox Controls (Level 1)",
                domain=domain,
                status="PASS",
                severity="HIGH",
                framework_refs=["CSA ATF Level 1"],
                evidence=(
                    "Sandbox isolation controls are active; agentic AI systems are "
                    "prevented from accessing production systems during evaluation "
                    "and testing phases."
                ),
                remediation_step="No action required — control is implemented.",
            ))
        else:
            findings.append(AuditFinding(
                control_id="GOV-CSA-001",
                control_name="Sandbox Controls (Level 1)",
                domain=domain,
                status="FAIL",
                severity="HIGH",
                framework_refs=["CSA ATF Level 1"],
                evidence=(
                    "csa_atf_sandbox_controls is False — no sandbox isolation controls "
                    "in place; CSA ATF Level 1 is the foundational trust level requiring "
                    "that agentic AI systems operate in isolated environments during "
                    "evaluation and testing, preventing untested agents from accessing "
                    "production data, APIs, or services; without sandbox controls, "
                    "evaluation mistakes cause production incidents."
                ),
                remediation_step=(
                    "Implement CSA ATF Level 1 sandbox controls: deploy agentic AI "
                    "systems in network-isolated sandbox environments with no access "
                    "to production credentials, APIs, or data stores during evaluation; "
                    "use mock tool implementations and synthetic data; enforce "
                    "environment separation via network policies and IAM boundaries; "
                    "gate production access on formal Level 1 evaluation completion."
                ),
            ))

        # GOV-CSA-002 — Level 2 Controlled Deployment
        if config.csa_atf_controlled_controls:
            findings.append(AuditFinding(
                control_id="GOV-CSA-002",
                control_name="Controlled Deployment (Level 2)",
                domain=domain,
                status="PASS",
                severity="HIGH",
                framework_refs=["CSA ATF Level 2"],
                evidence=(
                    "Controlled deployment controls are active: injection detection, "
                    "session-scoped memory, DLP on outputs, and tool allowlists are "
                    "all implemented."
                ),
                remediation_step="No action required — control is implemented.",
            ))
        else:
            findings.append(AuditFinding(
                control_id="GOV-CSA-002",
                control_name="Controlled Deployment (Level 2)",
                domain=domain,
                status="FAIL",
                severity="HIGH",
                framework_refs=["CSA ATF Level 2"],
                evidence=(
                    "csa_atf_controlled_controls is False — CSA ATF Level 2 controls "
                    "for controlled production deployment are absent; Level 2 requires "
                    "injection detection, session-scoped memory isolation, DLP on "
                    "outputs, and tool allowlist enforcement as the minimum set of "
                    "controls for an agent interacting with real users in a production "
                    "environment with restricted capabilities."
                ),
                remediation_step=(
                    "Implement CSA ATF Level 2 controlled deployment controls: enable "
                    "injection detection on all external agent inputs; enforce session-"
                    "scoped memory isolation; implement DLP scanning on all agent "
                    "outputs before delivery; define and enforce a tool allowlist "
                    "restricting the agent to its designated capabilities; verify "
                    "compliance with all Level 2 requirements before enabling production "
                    "user access."
                ),
            ))

        # GOV-CSA-003 — Level 3 Trusted Operations
        if config.csa_atf_trusted_controls:
            findings.append(AuditFinding(
                control_id="GOV-CSA-003",
                control_name="Trusted Operations (Level 3)",
                domain=domain,
                status="PASS",
                severity="HIGH",
                framework_refs=["CSA ATF Level 3"],
                evidence=(
                    "Trusted operations controls are active: full per-step audit trail, "
                    "formal capability attestation, and HITL gates for high-impact "
                    "actions are implemented."
                ),
                remediation_step="No action required — control is implemented.",
            ))
        else:
            findings.append(AuditFinding(
                control_id="GOV-CSA-003",
                control_name="Trusted Operations (Level 3)",
                domain=domain,
                status="FAIL",
                severity="HIGH",
                framework_refs=["CSA ATF Level 3"],
                evidence=(
                    "csa_atf_trusted_controls is False — CSA ATF Level 3 trusted "
                    "operations controls are absent; Level 3 is required for agents "
                    "performing consequential actions in production environments and "
                    "mandates full per-step audit trails, formal capability attestation, "
                    "and human-in-the-loop checkpoints for high-impact operations."
                ),
                remediation_step=(
                    "Implement CSA ATF Level 3 trusted operations controls: deploy "
                    "append-only, tamper-evident per-step audit logs covering all tool "
                    "invocations, memory accesses, and decision steps; establish formal "
                    "capability attestation (documented, versioned capability scope "
                    "verified at deployment); implement HITL gates that pause execution "
                    "and route to human operators for all high-impact actions."
                ),
            ))

        # GOV-CSA-004 — Level 4 Autonomous Operations
        if config.csa_atf_autonomous_controls:
            findings.append(AuditFinding(
                control_id="GOV-CSA-004",
                control_name="Autonomous Operations (Level 4)",
                domain=domain,
                status="PASS",
                severity="MEDIUM",
                framework_refs=["CSA ATF Level 4"],
                evidence=(
                    "Autonomous operations controls are active: continuous monitoring, "
                    "quarterly red teaming, and automated anomaly response are "
                    "implemented."
                ),
                remediation_step="No action required — control is implemented.",
            ))
        else:
            findings.append(AuditFinding(
                control_id="GOV-CSA-004",
                control_name="Autonomous Operations (Level 4)",
                domain=domain,
                status="FAIL",
                severity="MEDIUM",
                framework_refs=["CSA ATF Level 4"],
                evidence=(
                    "csa_atf_autonomous_controls is False — CSA ATF Level 4 autonomous "
                    "operations controls are absent; Level 4 is required for fully "
                    "autonomous agents operating without per-action human oversight and "
                    "mandates continuous runtime monitoring, quarterly adversarial red "
                    "teaming, and automated anomaly detection with autonomous response "
                    "capabilities."
                ),
                remediation_step=(
                    "Implement CSA ATF Level 4 autonomous operations controls: deploy "
                    "continuous runtime monitoring for agent behaviour anomalies; "
                    "establish a quarterly red team programme specifically targeting "
                    "autonomous agent attack surfaces (goal hijack, tool misuse, "
                    "cascading failures); implement automated anomaly detection with "
                    "agent suspension capability; maintain Level 4 compliance evidence "
                    "for regulatory and audit purposes."
                ),
            ))

        # GOV-CSA-005 — Continuous Trust Assessment
        if config.csa_atf_continuous_assessment:
            findings.append(AuditFinding(
                control_id="GOV-CSA-005",
                control_name="Continuous Trust Assessment",
                domain=domain,
                status="PASS",
                severity="HIGH",
                framework_refs=["CSA ATF §4.1", "ISO 42001 Cl.9.1"],
                evidence=(
                    "Continuous trust assessment process is operational; agent "
                    "trustworthiness is evaluated at runtime, not only at initial "
                    "deployment."
                ),
                remediation_step="No action required — control is implemented.",
            ))
        else:
            findings.append(AuditFinding(
                control_id="GOV-CSA-005",
                control_name="Continuous Trust Assessment",
                domain=domain,
                status="FAIL",
                severity="HIGH",
                framework_refs=["CSA ATF §4.1", "ISO 42001 Cl.9.1"],
                evidence=(
                    "csa_atf_continuous_assessment is False — no continuous trust "
                    "assessment process operational; CSA ATF §4.1 requires that agent "
                    "trustworthiness is evaluated continuously at runtime rather than "
                    "solely at deployment time; agent behaviour, capability scope, "
                    "and control effectiveness change over time as models drift, "
                    "toolsets evolve, and new attack techniques emerge."
                ),
                remediation_step=(
                    "Implement CSA ATF §4.1 continuous trust assessment: deploy "
                    "runtime behavioural monitoring measuring agent outputs against "
                    "trusted baselines; compute rolling trust scores based on policy "
                    "compliance, anomaly rates, and HITL escalation frequency; trigger "
                    "trust level re-evaluation on detected anomalies; integrate with "
                    "ISO 42001 Cl.9.1 monitoring processes to feed trust metrics into "
                    "management reporting."
                ),
            ))

        return findings


# ---------------------------------------------------------------------------
# Demo helpers
# ---------------------------------------------------------------------------


def _print_report(report: GovernanceAuditReport) -> None:
    """
    Print a concise governance audit report to stdout.

    Displays system identity, score, maturity level, per-domain statistics,
    and a summary of all FAIL findings with their remediation steps.

    Parameters
    ----------
    report : GovernanceAuditReport
        The audit report to display.
    """
    bar = "=" * 72
    print(bar)
    print(f"  GOVERNANCE AUDIT REPORT — {report.system_id}")
    print(bar)
    print(f"  Score         : {report.score}/100")
    print(f"  Maturity      : {report.maturity_level}")
    print(f"  Total Controls: {report.total_controls}")
    print(f"  Passed        : {report.passed}")
    print(f"  Failed        : {report.failed}")
    print(f"  Warned        : {report.warned}")
    print()

    print("  Domain Summary:")
    for domain, stats in report.domain_summary.items():
        print(
            f"    {domain:<35} "
            f"pass={stats['pass']:2d}  fail={stats['fail']:2d}  "
            f"total={stats['total']:2d}"
        )
    print()

    critical_fails = report.critical_failures()
    high_fails = report.high_failures()

    if critical_fails:
        print(f"  CRITICAL Failures ({len(critical_fails)}):")
        for f in critical_fails:
            print(f"    [{f.control_id}] {f.control_name}")
            print(f"      Refs     : {', '.join(f.framework_refs)}")
            print(f"      Remediate: {f.remediation_step[:100]}...")
        print()

    if high_fails:
        print(f"  HIGH Failures ({len(high_fails)}):")
        for f in high_fails:
            print(f"    [{f.control_id}] {f.control_name}")
        print()

    medium_fails = [f for f in report.findings if f.status == "FAIL" and f.severity == "MEDIUM"]
    if medium_fails:
        print(f"  MEDIUM Failures ({len(medium_fails)}):")
        for f in medium_fails:
            print(f"    [{f.control_id}] {f.control_name}")
        print()

    print(bar)
    print()


# ---------------------------------------------------------------------------
# Entry point — three demonstration configurations
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    auditor = GovernanceFrameworkAuditor()

    # ------------------------------------------------------------------
    # Config 1 — Minimal Governance
    # All controls absent; represents a newly deployed AI system with no
    # formal governance programme.  Expected: very low score, INITIAL maturity.
    # ------------------------------------------------------------------
    minimal_config = GovernanceFrameworkConfig(
        system_id="minimal-governance-system",
        # All fields default to False
    )
    minimal_report = auditor.audit(minimal_config)
    print("\n--- Demo 1: Minimal Governance (no controls implemented) ---\n")
    _print_report(minimal_report)

    # ------------------------------------------------------------------
    # Config 2 — Partial Governance
    # Core NIST and ISO policy controls plus basic OWASP LLM security
    # implemented.  Agentic controls, MITRE ATLAS, and CSA ATF largely
    # absent.  Expected: mid-range score, DEFINED or DEVELOPING maturity.
    # ------------------------------------------------------------------
    partial_config = GovernanceFrameworkConfig(
        system_id="partial-governance-system",
        # OWASP LLM — basic security controls
        owasp_llm_prompt_injection_controls=True,
        owasp_llm_sensitive_info_controls=True,
        owasp_llm_data_poisoning_controls=True,
        # NIST RMF — governance and management in place
        nist_govern_function_implemented=True,
        nist_map_function_implemented=True,
        nist_manage_function_implemented=True,
        # ISO 42001 — policy and risk assessment defined
        iso_ai_policy_defined=True,
        iso_ai_risk_assessment=True,
        iso_ai_documented_info=True,
        # MITRE ATLAS — prompt injection detection only
        mitre_prompt_injection_detection=True,
        # CSA ATF — sandbox and controlled deployment
        csa_atf_sandbox_controls=True,
        csa_atf_controlled_controls=True,
    )
    partial_report = auditor.audit(partial_config)
    print("--- Demo 2: Partial Governance (core controls, gaps in agentic/ATF) ---\n")
    _print_report(partial_report)

    # ------------------------------------------------------------------
    # Config 3 — Comprehensive Governance
    # All 49 controls implemented.  Represents a mature enterprise AI
    # governance programme targeting ISO 42001 certification with full
    # OWASP, NIST, ATLAS, and CSA ATF alignment.
    # Expected: 100/100 score, OPTIMIZING maturity, zero failures.
    # ------------------------------------------------------------------
    comprehensive_config = GovernanceFrameworkConfig(
        system_id="comprehensive-governance-system",
        # OWASP LLM Top 10 2025 — all controls
        owasp_llm_prompt_injection_controls=True,
        owasp_llm_insecure_output_handling=True,
        owasp_llm_supply_chain_controls=True,
        owasp_llm_data_poisoning_controls=True,
        owasp_llm_sensitive_info_controls=True,
        owasp_llm_vector_weakness_controls=True,
        owasp_llm_misinformation_controls=True,
        owasp_llm_unlimited_consumption_controls=True,
        # OWASP Agentic AI Top 10 2026 — all controls
        owasp_asi_goal_hijack_controls=True,
        owasp_asi_tool_misuse_controls=True,
        owasp_asi_memory_poisoning_controls=True,
        owasp_asi_trust_boundary_controls=True,
        # NIST AI RMF + AI 600-1 — all functions
        nist_map_function_implemented=True,
        nist_measure_function_implemented=True,
        nist_manage_function_implemented=True,
        nist_govern_function_implemented=True,
        nist_genai_testing_implemented=True,
        # ISO/IEC 42001:2023 — all clauses
        iso_ai_policy_defined=True,
        iso_ai_risk_assessment=True,
        iso_ai_objectives_set=True,
        iso_ai_competence_managed=True,
        iso_ai_documented_info=True,
        iso_ai_operational_controls=True,
        iso_ai_monitoring=True,
        iso_ai_internal_audit=True,
        iso_ai_management_review=True,
        # MITRE ATLAS v5.1 — all techniques
        mitre_recon_detection=True,
        mitre_poisoning_detection=True,
        mitre_extraction_controls=True,
        mitre_prompt_injection_detection=True,
        mitre_tool_invocation_controls=True,
        mitre_rag_db_controls=True,
        # CSA Agentic Trust Framework — all levels
        csa_atf_sandbox_controls=True,
        csa_atf_controlled_controls=True,
        csa_atf_trusted_controls=True,
        csa_atf_autonomous_controls=True,
        csa_atf_continuous_assessment=True,
    )
    comprehensive_report = auditor.audit(comprehensive_config)
    print("--- Demo 3: Comprehensive Governance (all 49 controls implemented) ---\n")
    _print_report(comprehensive_report)
