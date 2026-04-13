"""
41_trilogy_security_audit.py — Trilogy Enterprise AI Security Audit Orchestrator

Implements a unified enterprise AI security assessment that orchestrates three
independent security auditors — RAG, Agentic, and Governance — into one
combined Trilogy audit report.  The orchestrator runs all three stub auditors
in sequence, correlates their findings to surface cross-module gaps, and
produces a single scored, maturity-levelled report covering the full
enterprise AI stack.

Overview
--------
Each layer of a modern enterprise AI deployment has its own threat surface:

  Layer 1  — RAG (Retrieval-Augmented Generation)
             Prompt injection through the retrieval pipeline, vector-store
             namespace leakage, DLP failures on generated output, absence of
             action gating for agentic RAG.  The full implementation lives in
             ``enterprise-rag-patterns/examples/50_rag_security_auditor.py``.

  Layer 2  — Agentic AI
             Tool permission gaps, MCP server trust, agent identity and
             privilege escalation, multi-agent trust boundaries, and
             human-in-the-loop oversight.  The full implementation lives in
             ``integration-automation-patterns/examples/43_agentic_security_auditor.py``.

  Layer 3  — Governance Frameworks
             OWASP LLM Top 10 2025, OWASP Agentic AI Top 10 2026, NIST AI RMF,
             ISO/IEC 42001:2023, MITRE ATLAS v5.1, CSA Agentic Trust Framework.
             The full implementation lives in
             ``regulated-ai-governance/examples/40_governance_framework_auditor.py``
             (sibling file in this directory).

Cross-module gap detection
--------------------------
This orchestrator introduces seven cross-gap correlation rules (XG-001 through
XG-007) that can only be discovered by comparing findings *across* layers.
A gap that appears at a single layer is surfaced by the individual auditor;
a cross-gap appears only when two or three layers are examined together:

  XG-001 — Injection Defense Inconsistency        CRITICAL
  XG-002 — Data Exfiltration Gap                  CRITICAL
  XG-003 — Action Authorization Inconsistency     HIGH
  XG-004 — Audit Trail Gap                        HIGH
  XG-005 — Trust Boundary Policy Mismatch         HIGH
  XG-006 — Identity Without Governance            HIGH
  XG-007 — HITL Gap Across Layers                 CRITICAL

Scoring model
-------------
Each internal stub auditor applies the same deduction model:
  CRITICAL control failing: −15 points from 100-point baseline
  HIGH control failing:     −7 points
  MEDIUM control failing:   −3 points
  Score floor: 0

Combined score = rag_score × 0.35 + agent_score × 0.35 + gov_score × 0.30

Maturity thresholds (all three auditors share this scale)
----------------------------------------------------------
  Sandbox    — any CRITICAL failure, OR score < 50
  Controlled — no CRITICAL failures; score 50–69
  Trusted    — no CRITICAL failures; score 70–84
  Autonomous — no CRITICAL failures; score ≥ 85

Combined maturity = minimum of the three individual maturity levels.
Minimum ordering: Sandbox < Controlled < Trusted < Autonomous

Loading the full auditors at runtime (optional)
-----------------------------------------------
If the full auditor implementations are available on disk, they can be loaded
at runtime using ``importlib.util``.  Example::

    import importlib.util, pathlib

    def _load_module(path: str, name: str):
        spec = importlib.util.spec_from_file_location(name, path)
        mod  = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    rag_mod = _load_module(
        "/tmp/oss_work/enterprise-rag-patterns/examples/50_rag_security_auditor.py",
        "rag_security_auditor",
    )
    agent_mod = _load_module(
        "/tmp/oss_work/integration-automation-patterns/examples/43_agentic_security_auditor.py",
        "agentic_security_auditor",
    )
    gov_mod = _load_module(
        "40_governance_framework_auditor.py",
        "governance_framework_auditor",
    )

    # Then build native configs from TrilogySystemProfile fields and delegate:
    rag_report   = rag_mod.RAGSecurityAuditor().audit(...)
    agent_report = agent_mod.AgenticSecurityAuditor().audit(...)
    gov_report   = gov_mod.GovernanceFrameworkAuditor().audit(...)

This file is self-contained and uses only the Python standard library.  All
three auditors are re-implemented inline as lightweight stubs sufficient to
produce accurate scores, maturity levels, and CRITICAL counts from the fields
on ``TrilogySystemProfile``.

No external dependencies required.

Run::
    python examples/41_trilogy_security_audit.py
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import NamedTuple


# ---------------------------------------------------------------------------
# TrilogySystemProfile
# ---------------------------------------------------------------------------


@dataclass
class TrilogySystemProfile:
    """
    Combined system profile covering all three audit dimensions: RAG security,
    agentic AI security, and governance framework compliance.

    Fields are prefixed with their layer:
      ``rag_``  — RAG pipeline security controls
      ``agent_``— agentic AI runtime controls
      ``gov_``  — governance framework controls

    A value of ``True`` means the corresponding control is implemented and
    operational.  ``False`` means it is absent or unverified; the relevant
    stub auditor will raise a finding.

    Attributes
    ----------
    system_id : str
        Human-readable identifier for the enterprise AI system under audit.

    RAG layer controls (rag_*)
    --------------------------
    rag_query_injection_detection_enabled : bool
        Prompt injection detection layer active on all incoming RAG queries
        before they reach the vector store or LLM context window.
        Ref: OWASP LLM01 2025, MITRE ATLAS T0051
    rag_namespace_isolation_enforced : bool
        Vector store namespace isolation enforced so that retrieval cannot
        traverse tenant or classification boundaries.
        Ref: OWASP LLM08, FERPA §99.31
    rag_cross_tenant_isolation : bool
        Retrieval layer enforces cross-tenant data isolation; users cannot
        retrieve documents belonging to other tenants.
        Ref: SOC 2 CC6.1
    rag_dlp_scan_on_output : bool
        DLP scanning applied to LLM output before delivery; PII, credentials,
        and PHI are detected and redacted.
        Ref: OWASP LLM06 2025, GDPR Art.32
    rag_action_gating_enabled : bool
        Tool calls and code execution by agentic RAG are gated; allowlist
        enforced and irreversible actions require explicit approval.
        Ref: OWASP ASI02, NIST AI 600-1
    rag_query_logging_enabled : bool
        All queries logged with sufficient retention for forensic review.
        Ref: SOC 2 CC7.2, HIPAA §164.312(b)
    rag_vector_store_access_control : bool
        Access controls on the vector store enforce read/write permissions.
        Ref: NIST CSF PR.AC-3
    rag_document_integrity_checksums : bool
        Document integrity checksums verified on ingestion and retrieval to
        detect tampered or poisoned chunks.
        Ref: OWASP LLM08, MITRE ATLAS T0054
    rag_pre_filter_placement : str
        Indicates filter placement relative to ANN retrieval.
        ``"pre"`` — filters run before ANN (recommended).
        ``"post"`` — filters run after ANN (weaker).
        ``"none"`` — no filters (failing control).
    rag_output_schema_validation : bool
        LLM output validated against expected schema before delivery.
        Ref: OWASP LLM02
    rag_hallucination_detection_enabled : bool
        Hallucination and misinformation detection active on generated output.
        Ref: OWASP LLM09, ISO 42001 Cl.9.1
    rag_retrieval_audit_logging : bool
        Retrieval events (chunk ID, score, namespace, timestamp) logged for
        every query to support end-to-end audit trails.
        Ref: ISO 42001 Cl.9.1, NIST CSF DE.AE-1

    Agentic layer controls (agent_*)
    ---------------------------------
    agent_tool_permission_model : str
        Tool permission model active for the agent runtime.
        ``"allowlist"`` — explicit allowlist enforced.
        ``"jit"``       — just-in-time capability grant.
        ``"rbac"``      — role-based tool access control.
        ``"none"``      — no permission model (failing control).
    agent_unsafe_tool_calls_blocked : bool
        Known-dangerous tool invocations rejected at the runtime boundary.
        Ref: OWASP ASI02, MITRE ATLAS T0060
    agent_agent_identity_enforced : bool
        Each agent presents a verified identity credential before execution.
        Ref: OWASP ASI08
    agent_privilege_escalation_prevented : bool
        Agents cannot acquire permissions beyond those granted at
        instantiation; privilege escalation vectors are blocked.
        Ref: OWASP ASI08
    agent_prompt_context_sanitized : bool
        Retrieved content scrubbed for injection payloads before insertion
        into agent prompts.
        Ref: OWASP ASI03, MITRE ATLAS T0051
    agent_mcp_enabled : bool
        Whether the agent runtime exposes Model Context Protocol (MCP).
        When ``True``, MCP security controls are evaluated.
    agent_mcp_source_allowlisted : bool
        MCP servers drawn from an explicit origin allowlist.
        Evaluated only when ``agent_mcp_enabled`` is ``True``.
        Ref: CVE-2025-6514 class MCP tampering
    agent_hitl_for_high_risk_actions : bool
        Human approval gate required before irreversible or high-impact
        actions are executed by the agent.
        Ref: NIST AI 600-1, CSA ATF Level 2
    agent_multi_agent_enabled : bool
        Whether multi-agent pipelines are deployed.  When ``True``,
        multi-agent security controls are evaluated.
    agent_agent_trust_boundaries_defined : bool
        Each agent's authority scope declared and enforced.
        Evaluated only when ``agent_multi_agent_enabled`` is ``True``.
        Ref: OWASP ASI10
    agent_tool_invocation_logging : bool
        Every tool invocation written to a structured, immutable log.
        Ref: SOC 2 CC7.2, ISO 42001 Cl.9.1

    Governance layer controls (gov_*)
    ----------------------------------
    gov_owasp_llm_prompt_injection_controls : bool
        LLM01 — prompt injection detection and prevention active.
        Ref: OWASP LLM Top 10 2025
    gov_owasp_llm_sensitive_info_controls : bool
        LLM06 — DLP scanning, output filtering, and RAG access controls
        preventing sensitive information disclosure.
        Ref: OWASP LLM Top 10 2025
    gov_owasp_llm_data_poisoning_controls : bool
        LLM04 — training data integrity and anomaly detection controls.
        Ref: OWASP LLM Top 10 2025
    gov_owasp_asi_goal_hijack_controls : bool
        ASI01 — indirect prompt injection detection for all external inputs
        routed into agent context.
        Ref: OWASP Agentic AI Top 10 2026
    gov_owasp_asi_tool_misuse_controls : bool
        ASI02 — tool allowlist enforcement and invocation approval gates.
        Ref: OWASP Agentic AI Top 10 2026
    gov_nist_govern_function_implemented : bool
        GOVERN — AI governance structure, roles, accountability, policies,
        and oversight mechanisms formally established.
        Ref: NIST AI RMF
    gov_iso_ai_policy_defined : bool
        Cl.5.2 — formal AI policy documented and approved by top management.
        Ref: ISO/IEC 42001:2023
    gov_iso_ai_risk_assessment : bool
        Cl.6.1 — AI-specific risk assessment process defined and executed.
        Ref: ISO/IEC 42001:2023
    gov_mitre_prompt_injection_detection : bool
        T0051 — prompt injection detection controls aligned to MITRE ATLAS.
        Ref: MITRE ATLAS v5.1
    gov_mitre_poisoning_detection : bool
        T0020 — training data poisoning detection controls.
        Ref: MITRE ATLAS v5.1
    gov_csa_atf_sandbox_controls : bool
        CSA ATF Level 1 — sandbox isolation controls in place before any
        deployment to production or pilot environments.
        Ref: CSA Agentic Trust Framework
    gov_csa_atf_continuous_assessment : bool
        CSA ATF Level 5 — continuous trust assessment pipeline operational.
        Ref: CSA Agentic Trust Framework
    """

    system_id: str = "enterprise-ai-system"

    # ------------------------------------------------------------------
    # RAG layer controls
    # ------------------------------------------------------------------
    rag_query_injection_detection_enabled: bool = False
    rag_namespace_isolation_enforced: bool = False
    rag_cross_tenant_isolation: bool = False
    rag_dlp_scan_on_output: bool = False
    rag_action_gating_enabled: bool = False
    rag_query_logging_enabled: bool = False
    rag_vector_store_access_control: bool = False
    rag_document_integrity_checksums: bool = False
    rag_pre_filter_placement: str = "none"
    rag_output_schema_validation: bool = False
    rag_hallucination_detection_enabled: bool = False
    rag_retrieval_audit_logging: bool = False

    # ------------------------------------------------------------------
    # Agentic layer controls
    # ------------------------------------------------------------------
    agent_tool_permission_model: str = "none"
    agent_unsafe_tool_calls_blocked: bool = False
    agent_agent_identity_enforced: bool = False
    agent_privilege_escalation_prevented: bool = False
    agent_prompt_context_sanitized: bool = False
    agent_mcp_enabled: bool = False
    agent_mcp_source_allowlisted: bool = False
    agent_hitl_for_high_risk_actions: bool = False
    agent_multi_agent_enabled: bool = False
    agent_agent_trust_boundaries_defined: bool = False
    agent_tool_invocation_logging: bool = False

    # ------------------------------------------------------------------
    # Governance layer controls
    # ------------------------------------------------------------------
    gov_owasp_llm_prompt_injection_controls: bool = False
    gov_owasp_llm_sensitive_info_controls: bool = False
    gov_owasp_llm_data_poisoning_controls: bool = False
    gov_owasp_asi_goal_hijack_controls: bool = False
    gov_owasp_asi_tool_misuse_controls: bool = False
    gov_nist_govern_function_implemented: bool = False
    gov_iso_ai_policy_defined: bool = False
    gov_iso_ai_risk_assessment: bool = False
    gov_mitre_prompt_injection_detection: bool = False
    gov_mitre_poisoning_detection: bool = False
    gov_csa_atf_sandbox_controls: bool = False
    gov_csa_atf_continuous_assessment: bool = False


# ---------------------------------------------------------------------------
# TrilogyCrossGap
# ---------------------------------------------------------------------------


@dataclass
class TrilogyCrossGap:
    """
    A gap identified by correlating findings *across* two or more auditors.

    Cross-gaps cannot be detected by any single auditor in isolation; they
    emerge only when the combined state of multiple layers is examined.

    Attributes
    ----------
    gap_id : str
        Short identifier, e.g. ``"XG-001"``.
    title : str
        Human-readable gap title, e.g. ``"Injection Defense Inconsistency"``.
    description : str
        Detailed explanation of why this combination of control states
        creates a security exposure.
    affected_auditors : list[str]
        Names of the auditor layers implicated, e.g.
        ``["RAG", "Governance"]``.
    severity : str
        ``"CRITICAL"``, ``"HIGH"``, or ``"MEDIUM"``.
    remediation : str
        Specific, actionable remediation guidance.
    """

    gap_id: str
    title: str
    description: str
    affected_auditors: list[str]
    severity: str
    remediation: str


# ---------------------------------------------------------------------------
# TrilogyAuditResult
# ---------------------------------------------------------------------------


@dataclass
class TrilogyAuditResult:
    """
    Aggregated result from a full Trilogy audit run.

    Combines per-layer scores, maturity levels, and CRITICAL counts with
    cross-module gap findings and an overall combined assessment.

    Attributes
    ----------
    system_id : str
        Identifier of the audited system.
    rag_score : float
        RAG layer security score (0–100).
    agent_score : float
        Agentic layer security score (0–100).
    governance_score : float
        Governance framework compliance score (0–100).
    combined_score : float
        Weighted combined score:
        ``rag_score × 0.35 + agent_score × 0.35 + governance_score × 0.30``.
    rag_maturity : str
        Maturity level for the RAG layer.
    agent_maturity : str
        Maturity level for the agentic layer.
    governance_maturity : str
        Maturity level for the governance layer.
    combined_maturity : str
        Minimum of the three individual maturity levels.
        Order: Sandbox < Controlled < Trusted < Autonomous.
    cross_gaps : list[TrilogyCrossGap]
        Cross-module gaps detected by the orchestrator.
    rag_critical_count : int
        Number of CRITICAL control failures in the RAG layer.
    agent_critical_count : int
        Number of CRITICAL control failures in the agentic layer.
    gov_critical_count : int
        Number of CRITICAL control failures in the governance layer.
    """

    system_id: str
    rag_score: float
    agent_score: float
    governance_score: float
    combined_score: float
    rag_maturity: str
    agent_maturity: str
    governance_maturity: str
    combined_maturity: str
    cross_gaps: list[TrilogyCrossGap]
    rag_critical_count: int
    agent_critical_count: int
    gov_critical_count: int

    def summary(self) -> str:
        """
        Render a formatted console summary of the Trilogy audit result.

        The output is a fixed-width box displaying the combined score,
        combined maturity, a per-auditor breakdown table, and the full
        list of cross-module gaps with remediation guidance.

        Returns
        -------
        str
            Multi-line string suitable for printing directly to stdout.
        """
        width = 66
        border = "═" * width

        def pad(text: str, w: int = width - 2) -> str:
            """Left-align *text* inside a box row of total width *w* + 2."""
            return f"║  {text:<{w - 2}}║"

        lines: list[str] = []
        lines.append(f"╔{border}╗")
        lines.append(pad("TRILOGY ENTERPRISE AI SECURITY AUDIT REPORT", width - 2))
        lines.append(f"╠{border}╣")
        lines.append(pad(f"System: {self.system_id}"))
        lines.append(pad(f"Combined Score: {self.combined_score:.1f} / 100.0"))
        lines.append(pad(f"Combined Maturity: {self.combined_maturity}"))
        lines.append(f"╠{border}╣")
        lines.append(pad("AUDITOR BREAKDOWN"))

        # Table header
        col_w = [13, 7, 13, 10]
        h0 = f"{'Auditor':<{col_w[0]}}"
        h1 = f"{'Score':>{col_w[1]}}"
        h2 = f"{'Maturity':<{col_w[2]}}"
        h3 = f"{'Critical':<{col_w[3]}}"
        sep_row = (
            f"  ┌{'─' * col_w[0]}┬{'─' * col_w[1]}┬{'─' * col_w[2]}┬{'─' * col_w[3]}┐"
        )
        hdr_row = f"  │{h0}│{h1}│ {h2}│ {h3}│"
        mid_sep = (
            f"  ├{'─' * col_w[0]}┼{'─' * col_w[1]}┼{'─' * col_w[2]}┼{'─' * col_w[3]}┤"
        )
        end_sep = (
            f"  └{'─' * col_w[0]}┴{'─' * col_w[1]}┴{'─' * col_w[2]}┴{'─' * col_w[3]}┘"
        )
        lines.append(f"║{sep_row:<{width}}║")
        lines.append(f"║{hdr_row:<{width}}║")
        lines.append(f"║{mid_sep:<{width}}║")

        rows = [
            ("RAG", self.rag_score, self.rag_maturity, self.rag_critical_count),
            ("Agent", self.agent_score, self.agent_maturity, self.agent_critical_count),
            ("Governance", self.governance_score, self.governance_maturity, self.gov_critical_count),
        ]
        for name, score, mat, crit in rows:
            c0 = f"{name:<{col_w[0]}}"
            c1 = f"{score:>{col_w[1]}.1f}"
            c2 = f"{mat:<{col_w[2]}}"
            c3 = f"{crit:<{col_w[3]}}"
            data_row = f"  │{c0}│{c1}│ {c2}│ {c3}│"
            lines.append(f"║{data_row:<{width}}║")

        lines.append(f"║{end_sep:<{width}}║")
        lines.append(f"╠{border}╣")

        # Cross-gaps section
        gap_header = f"CROSS-MODULE GAPS ({len(self.cross_gaps)} found)"
        lines.append(pad(gap_header))
        if not self.cross_gaps:
            lines.append(pad("No cross-module gaps detected."))
        else:
            for gap in self.cross_gaps:
                lines.append(pad(f"[{gap.severity}] {gap.gap_id} {gap.title}"))
                affected = ", ".join(gap.affected_auditors)
                lines.append(pad(f"         Affected: {affected}"))
                # Word-wrap remediation to 58 chars
                rem = gap.remediation
                prefix = "         Fix: "
                max_rem = width - 6 - len(prefix)
                if len(rem) <= max_rem:
                    lines.append(pad(f"{prefix}{rem}"))
                else:
                    words = rem.split()
                    line_buf: list[str] = []
                    first = True
                    for word in words:
                        test = " ".join(line_buf + [word])
                        if len(test) <= max_rem:
                            line_buf.append(word)
                        else:
                            pfx = prefix if first else " " * len(prefix)
                            lines.append(pad(f"{pfx}{' '.join(line_buf)}"))
                            line_buf = [word]
                            first = False
                    if line_buf:
                        pfx = prefix if first else " " * len(prefix)
                        lines.append(pad(f"{pfx}{' '.join(line_buf)}"))

        lines.append(f"╚{border}╝")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Internal scoring helpers
# ---------------------------------------------------------------------------

#: Ordered maturity levels from weakest to strongest.
_MATURITY_ORDER = ("Sandbox", "Controlled", "Trusted", "Autonomous")


def _maturity_from_score(score: float, critical_count: int) -> str:
    """
    Derive a maturity label from a numeric score and CRITICAL failure count.

    Parameters
    ----------
    score : float
        Security score in the range 0–100.
    critical_count : int
        Number of CRITICAL-severity controls that failed.

    Returns
    -------
    str
        One of ``"Sandbox"``, ``"Controlled"``, ``"Trusted"``,
        ``"Autonomous"``.
    """
    if critical_count > 0 or score < 50:
        return "Sandbox"
    if score < 70:
        return "Controlled"
    if score < 85:
        return "Trusted"
    return "Autonomous"


def _minimum_maturity(*levels: str) -> str:
    """
    Return the minimum (weakest) maturity level from a collection.

    Parameters
    ----------
    *levels : str
        Maturity level strings; each must be one of the values in
        ``_MATURITY_ORDER``.

    Returns
    -------
    str
        The weakest maturity level present in *levels*.
    """
    indices = [_MATURITY_ORDER.index(lv) for lv in levels]
    return _MATURITY_ORDER[min(indices)]


def _floor(score: float) -> float:
    """Clamp *score* to the range [0, 100]."""
    return max(0.0, min(100.0, score))


# ---------------------------------------------------------------------------
# _StubRAGResult / _StubAgentResult / _StubGovResult  (internal named tuples)
# ---------------------------------------------------------------------------


class _StubRAGResult(NamedTuple):
    score: float
    maturity: str
    critical_count: int


class _StubAgentResult(NamedTuple):
    score: float
    maturity: str
    critical_count: int


class _StubGovResult(NamedTuple):
    score: float
    maturity: str
    critical_count: int


# ---------------------------------------------------------------------------
# StubRAGAuditor
# ---------------------------------------------------------------------------


class StubRAGAuditor:
    """
    Lightweight inline stub of the RAG security auditor.

    Evaluates 12 RAG-layer controls drawn from the fields of a
    ``TrilogySystemProfile`` that are prefixed ``rag_``.  The full
    implementation with detailed per-control findings is in
    ``enterprise-rag-patterns/examples/50_rag_security_auditor.py``; this
    stub produces an identical numeric score and maturity label without
    requiring that repository to be present.

    Scoring model
    -------------
    Starts at 100.  Each failing control deducts points based on severity:

    +---------------------------------------------------------+-----------+
    | Control                                                 | Severity  |
    +=========================================================+===========+
    | rag_query_injection_detection_enabled (False)           | CRITICAL  |
    | rag_cross_tenant_isolation (False)                      | CRITICAL  |
    | rag_dlp_scan_on_output (False)                          | CRITICAL  |
    | rag_action_gating_enabled (False)                       | CRITICAL  |
    | rag_namespace_isolation_enforced (False)                | HIGH      |
    | rag_vector_store_access_control (False)                 | HIGH      |
    | rag_document_integrity_checksums (False)                | HIGH      |
    | rag_pre_filter_placement != "pre"                       | HIGH      |
    | rag_output_schema_validation (False)                    | HIGH      |
    | rag_retrieval_audit_logging (False)                     | HIGH      |
    | rag_query_logging_enabled (False)                       | MEDIUM    |
    | rag_hallucination_detection_enabled (False)             | MEDIUM    |
    +---------------------------------------------------------+-----------+
    """

    def audit(self, profile: TrilogySystemProfile) -> _StubRAGResult:
        """
        Run the RAG stub audit against *profile*.

        Parameters
        ----------
        profile : TrilogySystemProfile
            Combined system profile; only ``rag_*`` fields are read.

        Returns
        -------
        _StubRAGResult
            Named tuple containing ``score``, ``maturity``, and
            ``critical_count``.
        """
        score = 100.0
        critical_count = 0

        # CRITICAL controls
        if not profile.rag_query_injection_detection_enabled:
            score -= 15
            critical_count += 1
        if not profile.rag_cross_tenant_isolation:
            score -= 15
            critical_count += 1
        if not profile.rag_dlp_scan_on_output:
            score -= 15
            critical_count += 1
        if not profile.rag_action_gating_enabled:
            score -= 15
            critical_count += 1

        # HIGH controls
        if not profile.rag_namespace_isolation_enforced:
            score -= 7
        if not profile.rag_vector_store_access_control:
            score -= 7
        if not profile.rag_document_integrity_checksums:
            score -= 7
        if profile.rag_pre_filter_placement != "pre":
            score -= 7
        if not profile.rag_output_schema_validation:
            score -= 7
        if not profile.rag_retrieval_audit_logging:
            score -= 7

        # MEDIUM controls
        if not profile.rag_query_logging_enabled:
            score -= 3
        if not profile.rag_hallucination_detection_enabled:
            score -= 3

        score = _floor(score)
        maturity = _maturity_from_score(score, critical_count)
        return _StubRAGResult(score=score, maturity=maturity, critical_count=critical_count)


# ---------------------------------------------------------------------------
# StubAgentAuditor
# ---------------------------------------------------------------------------


class StubAgentAuditor:
    """
    Lightweight inline stub of the agentic AI security auditor.

    Evaluates up to 10 agentic-layer controls from the ``agent_*`` fields of a
    ``TrilogySystemProfile``.  MCP controls are evaluated only when
    ``agent_mcp_enabled`` is ``True``; multi-agent controls are evaluated only
    when ``agent_multi_agent_enabled`` is ``True``.  The full implementation
    with detailed per-control findings is in
    ``integration-automation-patterns/examples/43_agentic_security_auditor.py``.

    Scoring model
    -------------
    Starts at 100.  Each failing control deducts points based on severity:

    +---------------------------------------------------------+-----------+
    | Control                                                 | Severity  |
    +=========================================================+===========+
    | agent_tool_permission_model == "none"                   | CRITICAL  |
    | agent_unsafe_tool_calls_blocked (False)                 | CRITICAL  |
    | agent_privilege_escalation_prevented (False)            | CRITICAL  |
    | agent_hitl_for_high_risk_actions (False)                | CRITICAL  |
    | agent_agent_identity_enforced (False)                   | HIGH      |
    | agent_prompt_context_sanitized (False)                  | HIGH      |
    | agent_mcp_source_allowlisted (False) [if MCP enabled]   | HIGH      |
    | agent_agent_trust_boundaries_defined [if MA enabled]    | HIGH      |
    | agent_tool_invocation_logging (False)                   | MEDIUM    |
    +---------------------------------------------------------+-----------+
    """

    def audit(self, profile: TrilogySystemProfile) -> _StubAgentResult:
        """
        Run the agentic stub audit against *profile*.

        Parameters
        ----------
        profile : TrilogySystemProfile
            Combined system profile; only ``agent_*`` fields are read.

        Returns
        -------
        _StubAgentResult
            Named tuple containing ``score``, ``maturity``, and
            ``critical_count``.
        """
        score = 100.0
        critical_count = 0

        # CRITICAL controls
        if profile.agent_tool_permission_model == "none":
            score -= 15
            critical_count += 1
        if not profile.agent_unsafe_tool_calls_blocked:
            score -= 15
            critical_count += 1
        if not profile.agent_privilege_escalation_prevented:
            score -= 15
            critical_count += 1
        if not profile.agent_hitl_for_high_risk_actions:
            score -= 15
            critical_count += 1

        # HIGH controls
        if not profile.agent_agent_identity_enforced:
            score -= 7
        if not profile.agent_prompt_context_sanitized:
            score -= 7
        if profile.agent_mcp_enabled and not profile.agent_mcp_source_allowlisted:
            score -= 7
        if profile.agent_multi_agent_enabled and not profile.agent_agent_trust_boundaries_defined:
            score -= 7

        # MEDIUM controls
        if not profile.agent_tool_invocation_logging:
            score -= 3

        score = _floor(score)
        maturity = _maturity_from_score(score, critical_count)
        return _StubAgentResult(score=score, maturity=maturity, critical_count=critical_count)


# ---------------------------------------------------------------------------
# StubGovernanceAuditor
# ---------------------------------------------------------------------------


class StubGovernanceAuditor:
    """
    Lightweight inline stub of the governance framework auditor.

    Evaluates 12 governance-layer controls from the ``gov_*`` fields of a
    ``TrilogySystemProfile``, covering OWASP LLM Top 10 2025, OWASP Agentic AI
    Top 10 2026, NIST AI RMF, ISO/IEC 42001:2023, MITRE ATLAS v5.1, and CSA
    Agentic Trust Framework.  The full implementation with 37 controls across
    all six framework domains is in
    ``regulated-ai-governance/examples/40_governance_framework_auditor.py``
    (the sibling file in this directory).

    Scoring model
    -------------
    Starts at 100.  Each failing control deducts points based on severity:

    +---------------------------------------------------------+-----------+
    | Control                                                 | Severity  |
    +=========================================================+===========+
    | gov_owasp_llm_prompt_injection_controls (False)         | CRITICAL  |
    | gov_owasp_llm_data_poisoning_controls (False)           | CRITICAL  |
    | gov_owasp_asi_goal_hijack_controls (False)              | CRITICAL  |
    | gov_owasp_llm_sensitive_info_controls (False)           | HIGH      |
    | gov_owasp_asi_tool_misuse_controls (False)              | HIGH      |
    | gov_nist_govern_function_implemented (False)            | HIGH      |
    | gov_iso_ai_policy_defined (False)                       | HIGH      |
    | gov_iso_ai_risk_assessment (False)                      | HIGH      |
    | gov_mitre_prompt_injection_detection (False)            | HIGH      |
    | gov_mitre_poisoning_detection (False)                   | HIGH      |
    | gov_csa_atf_sandbox_controls (False)                    | MEDIUM    |
    | gov_csa_atf_continuous_assessment (False)               | MEDIUM    |
    +---------------------------------------------------------+-----------+
    """

    def audit(self, profile: TrilogySystemProfile) -> _StubGovResult:
        """
        Run the governance stub audit against *profile*.

        Parameters
        ----------
        profile : TrilogySystemProfile
            Combined system profile; only ``gov_*`` fields are read.

        Returns
        -------
        _StubGovResult
            Named tuple containing ``score``, ``maturity``, and
            ``critical_count``.
        """
        score = 100.0
        critical_count = 0

        # CRITICAL controls
        if not profile.gov_owasp_llm_prompt_injection_controls:
            score -= 15
            critical_count += 1
        if not profile.gov_owasp_llm_data_poisoning_controls:
            score -= 15
            critical_count += 1
        if not profile.gov_owasp_asi_goal_hijack_controls:
            score -= 15
            critical_count += 1

        # HIGH controls
        if not profile.gov_owasp_llm_sensitive_info_controls:
            score -= 7
        if not profile.gov_owasp_asi_tool_misuse_controls:
            score -= 7
        if not profile.gov_nist_govern_function_implemented:
            score -= 7
        if not profile.gov_iso_ai_policy_defined:
            score -= 7
        if not profile.gov_iso_ai_risk_assessment:
            score -= 7
        if not profile.gov_mitre_prompt_injection_detection:
            score -= 7
        if not profile.gov_mitre_poisoning_detection:
            score -= 7

        # MEDIUM controls
        if not profile.gov_csa_atf_sandbox_controls:
            score -= 3
        if not profile.gov_csa_atf_continuous_assessment:
            score -= 3

        score = _floor(score)
        maturity = _maturity_from_score(score, critical_count)
        return _StubGovResult(score=score, maturity=maturity, critical_count=critical_count)


# ---------------------------------------------------------------------------
# TrilogyAuditOrchestrator
# ---------------------------------------------------------------------------


class TrilogyAuditOrchestrator:
    """
    Orchestrator that runs all three stub auditors and correlates their
    findings into a unified Trilogy audit result.

    Usage::

        orchestrator = TrilogyAuditOrchestrator()
        profile = TrilogySystemProfile(
            system_id="my-enterprise-ai",
            rag_query_injection_detection_enabled=True,
            ...
        )
        result = orchestrator.audit(profile)
        print(result.summary())

    The orchestrator:

    1.  Runs ``StubRAGAuditor``, ``StubAgentAuditor``, and
        ``StubGovernanceAuditor`` independently against *profile*.
    2.  Computes ``combined_score = rag × 0.35 + agent × 0.35 + gov × 0.30``.
    3.  Derives ``combined_maturity`` as the minimum of the three individual
        maturity levels.
    4.  Runs the seven cross-gap correlation rules and collects all applicable
        ``TrilogyCrossGap`` objects.
    5.  Returns a fully populated ``TrilogyAuditResult``.
    """

    def __init__(self) -> None:
        self._rag_auditor = StubRAGAuditor()
        self._agent_auditor = StubAgentAuditor()
        self._gov_auditor = StubGovernanceAuditor()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def audit(self, profile: TrilogySystemProfile) -> TrilogyAuditResult:
        """
        Execute a full Trilogy audit against *profile*.

        Runs all three stub auditors, computes combined scoring, determines
        the combined maturity tier, and detects cross-module gaps.

        Parameters
        ----------
        profile : TrilogySystemProfile
            Fully configured system profile describing the security posture
            of the enterprise AI deployment under assessment.

        Returns
        -------
        TrilogyAuditResult
            Complete audit result including per-layer scores, maturity
            levels, and cross-module gap findings.
        """
        rag_result = self._rag_auditor.audit(profile)
        agent_result = self._agent_auditor.audit(profile)
        gov_result = self._gov_auditor.audit(profile)

        combined_score = _floor(
            rag_result.score * 0.35
            + agent_result.score * 0.35
            + gov_result.score * 0.30
        )

        combined_maturity = _minimum_maturity(
            rag_result.maturity,
            agent_result.maturity,
            gov_result.maturity,
        )

        cross_gaps = self._detect_cross_gaps(profile)

        return TrilogyAuditResult(
            system_id=profile.system_id,
            rag_score=rag_result.score,
            agent_score=agent_result.score,
            governance_score=gov_result.score,
            combined_score=combined_score,
            rag_maturity=rag_result.maturity,
            agent_maturity=agent_result.maturity,
            governance_maturity=gov_result.maturity,
            combined_maturity=combined_maturity,
            cross_gaps=cross_gaps,
            rag_critical_count=rag_result.critical_count,
            agent_critical_count=agent_result.critical_count,
            gov_critical_count=gov_result.critical_count,
        )

    # ------------------------------------------------------------------
    # Cross-gap correlation rules
    # ------------------------------------------------------------------

    def _detect_cross_gaps(self, p: TrilogySystemProfile) -> list[TrilogyCrossGap]:
        """
        Apply the seven cross-gap correlation rules to *p*.

        Each rule compares field values from two or three different audit
        layers.  A gap is emitted only when the specific combination of
        control states is present that the rule targets.

        Parameters
        ----------
        p : TrilogySystemProfile
            System profile to inspect.

        Returns
        -------
        list[TrilogyCrossGap]
            All cross-module gaps that apply to the profile.  May be empty
            if the system has consistent controls across all layers.
        """
        gaps: list[TrilogyCrossGap] = []

        # ------------------------------------------------------------------
        # XG-001 — Injection Defense Inconsistency  (CRITICAL)
        # Governance policy says injection controls are in place, but the
        # RAG layer has not implemented them — or vice versa.  Policy
        # compliance and runtime enforcement are out of sync.
        # ------------------------------------------------------------------
        rag_injection = p.rag_query_injection_detection_enabled
        gov_injection = p.gov_owasp_llm_prompt_injection_controls
        if rag_injection != gov_injection:
            if gov_injection and not rag_injection:
                desc = (
                    "Governance policy (gov_owasp_llm_prompt_injection_controls=True) "
                    "declares prompt injection controls as active, but the RAG layer "
                    "(rag_query_injection_detection_enabled=False) has not implemented "
                    "them.  Attackers can bypass governance-certified defenses by "
                    "targeting the RAG input path directly."
                )
                rem = (
                    "Enable query injection detection in the RAG pipeline to match "
                    "the governance policy declaration; align runtime controls to "
                    "the OWASP LLM01 and MITRE ATLAS T0051 countermeasures already "
                    "reflected in the governance framework."
                )
            else:
                desc = (
                    "The RAG layer has injection detection active "
                    "(rag_query_injection_detection_enabled=True) but the governance "
                    "framework does not record this control "
                    "(gov_owasp_llm_prompt_injection_controls=False).  The runtime "
                    "implementation is undocumented and unauditable; it may be "
                    "removed or misconfigured without triggering a governance alert."
                )
                rem = (
                    "Update the governance framework to formally document the RAG "
                    "injection detection control; ensure OWASP LLM01 compliance is "
                    "recorded in the AI policy and monitored in the continuous "
                    "assessment pipeline."
                )
            gaps.append(TrilogyCrossGap(
                gap_id="XG-001",
                title="Injection Defense Inconsistency",
                description=desc,
                affected_auditors=["RAG", "Governance"],
                severity="CRITICAL",
                remediation=rem,
            ))

        # ------------------------------------------------------------------
        # XG-002 — Data Exfiltration Gap  (CRITICAL)
        # Neither the RAG layer nor the governance framework is enforcing
        # DLP; sensitive data can flow undetected through generated output.
        # ------------------------------------------------------------------
        if not p.rag_dlp_scan_on_output and not p.gov_owasp_llm_sensitive_info_controls:
            gaps.append(TrilogyCrossGap(
                gap_id="XG-002",
                title="Data Exfiltration Gap",
                description=(
                    "Neither the RAG output layer (rag_dlp_scan_on_output=False) nor "
                    "the governance framework (gov_owasp_llm_sensitive_info_controls=False) "
                    "is enforcing data loss prevention.  PII, credentials, PHI, and "
                    "classified content can be exfiltrated through LLM-generated "
                    "responses without detection at any layer."
                ),
                affected_auditors=["RAG", "Governance"],
                severity="CRITICAL",
                remediation=(
                    "Enable DLP scanning on RAG output (rag_dlp_scan_on_output) and "
                    "implement OWASP LLM06 sensitive information controls in the "
                    "governance framework; deploy a DLP service that inspects generated "
                    "text for PII patterns, credential formats, and classification "
                    "markers before delivery to any consumer."
                ),
            ))

        # ------------------------------------------------------------------
        # XG-003 — Action Authorization Inconsistency  (HIGH)
        # No action gating in the RAG layer and no safe tool-call blocking in
        # the agent layer; agentic RAG can execute arbitrary actions.
        # ------------------------------------------------------------------
        if not p.agent_unsafe_tool_calls_blocked and not p.rag_action_gating_enabled:
            gaps.append(TrilogyCrossGap(
                gap_id="XG-003",
                title="Action Authorization Inconsistency",
                description=(
                    "The RAG layer provides no action gating "
                    "(rag_action_gating_enabled=False) and the agent runtime does not "
                    "block unsafe tool calls (agent_unsafe_tool_calls_blocked=False).  "
                    "There is no enforcement point preventing agentic RAG from "
                    "executing arbitrary, destructive, or irreversible tool invocations "
                    "in response to adversarial instructions."
                ),
                affected_auditors=["RAG", "Agent"],
                severity="HIGH",
                remediation=(
                    "Enable RAG action gating (rag_action_gating_enabled) to enforce "
                    "an allowlist at the RAG layer, and enable unsafe tool call "
                    "blocking (agent_unsafe_tool_calls_blocked) at the agent runtime; "
                    "require explicit approval for any tool call that is irreversible "
                    "or has blast radius beyond the session."
                ),
            ))

        # ------------------------------------------------------------------
        # XG-004 — Audit Trail Gap  (HIGH)
        # Neither RAG retrieval events nor agent tool invocations are logged;
        # end-to-end forensic investigation is impossible.
        # ------------------------------------------------------------------
        if not p.rag_retrieval_audit_logging and not p.agent_tool_invocation_logging:
            gaps.append(TrilogyCrossGap(
                gap_id="XG-004",
                title="Audit Trail Gap",
                description=(
                    "RAG retrieval events are not logged "
                    "(rag_retrieval_audit_logging=False) and agent tool invocations "
                    "are not logged (agent_tool_invocation_logging=False).  No "
                    "end-to-end audit trail exists; incident investigation, compliance "
                    "reporting, and forensic analysis of agentic RAG behaviour are "
                    "all impossible after the fact."
                ),
                affected_auditors=["RAG", "Agent"],
                severity="HIGH",
                remediation=(
                    "Enable retrieval audit logging (rag_retrieval_audit_logging) to "
                    "capture chunk IDs, scores, namespaces, and timestamps; enable "
                    "tool invocation logging (agent_tool_invocation_logging) to "
                    "capture every tool call with inputs and outputs; retain both "
                    "logs for at least 90 days per ISO 42001 Cl.9.1."
                ),
            ))

        # ------------------------------------------------------------------
        # XG-005 — Trust Boundary Policy Mismatch  (HIGH)
        # Multi-agent trust boundaries are undefined at the runtime layer,
        # and governance has not defined tool-misuse controls either.
        # ------------------------------------------------------------------
        if not p.agent_agent_trust_boundaries_defined and not p.gov_owasp_asi_tool_misuse_controls:
            gaps.append(TrilogyCrossGap(
                gap_id="XG-005",
                title="Trust Boundary Policy Mismatch",
                description=(
                    "Agent trust boundaries are not defined "
                    "(agent_agent_trust_boundaries_defined=False) and the governance "
                    "framework has not implemented tool-misuse controls "
                    "(gov_owasp_asi_tool_misuse_controls=False).  Multi-agent pipelines "
                    "can invoke any tool in any agent's scope without restriction; "
                    "cascading tool misuse across agent boundaries is undetectable."
                ),
                affected_auditors=["Agent", "Governance"],
                severity="HIGH",
                remediation=(
                    "Define explicit trust boundaries for each agent "
                    "(agent_agent_trust_boundaries_defined) limiting its authority "
                    "scope; implement OWASP ASI02 tool-misuse controls in the "
                    "governance framework to formally enforce capability-scoped "
                    "permissions and approval gates across multi-agent pipelines."
                ),
            ))

        # ------------------------------------------------------------------
        # XG-006 — Identity Without Governance  (HIGH)
        # Agent identity is enforced at the runtime layer but no formal AI
        # policy documents or governs this control; it is invisible to auditors.
        # ------------------------------------------------------------------
        if p.agent_agent_identity_enforced and not p.gov_iso_ai_policy_defined:
            gaps.append(TrilogyCrossGap(
                gap_id="XG-006",
                title="Identity Without Governance",
                description=(
                    "Agent identity enforcement is active "
                    "(agent_agent_identity_enforced=True) but no formal AI policy "
                    "has been documented (gov_iso_ai_policy_defined=False).  The "
                    "identity control exists only as an undocumented runtime "
                    "behaviour; it is not governed, auditable, or reproducible "
                    "across environments, and may be silently disabled without "
                    "triggering any compliance alert."
                ),
                affected_auditors=["Agent", "Governance"],
                severity="HIGH",
                remediation=(
                    "Document the agent identity enforcement control in a formal "
                    "AI policy per ISO 42001 Cl.5.2; define identity verification "
                    "requirements, credential rotation schedules, and audit "
                    "procedures; ensure the policy is approved by top management "
                    "and communicated to all relevant stakeholders."
                ),
            ))

        # ------------------------------------------------------------------
        # XG-007 — HITL Gap Across Layers  (CRITICAL)
        # No human-in-the-loop gate at the agent layer AND no action gating
        # at the RAG layer; high-risk actions have no human oversight at any
        # layer of the stack.
        # ------------------------------------------------------------------
        if not p.agent_hitl_for_high_risk_actions and not p.rag_action_gating_enabled:
            gaps.append(TrilogyCrossGap(
                gap_id="XG-007",
                title="HITL Gap Across Layers",
                description=(
                    "Neither the agent runtime (agent_hitl_for_high_risk_actions=False) "
                    "nor the RAG layer (rag_action_gating_enabled=False) requires human "
                    "approval before executing high-risk or irreversible actions.  The "
                    "entire enterprise AI stack can autonomously execute destructive "
                    "operations — file deletion, data modification, API calls with "
                    "external side effects — without any human oversight gate."
                ),
                affected_auditors=["RAG", "Agent", "Governance"],
                severity="CRITICAL",
                remediation=(
                    "Implement human-in-the-loop approval gates at the agent runtime "
                    "(agent_hitl_for_high_risk_actions) for all irreversible or "
                    "high-impact actions; enable RAG action gating "
                    "(rag_action_gating_enabled) to enforce tool allowlists and "
                    "approval requirements at the retrieval layer; define 'high-risk "
                    "action' criteria in the formal AI policy per NIST AI 600-1 and "
                    "CSA ATF Level 2."
                ),
            ))

        return gaps


# ---------------------------------------------------------------------------
# Demo helper
# ---------------------------------------------------------------------------


def _print_result(result: TrilogyAuditResult) -> None:
    """Print a ``TrilogyAuditResult`` summary to stdout."""
    print(result.summary())
    print()


# ---------------------------------------------------------------------------
# __main__ demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    orchestrator = TrilogyAuditOrchestrator()

    # ------------------------------------------------------------------
    # Profile 1 — Minimal
    # All controls absent; represents a prototype system that has been
    # deployed without any security review.
    # Expected: very low scores across all three layers, Sandbox maturity
    # everywhere, multiple CRITICAL cross-gaps.
    # ------------------------------------------------------------------
    minimal_profile = TrilogySystemProfile(
        system_id="minimal-enterprise-ai",
        # All fields left at defaults (False / "none")
    )
    minimal_result = orchestrator.audit(minimal_profile)
    print("\n--- Profile 1: Minimal (no controls implemented) ---\n")
    _print_result(minimal_result)

    # ------------------------------------------------------------------
    # Profile 2 — Partial
    # Core injection and DLP controls active; logging and HITL gaps remain.
    # Expected: medium scores, Controlled / Sandbox maturity, some
    # cross-gaps remaining, notably XG-004 (audit trail) and XG-005
    # (trust boundary policy).
    # ------------------------------------------------------------------
    partial_profile = TrilogySystemProfile(
        system_id="partial-enterprise-ai",
        # RAG — injection detection and basic isolation in place
        rag_query_injection_detection_enabled=True,
        rag_namespace_isolation_enforced=True,
        rag_cross_tenant_isolation=True,
        rag_dlp_scan_on_output=True,
        rag_vector_store_access_control=True,
        rag_pre_filter_placement="pre",
        # RAG — gaps: no action gating, no retrieval logging
        rag_action_gating_enabled=False,
        rag_retrieval_audit_logging=False,
        # Agent — identity and privilege controls in place
        agent_tool_permission_model="allowlist",
        agent_unsafe_tool_calls_blocked=True,
        agent_agent_identity_enforced=True,
        agent_privilege_escalation_prevented=True,
        agent_prompt_context_sanitized=True,
        # Agent — gaps: no HITL, no tool invocation logging
        agent_hitl_for_high_risk_actions=False,
        agent_tool_invocation_logging=False,
        # Governance — OWASP LLM and NIST basics in place
        gov_owasp_llm_prompt_injection_controls=True,
        gov_owasp_llm_sensitive_info_controls=True,
        gov_owasp_llm_data_poisoning_controls=True,
        gov_nist_govern_function_implemented=True,
        gov_iso_ai_policy_defined=True,
        gov_mitre_prompt_injection_detection=True,
        # Governance — gaps: no ASI tool misuse, no trust boundary policy
        gov_owasp_asi_goal_hijack_controls=False,
        gov_owasp_asi_tool_misuse_controls=False,
    )
    partial_result = orchestrator.audit(partial_profile)
    print("--- Profile 2: Partial (core controls, notable gaps) ---\n")
    _print_result(partial_result)

    # ------------------------------------------------------------------
    # Profile 3 — Production-Ready
    # All controls fully implemented across all three layers.
    # Expected: scores near 100, Autonomous maturity, zero cross-gaps.
    # ------------------------------------------------------------------
    production_profile = TrilogySystemProfile(
        system_id="production-enterprise-ai",
        # RAG layer — all controls active
        rag_query_injection_detection_enabled=True,
        rag_namespace_isolation_enforced=True,
        rag_cross_tenant_isolation=True,
        rag_dlp_scan_on_output=True,
        rag_action_gating_enabled=True,
        rag_query_logging_enabled=True,
        rag_vector_store_access_control=True,
        rag_document_integrity_checksums=True,
        rag_pre_filter_placement="pre",
        rag_output_schema_validation=True,
        rag_hallucination_detection_enabled=True,
        rag_retrieval_audit_logging=True,
        # Agentic layer — all controls active
        agent_tool_permission_model="rbac",
        agent_unsafe_tool_calls_blocked=True,
        agent_agent_identity_enforced=True,
        agent_privilege_escalation_prevented=True,
        agent_prompt_context_sanitized=True,
        agent_mcp_enabled=True,
        agent_mcp_source_allowlisted=True,
        agent_hitl_for_high_risk_actions=True,
        agent_multi_agent_enabled=True,
        agent_agent_trust_boundaries_defined=True,
        agent_tool_invocation_logging=True,
        # Governance layer — all controls active
        gov_owasp_llm_prompt_injection_controls=True,
        gov_owasp_llm_sensitive_info_controls=True,
        gov_owasp_llm_data_poisoning_controls=True,
        gov_owasp_asi_goal_hijack_controls=True,
        gov_owasp_asi_tool_misuse_controls=True,
        gov_nist_govern_function_implemented=True,
        gov_iso_ai_policy_defined=True,
        gov_iso_ai_risk_assessment=True,
        gov_mitre_prompt_injection_detection=True,
        gov_mitre_poisoning_detection=True,
        gov_csa_atf_sandbox_controls=True,
        gov_csa_atf_continuous_assessment=True,
    )
    production_result = orchestrator.audit(production_profile)
    print("--- Profile 3: Production-Ready (all controls implemented) ---\n")
    _print_result(production_result)
