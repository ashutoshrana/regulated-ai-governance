"""OWASP-related local policy examples, not an OWASP compliance implementation.

Taxonomy: OWASP Top 10 for Agentic Applications 2026, checked 2026-11-13.
See docs/agentic-security-trends-2026.md for sources, attribution and limits.
Class names and input/decision behavior are retained for compatibility; citation
strings were corrected. LOCAL-DLP and LOCAL-AUDIT are supplemental controls,
not OWASP category IDs. ASI05 and ASI10 have no dedicated checks here.
All checks trust caller-supplied metadata, not independent detection or proof.
Wrappers are duck-typed demonstrations, not qualified native SDK integrations.
REQUIRES_HUMAN_REVIEW is returned but NOT blocked by these wrappers; applications
must route it explicitly before executing an action. Missing metadata may pass.
No external dependencies. Run: python examples/39_owasp_agentic_top10_governance.py
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

# ---------------------------------------------------------------------------
# Per-filter result
# ---------------------------------------------------------------------------


@dataclass
class FilterResult:
    """FilterResult: illustrative metadata policy; see module limitations."""

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
    "ASI02": "Tool Misuse",
    "ASI03": "Identity & Privilege Abuse",
    "ASI04": "Agentic Supply Chain Vulnerabilities",
    "ASI05": "Unexpected Code Execution",
    "ASI06": "Memory & Context Poisoning",
    "ASI07": "Insecure Inter-Agent Communication",
    "ASI08": "Cascading Failures",
    "ASI09": "Human-Agent Trust Exploitation",
    "ASI10": "Rogue Agents",
}

# Anomaly score threshold above which retrieved content triggers human review.
# Demonstration-only threshold; no statistical calibration is performed here.
_ANOMALY_SCORE_THRESHOLD: float = 0.7

# Confidence score below which agent outputs must be disclosed as uncertain
# or the output is blocked for human review.
_CONFIDENCE_THRESHOLD: float = 0.6


# ---------------------------------------------------------------------------
# Layer 1 — ASI01 Goal Hijack + ASI06 Memory & Context Poisoning
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class OWASPAgenticInjectionFilter:
    """OWASPAgenticInjectionFilter: illustrative metadata policy; see module limitations."""

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
                    "Local demonstration policy evaluated from caller-supplied metadata; not independent verification."
                ),
                filter_name=self.FILTER_NAME,
            )

        # ASI06 — retrieved document without integrity/checksum verification
        if doc.get("retrieved_document") and not doc.get("document_integrity_verified"):
            return FilterResult(
                decision="DENIED",
                regulation=(
                    "OWASP Agentic Top 10 2026 ASI06 — Memory & Context Poisoning: "
                    "document_integrity_verified required for all retrieved documents"
                ),
                reason=(
                    "Local demonstration policy evaluated from caller-supplied metadata; not independent verification."
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
                    "Local demonstration policy evaluated from caller-supplied metadata; not independent verification."
                ),
                filter_name=self.FILTER_NAME,
            )

        # ASI06 anomaly — retrieved content with anomaly score above threshold
        anomaly_score = doc.get("anomaly_score", 0)
        if isinstance(anomaly_score, (int, float)) and anomaly_score > _ANOMALY_SCORE_THRESHOLD:
            return FilterResult(
                decision="REQUIRES_HUMAN_REVIEW",
                regulation=(
                    "OWASP Agentic Top 10 2026 ASI06 — Memory & Context Poisoning: retrieved "
                    f"content anomaly score {anomaly_score:.2f} exceeds threshold "
                    f"{_ANOMALY_SCORE_THRESHOLD:.1f}; human review required before "
                    "routing to agent context"
                ),
                reason=("Local review threshold reached in caller-supplied metadata; not an OWASP-mandated threshold."),
                filter_name=self.FILTER_NAME,
            )

        return FilterResult(
            decision="PERMITTED",
            regulation=("OWASP Agentic Top 10 2026 ASI01 (Agent Goal Hijack) + ASI06 (Memory & Context Poisoning)"),
            reason="Local demonstration policy evaluated from caller-supplied metadata; not independent verification.",
            filter_name=self.FILTER_NAME,
        )


# ---------------------------------------------------------------------------
# Layer 2 — ASI02 Tool Misuse + ASI03 Identity & Privilege Abuse + ASI04 Supply Chain
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class OWASPAgenticToolSafetyFilter:
    """OWASPAgenticToolSafetyFilter: illustrative metadata policy; see module limitations."""

    FILTER_NAME: str = "OWASP_AGENTIC_TOOL_SAFETY_FILTER"

    def filter(self, doc: dict[str, Any]) -> FilterResult:
        # ASI02 — tool invocation without allowlist verification
        if doc.get("tool_invocation") and not doc.get("tool_allowlist_verified"):
            return FilterResult(
                decision="DENIED",
                regulation=(
                    "OWASP Agentic Top 10 2026 ASI02 — Tool Misuse: "
                    "tool_allowlist_verified required for all tool invocations"
                ),
                reason=(
                    "Local demonstration policy evaluated from caller-supplied metadata; not independent verification."
                ),
                filter_name=self.FILTER_NAME,
            )

        # ASI03 — agent operating with persistent cross-session privileges
        if doc.get("cross_session_privileges"):
            return FilterResult(
                decision="DENIED",
                regulation=(
                    "OWASP Agentic Top 10 2026 ASI03 — Identity & Privilege Abuse: "
                    "cross_session_privileges must be False; agent credentials must "
                    "be session-scoped and JIT-issued"
                ),
                reason=(
                    "Local demonstration policy evaluated from caller-supplied metadata; not independent verification."
                ),
                filter_name=self.FILTER_NAME,
            )

        # ASI04 — tool/plugin without cryptographic signature verification
        if doc.get("tool_plugin_loaded") and not doc.get("tool_signature_verified"):
            return FilterResult(
                decision="DENIED",
                regulation=(
                    "OWASP Agentic Top 10 2026 ASI04 — Agentic Supply Chain Vulnerabilities: "
                    "tool_signature_verified required for all loaded tools and plugins "
                ),
                reason=(
                    "Local demonstration policy evaluated from caller-supplied metadata; not independent verification."
                ),
                filter_name=self.FILTER_NAME,
            )

        # ASI02 approval gate — tool requiring approval invoked without confirmation
        if doc.get("requires_approval") and not doc.get("human_approved"):
            return FilterResult(
                decision="REQUIRES_HUMAN_REVIEW",
                regulation=(
                    "OWASP Agentic Top 10 2026 ASI02 — Tool Misuse (approval gate): "
                    "human_approved required before invoking tools marked requires_approval"
                ),
                reason=(
                    "Local demonstration policy evaluated from caller-supplied metadata; not independent verification."
                ),
                filter_name=self.FILTER_NAME,
            )

        return FilterResult(
            decision="PERMITTED",
            regulation=(
                "OWASP Agentic Top 10 2026 ASI02 (Tool Misuse) + "
                "ASI03 (Identity & Privilege Abuse) + ASI04 (Agentic Supply Chain Vulnerabilities)"
            ),
            reason="Local demonstration policy evaluated from caller-supplied metadata; not independent verification.",
            filter_name=self.FILTER_NAME,
        )


# ---------------------------------------------------------------------------
# Layer 3 — LOCAL-DLP Data Leakage + ASI09 Human-Agent Trust Exploitation
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class OWASPAgenticDataLeakageFilter:
    """OWASPAgenticDataLeakageFilter: illustrative metadata policy; see module limitations."""

    FILTER_NAME: str = "OWASP_AGENTIC_DATA_LEAKAGE_FILTER"

    def filter(self, doc: dict[str, Any]) -> FilterResult:
        # LOCAL-DLP — agent output containing PII/sensitive data without DLP scan
        if doc.get("agent_output") and not doc.get("dlp_scan_passed"):
            return FilterResult(
                decision="DENIED",
                regulation=(
                    "Supplemental local control LOCAL-DLP — Data Leakage: "
                    "dlp_scan_passed required for all agent outputs before delivery"
                ),
                reason=(
                    "Local demonstration policy evaluated from caller-supplied metadata; not independent verification."
                ),
                filter_name=self.FILTER_NAME,
            )

        # ASI06 — agent memory not session-scoped (cross-user contamination)
        if doc.get("agent_memory_access") and not doc.get("session_scoped_memory"):
            return FilterResult(
                decision="DENIED",
                regulation=(
                    "OWASP Agentic Top 10 2026 ASI06 — Memory & Context Poisoning (memory): "
                    "session_scoped_memory required; cross-session memory creates "
                    "cross-user data contamination risk"
                ),
                reason=(
                    "Local demonstration policy evaluated from caller-supplied metadata; not independent verification."
                ),
                filter_name=self.FILTER_NAME,
            )

        # ASI09 — agent claiming capabilities beyond its actual scope
        if doc.get("claimed_capabilities_exceed_actual"):
            return FilterResult(
                decision="DENIED",
                regulation=(
                    "OWASP Agentic Top 10 2026 ASI09 — Human-Agent Trust Exploitation: "
                    "agent must not claim capabilities beyond its documented actual scope"
                ),
                reason=(
                    "Local demonstration policy evaluated from caller-supplied metadata; not independent verification."
                ),
                filter_name=self.FILTER_NAME,
            )

        # ASI09 — agent output below confidence threshold without disclosure
        confidence_score = doc.get("confidence_score", 1.0)
        if (
            isinstance(confidence_score, (int, float))
            and confidence_score < _CONFIDENCE_THRESHOLD
            and not doc.get("confidence_disclosed")
        ):
            return FilterResult(
                decision="REQUIRES_HUMAN_REVIEW",
                regulation=(
                    "OWASP Agentic Top 10 2026 ASI09 — Human-Agent Trust Exploitation: "
                    f"confidence_score {confidence_score:.2f} below threshold "
                    f"{_CONFIDENCE_THRESHOLD:.1f}; confidence_disclosed required or "
                    "human review must be triggered"
                ),
                reason=("Local review threshold reached in caller-supplied metadata; not an OWASP-mandated threshold."),
                filter_name=self.FILTER_NAME,
            )

        return FilterResult(
            decision="PERMITTED",
            regulation=("Supplemental local control LOCAL-DLP (Data Leakage) + ASI09 (Human-Agent Trust Exploitation)"),
            reason="Local demonstration policy evaluated from caller-supplied metadata; not independent verification.",
            filter_name=self.FILTER_NAME,
        )


# ---------------------------------------------------------------------------
# Layer 4 — ASI08 Cascading Failures + LOCAL-AUDIT Monitoring + ASI07 Composition
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class OWASPAgenticGovernanceFilter:
    """OWASPAgenticGovernanceFilter: illustrative metadata policy; see module limitations."""

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
                    "Local demonstration policy evaluated from caller-supplied metadata; not independent verification."
                ),
                filter_name=self.FILTER_NAME,
            )

        # LOCAL-AUDIT — agent action without audit trail
        if doc.get("agent_action") and not doc.get("audit_trail_enabled"):
            return FilterResult(
                decision="DENIED",
                regulation=(
                    "Supplemental local control LOCAL-AUDIT — Inadequate Monitoring & Audit: "
                    "audit_trail_enabled required for all agent actions"
                ),
                reason=(
                    "Local demonstration policy evaluated from caller-supplied metadata; not independent verification."
                ),
                filter_name=self.FILTER_NAME,
            )

        # ASI07 — multi-agent message without sender identity verification
        if doc.get("multi_agent_message") and not doc.get("sender_verified"):
            return FilterResult(
                decision="DENIED",
                regulation=(
                    "OWASP Agentic Top 10 2026 ASI07 — Insecure Inter-Agent Communication: "
                    "sender_verified required for all multi-agent messages"
                ),
                reason=(
                    "Local demonstration policy evaluated from caller-supplied metadata; not independent verification."
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
                    "Local demonstration policy evaluated from caller-supplied metadata; not independent verification."
                ),
                filter_name=self.FILTER_NAME,
            )

        return FilterResult(
            decision="PERMITTED",
            regulation=(
                "OWASP Agentic Top 10 2026 ASI08 (Cascading Failures) + "
                "LOCAL-AUDIT (Inadequate Monitoring & Audit) + "
                "ASI07 (Insecure Inter-Agent Communication)"
            ),
            reason="Local demonstration policy evaluated from caller-supplied metadata; not independent verification.",
            filter_name=self.FILTER_NAME,
        )


# ---------------------------------------------------------------------------
# Integration wrappers — one per AI ecosystem (8 total)
# ---------------------------------------------------------------------------


class OWASPLangChainPolicyGuard:
    """OWASPLangChainPolicyGuard: illustrative metadata policy; see module limitations."""

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
    """OWASPCrewAIGovernanceGuard: illustrative metadata policy; see module limitations."""

    name: str = "OWASPAgenticGovernanceGuard"
    description: str = (
        "Evaluates local OWASP-related demonstration policies (Injection, "
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
    """OWASPAutoGenGovernedAgent: illustrative metadata policy; see module limitations."""

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
    """OWASPSemanticKernelPlugin: illustrative metadata policy; see module limitations."""

    def __init__(self, filter_instance: Any) -> None:
        self._filter = filter_instance

    def enforce_governance(self, doc: dict[str, Any]) -> dict[str, Any]:
        result = self._filter.filter(doc)
        if result.is_denied:
            raise PermissionError(result.regulation)
        return doc


class OWASPLlamaIndexWorkflowGuard:
    """OWASPLlamaIndexWorkflowGuard: illustrative metadata policy; see module limitations."""

    def __init__(self, filter_instance: Any) -> None:
        self._filter = filter_instance

    def process_event(self, doc: dict[str, Any]) -> dict[str, Any]:
        result = self._filter.filter(doc)
        if result.is_denied:
            raise PermissionError(result.regulation)
        return doc


class OWASPHaystackGovernanceComponent:
    """OWASPHaystackGovernanceComponent: illustrative metadata policy; see module limitations."""

    def __init__(self, filter_instance: Any) -> None:
        self._filter = filter_instance

    def run(self, documents: list[dict[str, Any]]) -> dict[str, Any]:
        passed = [doc for doc in documents if not self._filter.filter(doc).is_denied]
        return {"documents": passed}


class OWASPDSPyGovernanceModule:
    """OWASPDSPyGovernanceModule: illustrative metadata policy; see module limitations."""

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
    """OWASPMAFPolicyMiddleware: illustrative metadata policy; see module limitations."""

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
    # 2. Injection — retrieved doc without integrity check → DENIED (ASI06)
    # ------------------------------------------------------------------
    _show(
        "ASI06 — Retrieved Document Without Integrity Verification",
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
    # 4. Injection — anomaly score 0.85 → REQUIRES_HUMAN_REVIEW (ASI06)
    # ------------------------------------------------------------------
    _show(
        "ASI06 — High Anomaly Score Requires Human Review",
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
    # 6. Tool Safety — cross-session privileges → DENIED (ASI03)
    # ------------------------------------------------------------------
    _show(
        "ASI03 — Agent With Cross-Session Persistent Privileges",
        OWASPAgenticToolSafetyFilter().filter(
            {
                "cross_session_privileges": True,
            }
        ),
    )

    # ------------------------------------------------------------------
    # 7. Tool Safety — plugin without signature → DENIED (ASI04)
    # ------------------------------------------------------------------
    _show(
        "ASI04 — Tool Plugin Without Cryptographic Signature Verification",
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
    # 9. Data Leakage — output without DLP scan → DENIED (LOCAL-DLP)
    # ------------------------------------------------------------------
    _show(
        "LOCAL-DLP — Agent Output Without DLP Scan",
        OWASPAgenticDataLeakageFilter().filter(
            {
                "agent_output": True,
                "dlp_scan_passed": False,
            }
        ),
    )

    # ------------------------------------------------------------------
    # 10. Memory isolation — memory not session-scoped → DENIED (ASI06)
    # ------------------------------------------------------------------
    _show(
        "ASI06 — Agent Memory Not Session-Scoped",
        OWASPAgenticDataLeakageFilter().filter(
            {
                "agent_memory_access": True,
                "session_scoped_memory": False,
            }
        ),
    )

    # ------------------------------------------------------------------
    # 11. Data Leakage — capabilities exceed actual → DENIED (ASI09)
    # ------------------------------------------------------------------
    _show(
        "ASI09 — Agent Claiming Capabilities Beyond Actual Scope",
        OWASPAgenticDataLeakageFilter().filter(
            {
                "claimed_capabilities_exceed_actual": True,
            }
        ),
    )

    # ------------------------------------------------------------------
    # 12. Data Leakage — low confidence without disclosure → RHR (ASI09)
    # ------------------------------------------------------------------
    _show(
        "ASI09 — Low Confidence Output Without Disclosure",
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
    # 14. Governance — agent action without audit trail → DENIED (LOCAL-AUDIT)
    # ------------------------------------------------------------------
    _show(
        "LOCAL-AUDIT — Agent Action Without Audit Trail",
        OWASPAgenticGovernanceFilter().filter(
            {
                "agent_action": True,
                "audit_trail_enabled": False,
            }
        ),
    )

    # ------------------------------------------------------------------
    # 15. Governance — multi-agent message unverified sender → DENIED (ASI07)
    # ------------------------------------------------------------------
    _show(
        "ASI07 — Multi-Agent Message Without Sender Verification",
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
    # 17. All filters — passing demonstration metadata → PERMITTED
    # ------------------------------------------------------------------
    _show(
        "All Controls — All Demonstration Metadata Checks Pass Document",
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
