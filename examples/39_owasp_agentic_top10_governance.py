"""
39_owasp_agentic_top10_governance.py — OWASP Top 10 for Agentic Applications 2026

Implements governance filters for the OWASP Top 10 for Agentic Applications
2026 (published December 2025 after review by 100+ security practitioners and
red teamers).  This standard is specifically designed for autonomous AI agents
with tool access, memory, and multi-step execution — distinct from the earlier
OWASP LLM Top 10 (2025) which targets LLM inference endpoints.

Demonstrates a four-layer governance framework where four independent filters
enforce distinct requirements of the OWASP Agentic Top 10:

    Layer 1  — ASI01 Goal Hijack + ASI04 Data Poisoning
               (OWASPAgenticInjectionFilter):

               ASI01 Injection — external input without injection detection
                   in agent context is denied;
               ASI04 Data Poisoning — retrieved document without integrity/
                   checksum verification is denied;
               ASI01 Indirect — tool output routed back to agent without
                   sanitisation is denied;
               ASI04 Anomaly — retrieved content with anomaly score above
                   0.7 threshold triggers REQUIRES_HUMAN_REVIEW.

    Layer 2  — ASI02 Unsafe Tool Use + ASI05 Privilege Misuse + ASI06
               Supply Chain (OWASPAgenticToolSafetyFilter):

               ASI02 Tool Allowlist — tool invoked without allowlist
                   verification is denied;
               ASI05 Privilege Misuse — agent operating with persistent
                   cross-session privileges is denied;
               ASI06 Supply Chain — tool/plugin without cryptographic
                   signature verification is denied;
               ASI02 Approval Gate — tool requiring approval invoked
                   without human confirmation triggers
                   REQUIRES_HUMAN_REVIEW.

    Layer 3  — ASI03 Data Leakage + ASI07 Human-Agent Trust Exploitation
               (OWASPAgenticDataLeakageFilter):

               ASI03 DLP — agent output containing PII/sensitive data
                   without DLP scan is denied;
               ASI03 Memory — agent memory not session-scoped is denied;
               ASI07 Trust — agent claiming capabilities beyond its actual
                   scope is denied;
               ASI07 Confidence — agent output below confidence threshold
                   without disclosure triggers REQUIRES_HUMAN_REVIEW.

    Layer 4  — ASI08 Cascading Failures + ASI09 Monitoring + ASI10
               Unvalidated Composition (OWASPAgenticGovernanceFilter):

               ASI08 Irreversible — irreversible action without rollback
                   capability is denied;
               ASI09 Audit Trail — agent action without audit trail is
                   denied;
               ASI10 Composition — multi-agent message without sender
                   identity verification is denied;
               ASI08 HITL — high-impact action without human-in-the-loop
                   gate triggers REQUIRES_HUMAN_REVIEW.

Commercial use cases
--------------------
+----------------------------------------------+-----------------------------+
| Use case                                     | Primary filters applied     |
+----------------------------------------------+-----------------------------+
| RAG-augmented customer support agent         | OWASPAgenticInjectionFilter |
| Autonomous code-generation agent             | OWASPAgenticToolSafetyFilter|
| Multi-agent financial workflow               | OWASPAgenticGovernanceFilter|
| Document processing pipeline with LLM       | OWASPAgenticInjectionFilter |
| Healthcare diagnostic AI agent              | OWASPAgenticDataLeakageFilter|
| Agentic DevOps pipeline                     | OWASPAgenticToolSafetyFilter|
| Agent-to-agent delegation workflow          | OWASPAgenticGovernanceFilter|
| Public-facing GenAI chatbot                 | OWASPAgenticDataLeakageFilter|
+----------------------------------------------+-----------------------------+

No external dependencies required.

Run:
    python examples/39_owasp_agentic_top10_governance.py
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

# ---------------------------------------------------------------------------
# Per-filter result
# ---------------------------------------------------------------------------


@dataclass
class FilterResult:
    """
    Result returned by each OWASP Agentic Top 10 governance filter.

    Attributes
    ----------
    decision : str
        One of ``"PERMITTED"``, ``"DENIED"``, ``"REQUIRES_HUMAN_REVIEW"``.
    regulation : str
        Authoritative citation for the standard/category that drove the decision.
    reason : str
        Human-readable description of the compliance finding.
    filter_name : str
        Identifier for the filter that produced this result.
    """

    decision: str
    regulation: str
    reason: str
    filter_name: str

    @property
    def is_denied(self) -> bool:
        """``True`` only when ``decision == "DENIED"``."""
        return self.decision == "DENIED"


# ---------------------------------------------------------------------------
# Shared constants
# ---------------------------------------------------------------------------

OWASP_AGENTIC_TOP10_2026: dict[str, str] = {
    "ASI01": "Agent Goal Hijack",
    "ASI02": "Unsafe Tool Use",
    "ASI03": "Data Leakage",
    "ASI04": "Data Poisoning",
    "ASI05": "Privilege Misuse",
    "ASI06": "Supply Chain Risks",
    "ASI07": "Human-Agent Trust Exploitation",
    "ASI08": "Cascading Failures",
    "ASI09": "Inadequate Monitoring & Audit",
    "ASI10": "Unvalidated Agent Composition",
}

# Anomaly score threshold above which retrieved content triggers human review.
# Scores are expected in the range [0.0, 1.0]; content above this threshold
# has statistically anomalous semantic distance from known-good documents.
_ANOMALY_SCORE_THRESHOLD: float = 0.7

# Confidence score below which agent outputs must be disclosed as uncertain
# or the output is blocked for human review.
_CONFIDENCE_THRESHOLD: float = 0.6


# ---------------------------------------------------------------------------
# Layer 1 — ASI01 Goal Hijack + ASI04 Data Poisoning
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class OWASPAgenticInjectionFilter:
    """
    Layer 1: OWASP Agentic Top 10 2026 — ASI01 Agent Goal Hijack and
    ASI04 Data Poisoning.

    ASI01 (Agent Goal Hijack) addresses indirect prompt injection: adversarial
    instructions embedded in external content (retrieved documents, tool
    outputs, web pages, memory entries) that redirect the agent's goal state
    when processed.  Unlike direct prompt injection (which targets system or
    user prompts), indirect injection operates on the agent's context through
    channels the agent trusts.

    ASI04 (Data Poisoning) addresses the persistent compromise of retrieval
    infrastructure: an attacker who can write to a vector store, document
    repository, or web-accessible data source inserts adversarial content that
    will eventually appear in the agent's context.  This is distinct from
    ASI01 in that ASI04 focuses on the retrieval source integrity, not the
    injection moment.

    Four controls apply:

    (a) ASI01 Injection Detection — external input routed into agent context
        without injection detection enabled is denied; every document, tool
        output, or environmental input must pass through an injection
        detection check before it influences the agent's goal state;
    (b) ASI04 Document Integrity — retrieved documents without cryptographic
        integrity or checksum verification are denied; document integrity
        verification ensures the retrieved content has not been modified
        since it was indexed by a trusted source;
    (c) ASI01 Tool Output Sanitisation — tool outputs routed back into agent
        context without sanitisation are denied; raw tool output may contain
        embedded adversarial instructions and must be sanitised before
        re-injection into the agent's context window;
    (d) ASI04 Anomaly Scoring — retrieved content with a semantic anomaly
        score above 0.7 (indicating statistically unusual content relative
        to known-good documents) triggers REQUIRES_HUMAN_REVIEW; anomaly
        scoring provides a probabilistic early-warning layer complementing
        cryptographic integrity checks.

    References
    ----------
    OWASP Top 10 for Agentic Applications 2026 (December 2025)
        ASI01: Agent Goal Hijack — Indirect Prompt Injection
        ASI04: Data Poisoning — Corrupted Retrieval Sources
    MITRE ATLAS v5.1 (November 2025)
        AML.T0051.000 — Indirect Prompt Injection
        AML.T0069 — RAG Database Prompting
    CSA Agentic Trust Framework v1.0 (February 2026)
        Level 2 Controlled Production — injection detection required
    """

    FILTER_NAME: str = "OWASP_AGENTIC_INJECTION_FILTER"

    def filter(self, doc: dict[str, Any]) -> FilterResult:
        # ASI01 — unvalidated external input without injection detection
        if doc.get("external_input") and not doc.get("injection_detection_enabled"):
            return FilterResult(
                decision="DENIED",
                regulation=(
                    "OWASP Agentic Top 10 2026 ASI01 — Agent Goal Hijack: "
                    "injection_detection_enabled required for all external input "
                    "routed into agent context"
                ),
                reason=(
                    "External input routed into agent context without injection "
                    "detection violates OWASP Agentic Top 10 2026 ASI01 (Agent Goal "
                    "Hijack) — indirect prompt injection embeds adversarial instructions "
                    "in retrieved documents, tool outputs, web pages, or memory entries "
                    "that redirect the agent's goal state when processed; every external "
                    "input channel must pass through an injection detection layer "
                    "(pattern matching, semantic outlier detection, or sandboxed "
                    "pre-processing) before influencing the agent's context window; "
                    "processing unvalidated external input is the primary attack vector "
                    "for agent goal hijack and is unconditionally denied under the "
                    "OWASP Agentic Top 10 2026 baseline"
                ),
                filter_name=self.FILTER_NAME,
            )

        # ASI04 — retrieved document without integrity/checksum verification
        if doc.get("retrieved_document") and not doc.get("document_integrity_verified"):
            return FilterResult(
                decision="DENIED",
                regulation=(
                    "OWASP Agentic Top 10 2026 ASI04 — Data Poisoning: "
                    "document_integrity_verified required for all retrieved documents"
                ),
                reason=(
                    "Retrieved document without integrity/checksum verification "
                    "violates OWASP Agentic Top 10 2026 ASI04 (Data Poisoning) — an "
                    "attacker who can write to a vector store, document repository, or "
                    "web-accessible retrieval source can insert adversarial content that "
                    "will appear in the agent's context when retrieved; cryptographic "
                    "integrity verification (hash comparison, digital signature, or "
                    "content-addressed storage) ensures the retrieved document has not "
                    "been modified since it was indexed by a trusted source; documents "
                    "without integrity verification must not be routed to an agent's "
                    "context under the OWASP Agentic Top 10 2026 ASI04 control"
                ),
                filter_name=self.FILTER_NAME,
            )

        # ASI01 indirect — tool output routed back to agent without sanitisation
        if doc.get("tool_output") and not doc.get("output_sanitized"):
            return FilterResult(
                decision="DENIED",
                regulation=(
                    "OWASP Agentic Top 10 2026 ASI01 — Agent Goal Hijack (indirect): "
                    "output_sanitized required before tool output is re-injected into "
                    "agent context"
                ),
                reason=(
                    "Tool output routed back into agent context without sanitisation "
                    "violates OWASP Agentic Top 10 2026 ASI01 (Agent Goal Hijack — "
                    "indirect injection via tool outputs) — tool return values may "
                    "contain attacker-controlled content if the tool accessed external "
                    "data sources, executed shell commands, or fetched web content; "
                    "raw tool output must be sanitised (malicious instruction pattern "
                    "stripping, encoding normalisation, and semantic intent check) "
                    "before re-injection into the agent's context window; unsanitised "
                    "tool output is a confirmed attack vector per MITRE ATLAS v5.1 "
                    "AML.T0067 and is unconditionally denied under ASI01"
                ),
                filter_name=self.FILTER_NAME,
            )

        # ASI04 anomaly — retrieved content with anomaly score above threshold
        anomaly_score = doc.get("anomaly_score", 0)
        if isinstance(anomaly_score, (int, float)) and anomaly_score > _ANOMALY_SCORE_THRESHOLD:
            return FilterResult(
                decision="REQUIRES_HUMAN_REVIEW",
                regulation=(
                    "OWASP Agentic Top 10 2026 ASI04 — Data Poisoning: retrieved "
                    f"content anomaly score {anomaly_score:.2f} exceeds threshold "
                    f"{_ANOMALY_SCORE_THRESHOLD:.1f}; human review required before "
                    "routing to agent context"
                ),
                reason=(
                    f"Retrieved content with anomaly score {anomaly_score:.2f} exceeds "
                    f"the {_ANOMALY_SCORE_THRESHOLD:.1f} threshold and requires human "
                    "review under OWASP Agentic Top 10 2026 ASI04 (Data Poisoning) — "
                    "semantic anomaly scoring measures the statistical distance of "
                    "retrieved content from known-good document distributions; a score "
                    "above the threshold indicates content that is unusually dissimilar "
                    "to the indexed baseline, which may indicate adversarial content "
                    "injection, corruption of the retrieval source, or content that was "
                    "not present during the last integrity audit; human review is "
                    "required to determine whether the anomalous content is legitimate "
                    "before it is routed to the agent's context window"
                ),
                filter_name=self.FILTER_NAME,
            )

        return FilterResult(
            decision="PERMITTED",
            regulation=("OWASP Agentic Top 10 2026 ASI01 (Agent Goal Hijack) + ASI04 (Data Poisoning)"),
            reason="OWASP Agentic injection and data poisoning controls — compliant",
            filter_name=self.FILTER_NAME,
        )


# ---------------------------------------------------------------------------
# Layer 2 — ASI02 Unsafe Tool Use + ASI05 Privilege Misuse + ASI06 Supply Chain
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class OWASPAgenticToolSafetyFilter:
    """
    Layer 2: OWASP Agentic Top 10 2026 — ASI02 Unsafe Tool Use,
    ASI05 Privilege Misuse, and ASI06 Supply Chain Risks.

    ASI02 (Unsafe Tool Use) addresses typosquatting attacks on tool names
    and over-privileged tool access.  An attacker registers a tool with a
    name visually similar to a legitimate tool; the agent selects it based
    on name matching.  The correct mitigation is an explicit allowlist — not
    a blocklist — so that only cryptographically verified, pre-approved tools
    can be invoked.

    ASI05 (Privilege Misuse) addresses inherited and retained privileges.
    Agents that inherit user credentials or retain cross-session privileges
    become persistent high-privilege entities.  JIT (just-in-time) access —
    credentials issued at session start and revoked at session end — is the
    required mitigation.

    ASI06 (Supply Chain Risks) addresses compromised plugins and MCP packages.
    The first malicious MCP package (September 2025) remained undetected for
    two weeks; CVE-2025-6514 documented command injection via malicious MCP
    server tool definitions.  Cryptographic signature verification of all
    tool definitions is required.

    Four controls apply:

    (a) ASI02 Tool Allowlist — tool invocation without allowlist verification
        is denied; allowlist enforcement (not blocklisting) is the baseline
        control for ASI02;
    (b) ASI05 Cross-Session Privileges — agent operating with persistent
        cross-session privileges is denied; credentials must be session-scoped
        and JIT-issued;
    (c) ASI06 Tool Signature — tool/plugin without cryptographic signature
        verification is denied; MCP server identity and tool definition
        integrity must be verified;
    (d) ASI02 Approval Gate — tool requiring approval invoked without human
        confirmation triggers REQUIRES_HUMAN_REVIEW.

    References
    ----------
    OWASP Top 10 for Agentic Applications 2026 (December 2025)
        ASI02: Unsafe Tool Use — Typosquatting, Over-Privilege
        ASI05: Privilege Misuse — Inherited/Retained Privileges
        ASI06: Supply Chain Risks — Compromised Plugins, Malicious MCP
    CVE-2025-6514 — Command injection in malicious MCP servers
    NIST AI Agent Standards Initiative (February 2026)
        AI Agent Interoperability Profile (Q4 2026) — JIT access requirement
    CSA Agentic Trust Framework v1.0 (February 2026)
        Level 2 Controlled Production — tool allowlist required
        Level 3 Trusted Production — cryptographic verification required
    """

    FILTER_NAME: str = "OWASP_AGENTIC_TOOL_SAFETY_FILTER"

    def filter(self, doc: dict[str, Any]) -> FilterResult:
        # ASI02 — tool invocation without allowlist verification
        if doc.get("tool_invocation") and not doc.get("tool_allowlist_verified"):
            return FilterResult(
                decision="DENIED",
                regulation=(
                    "OWASP Agentic Top 10 2026 ASI02 — Unsafe Tool Use: "
                    "tool_allowlist_verified required for all tool invocations"
                ),
                reason=(
                    "Tool invocation without allowlist verification violates OWASP "
                    "Agentic Top 10 2026 ASI02 (Unsafe Tool Use) — typosquatting "
                    "attacks register tools with names visually similar to legitimate "
                    "tools (e.g. 'searh_web' for 'search_web'); agents selecting tools "
                    "by name similarity without an explicit allowlist will select the "
                    "malicious tool; the correct control is an explicit allowlist of "
                    "approved tools identified by exact name and cryptographic "
                    "signature, not a blocklist of known-bad names which can never be "
                    "complete; tool invocations against tools not present in the "
                    "verified allowlist are unconditionally denied under ASI02 as "
                    "confirmed by the CSA Agentic Trust Framework Level 2 requirement"
                ),
                filter_name=self.FILTER_NAME,
            )

        # ASI05 — agent operating with persistent cross-session privileges
        if doc.get("cross_session_privileges"):
            return FilterResult(
                decision="DENIED",
                regulation=(
                    "OWASP Agentic Top 10 2026 ASI05 — Privilege Misuse: "
                    "cross_session_privileges must be False; agent credentials must "
                    "be session-scoped and JIT-issued"
                ),
                reason=(
                    "Agent operating with persistent cross-session privileges violates "
                    "OWASP Agentic Top 10 2026 ASI05 (Privilege Misuse) — agents that "
                    "retain credentials, tokens, or capability grants from previous "
                    "sessions become persistent high-privilege entities; a compromised "
                    "or injected agent with cross-session privileges can access "
                    "resources far beyond the scope of any single legitimate request; "
                    "the required mitigation is JIT (just-in-time) access: agent "
                    "credentials issued at session start, scoped to the authenticated "
                    "session, and revoked at session end; this requirement is "
                    "formalised in the NIST AI Agent Interoperability Profile (Q4 2026) "
                    "and the CSA ATF Level 2 Controlled Production baseline"
                ),
                filter_name=self.FILTER_NAME,
            )

        # ASI06 — tool/plugin without cryptographic signature verification
        if doc.get("tool_plugin_loaded") and not doc.get("tool_signature_verified"):
            return FilterResult(
                decision="DENIED",
                regulation=(
                    "OWASP Agentic Top 10 2026 ASI06 — Supply Chain Risks: "
                    "tool_signature_verified required for all loaded tools and plugins "
                    "(see also CVE-2025-6514)"
                ),
                reason=(
                    "Tool or plugin loaded without cryptographic signature verification "
                    "violates OWASP Agentic Top 10 2026 ASI06 (Supply Chain Risks) — "
                    "the first confirmed malicious MCP package (September 2025) remained "
                    "undetected for approximately two weeks; CVE-2025-6514 documented "
                    "command injection in malicious MCP server tool definitions; any "
                    "unverified dependency in the tool supply chain is a potential "
                    "lateral movement vector; all MCP server identities and tool "
                    "definition schemas must be verified against cryptographic "
                    "signatures from a trusted, internal tool registry before the tool "
                    "is registered for agent use; loading tools from public registries "
                    "without signature verification is unconditionally denied under "
                    "ASI06 as confirmed by the CSA ATF Level 3 Trusted Production "
                    "requirement"
                ),
                filter_name=self.FILTER_NAME,
            )

        # ASI02 approval gate — tool requiring approval invoked without confirmation
        if doc.get("requires_approval") and not doc.get("human_approved"):
            return FilterResult(
                decision="REQUIRES_HUMAN_REVIEW",
                regulation=(
                    "OWASP Agentic Top 10 2026 ASI02 — Unsafe Tool Use (approval gate): "
                    "human_approved required before invoking tools marked requires_approval"
                ),
                reason=(
                    "Tool requiring human approval invoked without confirmation triggers "
                    "REQUIRES_HUMAN_REVIEW under OWASP Agentic Top 10 2026 ASI02 "
                    "(Unsafe Tool Use — approval gate) — tools with significant side "
                    "effects (send email, execute shell, modify database, purchase "
                    "resources) must be designated as requiring approval; when an agent "
                    "selects such a tool, execution must pause and route to a human "
                    "operator for confirmation before the tool call is executed; "
                    "this gate is distinct from the tool allowlist control: the tool "
                    "may be on the allowlist and signature-verified, but still require "
                    "per-invocation human approval based on its effect class"
                ),
                filter_name=self.FILTER_NAME,
            )

        return FilterResult(
            decision="PERMITTED",
            regulation=(
                "OWASP Agentic Top 10 2026 ASI02 (Unsafe Tool Use) + "
                "ASI05 (Privilege Misuse) + ASI06 (Supply Chain Risks)"
            ),
            reason="OWASP Agentic tool safety and supply chain controls — compliant",
            filter_name=self.FILTER_NAME,
        )


# ---------------------------------------------------------------------------
# Layer 3 — ASI03 Data Leakage + ASI07 Human-Agent Trust Exploitation
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class OWASPAgenticDataLeakageFilter:
    """
    Layer 3: OWASP Agentic Top 10 2026 — ASI03 Data Leakage and
    ASI07 Human-Agent Trust Exploitation.

    ASI03 (Data Leakage) addresses PII and sensitive data in agent responses
    and cross-session memory contamination.  Agents retrieve documents and
    synthesise responses; without DLP scanning of outputs, sensitive data can
    appear in responses to users not authorised to receive it.  Memory systems
    persisting across sessions create a second vector: data from one session
    contaminating another user's context.

    ASI07 (Human-Agent Trust Exploitation) addresses the trust asymmetry
    between users and AI agents.  Users anthropomorphize agents — attributing
    intent, trustworthiness, and authority beyond the agent's actual scope.
    An adversary who hijacks an agent via ASI01 or ASI06 can exploit this
    trust to extract sensitive information, manipulate decisions, or perform
    social engineering that would be immediately suspicious from a human.

    Four controls apply:

    (a) ASI03 DLP — agent output containing PII or sensitive data without
        DLP scan is denied; DLP scanning must occur before output delivery;
    (b) ASI03 Memory Scope — agent memory not session-scoped is denied;
        cross-session memory creates cross-user contamination risk that
        cannot be addressed by output scanning alone;
    (c) ASI07 Capability Scope — agent claiming capabilities beyond its
        documented actual scope is denied; capability scope verification
        detects when a hijacked agent misrepresents its authority;
    (d) ASI07 Confidence — agent output below the 0.6 confidence threshold
        without confidence disclosure triggers REQUIRES_HUMAN_REVIEW.

    References
    ----------
    OWASP Top 10 for Agentic Applications 2026 (December 2025)
        ASI03: Data Leakage — PII in Outputs, Memory Contamination
        ASI07: Human-Agent Trust Exploitation — Anthropomorphization
    CSA Agentic Trust Framework v1.0 (February 2026)
        Level 2 Controlled Production — DLP on outputs, session-scoped memory
    NIST AI 600-1 GenAI Profile (July 2024) — output validation requirements
    """

    FILTER_NAME: str = "OWASP_AGENTIC_DATA_LEAKAGE_FILTER"

    def filter(self, doc: dict[str, Any]) -> FilterResult:
        # ASI03 — agent output containing PII/sensitive data without DLP scan
        if doc.get("agent_output") and not doc.get("dlp_scan_passed"):
            return FilterResult(
                decision="DENIED",
                regulation=(
                    "OWASP Agentic Top 10 2026 ASI03 — Data Leakage: "
                    "dlp_scan_passed required for all agent outputs before delivery"
                ),
                reason=(
                    "Agent output containing PII or sensitive data without DLP scan "
                    "violates OWASP Agentic Top 10 2026 ASI03 (Data Leakage) — agents "
                    "retrieve documents and synthesise responses; without DLP (Data Loss "
                    "Prevention) scanning of agent outputs, sensitive data including PII, "
                    "authentication credentials, health records, financial data, and "
                    "proprietary information can appear in responses to users who are not "
                    "authorised to receive it; DLP scanning must occur as the final gate "
                    "before agent output is delivered to any user or downstream system; "
                    "outputs that fail or have not been scanned are unconditionally denied "
                    "under OWASP Agentic Top 10 2026 ASI03"
                ),
                filter_name=self.FILTER_NAME,
            )

        # ASI03 — agent memory not session-scoped (cross-user contamination)
        if doc.get("agent_memory_access") and not doc.get("session_scoped_memory"):
            return FilterResult(
                decision="DENIED",
                regulation=(
                    "OWASP Agentic Top 10 2026 ASI03 — Data Leakage (memory): "
                    "session_scoped_memory required; cross-session memory creates "
                    "cross-user data contamination risk"
                ),
                reason=(
                    "Agent memory access not session-scoped violates OWASP Agentic "
                    "Top 10 2026 ASI03 (Data Leakage — memory contamination) — memory "
                    "systems that persist across sessions (episodic memory, semantic "
                    "memory, and working memory caches) create cross-user contamination "
                    "risk: data from User A's session can appear in User B's context "
                    "when retrieved from the shared memory store; this is a data "
                    "leakage vulnerability that cannot be addressed by output DLP "
                    "scanning alone because the leakage occurs at the memory retrieval "
                    "layer, before the output is generated; all memory must be scoped "
                    "to the authenticated session and user, purged or encrypted with "
                    "session-specific keys on session end, per CSA ATF Level 2"
                ),
                filter_name=self.FILTER_NAME,
            )

        # ASI07 — agent claiming capabilities beyond its actual scope
        if doc.get("claimed_capabilities_exceed_actual"):
            return FilterResult(
                decision="DENIED",
                regulation=(
                    "OWASP Agentic Top 10 2026 ASI07 — Human-Agent Trust Exploitation: "
                    "agent must not claim capabilities beyond its documented actual scope"
                ),
                reason=(
                    "Agent claiming capabilities beyond its actual documented scope "
                    "violates OWASP Agentic Top 10 2026 ASI07 (Human-Agent Trust "
                    "Exploitation) — users anthropomorphize AI agents, attributing "
                    "intent, authority, and trustworthiness beyond the agent's actual "
                    "capability scope; an adversary who hijacks an agent via indirect "
                    "injection (ASI01) or supply chain compromise (ASI06) can exploit "
                    "this trust asymmetry by causing the agent to claim capabilities or "
                    "authority it does not have, manipulating users into sharing "
                    "sensitive information or taking actions they would not otherwise "
                    "take; capability scope verification detects when an agent output "
                    "asserts capabilities inconsistent with the agent's documented "
                    "specification; such outputs are unconditionally denied under ASI07"
                ),
                filter_name=self.FILTER_NAME,
            )

        # ASI07 — agent output below confidence threshold without disclosure
        confidence_score = doc.get("confidence_score", 1.0)
        if (
            isinstance(confidence_score, (int, float))
            and confidence_score < _CONFIDENCE_THRESHOLD
            and not doc.get("confidence_disclosed")
        ):
            return FilterResult(
                decision="REQUIRES_HUMAN_REVIEW",
                regulation=(
                    "OWASP Agentic Top 10 2026 ASI07 — Human-Agent Trust Exploitation: "
                    f"confidence_score {confidence_score:.2f} below threshold "
                    f"{_CONFIDENCE_THRESHOLD:.1f}; confidence_disclosed required or "
                    "human review must be triggered"
                ),
                reason=(
                    f"Agent output with confidence score {confidence_score:.2f} below "
                    f"threshold {_CONFIDENCE_THRESHOLD:.1f} without confidence "
                    "disclosure requires human review under OWASP Agentic Top 10 2026 "
                    "ASI07 (Human-Agent Trust Exploitation — confidence misrepresentation) "
                    "— users trust agent outputs as authoritative; an agent that delivers "
                    "low-confidence outputs without disclosing uncertainty exploits the "
                    "user's tendency to over-trust AI systems; low-confidence outputs "
                    "must either include an explicit confidence disclosure in the response "
                    "metadata or be escalated to human review before delivery; this "
                    "aligns with NIST AI 600-1 GenAI Profile output validation requirements "
                    "and the CSA ATF Level 2 transparency controls"
                ),
                filter_name=self.FILTER_NAME,
            )

        return FilterResult(
            decision="PERMITTED",
            regulation=("OWASP Agentic Top 10 2026 ASI03 (Data Leakage) + ASI07 (Human-Agent Trust Exploitation)"),
            reason="OWASP Agentic data leakage and trust exploitation controls — compliant",
            filter_name=self.FILTER_NAME,
        )


# ---------------------------------------------------------------------------
# Layer 4 — ASI08 Cascading Failures + ASI09 Monitoring + ASI10 Composition
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class OWASPAgenticGovernanceFilter:
    """
    Layer 4: OWASP Agentic Top 10 2026 — ASI08 Cascading Failures,
    ASI09 Inadequate Monitoring & Audit, and ASI10 Unvalidated Agent
    Composition.

    ASI08 (Cascading Failures) addresses irreversible actions executed before
    human oversight can detect anomalies.  Agents execute irreversible actions
    (emails sent, files deleted, APIs called, purchases made) as readily as
    reversible ones unless explicitly constrained.  In multi-step workflows,
    a single compromised early step can trigger a cascade of irreversible
    downstream actions.

    ASI09 (Inadequate Monitoring & Audit) addresses the observability gap
    in agentic systems.  A single user interaction may trigger dozens of tool
    calls, memory reads, and sub-agent invocations.  Without per-step audit
    trails, it is impossible to reconstruct what the agent did, why it did it,
    and what data it accessed.

    ASI10 (Unvalidated Agent Composition) addresses multi-agent trust
    boundaries.  In multi-agent systems, messages from subagents carry no
    inherent authority and may have been generated by a compromised agent,
    injected by an adversary, or fabricated entirely.  Cryptographic sender
    identity verification is required.

    Four controls apply:

    (a) ASI08 Rollback — irreversible action without rollback capability
        is denied; compensation transactions must be defined for every
        write operation;
    (b) ASI09 Audit Trail — agent action without audit trail enabled is
        denied; structured audit records must be emitted for every tool
        invocation, memory access, and decision step;
    (c) ASI10 Sender Verification — multi-agent message without sender
        identity verification is denied; agent-specific cryptographic
        credentials must be used for A2A communication;
    (d) ASI08 Human-in-the-Loop — high-impact action without human-in-the-
        loop gate triggers REQUIRES_HUMAN_REVIEW.

    References
    ----------
    OWASP Top 10 for Agentic Applications 2026 (December 2025)
        ASI08: Cascading Failures — Irreversible Actions, Runaway Execution
        ASI09: Inadequate Monitoring & Audit — No Observability
        ASI10: Unvalidated Agent Composition — Multi-Agent Trust Boundaries
    NIST AI Agent Standards Initiative (February 2026)
        AI Agent Interoperability Profile (Q4 2026) — audit record schema,
        A2A sender identity requirements
    CSA Agentic Trust Framework v1.0 (February 2026)
        Level 3 Trusted Production — full audit trail, formal capability
        attestation
        Level 4 Autonomous — continuous monitoring, quarterly red team
    """

    FILTER_NAME: str = "OWASP_AGENTIC_GOVERNANCE_FILTER"

    def filter(self, doc: dict[str, Any]) -> FilterResult:
        # ASI08 — irreversible action without rollback capability
        if doc.get("action_irreversible") and not doc.get("rollback_available"):
            return FilterResult(
                decision="DENIED",
                regulation=(
                    "OWASP Agentic Top 10 2026 ASI08 — Cascading Failures: "
                    "rollback_available required before executing any irreversible action"
                ),
                reason=(
                    "Irreversible action without rollback capability violates OWASP "
                    "Agentic Top 10 2026 ASI08 (Cascading Failures) — agents execute "
                    "irreversible actions (email sends, file deletes, API state changes, "
                    "purchases, database writes) as readily as reversible ones unless "
                    "explicitly constrained; in a multi-step workflow, a single "
                    "compromised or erroneously-directed early step can trigger a "
                    "cascade of irreversible downstream actions before any human "
                    "oversight mechanism detects the anomaly; rollback capability "
                    "(compensation transactions, undo APIs, soft-delete patterns) must "
                    "be verified as available before any irreversible action executes; "
                    "if rollback is not available, the action must be redesigned to be "
                    "reversible or must be gated on explicit human approval per ASI08"
                ),
                filter_name=self.FILTER_NAME,
            )

        # ASI09 — agent action without audit trail
        if doc.get("agent_action") and not doc.get("audit_trail_enabled"):
            return FilterResult(
                decision="DENIED",
                regulation=(
                    "OWASP Agentic Top 10 2026 ASI09 — Inadequate Monitoring & Audit: "
                    "audit_trail_enabled required for all agent actions"
                ),
                reason=(
                    "Agent action without audit trail violates OWASP Agentic Top 10 "
                    "2026 ASI09 (Inadequate Monitoring & Audit) — agentic systems are "
                    "fundamentally harder to audit than request-response systems; a "
                    "single user interaction may trigger dozens of tool calls, memory "
                    "reads, and sub-agent invocations; without per-step audit trails "
                    "it is impossible to reconstruct what the agent did, why it did it, "
                    "and what data it accessed during an incident investigation; "
                    "structured audit records must be emitted for every tool invocation, "
                    "memory access, and agent decision step, including: actor identity, "
                    "session ID, tool name, input hash, output hash, timestamp, and "
                    "reasoning trace where available; records must be stored in an "
                    "append-only, tamper-evident log per the NIST AI Agent "
                    "Interoperability Profile audit record schema"
                ),
                filter_name=self.FILTER_NAME,
            )

        # ASI10 — multi-agent message without sender identity verification
        if doc.get("multi_agent_message") and not doc.get("sender_verified"):
            return FilterResult(
                decision="DENIED",
                regulation=(
                    "OWASP Agentic Top 10 2026 ASI10 — Unvalidated Agent Composition: "
                    "sender_verified required for all multi-agent messages"
                ),
                reason=(
                    "Multi-agent message without sender identity verification violates "
                    "OWASP Agentic Top 10 2026 ASI10 (Unvalidated Agent Composition) — "
                    "in multi-agent systems (orchestrator-subagent delegation, peer "
                    "agent coordination, human-agent-agent pipelines) messages from "
                    "other agents carry no inherent authority; a message claiming to "
                    "be from a trusted subagent may have been generated by a compromised "
                    "agent, injected by an adversary into the message channel, or "
                    "fabricated entirely; without cryptographic sender verification "
                    "using agent-specific credentials (not inherited user credentials), "
                    "any agent in the pipeline can be impersonated; the NIST AI Agent "
                    "Interoperability Profile (Q4 2026) and the A2A protocol both "
                    "require verified sender identity fields in all agent-to-agent "
                    "messages; unverified multi-agent messages are unconditionally "
                    "denied under ASI10"
                ),
                filter_name=self.FILTER_NAME,
            )

        # ASI08 human-in-the-loop — high-impact action without HITL gate
        if doc.get("action_impact") == "high" and not doc.get("human_in_loop"):
            return FilterResult(
                decision="REQUIRES_HUMAN_REVIEW",
                regulation=(
                    "OWASP Agentic Top 10 2026 ASI08 — Cascading Failures (HITL gate): "
                    "human_in_loop required for all high-impact agent actions"
                ),
                reason=(
                    "High-impact agent action without human-in-the-loop gate requires "
                    "human review under OWASP Agentic Top 10 2026 ASI08 (Cascading "
                    "Failures — human oversight) — actions classified as high-impact "
                    "(significant financial cost, data deletion, public communications, "
                    "security configuration changes, external API state modifications) "
                    "must pause execution and route to a human operator for confirmation "
                    "before proceeding; this gate is distinct from the rollback control: "
                    "the action may have rollback capability and still require per-"
                    "invocation human approval based on its impact class; the CSA ATF "
                    "Level 3 Trusted Production requirement mandates HITL checkpoints "
                    "for all high-impact operations regardless of rollback availability"
                ),
                filter_name=self.FILTER_NAME,
            )

        return FilterResult(
            decision="PERMITTED",
            regulation=(
                "OWASP Agentic Top 10 2026 ASI08 (Cascading Failures) + "
                "ASI09 (Inadequate Monitoring & Audit) + "
                "ASI10 (Unvalidated Agent Composition)"
            ),
            reason="OWASP Agentic governance, monitoring, and composition controls — compliant",
            filter_name=self.FILTER_NAME,
        )


# ---------------------------------------------------------------------------
# Integration wrappers — one per AI ecosystem (8 total)
# ---------------------------------------------------------------------------


class OWASPLangChainPolicyGuard:
    """
    LangChain integration — wraps the four OWASP Agentic governance filters
    as a LangChain-compatible ``Runnable``-style tool guard.

    Implements ``invoke(doc)`` and ``ainvoke(doc)`` so the guard can be
    inserted into a LangChain chain or used as a tool callback.  Raises
    ``PermissionError`` with the regulation citation when any filter returns
    DENIED.
    """

    def __init__(self, filter_instance: Any | None = None) -> None:
        if filter_instance is not None:
            self._filter = filter_instance
            self._multi = False
        else:
            self._filters: list[Any] = [
                OWASPAgenticInjectionFilter(),
                OWASPAgenticToolSafetyFilter(),
                OWASPAgenticDataLeakageFilter(),
                OWASPAgenticGovernanceFilter(),
            ]
            self._multi = True

    def process(self, doc: dict[str, Any]) -> dict[str, Any]:
        """Apply a single wrapped filter; raise on DENIED, pass through otherwise."""
        result = self._filter.filter(doc)
        if result.is_denied:
            raise PermissionError(result.regulation)
        return doc

    def invoke(self, doc: dict[str, Any]) -> list[FilterResult]:
        if not self._multi:
            result = self._filter.filter(doc)
            if result.is_denied:
                raise PermissionError(result.regulation)
            return [result]
        results = [f.filter(doc) for f in self._filters]
        for r in results:
            if r.is_denied:
                raise PermissionError(r.regulation)
        return results

    def ainvoke(self, doc: dict[str, Any]) -> list[FilterResult]:
        """Async-compatible entry point (synchronous implementation)."""
        return self.invoke(doc)


class OWASPCrewAIGovernanceGuard:
    """
    CrewAI integration — wraps an OWASP Agentic governance filter as a
    CrewAI ``BaseTool``-compatible guard.

    Implements ``_run(doc)`` so this class can be used as a drop-in CrewAI
    tool wrapper.  Raises ``PermissionError`` with the regulation citation
    when the filter returns DENIED.
    """

    name: str = "OWASPAgenticGovernanceGuard"
    description: str = (
        "Enforces OWASP Agentic Top 10 2026 governance policies (Injection, "
        "Tool Safety, Data Leakage, Governance) on documents processed by a "
        "CrewAI agent."
    )

    def __init__(self, filter_instance: Any) -> None:
        self._filter = filter_instance

    def _run(self, doc: dict[str, Any]) -> dict[str, Any]:
        result = self._filter.filter(doc)
        if result.is_denied:
            raise PermissionError(result.regulation)
        return doc


class OWASPAutoGenGovernedAgent:
    """
    AutoGen integration — duck-typed ``ConversableAgent`` wrapper enforcing
    OWASP Agentic governance on each ``generate_reply`` call.

    NOTE: AutoGen (``pyautogen``) is in maintenance mode as of 2026.  New
    projects should use ``OWASPMAFPolicyMiddleware`` for the Microsoft Agent
    Framework.  Raises ``PermissionError`` with the regulation citation when
    the filter returns DENIED.
    """

    def __init__(self, filter_instance: Any) -> None:
        self._filter = filter_instance

    def generate_reply(
        self,
        messages: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        doc = messages or {}
        result = self._filter.filter(doc)
        if result.is_denied:
            raise PermissionError(result.regulation)
        return doc


class OWASPSemanticKernelPlugin:
    """
    Semantic Kernel integration — wraps an OWASP Agentic governance filter
    as an SK ``Plugin``-compatible function provider.

    NOTE: Semantic Kernel is in maintenance mode as of 2026.  New projects
    should use ``OWASPMAFPolicyMiddleware`` for the Microsoft Agent Framework.
    Raises ``PermissionError`` with the regulation citation when the filter
    returns DENIED.
    """

    def __init__(self, filter_instance: Any) -> None:
        self._filter = filter_instance

    def enforce_governance(self, doc: dict[str, Any]) -> dict[str, Any]:
        result = self._filter.filter(doc)
        if result.is_denied:
            raise PermissionError(result.regulation)
        return doc


class OWASPLlamaIndexWorkflowGuard:
    """
    LlamaIndex integration — workflow guard step enforcing OWASP Agentic
    governance between retrieval and synthesis steps.

    Implements ``process_event(doc)`` compatible with LlamaIndex
    ``WorkflowStep`` protocol (LlamaIndex 0.14.x).  Raises ``PermissionError``
    with the regulation citation when the filter returns DENIED.
    """

    def __init__(self, filter_instance: Any) -> None:
        self._filter = filter_instance

    def process_event(self, doc: dict[str, Any]) -> dict[str, Any]:
        result = self._filter.filter(doc)
        if result.is_denied:
            raise PermissionError(result.regulation)
        return doc


class OWASPHaystackGovernanceComponent:
    """
    Haystack integration — ``@component``-compatible governance filter for
    Haystack 2.x pipelines (current: Haystack 2.27.0).

    Implements ``run(documents)`` following the Haystack component protocol.
    Filters each document dict individually; denied documents are excluded
    from the output.  Does not raise; returns only permitted documents.
    """

    def __init__(self, filter_instance: Any) -> None:
        self._filter = filter_instance

    def run(self, documents: list[dict[str, Any]]) -> dict[str, Any]:
        passed = [doc for doc in documents if not self._filter.filter(doc).is_denied]
        return {"documents": passed}


class OWASPDSPyGovernanceModule:
    """
    DSPy integration — governance-enforcing wrapper for DSPy ``Module``
    objects (DSPy >= 2.5.0, Pydantic v2).

    Implements ``forward(doc, **kwargs)`` and delegates to the wrapped module
    only after the filter passes.  Raises ``PermissionError`` with the
    regulation citation when the filter returns DENIED.
    """

    def __init__(self, filter_instance: Any, module: Any) -> None:
        self._filter = filter_instance
        self._module = module

    def forward(self, doc: dict[str, Any], **kwargs: Any) -> Any:
        result = self._filter.filter(doc)
        if result.is_denied:
            raise PermissionError(result.regulation)
        return self._module(doc, **kwargs)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._module, name)


class OWASPMAFPolicyMiddleware:
    """
    Microsoft Agent Framework (MAF) integration — middleware intercepting
    agent messages and applying OWASP Agentic governance filters.

    MAF is the enterprise successor to AutoGen and Semantic Kernel (released
    2025).  Implements ``process(message, next_handler)`` so this middleware
    can be registered in an MAF agent pipeline.  Raises ``PermissionError``
    with the regulation citation when the filter returns DENIED.
    """

    def __init__(self, filter_instance: Any) -> None:
        self._filter = filter_instance

    def process(self, message: dict[str, Any], next_handler: Any) -> Any:
        result = self._filter.filter(message)
        if result.is_denied:
            raise PermissionError(result.regulation)
        return next_handler(message)


# ---------------------------------------------------------------------------
# Demo helpers
# ---------------------------------------------------------------------------


def _show(title: str, result: FilterResult) -> None:
    print("=" * 70)
    print(f"Scenario : {title}")
    print(f"  Decision   : {result.decision}")
    print(f"  Regulation : {result.regulation}")
    print(f"  Reason     : {result.reason[:120]}...")
    print(f"  is_denied  : {result.is_denied}")
    print("=" * 70)


if __name__ == "__main__":
    # ------------------------------------------------------------------
    # 1. Injection — external input without injection detection → DENIED (ASI01)
    # ------------------------------------------------------------------
    _show(
        "ASI01 — External Input Without Injection Detection",
        OWASPAgenticInjectionFilter().filter(
            {
                "external_input": True,
                "injection_detection_enabled": False,
            }
        ),
    )

    # ------------------------------------------------------------------
    # 2. Injection — retrieved doc without integrity check → DENIED (ASI04)
    # ------------------------------------------------------------------
    _show(
        "ASI04 — Retrieved Document Without Integrity Verification",
        OWASPAgenticInjectionFilter().filter(
            {
                "retrieved_document": True,
                "document_integrity_verified": False,
            }
        ),
    )

    # ------------------------------------------------------------------
    # 3. Injection — tool output without sanitisation → DENIED (ASI01 indirect)
    # ------------------------------------------------------------------
    _show(
        "ASI01 Indirect — Tool Output Without Sanitisation",
        OWASPAgenticInjectionFilter().filter(
            {
                "tool_output": True,
                "output_sanitized": False,
            }
        ),
    )

    # ------------------------------------------------------------------
    # 4. Injection — anomaly score 0.85 → REQUIRES_HUMAN_REVIEW (ASI04)
    # ------------------------------------------------------------------
    _show(
        "ASI04 — High Anomaly Score Requires Human Review",
        OWASPAgenticInjectionFilter().filter(
            {
                "anomaly_score": 0.85,
            }
        ),
    )

    # ------------------------------------------------------------------
    # 5. Tool Safety — tool invoked without allowlist → DENIED (ASI02)
    # ------------------------------------------------------------------
    _show(
        "ASI02 — Tool Invocation Without Allowlist Verification",
        OWASPAgenticToolSafetyFilter().filter(
            {
                "tool_invocation": True,
                "tool_allowlist_verified": False,
            }
        ),
    )

    # ------------------------------------------------------------------
    # 6. Tool Safety — cross-session privileges → DENIED (ASI05)
    # ------------------------------------------------------------------
    _show(
        "ASI05 — Agent With Cross-Session Persistent Privileges",
        OWASPAgenticToolSafetyFilter().filter(
            {
                "cross_session_privileges": True,
            }
        ),
    )

    # ------------------------------------------------------------------
    # 7. Tool Safety — plugin without signature → DENIED (ASI06)
    # ------------------------------------------------------------------
    _show(
        "ASI06 — Tool Plugin Without Cryptographic Signature Verification",
        OWASPAgenticToolSafetyFilter().filter(
            {
                "tool_plugin_loaded": True,
                "tool_signature_verified": False,
            }
        ),
    )

    # ------------------------------------------------------------------
    # 8. Tool Safety — approval required, no human approval → RHR (ASI02)
    # ------------------------------------------------------------------
    _show(
        "ASI02 Approval Gate — Requires Approval Without Human Confirmed",
        OWASPAgenticToolSafetyFilter().filter(
            {
                "requires_approval": True,
                "human_approved": False,
            }
        ),
    )

    # ------------------------------------------------------------------
    # 9. Data Leakage — output without DLP scan → DENIED (ASI03)
    # ------------------------------------------------------------------
    _show(
        "ASI03 — Agent Output Without DLP Scan",
        OWASPAgenticDataLeakageFilter().filter(
            {
                "agent_output": True,
                "dlp_scan_passed": False,
            }
        ),
    )

    # ------------------------------------------------------------------
    # 10. Data Leakage — memory not session-scoped → DENIED (ASI03)
    # ------------------------------------------------------------------
    _show(
        "ASI03 — Agent Memory Not Session-Scoped",
        OWASPAgenticDataLeakageFilter().filter(
            {
                "agent_memory_access": True,
                "session_scoped_memory": False,
            }
        ),
    )

    # ------------------------------------------------------------------
    # 11. Data Leakage — capabilities exceed actual → DENIED (ASI07)
    # ------------------------------------------------------------------
    _show(
        "ASI07 — Agent Claiming Capabilities Beyond Actual Scope",
        OWASPAgenticDataLeakageFilter().filter(
            {
                "claimed_capabilities_exceed_actual": True,
            }
        ),
    )

    # ------------------------------------------------------------------
    # 12. Data Leakage — low confidence without disclosure → RHR (ASI07)
    # ------------------------------------------------------------------
    _show(
        "ASI07 — Low Confidence Output Without Disclosure",
        OWASPAgenticDataLeakageFilter().filter(
            {
                "confidence_score": 0.45,
                "confidence_disclosed": False,
            }
        ),
    )

    # ------------------------------------------------------------------
    # 13. Governance — irreversible action without rollback → DENIED (ASI08)
    # ------------------------------------------------------------------
    _show(
        "ASI08 — Irreversible Action Without Rollback Capability",
        OWASPAgenticGovernanceFilter().filter(
            {
                "action_irreversible": True,
                "rollback_available": False,
            }
        ),
    )

    # ------------------------------------------------------------------
    # 14. Governance — agent action without audit trail → DENIED (ASI09)
    # ------------------------------------------------------------------
    _show(
        "ASI09 — Agent Action Without Audit Trail",
        OWASPAgenticGovernanceFilter().filter(
            {
                "agent_action": True,
                "audit_trail_enabled": False,
            }
        ),
    )

    # ------------------------------------------------------------------
    # 15. Governance — multi-agent message unverified sender → DENIED (ASI10)
    # ------------------------------------------------------------------
    _show(
        "ASI10 — Multi-Agent Message Without Sender Verification",
        OWASPAgenticGovernanceFilter().filter(
            {
                "multi_agent_message": True,
                "sender_verified": False,
            }
        ),
    )

    # ------------------------------------------------------------------
    # 16. Governance — high-impact action without HITL → RHR (ASI08)
    # ------------------------------------------------------------------
    _show(
        "ASI08 HITL — High-Impact Action Without Human-in-the-Loop",
        OWASPAgenticGovernanceFilter().filter(
            {
                "action_impact": "high",
                "human_in_loop": False,
            }
        ),
    )

    # ------------------------------------------------------------------
    # 17. All filters — fully compliant → PERMITTED
    # ------------------------------------------------------------------
    _show(
        "All Controls — Fully Compliant Document",
        OWASPAgenticInjectionFilter().filter(
            {
                "external_input": True,
                "injection_detection_enabled": True,
                "retrieved_document": True,
                "document_integrity_verified": True,
                "tool_output": True,
                "output_sanitized": True,
                "anomaly_score": 0.2,
            }
        ),
    )
